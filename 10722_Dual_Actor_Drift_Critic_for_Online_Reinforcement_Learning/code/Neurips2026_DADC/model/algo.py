import torch
import torch.nn.functional as F
from torch.amp import autocast, GradScaler
import torch.optim as optim
import numpy as np

from .utils import soft_update, hard_update, compute_soft_boosted_drifting_v
from .model import QNetwork, ValueNetwork, Policy_flow, MultimodalGaussianActor

CFM_MIN = 1e-3
CFM_MAX = 1

mode = "reduce-overhead"
compile_model = False


class flowAC(object):
    def __init__(self, num_inputs, action_space, args):
        self.gamma = args.gamma
        self.tau = args.tau
        self.quantile = args.quantile

        self.drift_lamda = getattr(args, "drift_lamda", 0.1)
        self.drift_num_anchors = getattr(args, "drift_num_anchors", 16)
        self.drift_drift_scale = float(getattr(args, "drift_drift_scale", 1.0))
        self.drift_actor_alpha = float(getattr(args, "drift_actor_alpha", 1.0))
        self.drift_reward_scale = float(getattr(args, "drift_reward_scale", 1.0))
        self.drift_langevin_topk = int(getattr(args, "drift_langevin_topk", 5))
        self.drift_langevin_eta = float(getattr(args, "drift_langevin_eta", 0.02))
        self.drift_langevin_noise = float(getattr(args, "drift_langevin_noise", 0.01))
        self.drift_langevin_steps = int(getattr(args, "drift_langevin_steps", 4))
        self.drift_num_modes = int(getattr(args, "drift_num_modes", 4))

        self.noise_level = args.epsilon
        self.action_space = action_space
        self.sample_count = 0
        self.policy_type = "Drift"

        self.action_dim = action_space.shape[0]
        self.critic_action_dim = self.action_dim
        self.target_update_interval = args.target_update_interval
        self.device = torch.device(f"cuda:{args.device}" if args.cuda else "cpu")
        self.amp_enabled = args.cuda and torch.cuda.is_available()
        self.amp_dtype = torch.bfloat16
        self.scaler = GradScaler(enabled=self.amp_enabled and self.amp_dtype == torch.float16)

        self.critic = QNetwork(num_inputs, self.critic_action_dim, args.hidden_size).to(self.device)
        self.critic_optim = optim.Adam(self.critic.parameters(), lr=args.lr)
        self.critic_target = QNetwork(num_inputs, self.critic_action_dim, args.hidden_size).to(self.device)
        hard_update(self.critic_target, self.critic)

        self.flow_teacher = Policy_flow(
            num_inputs,
            action_space.shape[0],
            args.hidden_size,
            args.steps,
            action_space,
        ).to(self.device)
        self.flow_optim = optim.Adam(self.flow_teacher.parameters(), lr=args.lr)

        self.actor = MultimodalGaussianActor(
            num_inputs,
            action_space.shape[0],
            args.hidden_size,
            action_space,
            num_modes=self.drift_num_modes,
        ).to(self.device)
        self.actor_optim = optim.Adam(self.actor.parameters(), lr=args.lr)

        self.policy = self.actor
        self.policy_optim = self.actor_optim

        self.critic_buffer = QNetwork(num_inputs, self.critic_action_dim, args.hidden_size).to(self.device)
        self.critic_buffer_optim = optim.Adam(self.critic_buffer.parameters(), lr=args.lr)
        hard_update(self.critic_buffer, self.critic)

        self.critic_target_buffer = QNetwork(num_inputs, self.critic_action_dim, args.hidden_size).to(self.device)
        hard_update(self.critic_target_buffer, self.critic_buffer)

        self.V_critic_buffer = ValueNetwork(num_inputs, args.hidden_size).to(device=self.device)
        self.V_critic_buffer_optim = optim.Adam(self.V_critic_buffer.parameters(), lr=args.lr)

        if compile_model:
            self.critic = torch.compile(self.critic, mode=mode)
            self.critic_target = torch.compile(self.critic_target, mode=mode)
            self.critic_buffer = torch.compile(self.critic_buffer, mode=mode)
            self.critic_target_buffer = torch.compile(self.critic_target_buffer, mode=mode)
            self.V_critic_buffer = torch.compile(self.V_critic_buffer, mode=mode)

    def select_action(self, state, evaluate=False):
        if not evaluate:
            self.sample_count += 1
            if self.sample_count % 1e5 == 0:
                self.noise_level = self.noise_level * 0.8

        state = torch.FloatTensor(state).to(self.device).unsqueeze(0)
        with torch.no_grad():
            if evaluate:
                action = self.actor(state)
            else:
                action = self.actor.rsample(state)

        return action.detach().cpu().numpy()[0].clip(self.action_space.low, self.action_space.high)

    def replay_action_from_env(self, action_env):
        return action_env

    def update_critic(self, state_batch, action_batch, reward_batch, next_state_batch, mask_batch):
        with autocast(device_type=self.device.type, dtype=self.amp_dtype, enabled=self.amp_enabled):
            with torch.no_grad():
                next_state_action = self.actor.rsample(next_state_batch)
                next_state_action = next_state_action.clone()
                noise = (torch.randn_like(next_state_action) * 0.2).clamp(-0.5, 0.5)
                next_state_action = (next_state_action + noise).clamp(-1.0, 1.0)

                qf1_next_target, qf2_next_target = self.critic_target(next_state_batch, next_state_action)
                qf1_next_target = qf1_next_target.clone()
                qf2_next_target = qf2_next_target.clone()
                min_qf_next_target = torch.min(qf1_next_target, qf2_next_target)
                next_q_value = reward_batch + mask_batch * self.gamma * min_qf_next_target

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
                target_Vf_pred = self.V_critic_buffer(next_state_batch)
                target_Vf_pred = target_Vf_pred.clone()
                next_q_value_buffer = reward_batch + mask_batch * self.gamma * target_Vf_pred

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
            vf_pred = self.V_critic_buffer(state_batch)
            vf_pred = vf_pred.clone()

            with torch.no_grad():
                q_pred_1, q_pred_2 = self.critic_target_buffer(state_batch, action_batch)
                q_pred_1 = q_pred_1.clone()
                q_pred_2 = q_pred_2.clone()
                q_pred = torch.min(q_pred_1, q_pred_2)

            vf_err = q_pred - vf_pred
            vf_sign = (vf_err < 0).float()
            vf_weight = (1 - vf_sign) * self.quantile + vf_sign * (1 - self.quantile)
            vf_loss = (vf_weight * (vf_err ** 2)).to(torch.float32).mean()

        self.V_critic_buffer_optim.zero_grad()
        self.scaler.scale(vf_loss).backward()
        self.scaler.step(self.V_critic_buffer_optim)
        self.scaler.update()

        return q_buffer.detach()

    def update_policy(self, state_batch, action_batch, action_0, q_buffer):
        batch_size = state_batch.shape[0]
        action_dim = action_batch.shape[1]

        with autocast(device_type=self.device.type, dtype=self.amp_dtype, enabled=self.amp_enabled):
            with torch.no_grad():
                pi_flow, _, _ = self.flow_teacher.sample(state_batch)
                qf1_flow, qf2_flow = self.critic(state_batch, pi_flow)
                min_qf_flow = torch.min(qf1_flow, qf2_flow).view(-1, 1)

            q_buf = q_buffer.view(-1, 1)
            weights = torch.relu(q_buf - min_qf_flow).detach()
            weights = torch.exp(weights - weights.mean())
            weights = torch.clamp(self.drift_lamda * weights, CFM_MIN, CFM_MAX)

            velocity_target = action_batch - action_0
            t = torch.rand(batch_size, 1).to(self.device)
            action_t = t * action_batch + (1.0 - t) * action_0
            pred_vel = self.flow_teacher(state_batch, action_t, t)
            cfmloss = (weights * F.mse_loss(pred_vel, velocity_target, reduction='none').mean(dim=1, keepdim=True)).mean()

        self.flow_optim.zero_grad()
        self.scaler.scale(cfmloss).backward()
        self.scaler.step(self.flow_optim)
        self.scaler.update()

        with autocast(device_type=self.device.type, dtype=self.amp_dtype, enabled=self.amp_enabled):
            with torch.no_grad():
                m = self.drift_num_anchors
                state_expanded = state_batch.repeat_interleave(m, dim=0)
                anchors, _, _ = self.flow_teacher.sample(state_expanded)
                anchors = anchors.view(batch_size, m, action_dim)

                q1_anchors, q2_anchors = self.critic(state_expanded, anchors.view(batch_size * m, -1))
                q_anchors = torch.min(q1_anchors, q2_anchors).view(batch_size, m)

            pi_actor = self.actor.rsample(state_batch)
            q1_pi, q2_pi = self.critic(state_batch, pi_actor)
            min_qf_pi = torch.min(q1_pi, q2_pi)

            k_top = max(1, min(self.drift_langevin_topk, m))
            with torch.no_grad():
                _, topk_q_idx = torch.topk(q_anchors, k_top, dim=1, largest=True)
                gather_top = topk_q_idx.unsqueeze(-1).expand(-1, -1, action_dim)
                y_topk = torch.gather(anchors, 1, gather_top)

            st_rep_k = state_batch.unsqueeze(1).expand(-1, k_top, -1).reshape(batch_size * k_top, -1).float()
            eta_lv = self.drift_langevin_eta
            nstd_lv = self.drift_langevin_noise
            n_lv_steps = max(1, self.drift_langevin_steps)
            a_cur = y_topk.detach().float().clone()
            for _ in range(n_lv_steps):
                a_lv = a_cur.clone().requires_grad_(True)
                with autocast(device_type=self.device.type, dtype=self.amp_dtype, enabled=False):
                    q1_lv, q2_lv = self.critic(st_rep_k, a_lv.reshape(batch_size * k_top, action_dim))
                qm_lv = torch.min(q1_lv, q2_lv)
                grad_a = torch.autograd.grad(qm_lv.sum(), a_lv, retain_graph=False, create_graph=False)[0]
                with torch.no_grad():
                    if nstd_lv > 0:
                        noise = nstd_lv * torch.randn_like(a_cur)
                    else:
                        noise = torch.zeros_like(a_cur)
                    a_cur = (a_lv.detach() + eta_lv * grad_a.detach() + noise).float()

            low_b = torch.as_tensor(self.action_space.low, dtype=a_cur.dtype, device=a_cur.device).view(1, 1, -1)
            high_b = torch.as_tensor(self.action_space.high, dtype=a_cur.dtype, device=a_cur.device).view(1, 1, -1)
            anchors_pos = torch.max(torch.min(a_cur, high_b), low_b).to(dtype=pi_actor.dtype)

            with torch.no_grad():
                state_exp_k = state_batch.repeat_interleave(k_top, dim=0)
                q1_pos, q2_pos = self.critic(state_exp_k, anchors_pos.reshape(batch_size * k_top, action_dim))
                q_pos = torch.min(q1_pos, q2_pos).view(batch_size, k_top)
                adv_matrix = q_pos - min_qf_pi.view(batch_size, 1).detach()

                # Match Appendix setting when m=16: K=4 (25% low-Q negatives).
                k_neg = min(4, m)
                actor_pool = self.actor.rsample_n(state_batch, m)

                state_exp_actor = state_batch.repeat_interleave(m, dim=0)
                q1_ap, q2_ap = self.critic(state_exp_actor, actor_pool.reshape(batch_size * m, action_dim))
                q_actor_pool = torch.min(q1_ap, q2_ap).view(batch_size, m)
                _, bottom_idx = torch.topk(q_actor_pool, k_neg, dim=1, largest=False)
                gather_n = bottom_idx.unsqueeze(-1).expand(-1, -1, action_dim)
                neg_anchors = torch.gather(actor_pool, 1, gather_n)
                q_neg = torch.gather(q_actor_pool, 1, bottom_idx)
                adv_neg = q_neg - min_qf_pi.view(batch_size, 1).detach()

                v_drift = compute_soft_boosted_drifting_v(
                    x=pi_actor.detach(),
                    y=anchors_pos,
                    adv_matrix=adv_matrix,
                    temperatures=(0.1, 0.2, 0.5),
                    omega=0.05,
                    tau=0.1,
                    neg_anchors=neg_anchors,
                    adv_neg=adv_neg,
                )

                drift_target = pi_actor.detach() + self.drift_drift_scale * v_drift

            actor_loss = -min_qf_pi.mean() + self.drift_actor_alpha * F.mse_loss(pi_actor, drift_target)

        self.actor_optim.zero_grad()
        self.scaler.scale(actor_loss).backward()
        self.scaler.step(self.actor_optim)
        self.scaler.update()

    def update_parameters(self, memory, batch_size, updates):
        state_batch, action_batch, reward_batch, next_state_batch, mask_batch = memory.sample(batch_size=batch_size)
        state_batch = torch.FloatTensor(state_batch).to(self.device)
        next_state_batch = torch.FloatTensor(next_state_batch).to(self.device)
        action_batch = torch.FloatTensor(action_batch).to(self.device)
        reward_batch = torch.FloatTensor(reward_batch).to(self.device).unsqueeze(1)

        reward_batch = reward_batch * self.drift_reward_scale

        mask_batch = torch.FloatTensor(mask_batch).to(self.device).unsqueeze(1)

        action_0 = torch.randn_like(action_batch, device=self.device)
        action_0 = torch.clamp(action_0, -1, 1)

        q_buffer = self.update_critic(state_batch, action_batch, reward_batch, next_state_batch, mask_batch)

        if updates % self.target_update_interval == 0:
            q_buffer_cloned = q_buffer.clone()
            self.update_policy(state_batch, action_batch, action_0, q_buffer_cloned)
            with torch.no_grad():
                soft_update(self.critic_target, self.critic, self.tau)
                soft_update(self.critic_target_buffer, self.critic_buffer, self.tau)

    def save_checkpoint(self, path, i_episode):
        ckpt_path = path + '/' + '{}.torch'.format(i_episode)
        print('Saving models to {}'.format(ckpt_path))
        checkpoint_dict = {
            'policy_state_dict': self.policy.state_dict(),
            'critic_state_dict': self.critic.state_dict(),
            'critic_target_state_dict': self.critic_target.state_dict(),
            'critic_optimizer_state_dict': self.critic_optim.state_dict(),
            'policy_optimizer_state_dict': self.policy_optim.state_dict(),
            'critic_buffer_state_dict': self.critic_buffer.state_dict(),
            'critic_target_buffer_state_dict': self.critic_target_buffer.state_dict(),
            'critic_buffer_optimizer_state_dict': self.critic_buffer_optim.state_dict(),
            'V_critic_buffer_state_dict': self.V_critic_buffer.state_dict(),
            'V_critic_buffer_optimizer_state_dict': self.V_critic_buffer_optim.state_dict(),
            'flow_teacher_state_dict': self.flow_teacher.state_dict(),
            'flow_optimizer_state_dict': self.flow_optim.state_dict(),
            'actor_state_dict': self.actor.state_dict(),
            'actor_optimizer_state_dict': self.actor_optim.state_dict(),
        }
        torch.save(checkpoint_dict, ckpt_path)

    def load_checkpoint(self, path, i_episode, evaluate=False):
        ckpt_path = path + '/' + 'checkpoint/' + 'best.torch'
        print('Loading models from {}'.format(ckpt_path))
        if ckpt_path is not None:
            checkpoint = torch.load(ckpt_path)
            self.policy.load_state_dict(checkpoint['policy_state_dict'])
            self.critic.load_state_dict(checkpoint['critic_state_dict'])
            self.critic_target.load_state_dict(checkpoint['critic_target_state_dict'])
            self.critic_optim.load_state_dict(checkpoint['critic_optimizer_state_dict'])
            self.policy_optim.load_state_dict(checkpoint['policy_optimizer_state_dict'])
            self.critic_buffer.load_state_dict(checkpoint['critic_buffer_state_dict'])
            self.critic_target_buffer.load_state_dict(checkpoint['critic_target_buffer_state_dict'])
            self.critic_buffer_optim.load_state_dict(checkpoint['critic_buffer_optimizer_state_dict'])
            self.V_critic_buffer.load_state_dict(checkpoint['V_critic_buffer_state_dict'])
            self.V_critic_buffer_optim.load_state_dict(checkpoint['V_critic_buffer_optimizer_state_dict'])

            if 'flow_teacher_state_dict' in checkpoint:
                self.flow_teacher.load_state_dict(checkpoint['flow_teacher_state_dict'])
                self.flow_optim.load_state_dict(checkpoint['flow_optimizer_state_dict'])
            if 'actor_state_dict' in checkpoint:
                self.actor.load_state_dict(checkpoint['actor_state_dict'])
                self.actor_optim.load_state_dict(checkpoint['actor_optimizer_state_dict'])

            if evaluate:
                self.policy.eval()
                self.critic.eval()
                self.critic_target.eval()
                self.critic_buffer.eval()
                self.critic_target_buffer.eval()
                self.V_critic_buffer.eval()
                self.flow_teacher.eval()
                self.actor.eval()
            else:
                self.policy.train()
                self.critic.train()
                self.critic_target.train()
                self.critic_buffer.train()
                self.critic_target_buffer.train()
                self.V_critic_buffer.train()
                self.flow_teacher.train()
                self.actor.train()
