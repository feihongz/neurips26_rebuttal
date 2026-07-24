# Submission 16069: Required Additional Experiments

## 使用说明

本文档是 rebuttal 期间的内部实验清单，不是论文修订稿。

- response period 不能修改或重新上传论文与 supplementary material。
- 新结果只能以纯文本形式写入对应 reviewer 的 OpenReview Rebuttal。
- 不上传图表或文件，不提供链接，不暴露作者或机构信息。
- 所有数字必须来自可追溯日志；无法核验的结果不得写入回复。
- 优先完成能够同时回答多位 reviewer、且不需要大规模重训的实验。

## 总体优先级

| ID | 实验或分析 | 优先级 | 是否需要重训 | 主要回应 |
|---|---|---:|---:|---|
| E0 | 现有结果的统计重分析 | P0 | 否 | BXmK：显著性、SOTA 表述 |
| E1 | 训练与推理开销基准 | P0 | 少量短跑/计时 | tShQ、4ynL：computational overhead |
| E2 | 直接 state-space exploration 指标 | P0 | 视轨迹是否保存 | 三位 reviewer：exploration evidence |
| E3 | Dummy entropy 与环境动作 entropy 对齐诊断 | P0 | 通常只需 checkpoint | meaningful exploration 的核心机制 |
| E4 | Naive Euler inversion 对比 | P0 | 只需 toy experiment | BXmK：Figure 4 缺失对比 |
| E5 | RL 中 affine logdet 的机制消融 | P1 | 是 | novelty、entropy 是否真正驱动收益 |
| E6 | Gaussian SAC baseline | P1 | 是 | BXmK：缺少 non-flow MaxEnt baseline |
| E7 | SimbaV2、MAD-TD、BRO 与 DMC Hard | P2 | 大规模重训 | 4ynL：baseline scope |
| E8 | 精细控制中的 entropy trade-off | P2 | 中等 | 4ynL：低方差控制局限 |
| E9 | 增加 seeds 或补充稳健性运行 | P2 | 大规模重训 | BXmK：统计可信度 |

P0 项应优先形成可直接放入 OpenReview 的数字。P1 项在算力允许时完成。P2 项成本较高，若无法完成，应在 rebuttal 中收窄 claim，而不是给出无法兑现的承诺。

---

## E0. 现有结果的统计重分析

### 目的

回答 Reviewer BXmK 关于五个 seeds、重叠标准差和 “best/SOTA” 表述过强的问题。

### 所需数据

- 每种方法、每个任务、每个 seed 的原始 TAR。
- 明确 Table 1 中 AVG. DMC 和 AVG. H-Bench 的计算方式。
- 如不同方法使用相同 seed，应保留 paired-seed 对应关系。

### 建议分析

1. 报告每个 benchmark aggregate 的 mean、median 和 IQM。
2. 使用 stratified bootstrap 给出 95% confidence interval。
3. 报告 GENIEO 相对 FlowRL、DIME 的 aggregate performance difference。
4. 如使用 paired test，写清检验方法；不要仅凭 `mean +/- std` 判断显著性。
5. 对多任务比较避免逐任务无校正地宣称 significance。
6. 明确 bold 仅表示 highest reported sample mean。

### 最低交付

- DMC aggregate：GENIEO、FlowRL、DIME 的 point estimate 和 95% CI。
- H-Bench aggregate：同上。
- 一句结论说明哪些 aggregate comparison 稳健，哪些 individual tasks 证据不足。

### Rebuttal 文本模板

> Using the original seed-level results, we recomputed [METRIC] with [BOOTSTRAP/TEST]. On DMC, GENIEO achieved [X, CI] versus FlowRL [Y, CI] and DIME [Z, CI]. On H-Bench, [RESULT]. We therefore use “highest reported mean” for individual tasks and restrict the stronger claim to [SUPPORTED AGGREGATE].

---

## E1. 训练与推理开销基准

### 目的

同时回答 tShQ Q1 和 4ynL Q2。

### 对照方法

最低配置：

- GENIEO，默认 `K=5`。
- Gaussian SAC 或统一框架中的 vanilla Gaussian actor。
- FlowRL。
- DIME 或另一个多步 diffusion baseline。

若完整 baseline 环境暂时不可用，至少完成 GENIEO 与 Gaussian SAC，并说明测量范围。

### 测量设置

