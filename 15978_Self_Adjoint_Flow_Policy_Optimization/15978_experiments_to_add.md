# SAFLOW Rebuttal：待补实验清单

> 本文档仅用于内部安排实验。Rebuttal 期间不能修改原论文或补充材料；新结果只能以纯文本/Markdown 写入对应审稿人的 OpenReview 回复。不得上传文件、放链接或泄露身份。每位审稿人的最终回复仍需控制在 10,000 字符以内。

## 一、结论先行：建议优先补什么

### P0：最值得优先完成

1. **Compute-matched GenPO 对照**：同 \(K\)、同 velocity-network evaluations（NFE）、GenPO doubled steps、同 wall-clock 四种口径至少覆盖其中前三种。
2. **Augmented ratio 与 executed-action change 的对齐诊断**：报告 augmented KL/ratio、clip fraction、实际动作变化和 fiber-only 变化。
3. **训练后非线性 velocity field 上的数值误差诊断**：相对高精度 continuous reference 测 state、inverse、log-likelihood 和 old/new ratio error，并与 clipping/return 联合分析。

这三项共同回答 sTxw 和 pw8T 最核心的质疑，也能加强 Gdko 所问的“二阶结构什么时候真正有用”。E2、E3 可复用 E1 的 checkpoints 和 rollout，适合一起设计。

### P1：有资源时应补

4. **H1、Go2、Shadow Hand 的效率测量**：wall-clock、throughput、peak memory 和 time-to-threshold，对比 PPO/GenPO。
5. **Compression 的跨任务敏感性与 fiber 诊断**：在 Ant 之外至少增加 Humanoid 和一个高维任务。
6. **2d augmentation / original-d block split 对照**：用于回答 h1HA；实现和公平匹配难度较高，只有在能做严谨对照时再报告。

### P2：实现成本较高、可用充分讨论替代

7. **GenPO++ baseline**：若能获得可信、匿名且 compute-matched 的实现则补；否则只做准确的机制与成本讨论。
8. **RN-D baseline**：可检验“更 expressive actor 是否普遍有效”，但不是隔离 integrator 的直接对照，优先级低于 E1。
9. **Adaptive \(\nu\) schedule**：审稿人将其作为改进建议而非必要要求；固定 \(\nu\) 的跨任务证据更优先。

## 二、审稿人—实验映射

| 实验包 | 主要回答 | 对应审稿意见 |
|---|---|---|
| E1 Compute-matched GenPO | 收益是否只是 SAFLOW 多做了 velocity evaluations；额外成本是否值得 | sTxw W2/Q2；Gdko W4/W6；pw8T Q4/Q5 |
| E2 Augmented/projected alignment | dummy-action clipping 是否约束了有意义的实际动作变化 | pw8T C1/Q2；间接回应 h1HA 的 augmentation/regularization |
| E3 Nonlinear numerical-to-RL chain | toy 的二阶优势能否迁移到训练后的高维非线性 flow，并影响 PPO | sTxw W1/Q1；pw8T C4/Q5；Gdko W6 |
| E4 High-dimensional efficiency | H1、Go2、Shadow Hand 上相对 PPO/GenPO 的实际代价 | Gdko W3/W4；pw8T C3/Q4 |
| E5 Compression robustness | \(\nu\) 怎么选、是否改变优化、能否控制 null fiber | Gdko W5/Q2；pw8T Q3；h1HA T1/Q2 |
| E6 Augmentation ablation | 为什么使用 \(2d\)，original-d block split 是否也可以 | h1HA Q2；pw8T C1 |
| E7 Recent baselines | 与 RN-D、GenPO++ 的经验定位 | Gdko W2；pw8T C2/Q1/Q4 |

## 三、各实验包的具体设计

## E1. Compute-matched GenPO 对照

### 目的

排除“SAFLOW 仅仅因为每步计算更多”这一解释，并直接回答 doubled-flow-step GenPO 和计算成本问题。

### 最小实验矩阵

- 任务：Ant、Humanoid。
- 方法：
  1. GenPO，原论文默认 \(K\)；
  2. SAFLOW，相同 nominal \(K\)；
  3. GenPO，增加步数使总 NFE 与 SAFLOW 匹配；
  4. GenPO，flow steps 直接加倍（审稿人明确要求）；
  5. 若资源允许，再加入严格相同 wall-clock budget 的比较。
