import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Normal


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
        x = self.v_output(x)
        return x


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


class Policy_flow(nn.Module):
    def __init__(self, num_inputs, num_actions, hidden_dim, steps, action_space=None):
        super().__init__()
        self.num_inputs = num_inputs
        self.num_actions = num_actions
        self.linear1 = nn.Linear(num_inputs + num_actions + 1, hidden_dim)
        self.linear2 = nn.Linear(hidden_dim, hidden_dim)
        self.LayerNorm = nn.LayerNorm(hidden_dim)
        self.LayerNorm2 = nn.LayerNorm(hidden_dim)
        self.linear3 = nn.Linear(hidden_dim, num_actions)
        self.steps = steps
        self.apply(weights_init_)

        if action_space is None:
            self.action_scale = torch.tensor(1.0)
            self.action_bias = torch.tensor(0.0)
        else:
            self.action_scale = torch.FloatTensor((action_space.high - action_space.low) / 2.0)
            self.action_bias = torch.FloatTensor((action_space.high + action_space.low) / 2.0)

    def forward(self, state, action_0, time):
        x = torch.cat([state, action_0, time], 1)
        x = self.linear1(x)
        x = self.LayerNorm(x)
        x = F.elu(x)
        x = self.linear2(x)
        x = self.LayerNorm2(x)
        x = F.elu(x)
        x = self.linear3(x)
        return x

    def step(self, state, action, time_start, time_end):
        velocity_start = self.forward(state, action, time_start)
        intermediate_state = action + velocity_start * (time_end - time_start) / 2
        velocity_mid = self.forward(state, intermediate_state, time_start + (time_end - time_start) / 2)
        action_t = action + velocity_mid * (time_end - time_start)
        return action_t

    @torch.compile
    def sample(self, state):
        device = next(self.parameters()).device
        time_start = torch.zeros(state.shape[0], 1, device=device)
        time_step = 1.0 / self.steps
        action = torch.normal(0, 1, size=(state.shape[0], self.num_actions), device=device)
        action = torch.clamp(action, -1.0, 1.0)

        for _ in range(self.steps):
            time_end = time_start + time_step
            action = self.step(state, action, time_start, time_end)
            time_start = time_end

        action = torch.tanh(action)
        action = action * self.action_scale.to(action.device) + self.action_bias.to(action.device)
        return action, 0, action

    @torch.compile
    def sample_env(self, state):
        device = next(self.parameters()).device
        time_start = torch.zeros(state.shape[0], 1, device=device)
        time_step = 1.0 / self.steps
        action = torch.normal(0, 1, size=(state.shape[0], self.num_actions), device=device)
        action = torch.clamp(action, -1.0, 1.0)

        for _ in range(self.steps):
            time_end = time_start + time_step
            action = self.step(state, action, time_start, time_end)
            time_start = time_end

        action = torch.tanh(action)
        action = action * self.action_scale.to(action.device) + self.action_bias.to(action.device)
        return action, 0, action


class MultimodalGaussianActor(nn.Module):
    def __init__(self, num_inputs, num_actions, hidden_dim, action_space=None, num_modes=4):
        super().__init__()
        self.num_actions = num_actions
        self.num_modes = int(num_modes)
        if self.num_modes < 2:
            raise ValueError("num_modes must be >= 2 for a mixture policy")

        self.net = nn.Sequential(
            nn.Linear(num_inputs, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
        )
        self.logits_head = nn.Linear(hidden_dim, self.num_modes)
        self.mean_head = nn.Linear(hidden_dim, self.num_modes * num_actions)
        self.log_std_head = nn.Linear(hidden_dim, self.num_modes * num_actions)
        self.apply(weights_init_)

        if action_space is None:
            self.register_buffer("action_scale", torch.tensor(1.0))
            self.register_buffer("action_bias", torch.tensor(0.0))
        else:
            high = torch.as_tensor(action_space.high, dtype=torch.float32).flatten()
            low = torch.as_tensor(action_space.low, dtype=torch.float32).flatten()
            self.register_buffer("action_scale", (high - low) / 2.0)
            self.register_buffer("action_bias", (high + low) / 2.0)

    def _component_params(self, state):
        h = self.net(state)
        logits = self.logits_head(h)
        means = self.mean_head(h).view(-1, self.num_modes, self.num_actions)
        log_std = torch.clamp(
            self.log_std_head(h).view(-1, self.num_modes, self.num_actions),
            min=-20,
            max=2,
        )
        std = log_std.exp()
        return logits, means, std

    def _squash(self, pre_tanh):
        y = torch.tanh(pre_tanh)
        return y * self.action_scale.to(y.device) + self.action_bias.to(y.device)

    def forward(self, state):
        logits, means, _ = self._component_params(state)
        bsz = means.shape[0]
        device = means.device
        k = logits.argmax(dim=-1)
        b_idx = torch.arange(bsz, device=device)
        mean_sel = means[b_idx, k]
        return self._squash(mean_sel)

    def rsample(self, state):
        logits, means, std = self._component_params(state)
        bsz = means.shape[0]
        device = means.device
        cat = torch.distributions.Categorical(logits=logits)
        k = cat.sample()
        b_idx = torch.arange(bsz, device=device)
        mean_sel = means[b_idx, k]
        std_sel = std[b_idx, k]
        eps = torch.randn_like(mean_sel)
        return self._squash(mean_sel + std_sel * eps)

    def rsample_n(self, state, n):
        logits, means, std = self._component_params(state)
        bsz = means.shape[0]
        device = means.device
        cat = torch.distributions.Categorical(logits=logits)
        k = cat.sample((n,))
        b_idx = torch.arange(bsz, device=device).unsqueeze(0).expand(n, bsz)
        mean_sel = means[b_idx, k]
        std_sel = std[b_idx, k]
        eps = torch.randn(n, bsz, self.num_actions, device=device)
        pre_tanh = mean_sel + std_sel * eps
        y = torch.tanh(pre_tanh)
        a = y * self.action_scale.to(y.device) + self.action_bias.to(y.device)
        return a.permute(1, 0, 2).contiguous()
