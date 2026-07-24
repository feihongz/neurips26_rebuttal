# Submission 10722 — Rebuttal 待补实验清单

> **用途：内部实验规划，不要整份粘贴到 OpenReview。**
>
> - 回复期不能修改论文或补充材料；新结果只能以简短文字或 Markdown 表格写入各审稿人的 Rebuttal。
> - 每位审稿人回复不超过 10,000 字符，不能上传文件或放置链接。
> - 所有 `[待填]`、`[待核实]` 和内部说明都应在提交回复前删除。
> - 新实验只能提供经验支持，不能替代对过强理论结论的澄清或收缩。

## 一、结论先行：实验优先级

不建议先做更密集的 flow-step、anchor-count 或大规模超参数网格。最能改变审稿判断的顺序是：

| 优先级 | 实验 | 主要回应 | 预计价值 | 主要成本 |
|---|---|---|---|---|
| P0-1 | 两任务四格组件消融 | MeUK、qUFY、4kU9 | 直接判断 positive/negative branch 是否真正贡献性能 | 中高 |
| P0-2 | DIME、DACERv2 强基线与统一统计 | 4kU9 | 决定经验优势和 SOTA 叙事是否仍成立 | 很高 |
| P0-3 | 现有日志重算 IQM、CI 和 aggregate | 4kU9 | 成本最低，直接修复标准化评估问题 | 低 |
| P0-4 | critic 排序可靠性与非平稳鲁棒性 | qUFY、4kU9 | 回答 noisy/non-stationary Q 是否会错误引导 anchors | 中 |
| P0-5 | 训练成本、显存和 batch-1 推理延迟 | qUFY | 直接回答审稿人的明确问题 | 低至中 |
| P0-6 | negative fraction：0%/25%/50% | MeUK、qUFY | 直接回答 no-negative 与 threshold 问题 | 中 |
| P1-1 | 低价值概率质量与 negative-anchor 有效性诊断 | 4kU9、MeUK | 为论文核心机制提供直接证据 | 低至中 |
| P1-2 | 粗粒度超参数敏感性 | qUFY、MeUK | 回答调参难度与默认值稳定性 | 中高 |
| P1-3 | Langevin 正锚点质量诊断 | qUFY、4kU9、MeUK | 判断 refinement 是否真实改善 anchors | 低；若重训则中高 |
| P2 | 合成环境中的理论 sanity check | 4kU9 | 只能说明标准 ULA 现象，不能解决在线 RL 理论问题 | 低 |

## 二、实验前必须先锁定的口径

在启动新实验前，应写出一份不可再变化的 canonical configuration。否则消融之间可能不是单变量对照。

必须核实：

1. 正式主结果实际使用的 repulsive coefficient \(\omega\) 是多少。论文表中为 \(0.1\)，当前代码调用为 \(0.05\)。
2. “16 positive anchors”究竟表示 16 个 flow candidates，还是实际进入正向 drift 的 top-5 anchors。
3. positive candidate 数和 negative candidate 数必须拆成独立参数，不能让一个 \(M\) 同时改变两边。
4. `no Langevin` 必须真正绕过 refinement；当前把 steps 设为 0 仍可能执行一步。
5. `random negative` 是否仅取消 bottom-Q selection，还是同时取消选中后的 Q-softmax weighting。两种实验回答的问题不同。
6. `no negative` 必须只屏蔽 repulsive force，不能同时删除 positive force 或把 positive anchors 回退为 negative anchors。
7. Naive Drift 的正负样本来源、candidate 数、top/bottom split、网络骨架、更新次数和 seeds 必须精确定义。
8. 所有新实验固定同一 actor/critic 架构、environment version、action repeat、warm-up、replay size、update-to-data ratio、evaluation schedule 和 checkpoint 选择规则。

建议所有训练变体同时保存：

- 环境步数与 wall-clock 时间；
- actor、critic、flow 各自更新时间；
- peak GPU memory；
- positive/negative field 的 unclipped norm、clipped norm 和 clipping rate；
- online/target/twin critic disagreement；
- early/mid/late checkpoints。

这样可以让同一批运行同时服务于组件归因、critic 诊断和计算成本分析。

---

## 三、P0-1：两任务四格组件消融

### 要回答的问题