- Seeds：最好沿用主论文的 5 seeds；若只能做 3 seeds，必须明确标为追加/初步结果并报告每个 seed。
- 保持一致：actor/critic size、batch size、parallel environments、PPO epochs、训练 environment steps、硬件和软件设置。

### 必须记录的指标

- Return-versus-environment-steps。
- Return-versus-wall-clock-time。
- 最终 return：mean ± std，并保留逐 seed 数值。
- 每次 action sampling、likelihood evaluation 和完整 PPO update 的 velocity-network calls。
- Samples/second、总 wall-clock 和 peak GPU memory。
- 如报告 time-to-threshold，阈值需在看新增结果前固定，并对所有方法一致。

### 公平性注意

- equal \(K\) 不等于 equal compute。按单个 split step 计，SAFLOW 通常有三次 velocity evaluations，而一阶 alternating GenPO 有两次；应以实际 instrumentation 为准。
- PPO 会在多个 minibatch/epoch 中重复计算 likelihood，因此不能只统计 rollout sampling 的 NFE。
- 不要只给最终 return；审稿人关心的是 performance-cost frontier。

### 可直接复用到哪些回复

- sTxw：doubled-step GenPO、计算成本。
- Gdko：23–32% overhead 是否值得、二阶何时有效。
- pw8T：wall-clock trade-off、数值结构是否改善优化。

## E2. Augmented ratio 与 executed-action change 的对齐诊断

### 目的

检验 augmented dummy-action ratio/clipping 在训练中是否主要对应实际执行动作的变化，还是大量消耗在 projection null fiber 上。

### 推荐做法

- 任务：Ant、Humanoid；可直接复用 E1 的 old/new policy checkpoints 和 rollout buffer。
- 对每次 PPO update 记录：
  - augmented log-ratio \(\log r_{\widetilde{\mathcal A}}\) 的均值、标准差和分位数；
  - augmented empirical KL；
  - clip fraction；
  - paired/common-noise 下的 augmented change \(\|z_{new}-z_{old}\|\)；
  - executed-action change \(\|M(z_{new})-M(z_{old})\|\)；
  - fiber change，例如 \(\|(x-y)_{new}-(x-y)_{old}\|\)；
  - compression energy \(\|x-y\|^2\)。
- 给出 \(|\log r_{\widetilde{\mathcal A}}|\) 与 executed-action change 的相关性，同时报告其与 fiber change 的相关性。
- 比较 \(\nu=0\) 与默认 \(\nu=0.01\)，观察 compression 是否减少 fiber-only change，以及是否改善 ratio/action-change 对齐。

### 可选但需谨慎的指标

- Projected-action KL 或 projected density ratio。由于 \(M:\mathbb R^{2d}\to\mathbb R^d\) 是 many-to-one，projected density 需要沿 fiber 积分，不能把 augmented ratio 当成 projected ratio。
- 只有在 sample-based KL/ratio estimator 经低维校准并给出误差条后才报告；否则优先报告可靠的样本级 executed-action change、MMD/energy distance 等分布变化指标，并准确注明它们不是 exact KL。

### 结果应如何解释

- 理论上 projected ratio 是 augmented ratio 在 fiber 上的条件期望，divergence 在 projection 下收缩；实验用于量化保守程度，不是重新证明该结论。
- 若 augmented clipping 对 fiber-only change 很敏感，应坦率报告，并观察 compression 能缓解多少。
- 不要使用“两个 trust region 等价”；最多说 augmented control 是 valid and conservative。

## E3. 训练后非线性 flow 的数值误差—PPO 行为链

### 目的

把 Appendix C.4 的线性 2D toy 扩展到真实训练所得的高维、非线性、time-conditioned velocity field，并区分“离散策略自身 likelihood 的精确性”和“相对 continuous flow 的 discretization bias”。

### 数值诊断设计

- 从 Ant、Humanoid 的不同训练阶段抽取固定 checkpoints、states 和 base latents。
- 冻结 velocity network，不再训练。
- 用足够严格容差的高精度 ODE solver 产生 continuous reference；验证收紧容差后结果稳定。
- 对 GenPO 与 SAFLOW，在 equal \(K\) 和 equal NFE 两种条件下测：
  - forward terminal-state error；
  - 从 continuous terminal point 反推 latent 的 inverse-to-continuous error；
  - continuous-reference log-likelihood error；
  - old/new log-ratio error；
  - 随 \(h\) 或 \(K\) 的 empirical convergence slope。

