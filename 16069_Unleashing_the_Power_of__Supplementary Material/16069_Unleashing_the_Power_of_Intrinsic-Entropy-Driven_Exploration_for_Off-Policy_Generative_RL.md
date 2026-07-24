# 16069 Unleashing the Power of Intrinsic-Entropy-Driven Exploration for Off-Policy Generative RL

## Rebuttal 写作规则

> 内部写作大纲。提交 OpenReview 前删除所有中文提示、`[待补]` 占位符和本节说明。

- 三位审稿人分别使用各自的 **Rebuttal** 按钮提交，不能合并成一份总回复。
- 每位审稿人的回复不得超过 **10,000 characters**，建议成稿控制在 8,000--9,000 characters。
- 只能提交 plain text/Markdown，不上传文件，不放链接。
- 保持双盲匿名，不出现作者、单位、仓库或其他身份信息。
- 不能说论文或 supplementary material 已被修改。使用 “We clarify...” 或 “Our intended claim is...”，不要使用 “We have revised/added...” 。
- 新实验只能在文本中报告已经核验的数字；没有结果时应诚实收窄主张，不能承诺不存在的结果。
- 每份回复采用：**感谢与总述 -> 按原编号逐条回复 weakness/question -> 一句话总结**。

## 三份回复共用的口径

1. **关于 exact：** 精确的是 affine map 的逆、sample-wise log-determinant 和 augmented-action log-density；entropy 是一个精确可写的期望，其数值仍由 Monte Carlo 估计。建议统一称为 “tractable entropy expression with an unbiased Monte Carlo estimator”。
2. **关于 exploration：** MaxEnt 维持 policy stochasticity 和 action diversity，但不是 UCB、information gain 或 state-occupancy entropy 意义上的定向探索。
3. **关于 novelty：** affine coupling 和 normalizing flow 不是本文发明。贡献应定位为 parameter-dependent log-determinant 的 augmented generative policy，以及它与 replay-based soft policy evaluation/improvement 的结合。
4. **关于 SOTA：** Table 1 的 bold 只表示 evaluated methods 中最高的 sample mean，不表示每个任务都具有统计显著性。
5. **关于语气：** 先直接回答，再给证据和边界；承认合理问题，但不要把可成立的核心方法一并否定。

---

## Rebuttal to Reviewer tShQ

### Opening / 感谢与总述

> We sincerely thank the reviewer for the careful reading, the strong assessment, and the positive comments on the theoretical foundation, clarity, and empirical evaluation. We especially appreciate the questions concerning computational cost, the scope of maximum-entropy exploration, and direct exploration evidence. We respond to them individually below.

### Q1. Training and inference overhead

**审稿人问题：** doubled dummy-action space 是否显著增加训练和推理成本？

**回复结构：**

- 直接承认：相较 one-pass Gaussian actor，GENIEO 存在额外开销。
- 区分两类成本：动作表示由 `d` 变成 `2d`；`K` 个 flow steps 每步需要两次共享 MLP，默认 `K=5`，即每次采样有 `2K=10` 次顺序网络调用。
- 说明 critic/replay 的动作维度翻倍，但 hidden width 不变；主要 actor 开销来自多步 flow，而不只是 latent doubling。
- 与 generative baselines 公平比较：它们通常使用 15--20 个 diffusion/flow steps，因此需要同时给出相对 Gaussian policy 和相对 generative policy 的开销。
- 报告同硬件、同 batch size、同环境步数下的数字：
  - GENIEO 训练时间或 updates/sec：`[待补]`
  - Gaussian SAC/vanilla policy：`[待补]`
  - FlowRL、DIME 或其他主要 baseline：`[待补]`
  - inference latency/actions per second：`[待补]`
  - peak GPU memory（如有）：`[待补]`
- 没有实测数字前不要写 “negligible overhead”。

### Q2. Extremely sparse rewards

**审稿人问题：** 稀疏奖励限制来自 MaxEnt 范式，还是 GENIEO 实现？

**回复结构：**

- 直接回答：主要是 action-entropy-based MaxEnt RL 的范式级限制，不是 GENIEO 特有 bug。
- GENIEO 能维持更多 stochastic action hypotheses，但不会显式寻找高不确定状态，也不优化 information gain/state occupancy entropy。
- 因此它可以在已有学习信号时保持行为多样性，但不能保证在极端稀疏奖励下发现奖励区域。
- GENIEO 自身还会受到 augmented entropy coefficient 和 coherence penalty 的调参影响，但这是次要的实现层因素。
- 引用已有 `alpha` ablation：`alpha=0` 较差，过大的 `alpha` 同样较差，说明存在 exploration-control trade-off，而不是 entropy 越大越好。

