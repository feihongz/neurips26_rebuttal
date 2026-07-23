import numpy as np
import torch
import torch.nn.functional as F
import torch.optim as optim
from torch.amp import autocast, GradScaler

from .model import InvertibleGENIEOAffineActor, QNetwork, ValueNetwork
from .utils import hard_update, soft_update


class flowAC(object):
    """
    GENIEO-only minimal training core (new affine version).
    """

    def __init__(self, num_inputs, action_space, args):
        self.gamma = args.gamma
        self.tau = args.tau
        self.quantile = args.quantile
        self.noise_level = args.epsilon
        self.action_space = action_space
        self.sample_count = 0

        self.policy_type = "GENIEO"
        self.action_dim = action_space.shape[0]
        self.critic_action_dim = self.action_dim * 2
        self.target_update_interval = args.target_update_interval
        self.device = torch.device(f"cuda:{args.device}" if args.cuda else "cpu")
        self.amp_enabled = args.cuda and torch.cuda.is_available()
        self.amp_dtype = torch.bfloat16
        self.scaler = GradScaler(enabled=self.amp_enabled and self.amp_dtype == torch.float16)

        self.critic = QNetwork(num_inputs, self.critic_action_dim, args.hidden_size).to(self.device)
        self.critic_optim = optim.Adam(self.critic.parameters(), lr=args.lr)
        self.critic_target = QNetwork(num_inputs, self.critic_action_dim, args.hidden_size).to(self.device)
        hard_update(self.critic_target, self.critic)

        self.genieo_actor_lr_scale = float(getattr(args, "genieo_actor_lr_scale", 0.1))
        self.genieo_ent_lr_scale = float(getattr(args, "genieo_ent_lr_scale", 0.1))
        self.genieo_reward_scale = float(getattr(args, "genieo_reward_scale", 1.0))
        self.genieo_zero_last_init_scale = float(getattr(args, "genieo_zero_last_init_scale", 1e-4))
        self.genieo_ent_grad_clip = float(getattr(args, "genieo_ent_grad_clip", 1.0))
        self.genieo_actor_grad_clip = float(getattr(args, "genieo_actor_grad_clip", 10.0))
        self.genieo_log_ent_min = float(getattr(args, "genieo_log_ent_min", -10.0))
        self.genieo_log_ent_max = float(getattr(args, "genieo_log_ent_max", 0.0))
        self.genieo_p_mix = float(getattr(args, "p_mix", 1.0))

        actor_lr = args.lr * self.genieo_actor_lr_scale
        ent_lr = args.lr * self.genieo_ent_lr_scale

        self.policy = InvertibleGENIEOAffineActor(
            num_inputs,
            action_space.shape[0],
            args.hidden_size,
            args.steps,
            action_space,
            # Keep the default actor conservative: small bounded log-scale,
            # slow warmup, and no extra squash correction unless explicitly enabled.
            p_mix=self.genieo_p_mix,
            base_std=float(getattr(args, "genieo_init_std", 1.0)),
            tail_init_scale=self.genieo_zero_last_init_scale,
            log_scale_bound=float(getattr(args, "genieo_log_scale_bound", 0.02)),
            log_scale_warmup=int(getattr(args, "genieo_log_scale_warmup", 100000)),
            use_projected_squash_correction=bool(
                getattr(args, "genieo_use_projected_squash_correction", False)
            ),
        ).to(self.device)
        self.policy_optim = optim.Adam(self.policy.parameters(), lr=actor_lr)

        self.ent_coef = float(getattr(args, "genieo_ent_coef", getattr(args, "ent_coef", 0.001)))
        self.comp_coef = float(getattr(args, "genieo_comp_coef", getattr(args, "comp_coef", 0.1)))
        self.genieo_explore_noise = float(getattr(args, "genieo_explore_noise", 0.0))
        self.genieo_use_mean_action = bool(getattr(args, "genieo_use_mean_action", False))
        self.genieo_target_tau = float(getattr(args, "genieo_target_tau", 0.005))
        self.genieo_auto_entropy_tuning = bool(getattr(args, "genieo_auto_entropy_tuning", True))
        self.genieo_target_entropy_scale = float(getattr(args, "genieo_target_entropy_scale", 1.0))
        self.target_entropy = -2.0 * float(action_space.shape[0]) * self.genieo_target_entropy_scale

        self.last_genieo_env_action = None
        self.last_genieo_replay_action = None
        self.last_genieo_debug = {}

        if self.genieo_auto_entropy_tuning:
            init_ent_coef = max(self.ent_coef, 1e-6)
            self.log_ent_coef = torch.tensor(
                [np.log(init_ent_coef)],
                device=self.device,
                requires_grad=True,
                dtype=torch.float32,
            )
            self.log_ent_coef.data.clamp_(
                min=self.genieo_log_ent_min,
                max=self.genieo_log_ent_max,
            )
            self.ent_coef_optim = optim.Adam([self.log_ent_coef], lr=ent_lr)
            self.ent_coef = float(init_ent_coef)
        else:
            self.log_ent_coef = None
            self.ent_coef_optim = None

        self.critic_buffer = QNetwork(num_inputs, self.critic_action_dim, args.hidden_size).to(self.device)
        self.critic_buffer_optim = optim.Adam(self.critic_buffer.parameters(), lr=args.lr)
        hard_update(self.critic_buffer, self.critic)

        self.critic_target_buffer = QNetwork(num_inputs, self.critic_action_dim, args.hidden_size).to(self.device)
        hard_update(self.critic_target_buffer, self.critic_buffer)
        self.V_critic_buffer = ValueNetwork(num_inputs, args.hidden_size).to(device=self.device)
        self.V_critic_buffer_optim = optim.Adam(self.V_critic_buffer.parameters(), lr=args.lr)

    def select_action(self, state, evaluate=False):
        if not evaluate:
            self.sample_count += 1
            if self.sample_count % 1e5 == 0:
                self.noise_level = self.noise_level * 0.8

        state = torch.as_tensor(state, dtype=torch.float32, device=self.device).unsqueeze(0)
        with torch.no_grad():
            if evaluate:
                action = self.policy.mean_action(state)
                proto_action = self.policy.unsquash_from_env(action)
                replay_action = torch.cat([proto_action, proto_action], dim=-1)
            elif self.genieo_use_mean_action:
                action = self.policy.mean_action(state)
                if self.genieo_explore_noise > 0:
                    noise = torch.randn_like(action) * self.genieo_explore_noise
                    noise = torch.clamp(noise, -0.25, 0.25)
                    action = action + noise
                action_low = torch.as_tensor(self.action_space.low, device=action.device, dtype=action.dtype).view(1, -1)
                action_high = torch.as_tensor(self.action_space.high, device=action.device, dtype=action.dtype).view(1, -1)
                action = torch.max(torch.min(action, action_high), action_low)
                proto_action = self.policy.unsquash_from_env(action)
                replay_action = torch.cat([proto_action, proto_action], dim=-1)
            else:
                action, (x_1, y_1), _ = self.policy.sample_env(state)
                replay_action = torch.cat([x_1, y_1], dim=-1)

            if not evaluate:
                self.last_genieo_env_action = action.detach().cpu().numpy()[0].astype(np.float32).copy()
                self.last_genieo_replay_action = replay_action.detach().cpu().numpy()[0].astype(np.float32).copy()

        return action.detach().cpu().numpy()[0].clip(self.action_space.low, self.action_space.high)

    def replay_action_from_env(self, action_env):
        action_np = np.asarray(action_env, dtype=np.float32).reshape(-1)
        if (
            self.last_genieo_env_action is not None
            and np.allclose(action_np, self.last_genieo_env_action, atol=1e-6, rtol=1e-6)
        ):
            replay_action = self.last_genieo_replay_action.copy()
            self.last_genieo_env_action = None
            self.last_genieo_replay_action = None
            return replay_action

        with torch.no_grad():
            action_tensor = torch.as_tensor(action_np, device=self.device, dtype=torch.float32).unsqueeze(0)
            proto_action = self.policy.unsquash_from_env(action_tensor)
            replay_action = torch.cat([proto_action, proto_action], dim=-1)
        return replay_action.squeeze(0).cpu().numpy().astype(np.float32)

    def update_critic(self, state_batch, action_batch, reward_batch, next_state_batch, mask_batch):
        with autocast(device_type=self.device.type, dtype=self.amp_dtype, enabled=self.amp_enabled):
            with torch.no_grad():
                _, (x_next, y_next), next_log_prob = self.policy.sample_with_logprob(next_state_batch)
                next_state_action = torch.cat([x_next, y_next], dim=-1).clone()

                qf1_next_target, qf2_next_target = self.critic_target(next_state_batch, next_state_action)
                qf1_next_target = qf1_next_target.clone()
                qf2_next_target = qf2_next_target.clone()
                min_qf_next_target = torch.min(qf1_next_target, qf2_next_target)
                ent_coef = self.log_ent_coef.exp() if self.genieo_auto_entropy_tuning else next_log_prob.new_tensor(self.ent_coef)
                next_q_value = reward_batch + mask_batch * self.gamma * (min_qf_next_target - ent_coef * next_log_prob)

            next_q_clone = next_q_value.clone()
            qf1, qf2 = self.critic(state_batch, action_batch)
            qf1 = qf1.clone()
            qf2 = qf2.clone()
            qf1_loss = F.mse_loss(qf1, next_q_value)
            qf2_loss = F.mse_loss(qf2, next_q_clone)
            qf_loss = qf1_loss + qf2_loss

        self.critic_optim.zero_grad()
        self.scaler.scale(qf_loss).backward()
        self.scaler.step(self.critic_optim)
        self.scaler.update()

        with autocast(device_type=self.device.type, dtype=self.amp_dtype, enabled=self.amp_enabled):
            with torch.no_grad():
                target_vf_pred = self.V_critic_buffer(next_state_batch).clone()
                next_q_value_buffer = reward_batch + mask_batch * self.gamma * target_vf_pred

            qf1_buffer, qf2_buffer = self.critic_buffer(state_batch, action_batch)
            qf1_buffer = qf1_buffer.clone()
            qf2_buffer = qf2_buffer.clone()
            q_buffer = torch.min(qf1_buffer, qf2_buffer)
            qf1_buffer_loss = F.mse_loss(qf1_buffer, next_q_value_buffer)
            qf2_buffer_loss = F.mse_loss(qf2_buffer, next_q_value_buffer)
            qf_buffer_loss = qf1_buffer_loss + qf2_buffer_loss

        self.critic_buffer_optim.zero_grad()
        self.scaler.scale(qf_buffer_loss).backward()
        self.scaler.step(self.critic_buffer_optim)
        self.scaler.update()

        with autocast(device_type=self.device.type, dtype=self.amp_dtype, enabled=self.amp_enabled):
            vf_pred = self.V_critic_buffer(state_batch).clone()
            with torch.no_grad():
                q_pred_1, q_pred_2 = self.critic_target_buffer(state_batch, action_batch)
                q_pred = torch.min(q_pred_1.clone(), q_pred_2.clone())
            vf_err = q_pred - vf_pred
            vf_sign = (vf_err < 0).float()
            vf_weight = (1 - vf_sign) * self.quantile + vf_sign * (1 - self.quantile)
            vf_loss = (vf_weight * (vf_err ** 2)).to(torch.float32).mean()

        self.V_critic_buffer_optim.zero_grad()
        self.scaler.scale(vf_loss).backward()
        self.scaler.step(self.V_critic_buffer_optim)
        self.scaler.update()
        return q_buffer.detach()

    def update_policy(self, state_batch):
        with autocast(device_type=self.device.type, dtype=self.amp_dtype, enabled=self.amp_enabled):
            _a_env, (x_1, y_1), log_prob = self.policy.sample_with_logprob(state_batch)
            aug_action = torch.cat([x_1, y_1], dim=-1)

            q1_pi, q2_pi = self.critic(state_batch, aug_action)
            min_qf_pi = torch.min(q1_pi, q2_pi)
            ent_coef = self.log_ent_coef.exp().detach() if self.genieo_auto_entropy_tuning else log_prob.new_tensor(self.ent_coef)
            q_objective = -min_qf_pi.mean()
            entropy_loss = (ent_coef * log_prob).mean()
            compression_loss = self.comp_coef * F.mse_loss(x_1, y_1)
            policy_loss = q_objective + entropy_loss + compression_loss

        self.policy_optim.zero_grad()
        self.scaler.scale(policy_loss).backward()
        if self.scaler.is_enabled():
            self.scaler.unscale_(self.policy_optim)
        torch.nn.utils.clip_grad_norm_(self.policy.parameters(), self.genieo_actor_grad_clip)
        self.scaler.step(self.policy_optim)
        self.scaler.update()

        if self.genieo_auto_entropy_tuning:
            with autocast(device_type=self.device.type, dtype=self.amp_dtype, enabled=self.amp_enabled):
                ent_coef_loss = -(self.log_ent_coef.exp() * (log_prob + self.target_entropy).detach()).mean()

            self.ent_coef_optim.zero_grad()
            self.scaler.scale(ent_coef_loss).backward()
            if self.scaler.is_enabled():
                self.scaler.unscale_(self.ent_coef_optim)
            torch.nn.utils.clip_grad_norm_([self.log_ent_coef], self.genieo_ent_grad_clip)
            self.scaler.step(self.ent_coef_optim)
            self.scaler.update()
            with torch.no_grad():
                self.log_ent_coef.clamp_(min=self.genieo_log_ent_min, max=self.genieo_log_ent_max)
            self.ent_coef = float(self.log_ent_coef.exp().item())

        if hasattr(self.policy, "last_debug"):
            self.last_genieo_debug = dict(self.policy.last_debug)

    def update_parameters(self, memory, batch_size, updates):
        state_batch, action_batch, reward_batch, next_state_batch, mask_batch = memory.sample(batch_size=batch_size)
        state_batch = torch.as_tensor(state_batch, dtype=torch.float32, device=self.device)
        next_state_batch = torch.as_tensor(next_state_batch, dtype=torch.float32, device=self.device)
        action_batch = torch.as_tensor(action_batch, dtype=torch.float32, device=self.device)
        reward_batch = torch.as_tensor(reward_batch, dtype=torch.float32, device=self.device).unsqueeze(1)
        reward_batch = reward_batch * self.genieo_reward_scale
        mask_batch = torch.as_tensor(mask_batch, dtype=torch.float32, device=self.device).unsqueeze(1)

        if hasattr(self.policy, "set_update_step"):
            self.policy.set_update_step(updates)

        self.update_critic(state_batch, action_batch, reward_batch, next_state_batch, mask_batch)

        if updates % self.target_update_interval == 0:
            self.update_policy(state_batch)
            with torch.no_grad():
                soft_update(self.critic_target, self.critic, self.genieo_target_tau)
                soft_update(self.critic_target_buffer, self.critic_buffer, self.genieo_target_tau)

    def save_checkpoint(self, path, i_episode):
        ckpt_path = path + "/" + "{}.torch".format(i_episode)
        checkpoint_dict = {
            "policy_state_dict": self.policy.state_dict(),
            "critic_state_dict": self.critic.state_dict(),
            "critic_target_state_dict": self.critic_target.state_dict(),
            "critic_optimizer_state_dict": self.critic_optim.state_dict(),
            "policy_optimizer_state_dict": self.policy_optim.state_dict(),
            "critic_buffer_state_dict": self.critic_buffer.state_dict(),
            "critic_target_buffer_state_dict": self.critic_target_buffer.state_dict(),
            "critic_buffer_optimizer_state_dict": self.critic_buffer_optim.state_dict(),
            "V_critic_buffer_state_dict": self.V_critic_buffer.state_dict(),
            "V_critic_buffer_optimizer_state_dict": self.V_critic_buffer_optim.state_dict(),
        }
        if self.genieo_auto_entropy_tuning:
            checkpoint_dict["genieo_log_ent_coef"] = self.log_ent_coef.item()
            checkpoint_dict["genieo_ent_coef"] = self.ent_coef
            checkpoint_dict["genieo_ent_coef_optim_state_dict"] = self.ent_coef_optim.state_dict()
        torch.save(checkpoint_dict, ckpt_path)

    def load_checkpoint(self, path, i_episode, evaluate=False):
        ckpt_path = path + "/" + "checkpoint/" + "best.torch"
        checkpoint = torch.load(ckpt_path)
        self.policy.load_state_dict(checkpoint["policy_state_dict"])
        self.critic.load_state_dict(checkpoint["critic_state_dict"])
        self.critic_target.load_state_dict(checkpoint["critic_target_state_dict"])
        self.critic_optim.load_state_dict(checkpoint["critic_optimizer_state_dict"])
        self.policy_optim.load_state_dict(checkpoint["policy_optimizer_state_dict"])
        self.critic_buffer.load_state_dict(checkpoint["critic_buffer_state_dict"])
        self.critic_target_buffer.load_state_dict(checkpoint["critic_target_buffer_state_dict"])
        self.critic_buffer_optim.load_state_dict(checkpoint["critic_buffer_optimizer_state_dict"])
        self.V_critic_buffer.load_state_dict(checkpoint["V_critic_buffer_state_dict"])
        self.V_critic_buffer_optim.load_state_dict(checkpoint["V_critic_buffer_optimizer_state_dict"])
        if self.genieo_auto_entropy_tuning:
            if "genieo_log_ent_coef" in checkpoint:
                self.log_ent_coef.data = torch.tensor(
                    [checkpoint["genieo_log_ent_coef"]],
                    device=self.device,
                    dtype=torch.float32,
                )
                self.ent_coef = checkpoint.get("genieo_ent_coef", float(self.log_ent_coef.exp().item()))
            if "genieo_ent_coef_optim_state_dict" in checkpoint:
                self.ent_coef_optim.load_state_dict(checkpoint["genieo_ent_coef_optim_state_dict"])

        if evaluate:
            self.policy.eval()
            self.critic.eval()
            self.critic_target.eval()
            self.critic_buffer.eval()
            self.critic_target_buffer.eval()
            self.V_critic_buffer.eval()
        else:
            self.policy.train()
            self.critic.train()
            self.critic_target.train()
            self.critic_buffer.train()
            self.critic_target_buffer.train()
            self.V_critic_buffer.train()
