import math

import torch
import torch.nn as nn


def weights_init_(m):
    if isinstance(m, nn.Linear):
        torch.nn.init.xavier_uniform_(m.weight, gain=1)
        torch.nn.init.constant_(m.bias, 0)


def create_value_block(hidden_dim):
    return nn.Sequential(
        nn.LayerNorm(hidden_dim),
        nn.Linear(hidden_dim, hidden_dim),
        nn.LayerNorm(hidden_dim),
        nn.GELU(),
        nn.Linear(hidden_dim, hidden_dim),
        nn.LayerNorm(hidden_dim),
        nn.GELU(),
        nn.Linear(hidden_dim, hidden_dim),
        nn.LayerNorm(hidden_dim),
    )


class ValueNetwork(nn.Module):
    def __init__(self, num_inputs, hidden_dim):
        super().__init__()
        self.v_input = nn.Linear(num_inputs, hidden_dim)
        self.block = create_value_block(hidden_dim)
        self.v_output = nn.Linear(hidden_dim, 1)
        self.apply(weights_init_)

    def forward(self, state):
        x = self.v_input(state)
        x = self.block(x)
        return self.v_output(x)


class QNetwork(nn.Module):
    def __init__(self, num_inputs, num_actions, hidden_dim):
        super().__init__()

        self.Q1_input = nn.Linear(num_inputs + num_actions, hidden_dim)
        self.Q1_block = create_value_block(hidden_dim)
        self.Q1_output = nn.Linear(hidden_dim, 1)

        self.Q2_input = nn.Linear(num_inputs + num_actions, hidden_dim)
        self.Q2_block = create_value_block(hidden_dim)
        self.Q2_output = nn.Linear(hidden_dim, 1)
        self.apply(weights_init_)

    def forward(self, state, action):
        x = torch.cat([state, action], dim=-1)

        x1 = self.Q1_input(x)
        x1 = self.Q1_block(x1)
        q_value_1 = self.Q1_output(x1)

        x2 = self.Q2_input(x)
        x2 = self.Q2_block(x2)
        q_value_2 = self.Q2_output(x2)
        return q_value_1, q_value_2