性能提升究竟来自 base Max-Q objective、positive attraction、negative repulsion，还是两者组合？这是 MeUK 的核心问题，也是 qUFY 对组件复杂度以及 4kU9 对 originality/negative validity 的共同疑问。

### 最小因子设计

所有行均保留相同的 Max-Q/base actor objective：

| 变体 | Max-Q/base | Positive branch | Negative branch | 目的 |
|---|---|---|---|---|
| Base / Max-Q only | On | Off | Off | 给出共同基线 |
| Positive-only | On | On | Off | positive branch 的增量 |
| Negative-only | On | Off | Q-filtered | negative branch 的增量 |
| Full DADC | On | On | Q-filtered | 检查组合和交互效应 |

强烈建议再复用或补充：

| 变体 | 与 Full 的唯一目标差异 | 目的 |
|---|---|---|
| Full without Langevin | positive anchors 不做 stochastic refinement | 隔离 refinement |
| Full with random-negative selection | 从同一 actor pool 随机选 \(K\) 个 | 隔离 bottom-Q selection |
| Naive Drift | 正负 anchors 均由 current actor 产生并按 Q 划分 | 检验“decoupled source”是否重要 |

### 任务与随机种子

- 必须包含 Dog Run，以便连接原有 Figure 4。
- 至少增加一个形态、动作维数或动力学明显不同的任务。推荐预先指定一个稳定的 HumanoidBench 任务，例如 H1 Crawl；不要看完结果后再选择。
- 资源允许时再加入 Humanoid Run，形成 Dog Run、Humanoid Run、H1 Crawl 三任务组合。
- 每项至少 5 个 paired seeds；关键比较若方差较大，补到 10 seeds。
- 不允许为每个 ablation 单独调参。

### 干净对照要求

- 因果归因版本中，最好仍计算被屏蔽分支，只在最终 vector field 处 mask 掉，使训练计算量匹配。
- 系统成本版本中，可完全移除该分支，但必须明确其同时减少了计算量。
- `no Langevin` 保留同一批 flow candidates 和同一 top-\(k\)，只绕过 refinement。
- `random-negative selection` 使用同一 actor candidate pool、相同 \(M\) 和 \(K\)，不能重新采另一批动作。
- 若随机选中后仍使用 Q-softmax weighting，应命名为“random selection, Q-weighted field”，不能称为“without Q-value”。

### 应报告的指标

- 固定 final window 的 return；
- learning-curve AUC；
- 达到预设 return threshold 的环境步数和 wall-clock；
- paired-seed 差值及 bootstrap 95% CI；
- 失败种子比例；
- positive/negative field norm 与 clipping rate。

### 结果占位表

| Variant | Dog Run | H1 Crawl / 另一预设任务 | AUC | Paired difference vs Full |
|---|---:|---:|---:|---:|
| Base / Max-Q only | [待填] | [待填] | [待填] | [待填] |
| Positive-only | [待填] | [待填] | [待填] | [待填] |
| Negative-only | [待填] | [待填] | [待填] | [待填] |
| Full DADC | [待填] | [待填] | [待填] | — |
| Full without Langevin | [待填] | [待填] | [待填] | [待填] |
| Random-negative selection | [待填] | [待填] | [待填] | [待填] |
| Naive Drift | [待填] | [待填] | [待填] | [待填] |

### 能与不能得出的结论

可以判断各 branch 在所测任务上的增量和交互效应。不能据此证明 monotonic policy improvement、全局最优、多模态收敛，或 negative repulsion 在所有任务上都必需。

---

## 四、P0-2：补 DIME、DACERv2，并统一 baseline 协议

### 理想设计

- 在原论文全部 14 个任务上补 DIME 和 DACERv2。
- 每个方法使用与 DADC 相同的 environment interactions、evaluation schedule 和 5 个 paired seeds。
- 同时保留原有 SAC、FlowRL、DACER 等结果。
- baseline 使用其推荐配置，但每个方法获得相近的 tuning budget。

### Rebuttal 时间有限时的最低设计

预先指定而非按结果筛选：

1. 一个 DMC hard task，例如 Dog Run；
2. 一个高维 HumanoidBench task，例如 H1 Crawl；
3. 资源允许时再加入一个 DMC easy 或中等难度任务。