### Q3. Direct exploration evidence

**审稿人问题：** 能否提供 state-space coverage 等直接探索证据？

**回复结构：**

- 先同意：final return 是间接证据，不能单独证明 state-space exploration 的因果改善。
- 明确 submitted paper 已有证据的范围：更高 return + entropy coefficient ablation。
- 如果已有额外分析，优先以文本报告：
  - representative task 的 occupied-state bins/state coverage：`[待补]`
  - kNN state entropy 或 visitation dispersion：`[待补]`
  - environment-action diversity，而非只报告 `(x,y)` entropy：`[待补]`
  - 与 FlowRL、DIME 或 `alpha=0` 版本比较：`[待补]`
  - 最好报告 reward 明显上升前的 early-training coverage：`[待补]`
- 如果没有直接分析，应明确收窄结论：实验显示 better task performance，但尚不能给出 state-coverage 层面的因果证明。

### Closing / 总结

> In summary, GENIEO provides a tractable augmented-policy entropy regularizer with a measurable computational trade-off. Its role is to preserve expressive policy stochasticity rather than provide directed epistemic exploration. We thank the reviewer for helping us clarify this scope and distinguish direct exploration evidence from final-control performance.

---

## Rebuttal to Reviewer 4ynL

### Opening / 感谢与总述

> We thank the reviewer for recognizing the mathematical foundation and the strong empirical performance of GENIEO. We also appreciate the concerns regarding novelty, baseline scope, direct exploration evidence, computational overhead, and the limitations of maximum-entropy control. We address each point separately below.

### W1/Q1. Novelty relative to Real NVP and affine coupling

**审稿人问题：** space expansion 和 triangular affine coupling 已经存在，本文的技术创新是什么？

**回复结构：**

- 明确认同：affine coupling 本身属于成熟 normalizing-flow machinery，不是本文的新变换。
- 不要辩称 Real NVP 与本文毫无关系。
- 将创新点限定为 RL-specific construction：
  - 构造 `2d` augmented policy，并通过 affine scale 获得 parameter-dependent、non-degenerate log-determinant；
  - 避免 numerical ODE inversion，获得 exact sample-wise augmented-action likelihood；
  - entropy gradient 可直接反向传播；
  - 与 replay-based soft Bellman target、actor improvement、automatic temperature tuning 结合；
  - coherence penalty 将 augmented variables 与 executed projection 联系起来。
- 与现有方法区分：black-box sampler、heuristic noise、approximate entropy，或 additive/volume-preserving update 的 entropy gradient 退化问题。
- 与 GenPO 区分：GenPO 面向 on-policy optimization；GENIEO 面向 off-policy MaxEnt actor-critic，并使用 parameter-dependent affine log-scale。
- 推荐核心句：**The novelty is not affine coupling in isolation, but the augmented entropy construction and its off-policy MaxEnt formulation.**

### W2. Missing baselines and DMC Hard

**审稿人问题：** 缺少 SimbaV2、MAD-TD、BRO 和 DMC Hard，SOTA claim 不充分。

**回复结构：**

- 解释 baseline 选择目的：DACER、QSM、QVPO、SDAC、DIME、FlowRL 都是 diffusion/flow generative-policy methods，用于隔离 policy/entropy mechanism 的比较。
- 承认 SimbaV2、MAD-TD、BRO 是强 general-purpose continuous-control systems，但它们同时改变 network scaling、model augmentation 或 critic optimization 等因素。
- 不要说这些 baseline “不相关”；应承认它们能检验 overall competitiveness。
- 将 claim 限定为 evaluated generative-policy baselines，而不是所有 online RL 方法的 universal SOTA。
- 说明已有 DMC dog/humanoid 等高维任务，但不要声称它们完全替代 reviewer 请求的 DMC Hard protocol。
- 如有新结果，仅报告已核验数字：
  - requested baselines：`[待补]`
  - requested DMC Hard tasks：`[待补]`

### W3/Q3. Does higher entropy mean meaningful exploration?

**审稿人问题：** 更高 policy entropy 是否真的带来有效探索？是否可能损害任务？

**回复结构：**