- 首选 Dog Run，与论文已有约 10 小时/1M steps 的描述保持一致。
- 同一 GPU、CPU、batch size、UTD ratio、hidden size和 mixed-precision 设置。
- 区分 environment throughput 和 learner throughput。
- CUDA 计时前 warm up，并在计时点执行同步。
- 每项至少重复 3 个 timing windows，报告 mean 和 std。

### 必报指标

1. Wall-clock time per 100k environment steps。
2. Learner updates per second。
3. Actor inference latency：
   - batch size 1；
   - batch size 256。
4. Peak GPU memory。
5. Actor parameter count 与总 parameter count。
6. Replay-buffer action storage 相对 `d` 维策略的增加量。

### 需要解释的复杂度

- 每个 affine step 调用两次共享 MLP，因此 actor sampling 为 `2K` 次顺序网络调用；默认 `K=5`。
- replay action 和 critic input 从 `d` 增至 `2d`。
- 相对 Gaussian actor 会更慢，但相对 15--20 step diffusion policy 未必更慢，必须以实测数字为准。

### Rebuttal 文本模板

> Under the same [GPU/BATCH/UTD] setting on Dog Run, GENIEO required [X] hours per [STEPS], compared with [Y] for Gaussian SAC, [Z] for FlowRL, and [W] for DIME. Batch-1 inference latency was [X] ms/action and peak memory was [Y] GB. The main overhead comes from `2K` sequential affine-network evaluations rather than the `2d` representation alone.

---

## E2. 直接的 state-space exploration 证据

### 目的

回答三位 reviewer 共同提出的核心问题：higher return 是否真的来自更有效的探索。

### 推荐任务

- Dog Run：与现有 ablation 一致，训练成本和日志最容易复用。
- 可增加 H1 Sit Hard 或 H1 Crawl：验证结论不只存在于一个 DMC task。

### 对照方法

- GENIEO。
- GENIEO with `alpha=0`。
- FlowRL。
- DIME 或 Gaussian SAC。

所有方法使用相同 episode 数、environment steps 和 evaluation protocol。

### 时间点

- 100k steps：观察 reward 提升前后的 early exploration。
- 250k steps。
- 500k steps。
- 1M steps（若已有完整轨迹）。

### 推荐指标

1. **State coverage：** 对预先确定的 task-relevant state descriptors 做 occupancy bins。
2. **kNN state entropy：** 对标准化 observation/state 使用统一的 k 和样本数。
3. **Visitation dispersion：** 状态到初始状态或轨迹质心的平均距离。
4. **Behavioral coverage：** COM velocity、height、orientation、contact pattern 等物理量覆盖范围。
5. **Success/reward discovery time：** 首次达到固定 reward threshold 的 environment step。

### 防止 cherry-picking

- 在看结果前固定 descriptor、bin 范围、bin 数和 kNN 参数。
- 不能只选择 GENIEO 有利的二维投影。
- high-dimensional state coverage 至少同时报告一个 task-relevant descriptor metric 和一个全 observation metric。
- 报告 mean +/- std 或 bootstrap CI。

### 最低交付

- Dog Run 上 GENIEO、`alpha=0`、FlowRL 三种方法。
- 100k 与 500k 两个时间点。
- 一个 state coverage 指标 + 一个 reward discovery 指标。

### Rebuttal 文本模板

> At [100k/500k] steps on Dog Run, GENIEO covered [X] state bins versus [Y] for `alpha=0` and [Z] for FlowRL under the same descriptor and trajectory count. Its kNN state-entropy estimate was [X] versus [Y/Z], and it reached return [THRESHOLD] after [STEPS]. These measurements provide direct evidence of broader visitation on this task, while we do not claim uncertainty-directed exploration in general.

---

## E3. Dummy entropy 与环境动作 entropy 的对齐诊断

### 目的

验证最大化 `H(x,y|s)` 是否真的增加环境执行动作
`a = tanh((x+y)/2)` 的多样性，而不是只沿不影响环境的 `x-y` 方向增加 entropy。

这是当前方法最关键的机制诊断，能够直接支撑或限制 exploration claim。

### 数据与设置

- 从 replay buffer 固定抽取至少 1,000 个 states。
- 每个 state 从 policy 采样至少 128 个 augmented actions。
- 使用相同 checkpoint 对以下设置比较：
  - 默认 GENIEO；
  - `alpha=0`；
  - `nu=0`；
  - 默认 `nu=0.1`；
  - 较大 `nu`（如已有 checkpoint）。