若只完成少数任务，回复中必须将结论限定为“在新增的代表性任务上”，不能继续用这些结果支撑 14-task 全面 SOTA。

### 公平性控制

- 相同 environment/version、action repeat、observation/action normalization 和 reward preprocessing；
- 相同 warm-up、environment budget、evaluation episodes/frequency 和 seeds；
- 明确 update-to-data ratio、网络规模、replay size 与 checkpoint selection；
- 同时报 equal-environment-step 和 equal-wall-clock 结果；
- 所有方法的运行配置与调参预算用简洁文字或表格写入回复，不能放链接。

### 应报告的指标

- per-task final-window return 与 AUC；
- task-normalized IQM 和 stratified bootstrap 95% CI；
- probability of improvement 或 performance profile；
- 总 GPU-hours、training steps/s、peak memory；
- actor inference latency。

### 结果占位表

| Method | DMC normalized IQM [95% CI] | H-Bench normalized IQM [95% CI] | Seeds | Environment budget | GPU-hours |
|---|---:|---:|---:|---:|---:|
| DADC | [待填] | [待填] | [待填] | [待填] | [待填] |
| DACERv2 | [待填] | [待填] | [待填] | [待填] | [待填] |
| DIME | [待填] | [待填] | [待填] | [待填] | [待填] |
| FlowRL | [待填] | [待填] | [待填] | [待填] | [待填] |
| SAC | [待填] | [待填] | [待填] | [待填] | [待填] |

---

## 五、P0-3：用现有 raw logs 重做统计

这部分几乎不增加训练成本，应最先完成。

### 必做项目

1. 预先固定 final-window 定义，例如最后 10 次 evaluation 的平均值。
2. 保留每个 task、每个 seed 的原始 score。
3. 按 task 先做预先定义的 normalization，再计算 benchmark IQM；不能直接对量纲悬殊的 H-Bench raw returns 求平均。
4. 使用 stratified bootstrap 给出 95% CI。
5. 对同 seed 运行报告 paired difference 或 probability of improvement。
6. 正确计算 suite aggregate 的 seed-level variability；不能把各任务标准差简单平均后称为 aggregate std。
7. 明确区分 std、SEM 和 95% CI。
8. 对 H1 Reach 等高方差任务，资源允许时将关键方法增加到 10 seeds。

### 必须避免

- 不能说“IQM 可以替代更多 seeds”；它只是更稳健的 aggregate。
- 没有正式检验时不要声称 statistical significance。
- normalization 不能使用观察到的 test maximum 临时定义。
- 不能只报告 best checkpoint。

---

## 六、P0-4：critic 排序可靠性与非平稳鲁棒性

建议将“诊断 critic 是否可靠”和“训练在错误 critic 下是否稳健”拆成两项。

### A. Negative-anchor 排序审计

在 Dog Run 和第二个预设任务的 early/mid/late checkpoint：

1. 选取约 32–64 个可恢复的 simulator states；
2. 每个状态从 current actor 采样 16 个候选动作；
3. 按训练时的 online critic 选择 bottom-4；
4. 若环境允许恢复状态，对每个动作执行一次后，用冻结当前 policy 做 5–10 次 rollout，估计 \(Q^\pi(s,a)\)；
5. 比较 online critic ranking、target/twin critic ranking 与 Monte Carlo ranking。

应报告：

- Spearman/Kendall rank correlation；
- bottom-4 precision/recall；
- 被错误排斥的 true top-quartile 比例；
- selection regret；
- online/target/twin critic disagreement；
- bottom-\(K\) 集合的 overlap 或 Jaccard similarity。

若不能进行 simulator branching，可使用未参与训练的 critic ensemble 作为较弱代理，但必须明确它不是 ground-truth return。该实验验证的是对当前 \(Q^\pi\) 的 operational ranking，不能验证与 \(Q^*\) 的梯度误差假设。

### B. 训练鲁棒性对照

最低比较：

| Setting | 仅改变的部分 | 目的 |
|---|---|---|
| Default | online critic 从训练开始筛选 | 主设置 |
| Delayed repulsion | 前 50k/100k steps 关闭 negative branch | 检查 early noisy Q |
| Target-critic screening | 用 target critic 做 top/bottom selection | 检查较平滑 guidance |

