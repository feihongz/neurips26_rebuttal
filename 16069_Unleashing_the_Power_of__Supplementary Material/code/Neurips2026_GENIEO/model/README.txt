GENIEO minimal code subset (new affine version)

This folder keeps only the core GENIEO modules for online continuous-control RL,
updated to the newer affine-coupling actor version.

Included files
- model/algo.py
- model/model.py
- model/utils.py

What is new in this version
- Actor upgraded from additive coupling to affine coupling with bounded log-scale.
- Exact per-step logdet accumulation inside the actor.
- Optional log-scale warmup (`genieo_log_scale_warmup`).
- Optional projected squash correction (`genieo_use_projected_squash_correction`).
- Policy update includes actor grad clipping (`genieo_actor_grad_clip`).
- Auto entropy tuning with clamp bounds is retained.
- Internal debug stats are exposed via `flowAC.last_genieo_debug`.

Core interfaces
- Agent class: `flowAC` (GENIEO-only)
- Actor class: `InvertibleGENIEOAffineActor`
- Replay action encoding helper: `flowAC.replay_action_from_env(action_env)`

Expected external dependencies
- Your own replay buffer implementation with:
  `sample(batch_size) -> (state, action, reward, next_state, mask)`
- Env/trainer loop and logging/evaluation pipeline.

Key hyperparameters (args)
- Common: `gamma, tau, quantile, epsilon, target_update_interval, hidden_size, lr, steps, cuda, device`
- GENIEO-specific:
  - `genieo_actor_lr_scale` (default 0.1)
  - `genieo_ent_lr_scale` (default 0.1)
  - `genieo_reward_scale` (default 1.0)
  - `genieo_zero_last_init_scale` (default 1e-4)
  - `genieo_ent_grad_clip` (default 1.0)
  - `genieo_actor_grad_clip` (default 10.0)
  - `genieo_log_ent_min` (default -10.0)
  - `genieo_log_ent_max` (default 0.0)
  - `p_mix` (default 1.0)
  - `genieo_init_std` (default 1.0)
  - `genieo_log_scale_bound` (default 0.02)
  - `genieo_log_scale_warmup` (default 100000)
  - `genieo_use_projected_squash_correction` (default False)
  - `genieo_ent_coef` or fallback `ent_coef` (default 0.001)
  - `genieo_comp_coef` or fallback `comp_coef` (default 0.1)
  - `genieo_explore_noise` (default 0.0)
  - `genieo_use_mean_action` (default False)
  - `genieo_target_tau` (default 0.005)
  - `genieo_auto_entropy_tuning` (default True)
  - `genieo_target_entropy_scale` (default 1.0)

Notes
- This repo is intentionally minimal; full reproduction scripts and env wrappers
  are not included.
- If your old code imports `InvertibleGENIEOActor`, compatibility alias is kept.

Conservative preset (recommended when upgrading from old GENIEO)
- Keep these defaults unless you have evidence to change them:
  - `genieo_log_scale_bound = 0.02`
  - `genieo_log_scale_warmup = 100000`
  - `p_mix = 1.0`
  - `genieo_actor_grad_clip = 10.0`
  - `genieo_ent_grad_clip = 1.0`
  - `genieo_auto_entropy_tuning = True`
- Start from your old training/eval pipeline and only swap these three files.
- Validate with at least:
  - episode return curve vs old baseline
  - critic loss stability
  - entropy coefficient trajectory (if auto tuning enabled)