- 同意 action entropy 不等于 state coverage 或 uncertainty-directed exploration。
- 区分 augmented-policy entropy、executed-action diversity 和 state-visitation coverage。
- 解释 automatic temperature tuning 和 coherence penalty 用于平衡 stochasticity 与 task-directed control。
- 使用 `alpha` ablation：`alpha=0` 与过大 `alpha` 都较差，证明本文不主张 entropy 单调越大越好。
- 如有数据，报告 environment-action entropy/state coverage：`[待补]`。
- 不要把 dummy-action entropy 直接当作 meaningful exploration 的充分证据。

### Q2. Computational overhead

**回复结构：**

- 使用与 tShQ Q1 相同、已核验的成本数字，不要重新定义测量口径。
- 明确 `2K` actor evaluations、`2d` critic/replay representation。
- 分别比较 vanilla Gaussian policy 和 multi-step generative baselines。
- 数字：`[待补]`。

### Limitation. Precision control versus stochasticity

**审稿人问题：** MaxEnt 可能损害依赖低方差、稳定行为的精细控制任务。

**回复结构：**

- 承认这是 MaxEnt 的真实适用范围限制。
- automatic temperature tuning 可以调节 entropy pressure；evaluation 使用 deterministic zero-latent action，training 保持 stochastic。
- 不要声称这些机制完全消除了 trade-off。
- 当前证据主要来自 locomotion 和 whole-body control，不能外推到所有 fine-grained manipulation。

### Closing / 总结

> In summary, the novelty of GENIEO is not the affine-coupling primitive itself, but its augmented, parameter-dependent entropy construction and off-policy MaxEnt integration. We agree that the empirical claim should be scoped to the evaluated generative-policy baselines and that action entropy should not be equated with uncertainty-directed exploration. We thank the reviewer for helping clarify both the contribution and its valid scope.

---

## Rebuttal to Reviewer BXmK

### Opening / 感谢与总述

> We sincerely thank the reviewer for the detailed and technically insightful assessment, and for recognizing the usefulness of tractable likelihoods for MaxEnt reinforcement learning with flow policies. We particularly appreciate the distinctions concerning exact likelihood versus entropy estimation, exploration framing, normalizing flows, statistical reporting, and the relationship to SAC. We respond point by point below.

### W1. MaxEnt is not directed epistemic exploration

**审稿人问题：** 论文过度强调 “maximum entropy improves exploration”。

**回复结构：**

- 同意 reviewer 的概念区分。
- GENIEO 保持 policy stochasticity/action diversity，但不估计 epistemic uncertainty、information gain 或 state-occupancy entropy。
- 删除因果口径：不能从 higher return 推出 “explored better, therefore performed better”。
- 推荐口径：**GENIEO’s tractable augmented-policy entropy regularization achieved higher returns on the evaluated tasks.**

### W2. “Exact entropy” terminology

**审稿人问题：** likelihood 是 exact，但 entropy 仍需要 Monte Carlo marginalization。

**回复结构：**

- 明确认同，不回避措辞问题。
- 精确项：affine inverse、accumulated log-determinant、generated sample 的 augmented-action log-density。
- entropy identity 是 exact expression，但数值是 Monte Carlo estimate；使用 “tractable/unbiased estimator”。
- 引用 toy 数字：reference `1.4314`，GENIEO `1.4387`，absolute error `0.0074`，200k samples。
- 不再使用 “exactly evaluated entropy scalar”。

### W3. Relation to normalizing flows

**审稿人问题：** 论文使用 normalizing-flow 构件，却没有清楚承认和定位。

**回复结构：**

- 承认 triangular affine coupling 和 change of variables 是 established NF tools。
- Theorem 2 的作用是形式化 GENIEO 采用的具体 architecture，不是声称一般 NF 原理为新。
- 本文特定贡献是 augmented generative RL policy 中的 parameter-dependent log-volume change，以及 entropy gradient 在 off-policy soft policy optimization 中的直接使用。
- 与 additive/volume-preserving flow 的 degenerate entropy gradient 对比。

### W4/Q2/Q3. Relationship to SAC and why Algorithm 1 is needed

**审稿人问题：** 为什么不直接把 flow 接入 SAC/PPO？是否真的需要新 RL algorithm？

**回复结构：**