资源允许时再增加：

- 只对 negative ranking score 加标准化噪声；
- 只对 Langevin \(\nabla_a Q\) 加 gradient noise；
- twin critic disagreement 较高时跳过或减弱 repulsion。

噪声应按同一状态 candidate Q 的标准差归一化，例如
\[
\widetilde Q_i=Q_i+c\,\mathrm{Std}(Q_{1:M})\epsilon_i,\qquad
c\in\{0,0.25,0.5,1.0\}.
\]

不要向整个 critic 或 Bellman target 一次性加噪声，否则会同时污染 Max-Q、flow weighting、ranking、Langevin gradient 和 field weighting，无法定位原因。

### 结果占位表

| Setting | Dog Run return | 第二任务 return | Early bottom-4 precision | Rank correlation | Failure rate |
|---|---:|---:|---:|---:|---:|
| Default | [待填] | [待填] | [待填] | [待填] | [待填] |
| Delayed repulsion | [待填] | [待填] | [待填] | [待填] | [待填] |
| Target-critic screening | [待填] | [待填] | [待填] | [待填] | [待填] |
| Ranking noise \(c=[\,]\) | [待填] | [待填] | [待填] | [待填] | [待填] |

这些结果只能说明经验鲁棒性，不能证明 Assumption 2、critic convergence 或 policy improvement。

---

## 七、P0-5：训练与推理成本

### 比较对象

至少比较 DADC、SAC、FlowRL；若已补齐，加入 DIME 和 DACERv2。硬件、软件、网络规模、dtype 与计时方式必须一致。

### 推理

分别测：

- deterministic evaluation action；
- stochastic action generation；
- batch size 1、16、256；资源允许时再测 1024；
- model-only latency 与包含数据传输的 end-to-end latency。

计时要求：

- 足够 warm-up；
- CUDA 计时前后同步；
- inference mode；
- 数千次重复；
- 报告 median 和 P95；
- compile time 与 steady-state latency 分开。

batch-256 的 GPU forward latency不能代替真实控制更相关的 batch-1 latency。

### 训练

报告：

- environment steps/s；
- gradient updates/s；
- 固定环境步数的总 wall-clock；
- peak GPU memory；
- actor、critic、flow、anchor/Langevin 各模块时间占比；
- wall-clock learning curve；
- time-to-50%/80% target return。

DADC 的训练成本必须包含 flow prior、candidate generation、Q filtering 和全部 refinement steps。所有新训练都应顺手记录这些数据，无需另跑完整性能实验。

### 结果占位表

| Method | Train env steps/s | Total hours | Peak memory | Batch-1 median/P95 | Batch-256 median/P95 |
|---|---:|---:|---:|---:|---:|
| DADC | [待填] | [待填] | [待填] | [待填] | [待填] |
| FlowRL | [待填] | [待填] | [待填] | [待填] | [待填] |
| SAC | [待填] | [待填] | [待填] | [待填] | [待填] |
| DACERv2 / DIME | [待填] | [待填] | [待填] | [待填] | [待填] |

---

## 八、P0-6：negative fraction 与 \(\omega\)

### Negative fraction

- 固定 \(M_{\text{neg}}=16\)；
- 只改变 \(K\)：0、4、8，对应 0%、25%、50%；
- 固定 \(\omega\)；
- 固定 positive candidate 数和 positive top-\(k\)；
- 在 Dog Run 与第二个预设任务上运行。

0% 就是 no-negative，因此可与四格消融复用。当前整理版评审把 50% 称作“更严格”，该措辞语义可疑，正式实验前应回到 OpenReview 原始渲染核实。

### \(\omega\) sensitivity

另做独立 sweep，固定 \(K/M=4/16\)。建议以已核实的正式默认值 \(\omega_0\) 为中心测试：

\[
\omega\in\{0,\;0.5\omega_0,\;\omega_0,\;2\omega_0\}.
\]

\(\omega=0\) 同样可复用 no-negative。不要把 negative fraction 和 \(\omega\) 同时改变，否则无法判断是负样本数量还是 force scale 起作用。

### 同时记录

- return/AUC；
- unclipped positive/negative field norm；
- clipped field norm；
- vector-field clipping fraction。