class InvertibleGENIEOAffineActor(nn.Module):
    """
    GENIEO affine-coupling actor:
      X = x * exp(dt * ell(y,t,s)) + dt * u(y,t,s)
      Y = y * exp(dt * rho(X,t,s)) + dt * w(X,t,s)
    with bounded log-scale and exact per-step logdet accumulation.
    """

    def __init__(
        self,
        num_inputs,
        num_actions,
        hidden_dim,
        steps,
        action_space=None,
        p_mix=1.0,
        base_std=1.0,
        tail_init_scale=1e-4,
        log_scale_bound=0.02,
        log_scale_warmup=100000,
        use_projected_squash_correction=False,
    ):
        super().__init__()
        self.num_inputs = num_inputs
        self.num_actions = num_actions
        self.steps = steps
        self.p_mix = float(p_mix)
        self.base_std = float(base_std)
        self.tail_init_scale = float(tail_init_scale)
        self.log_scale_bound = float(log_scale_bound)
        self.log_scale_warmup = int(log_scale_warmup)
        self.use_projected_squash_correction = bool(use_projected_squash_correction)
        self.update_step = 0
        self.last_debug = {}
        if abs(2.0 * self.p_mix - 1.0) < 1e-6:
            raise ValueError("p_mix=0.5 makes the GENIEO mixing matrix singular")

        self.net = nn.Sequential(
            nn.Linear(num_inputs + num_actions + 1, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ELU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ELU(),
            nn.Linear(hidden_dim, 2 * num_actions),
        )
        self.apply(weights_init_)
        if self.tail_init_scale > 0:
            last_linear = self.net[-1]
            nn.init.uniform_(
                last_linear.weight[: self.num_actions],
                -self.tail_init_scale,
                self.tail_init_scale,
            )
            nn.init.uniform_(
                last_linear.bias[: self.num_actions],
                -self.tail_init_scale,
                self.tail_init_scale,
            )
            nn.init.constant_(last_linear.weight[self.num_actions :], 0.0)
            nn.init.constant_(last_linear.bias[self.num_actions :], 0.0)

        if action_space is None:
            self.register_buffer("action_scale", torch.tensor(1.0))
            self.register_buffer("action_bias", torch.tensor(0.0))
        else:
            high = torch.as_tensor(action_space.high, dtype=torch.float32).flatten()
            low = torch.as_tensor(action_space.low, dtype=torch.float32).flatten()
            self.register_buffer("action_scale", (high - low) / 2.0)
            self.register_buffer("action_bias", (high + low) / 2.0)

    def set_update_step(self, step: int):
        self.update_step = int(step)

    def _current_warmup_coef(self):
        if self.log_scale_warmup <= 0:
            return 1.0
        return min(1.0, float(self.update_step) / float(max(1, self.log_scale_warmup)))

    def forward_affine_params(self, state, half_action, time):
        h = torch.cat([state, half_action, time], dim=-1)
        out = self.net(h)
        shift, raw_log_scale = out.chunk(2, dim=-1)
        warm = self._current_warmup_coef()
        bound = warm * self.log_scale_bound
        log_scale = bound * torch.tanh(raw_log_scale)
        return shift, log_scale

    def step(self, state, x_t, y_t, time_start, time_end):
        dt = time_end - time_start

        shift_x, log_scale_x = self.forward_affine_params(state, y_t, time_start)
        x_next = x_t * torch.exp(dt * log_scale_x) + dt * shift_x

        shift_y, log_scale_y = self.forward_affine_params(state, x_next, time_start)
        y_next = y_t * torch.exp(dt * log_scale_y) + dt * shift_y

        step_logdet = dt * (
            log_scale_x.sum(dim=-1, keepdim=True)
            + log_scale_y.sum(dim=-1, keepdim=True)
        )

        if self.p_mix != 1.0:
            x_out = self.p_mix * x_next + (1.0 - self.p_mix) * y_next
            y_out = self.p_mix * y_next + (1.0 - self.p_mix) * x_next
            mix_logdet = self.num_actions * math.log(abs(2.0 * self.p_mix - 1.0))
            step_logdet = step_logdet + step_logdet.new_tensor(mix_logdet)
        else:
            x_out, y_out = x_next, y_next

        absmax = torch.maximum(
            log_scale_x.detach().abs().amax(),
            log_scale_y.detach().abs().amax(),
        )
        mean_val = 0.5 * (
            log_scale_x.detach().mean() + log_scale_y.detach().mean()
        )
        return x_out, y_out, step_logdet, absmax, mean_val

    def _integrate(self, state, x_t, y_t):
        time_start = torch.zeros(state.shape[0], 1, device=state.device, dtype=state.dtype)
        time_step = 1.0 / self.steps
        total_logdet = torch.zeros(state.shape[0], 1, device=state.device, dtype=state.dtype)
        running_absmax = torch.zeros((), device=state.device, dtype=state.dtype)
        running_mean = torch.zeros((), device=state.device, dtype=state.dtype)

        for _ in range(self.steps):
            time_end = time_start + time_step
            x_t, y_t, step_logdet, absmax, mean_val = self.step(
                state, x_t, y_t, time_start, time_end
            )
            total_logdet = total_logdet + step_logdet
            running_absmax = torch.maximum(running_absmax, absmax.to(running_absmax.dtype))
            running_mean = running_mean + mean_val.to(running_mean.dtype)
            time_start = time_end

        running_mean = running_mean / float(max(1, self.steps))
        return x_t, y_t, total_logdet, running_absmax, running_mean

    def _squash_to_env(self, proto_action):
        action = torch.tanh(proto_action)
        action_env = action * self.action_scale.to(action.device) + self.action_bias.to(action.device)
        return action_env, action

    def unsquash_from_env(self, action_env):
        scale = self.action_scale.to(device=action_env.device, dtype=action_env.dtype)
        bias = self.action_bias.to(device=action_env.device, dtype=action_env.dtype)
        norm_action = (action_env - bias) / torch.clamp(scale, min=1e-6)
        norm_action = torch.clamp(norm_action, -0.99999, 0.99999)
        return torch.atanh(norm_action)

    def sample_base(self, batch_size, device, dtype):
        x_t = torch.randn(batch_size, self.num_actions, device=device, dtype=dtype) * self.base_std
        y_t = torch.randn(batch_size, self.num_actions, device=device, dtype=dtype) * self.base_std
        return x_t, y_t

    def sample_with_logprob(self, state):
        batch_size = state.shape[0]
        device = state.device
        x_t, y_t = self.sample_base(batch_size, device, state.dtype)

        var = self.base_std ** 2
        log_norm = math.log(2.0 * math.pi * var)
        log_prob_x0 = -0.5 * ((x_t.pow(2) / var) + log_norm).sum(dim=-1, keepdim=True)
        log_prob_y0 = -0.5 * ((y_t.pow(2) / var) + log_norm).sum(dim=-1, keepdim=True)
        base_log_prob = log_prob_x0 + log_prob_y0

        x_t, y_t, flow_logdet, log_scale_absmax, log_scale_mean = self._integrate(state, x_t, y_t)
        dummy_log_prob = base_log_prob - flow_logdet

        a_mean = (x_t + y_t) / 2.0
        action_env, a_squashed = self._squash_to_env(a_mean)
        if self.use_projected_squash_correction:
            squash_correction = torch.clamp(
                1.0 - a_squashed.pow(2), min=1e-6
            ).log().sum(dim=-1, keepdim=True)
            log_prob = dummy_log_prob - squash_correction
        else:
            log_prob = dummy_log_prob

        self.last_debug = {
            "base_log_prob_mean": float(base_log_prob.detach().mean().item()),
            "flow_logdet_mean": float(flow_logdet.detach().mean().item()),
            "flow_logdet_std": float(flow_logdet.detach().std(unbiased=False).item()),
            "dummy_log_prob_mean": float(dummy_log_prob.detach().mean().item()),
            "log_scale_absmax": float(log_scale_absmax.detach().item()),
            "log_scale_mean": float(log_scale_mean.detach().item()),
        }
        return action_env, (x_t, y_t), log_prob

    def sample(self, state):
        return self.sample_with_logprob(state)

    def sample_env(self, state):
        return self.sample_with_logprob(state)

    def mean_action(self, state):
        x_t = torch.zeros(state.shape[0], self.num_actions, device=state.device, dtype=state.dtype)
        y_t = torch.zeros_like(x_t)
        x_t, y_t, _, _, _ = self._integrate(state, x_t, y_t)
        action_env, _ = self._squash_to_env((x_t + y_t) / 2.0)
        return action_env


class InvertibleGENIEOActor(InvertibleGENIEOAffineActor):
    """Backward-compatible alias for older imports."""