### 必须区分的两个 inverse 指标

1. **Discrete round-trip error**：numerical forward 后再用其代数 inverse 返回，SAFLOW 理论上应接近浮点误差。
2. **Continuous inverse approximation error**：从 continuous reference terminal point 用离散 inverse 返回，这是随 \(h\) 收敛的量。

两者不能混写，否则会加重审稿人对 Theorem 3/Table 5 的疑问。

### 与 RL 行为的联合分析

- 将上述 ratio error 与同一 checkpoint/update 的：
  - clip fraction；
  - augmented KL；
  - executed-action change；
  - policy loss/gradient norm；
  - 后续短窗口 return change
  联合报告。
- 可给 Spearman correlation 和 bootstrap confidence interval，但应标为关联性分析，不声称因果。
- 最有说服力的图是：随着 \(K\)/NFE 变化，continuous-reference ratio error、clip fraction 和 return 同时如何变化。

### 与 degradation-curve 请求的关系

- sTxw 的原评审在 “when” 后缺少具体符号。最稳妥的执行解释是扫描 solver coarseness：\(K\) 增大、\(h\) 减小。
- 若还要扫描“训练难度”，可选择预先定义的 PPO update magnitude 或 rollout setting；不要在不确定审稿人原意时堆很多任意 sweep。

## E4. H1、Go2、Shadow Hand 的高维效率

### 目的

补足论文只在 Ant/Humanoid 报 wall-clock 的缺口，并回答与 PPO 相比的实际价值。

### 实验矩阵

- 任务：
  - Isaac-Velocity-Rough-H1-v0；
  - Isaac-Velocity-Rough-Unitree-Go2-v0；
  - Isaac-Repose-Cube-Shadow-Direct-v0。
- 方法：PPO、GenPO、SAFLOW；若资源不足，优先保证三种方法使用完全相同的 profiling protocol。
- Seeds：完整学习曲线最好 5 seeds；纯系统 profiling 可在固定 seed/固定步数重复 3 次，但必须与 return 统计分开。

### 指标

- Final return 和 return-versus-environment-steps。
- Return-versus-wall-clock、time-to-threshold。
- Environment steps/second、policy updates/second。
- Actor sampling time、likelihood/update time、environment simulation time的分解。
- Peak allocated/reserved GPU memory 和 host memory。
- Parameter count、NFE 和并行环境数。

### 省算力方案

- 先检查既有训练日志是否已保存 wall-clock timestamps；若有，可直接重建 performance-time curves，无需重跑 return。
- Memory 和 component timing 可用一个固定 checkpoint 做短时 instrumented profiling，但应明确它不是完整训练时间。

## E5. Compression 的跨任务敏感性与 adaptive schedule

### 已有证据

- Figure 4(b) 已在 Ant 上扫描 \(\nu\in\{0,0.01,0.1,0.5,1\}\)。这项不需要原样重跑。
- 主实验随后统一使用 \(\nu=0.01\)。

### 最小新增实验

- 任务：Humanoid + 一个高维任务（优先 Shadow Hand，或根据算力选择 H1）。
- 固定值：至少 \(\nu\in\{0,0.01,0.1\}\)；有资源再补齐与 Ant 相同的完整网格。
- 指标：return、compression energy、fiber change、executed-action change、augmented KL、ratio std、clip fraction、action diversity/entropy proxy。
- 与 E2 共用 instrumentation，避免单独开发。

### Adaptive schedule（可选）

- 只有在固定 \(\nu\) 的结果显示明显 task dependence 时再做。
- 至少比较：固定 \(0.01\)、简单 warm-up/annealing、基于 fiber energy 的反馈方案。
- 在定义 schedule 前固定目标和阈值，避免根据最终 return 反复调节。
- 若未完成，回复中只把 adaptive schedule 作为 future direction，不写成已经验证的解决方案。

## E6. \(2d\) augmentation / block-split ablation

### 目的

回答 h1HA：“为什么必须升到 \(2d\)，把原始 \(d\) 维动作拆成两块是否也能做 Verlet？”

### 建议比较

1. SAFLOW \(2d\) + 默认 compression。
2. SAFLOW \(2d\) + \(\nu=0\)（Ant 已有部分证据，可复用）。
3. Original-\(d\) two-block self-adjoint/coupling variant。
4. 若可行，加入多 mask/permutation 的 original-\(d\) variant，避免单一 partition 人为限制 expressivity。