### 指标

1. Augmented-policy entropy `H(x,y|s)`。
2. Environment-action entropy `H(a|s)`：
   - 使用统一 kNN estimator；或
   - 报告 covariance log-determinant/effective rank 作为稳定 proxy。
3. Coherence：`E[||x-y||^2]`。
4. Null-space variance ratio：
   `Var(x-y) / (Var(x+y) + epsilon)`。
5. Augmented entropy、environment-action entropy、state coverage 与 return 之间的相关性。

### 判读标准

- 理想结果：GENIEO 同时提高 environment-action diversity 和 state coverage，且 null-space ratio 受 coherence penalty 控制。
- 如果只提高 augmented entropy 而 environment-action entropy 不变，应主动收窄 “exploration” 主张。
- 不要把 optional squash correction 当作 projected-action exact likelihood；投影是降维、多对一映射。

### Rebuttal 文本模板

> Across [N] replay states with [M] samples per state, GENIEO increased the executed-action diversity metric from [X] to [Y], while the null-space variance ratio remained [Z] under the coherence penalty. Removing the penalty changed `E||x-y||^2` from [X] to [Y] and [did/did not] improve environment-action diversity. This separates useful projected-action diversity from entropy that exists only in the augmented null direction.

---

## E4. Naive Euler inversion 对比

### 目的

回应 BXmK 对 Figure 4 的直接批评：现有 zero-logdet baseline 只证明 Jacobian term 必要，没有验证论文批评的 naive Euler inversion。

### 实验设置

- 使用论文已有 two-peak MoG toy task。
- 固定相同 base samples 和 target samples。
- 比较：
  - GENIEO affine exact inverse/logdet；
  - forward Euler + naive reverse Euler；
  - zero-logdet；
  - 如实现方便，增加标准 ODE likelihood solver 作为参考。
- 步数设置：`K in {1, 5, 10, 20}`。

### 指标

1. Cycle/inversion error：
   `E[||z - F_reverse(F_forward(z))||_2]`。
2. Sample-wise log-likelihood error。
3. Entropy absolute/relative error against reference MoG。
4. Runtime per 100k samples。
5. 随 step size/step count 的误差曲线数值。

### 最低交付

- `K=5` 下 GENIEO 与 naive Euler 的 inversion error、entropy error 和 runtime。
- 保留现有 reference `1.4314` 与 GENIEO `1.4387` 作为一致性检查。

### Rebuttal 文本模板

> At the matched step count `K=[X]`, the naive reverse-Euler procedure produced cycle error [A] and entropy error [B], whereas GENIEO produced [C] and [D], respectively. This comparison directly tests the numerical-asymmetry motivation; the zero-logdet control separately isolates the role of the affine Jacobian.

---

## E5. RL 中 affine logdet 的机制消融

### 目的

区分性能提升究竟来自 expressive shift network、augmented critic，还是 parameter-dependent entropy gradient。

### 对照版本

1. Full affine GENIEO。
2. Additive/volume-preserving version：固定 log-scale 为零。
3. Full affine actor with `alpha=0`。
4. Full affine actor without coherence penalty。

所有版本保持 network width、flow steps、critic、seeds 和 training budget 一致。

### 指标

- Return curve 与 final TAR。
- Mean/std of flow logdet。
- Augmented entropy 与 environment-action diversity。
- State coverage。
- Critic loss 与 actor gradient norm（辅助判断稳定性）。

### 推荐任务

- Dog Run 为最低要求。
- 如资源允许，再增加 H1 Sit Hard。

### 关键问题

- Full affine 是否显著优于 additive version？
- `alpha=0` 是否消除 full affine 的主要收益？
- logdet/entropy 改善是否与 environment-action diversity 和 state coverage 同步？

---

## E6. Gaussian SAC baseline

### 目的

回应 BXmK 关于缺少 non-flow MaxEnt baseline 的问题，并回答复杂生成策略是否优于简单 Gaussian policy。

### 公平设置

- 与 GENIEO 使用相同 critic architecture、hidden width、batch size、UTD ratio、replay size 和 training steps。
- Gaussian actor 使用标准 bounded-action implementation。
- 同时报告 return 与 wall-clock efficiency。

### 任务范围

最低可行：

- Dog Run。
- Humanoid Run。
- H1 Sit Hard。