如果较大的 \(\omega\) 因最终 clipping 而进入平台，不能将其解释为方法天然对 \(\omega\) 不敏感。

### 结果占位表

| Bottom fraction | \(K/M\) | Fixed \(\omega\) | Dog Run | 第二任务 | Negative-field norm |
|---:|---:|---:|---:|---:|---:|
| 0% | 0/16 | [待填] | [待填] | [待填] | 0 |
| 25% | 4/16 | [待填] | [待填] | [待填] | [待填] |
| 50% | 8/16 | [待填] | [待填] | [待填] | [待填] |

---

## 九、P1-1：直接测量“低价值概率残留”

这是对核心机制最直接、且可以复用已有 checkpoints 的诊断。

### 最小设计

在一组固定 held-out states 上：

1. 每个 checkpoint、每个状态从 actor 采样 512–1024 个动作；
2. 使用 simulator branching Monte Carlo 或未参与训练的 evaluator 定义低价值动作；
3. 比较 Base、Positive-only、Negative-only、Random-repulsion 和 Full DADC；
4. low-value set 应用共同规则定义，例如同一状态候选动作中独立 \(Q^\pi\) 的 bottom 10%/25%，不能用每个方法自己的训练 critic 自我验证。

### 应报告

- 低价值动作概率质量；
- action-value CVaR-10%/25%；
- sampled-action mean value；
- kNN entropy、平均 pairwise distance 或 mode coverage；
- repulsion 更新前后的独立评价值；
- 训练阶段变化。

如果 Full 降低低价值尾部但也导致 action collapse，应如实报告。有限采样只能支持“减少了所定义低价值区域中的估计质量”，不能声称 probability residue 被完全消除。

---

## 十、P1-2：粗粒度超参数敏感性

qUFY 真正关心的是是否需要任务级精细调参，而不是一张更密的 sweep 图。

### 推荐范围

在 Dog Run 和第二个预设任务上，每个因素只取低/默认/高三个值：

| 因素 | 建议设计 | 注意事项 |
|---|---|---|
| attraction/drift coefficient \(\alpha\) | \(0.5\alpha_0,\alpha_0,2\alpha_0\) | 固定 \(\omega\) 与 field scale |
| repulsive coefficient \(\omega\) | \(0.5\omega_0,\omega_0,2\omega_0\)；另复用 0 | 固定 \(K/M\) |
| flow steps | 原有 1/5/10 或低/默认/高 | 同时报训练成本 |
| positive candidates | 低/默认/高 | 必须与 negative pool 解耦 |
| Langevin steps | 0/default/high | 0 必须真正 bypass |

优先使用一套跨任务共享 defaults，不要在测试任务上选出各自最优值后只汇报最优结果。报告稳定区间、失败率和训练成本，而不是只给最好的一点。

若预算紧，先复用原有 flow-step/anchor-count 结果，仅补 \(\alpha\)、\(\omega\) 和第二任务；不建议做完整笛卡尔积。

---

## 十一、P1-3：Langevin 正锚点质量

### 低成本 checkpoint 诊断

对固定 held-out states 和相同初始 flow anchors，记录：

- refinement 第 0、1、2、3、4 步的 online/target critic Q；
- 独立 rollout \(Q^\pi\)（若可行）；
- anchor displacement；
- action-boundary violation 与 clipping rate；
- anchor diversity；
- twin/target critic disagreement。

比较：

1. flow anchors + top-\(k\)，不 refinement；
2. deterministic Q-gradient ascent；
3. 实际实现的 stochastic refinement；
4. 仅作为内部核查：与论文公式一致的 noise scaling。

若实际实现使用 \(\eta=0.02\)、noise scale \(0.01\)，而论文公式给出 \(\sqrt{2\eta}=0.2\)，必须先核实真实主结果配置。训练 critic Q 上升不等于真实 return 上升，也不能证明分布收敛到 Boltzmann target。

---

## 十二、P2：合成环境理论 sanity check

可在一维或二维已知 \(Q^*\) 的固定 critic 中：

- 使用单峰强凹 quadratic \(Q\)；
- 改变步长 \(\eta\) 与可控 gradient bias \(\delta\)；
- 计算真实 \(W_2(q_k,p^*)\)；
- 观察 contraction 与 residual floor；
- 再用多峰 \(Q\) 展示局部强凸假设之外的行为。