### 公平匹配

- 匹配 parameter count、NFE、PPO budget 和 wall-clock；至少同时报告无法完全匹配的部分。
- 对 odd \(d\) 和 \(d=1\) 明确 block 定义。
- 保持投影、action squashing/clipping 和 base distribution 的差异透明。

### 指标

- Return、sample/wall-clock efficiency、memory。
- Continuous-reference numerical error 和 ratio statistics。
- Action-coordinate coverage、fiber energy（只适用于 augmented variant）和 executed-action diversity。

### 决策原则

- 这是实现风险最高的结构性 ablation。若 original-\(d\) variant 没有经过充分调试，仓促的负结果不能证明 \(2d\) 必要，反而容易被认为比较不公平。
- 没有可靠结果时，使用严谨的直觉回答：\(2d\) 不是数学上唯一方案，而是能让两个完整 action registers 对称耦合、适用于 odd/one-dimensional action 的充分设计。

## E7. RN-D 与 GenPO++ baselines

### E7-a. RN-D

- 任务建议：Ant、Humanoid；若 reviewer 特别关注高维，可再选 H1。
- 使用可信实现和相同 environment steps、parallelism、actor/critic budget。
- 报 final return、learning curve、wall-clock、memory、parameter count。
- 定位：它检验 expressive actor 的一般收益，不是 self-adjoint integrator 的 matched ablation。

### E7-b. GenPO++

- 只有在能确认实现语义、默认设置和 likelihood computation 均正确时才运行。
- 任务建议：Ant、Humanoid；至少做 equal environment steps、equal wall-clock 和明确的 NFE/solver-order 报告。
- 同时报告 action dimension、是否 augmentation、memory 和 inverse/ratio computation cost。
- 若来不及做公平实现：不放结果；将其定位为 concurrent closely related work，逐项比较 mechanism、order、augmentation 和计算 trade-off。

## 四、现有结果无需重复跑

以下内容已在原提交中，rebuttal 应优先直接引用和解释：

- 八任务主结果：Table 1。
- Ant 上 \(K\)、\(\nu\)、time-embedding dimension、hidden size sensitivity：Figure 4。
- SAFLOW 与 GenPO 在 Ant/Humanoid 的现有 wall-clock：Table 4。
- Performance-versus-normalized-time：Figure 7。
- 同一 SAFLOW 实现中的 first-order vs second-order return：Appendix C.2。
- Likelihood-ratio standard deviation：Appendix C.3。
- 2D time-varying toy 的一阶/二阶 convergence：Appendix C.4。

需要补的是这些已有证据之间的 **compute matching、high-dimensional generalization、projected-action alignment 和 mechanism-level linkage**，不是简单重复原图。

## 五、推荐执行顺序与数据复用

1. 先实现统一 instrumentation：NFE、component time、peak memory、augmented ratio/KL、clip fraction、executed/fiber action change。
2. 跑 E1 的 Ant/Humanoid compute-matched checkpoints。
3. 用 E1 checkpoints 和 buffers 离线完成 E2。
4. 冻结同一批 checkpoints，完成 E3 的 high-accuracy reference-solver 诊断。
5. 从既有日志恢复 E4 的 wall-clock；只对缺失的 memory/component timing 做短 profiling，必要时再重跑。
6. 复用 E2 instrumentation 跑 E5 的少量跨任务 \(\nu\) 网格。
7. 最后根据剩余时间决定 E6、RN-D 和 GenPO++；不要为了数量牺牲公平性。

## 六、每项实验完成后的统一检查

- 与原论文完全相同的 task version、training budget 和 evaluation protocol。
- 报告 seeds、mean、std，并保留逐 seed 值；不要只报最好一次。
- 同一硬件、并行环境数、batch size 和 PPO epochs；任何差异均显式说明。
- 同时给 environment-step 和 wall-clock 横轴。
- 明确 equal \(K\)、equal NFE、equal wall-clock 分别是什么，不混用“公平计算量”。
- 区分 discrete round-trip accuracy 与 continuous-flow approximation accuracy。
- 相关性不写成因果；单任务结果不写成跨任务普遍结论。
- 最终 OpenReview 回复只粘贴最关键的数字/小表格，不上传图或文件，不放链接。