理想范围：全部 14 个任务和 5 seeds。

### 必报结果

- TAR mean +/- std。
- Sample efficiency。
- Wall-clock time。
- 说明 Gaussian policy 的 bounded-action entropy/log-prob 处理方式。

---

## E7. SimbaV2、MAD-TD、BRO 与 DMC Hard

### 目的

回应 Reviewer 4ynL 对 universal SOTA claim 和 evaluation scope 的质疑。

### 成本与风险

- 这些方法不只是替换 policy class，还涉及 scaling、model augmentation 或 critic optimization。
- 统一重实现可能引入 fairness 问题，官方实现又可能采用不同训练协议。
- 完整 5-seed、全任务对比成本很高，不应挤占 E0--E4。

### 建议顺序

1. 先确认是否已有严格同协议结果。
2. 若没有，只选择一个最强且可公平复现的方法，不要匆忙给出不可靠数字。
3. 在一个明确的 DMC Hard protocol 上运行 GENIEO 与该 baseline。
4. 同时报告 environment steps、UTD ratio、网络规模和 wall-clock。

### 无法完成时的回复策略

- 承认这些方法是重要的 overall RL references。
- 解释 submitted comparison 聚焦 generative-policy methods。
- 将 SOTA claim 收窄为 evaluated generative-policy baselines。

---

## E8. 精细控制中的 entropy trade-off

### 目的

回应 4ynL 关于 MaxEnt 可能损害 deterministic/stable precision behavior 的 limitation。

### 推荐任务与对照

- 优先 H1 Reach；如果有更明确的 precision-control task，也可替换。
- 比较：
  - automatic entropy tuning；
  - fixed small `alpha`；
  - `alpha=0`；
  - 训练 stochastic、评估 deterministic zero-latent action。

### 指标

- Success rate 或 target distance。
- Executed-action variance。
- Final-state variance。
- Return。
- Learned temperature trajectory。

### 目标结论

- 说明 automatic tuning 是否能在训练后期降低不必要的随机性。
- 如结果不支持，不应宣称该 trade-off 已解决，只说明适用范围。

---

## E9. 增加 seeds 与稳健性运行

### 目的

提高统计可信度，特别是高方差 H-Bench 结果。

### 优先任务

1. H1 Reach：当前方差最大。
2. H1 Sit Hard。
3. Dog Run：核心 ablation task。
4. DMC aggregate 中与 FlowRL 差距较小的任务。

### 建议

- 优先从 5 seeds 增加到 10 seeds，而不是在大量新任务上只跑 1--2 seeds。
- 保持 seed 列表在方法间配对。
- 报告 bootstrap CI/IQM，不只报告 standard deviation。

---

## 最小可行 Rebuttal 实验包

如果时间和算力有限，建议按以下顺序完成：

1. **E0 统计重分析：** 不需要重训，立即完成。
2. **E1 efficiency table：** Dog Run 上 GENIEO、Gaussian SAC、FlowRL 的统一计时。
3. **E3 dummy/environment entropy diagnostic：** 使用现有 checkpoint，成本较低且能回答核心机制问题。
4. **E2 direct coverage：** Dog Run 上 GENIEO、`alpha=0`、FlowRL，至少两个训练时间点。
5. **E4 Euler toy comparison：** 成本低，直接回应 BXmK。
6. **E5 additive/logdet ablation 或 E6 SAC baseline：** 根据现有代码和算力选择至少一个完整运行。

这套最小实验包能够覆盖三位 reviewer 的共同问题，并优先争取明确表示可能升分的 Reviewer BXmK。

## 实验完成后的统一记录格式

每项实验完成后记录：

- commit/checkpoint 标识；
- environment 与 task version；
- hardware；
- seeds；
- training steps、UTD ratio、batch size；
- baseline 配置差异；
- metric 定义；
- 原始数值与聚合方法；
- 可直接放入 OpenReview 的 2--4 句英文结论；
- 失败结果或与预期不一致之处。

## 提交前数据检查

- 不从单个 seed 推导结论。
- 不混用 evaluation return、training return 和 TAR。
- 不比较不同 environment-step budgets。
- 不把标准差当 confidence interval。
- 不把 augmented entropy 当 environment-action entropy。
- 不把 action diversity 当 state-space exploration 的充分证明。
- 不把相关性写成因果性。
- 不在三份 reviewer response 中使用相互矛盾的数字或口径。