这项实验最多说明标准 fixed-target ULA bound 在适用条件下具有定性合理性。它不能修复：

- current \(Q^\pi\) 与 \(Q^*\) 的差异；
- online actor–critic convergence；
- Equation 9 的 monotonic policy improvement；
- 全局 multimodal convergence。

若时间有限，应优先诚实收缩理论结论，而不是做这项实验。

---

## 十三、按审稿人映射

### Reviewer qUFY

必须优先准备：

1. full component ablation；
2. default vs delayed/target critic robustness；
3. train throughput、wall-clock、memory、batch-1 inference；
4. \(\alpha,\omega\)、flow steps、anchor count 的粗粒度稳定范围；
5. 一套跨任务的统一默认参数和选择规则。

### Reviewer 4kU9

必须优先准备：

1. DIME、DACERv2；
2. normalized IQM 与 stratified bootstrap CI；
3. critic ranking、anchor validity 和 OOD/clipping diagnostics；
4. full component ablation；
5. 公平的 baseline 配置与任务选择原则。

但 policy improvement、critic convergence 和 exact convergence 不能靠实验回答，应在文字中明确不作这些保证。

### Reviewer MeUK

必须优先准备：

1. Dog Run + 至少一个新任务的四格消融；
2. no-negative；
3. no-positive；
4. 0%/25%/50% negative fraction，固定 \(\omega\)；
5. 第二任务复现 no-Langevin 与 random-negative；
6. Naive Drift 的精确定义，必要时在公平协议下重跑。

---

## 十四、计算预算有限时的最小可行方案

### 可信最小包

选择：

- Dog Run；
- 一个预先指定的 HumanoidBench task。

新训练：

1. Base、Positive-only、Negative-only：两任务各 5 seeds；Full 尽量复用已有结果，共约 30 个新 runs。
2. DIME、DACERv2：两任务各 5 seeds，共约 20 个新 runs。
3. Dog Run 上一个 delayed-repulsion 或 target-critic 变体，5 seeds。
4. 若还能增加 5–10 个 runs，优先补第二任务的 50% negative fraction，而不是新的 anchor-count 设置。

近乎零额外训练成本：

- 全部旧 logs 重算 IQM 与 bootstrap CI；
- 所有方法统一做 latency/throughput/memory benchmark；
- 用已有 early/mid/late checkpoints 统计 critic disagreement、anchor displacement、Q ranking 和 low-value mass；
- 复用已有 Dog Run no-Langevin、random-negative runs，但必须先确认其实现含义。

这一方案约需 55–65 个新训练 runs。它不能完全满足 4kU9 对 14 个任务强基线的理想要求，但能集中回答最有判别力的问题。

### 极低预算包

若只能增加约 20–25 个 runs：

1. 两任务的 Full vs no-negative，复用 Full，只补约 10 个 runs；
2. DIME 和 DACERv2 各在一个预先指定任务上跑 5 seeds，共约 10 个 runs；
3. 其余只做 IQM、latency 和 checkpoint diagnostics。

该版本无法充分回答 MeUK 对 no-positive/base factorial 的明确要求，也无法消除 4kU9 对 baseline 覆盖的批评。回复时必须主动承认覆盖范围。

---

## 十五、不能用新增实验“解决”的问题

以下问题只能通过澄清或收缩主张处理，不能因为某个 empirical curve 看起来稳定就宣称已经解决：

- Theorem 1 在固定非零 critic error 和 step size 下的 residual 不消失；
- Assumption 2 要求 learned critic 接近 \(Q^*\) 的 action gradient；
- Equation 9 没有 true-return monotonic policy-improvement guarantee；
- 没有完整 nonlinear off-policy critic/actor convergence；
- Q-gradient 是 local value ascent/exploitation，不是形式化 exploration guarantee；
- “decoupled”只能指 sample source、parameter role 或 optimization path，不能指与 Q nonstationarity 无关；
- Bottom-\(K\) 只能称为 critic-ranked relative negatives，不能称为 ground-truth bad actions。

实验的作用是说明方法在所测试条件下具有 operational validity 和 robustness，而不是把这些理论缺口变成定理。