- 直接澄清：GENIEO 有意保留 SAC/soft-policy-iteration backbone；Bellman update 本身不是新 policy-iteration principle。
- 与 standard SAC 的必要差异逐项列出：
  - actor sample 是 `2d` augmented action；
  - replay buffer 保存 augmented action；
  - twin critics 评价其 projection 被环境执行的 augmented action；
  - entropy 和 target entropy 定义在 augmented space；
  - actor objective 增加 coherence penalty。
- Algorithm 1 是这些修改的完整 implementation specification，不代表所有 SAC components 都是新贡献。
- 可以在回复里做文字版 side-by-side comparison，但不能说 Algorithm 1 已经修改。

### W5. Statistical reporting and SOTA claims

**审稿人问题：** 5 seeds 的 mean +/- std 不能证明每项显著最好，bold/SOTA 表述过强。

**回复结构：**

- 同意 bold 仅代表 highest reported sample mean。
- 明确不主张每个 individual task 都具有 statistical significance。
- 强调最稳健的 aggregate result：DMC average `749 +/- 17` vs. FlowRL `641 +/- 44`。
- 谨慎处理高方差 H-Bench，特别是 H1 Reach。
- 将 SOTA 限定为 evaluated methods and protocol。
- 如果有 raw seeds，报告 bootstrap CI、IQM 或 paired test：`[待补方法与数字]`。
- 不做未经 multiple-comparison correction 的显著性断言。

### W6. Incorrect causal interpretation

**审稿人问题：** 论文把 better exploration 当成 performance improvement 的原因。

**回复结构：**

- 同意现有 return curves 不能建立该因果链。
- 只说 complete GENIEO design/tractable entropy regularization 与更高 evaluated returns 相关。
- `alpha` ablation 能说明 entropy term 有贡献，但不能单独证明 state-space exploration 改善。

### W7. Toy entropy comparison

**审稿人问题：** Figure 4 缺少 naive Euler inversion 和代表性 baselines。

**回复结构：**

- 解释 zero-logdet baseline 的窄目的：隔离 affine Jacobian term 是否必要。
- 同意 naive Euler inversion 能更直接检验 numerical-inversion motivation。
- 如有 matched-step 结果，报告 inversion/likelihood/entropy error：`[待补]`。
- 如无结果，明确 toy experiment 只验证 affine logdet entropy identity，不声称完成 solver comparison。

### N1. Missing Gaussian SAC baseline

**回复结构：**

- 承认 Gaussian SAC 是重要的 non-generative MaxEnt reference。
- 解释 submitted experiments 聚焦 unified generative-policy comparison。
- 有 matched SAC 数字则报告：`[待补]`；没有则收窄 claim，不贬低 SAC。

### N2. Tanh-squashed Gaussian entropy

**回复结构：**

- 同意 unsquashed Gaussian 有 analytic entropy，但 bounded tanh-squashed/clipped policy 一般仍需 change of variables 和数值期望。
- 不再把所有实际 bounded Gaussian policies 笼统称为 exact-entropy policies。

### Q1. “Dummy action” terminology

**回复结构：**

- 同意 “dummy” 容易被理解成随后丢弃的 placeholder。
- 解释两个分量都保留用于 likelihood、critic 和 replay，只有 projection 被环境执行。
- 回复中改用更清楚的解释性称呼：**augmented paired action** 或 **dual-variable augmented action**。

### Minor comments

用一两句统一感谢，不占用太多字符：Figure 3 字号、Section 3.3 标题、与 SAC 的并排说明。不能声称这些内容已在原稿中修改。

### Closing / 总结

> In summary, the precise contribution is an exact augmented-action likelihood and a tractable, unbiased Monte Carlo entropy estimator, rather than an exactly evaluated entropy scalar or a directed epistemic-exploration mechanism. GENIEO retains the SAC backbone and contributes the augmented affine policy, its non-degenerate entropy gradient, and the corresponding critic/replay formulation. We thank the reviewer for identifying the distinctions needed to state these contributions accurately.

---

## 提交前检查清单

- 每位 reviewer 只看到针对自己的回复。
- 每个 weakness 和 numbered question 都有明确对应的小标题。
- 每份回复开头感谢，结尾一句总结。
- 每份少于 10,000 characters。
- 没有 links、attachments 或身份信息。
- 没有声称论文/supplement 已修改。
- 所有额外数字均来自已核验日志。
- exact likelihood/logdet 与 Monte Carlo entropy estimate 分开表述。
- policy stochasticity 与 directed/epistemic exploration 分开表述。
- highest sample mean 与 statistically significant improvement 分开表述。
