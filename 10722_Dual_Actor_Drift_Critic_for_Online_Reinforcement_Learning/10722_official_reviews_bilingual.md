# Submission 10722 Official Reviews - Bilingual Notes

本文档整理 Submission 10722 三位审稿人的官方评审意见，采用中英对照格式，便于撰写 rebuttal。

## Reviewer qUFY

### Metadata / 元信息

- **Review date / 评审日期:** 27 Jun 2026, 02:28; modified 23 Jul 2026, 22:22
- **Quality / 质量:** 2: not good
- **Clarity / 清晰度:** 2: not good
- **Significance / 重要性:** 3: good
- **Originality / 原创性:** 2: not good
- **Rating / 评分:** 3: Borderline reject
- **Confidence / 置信度:** 4
- **Ethical concerns / 伦理问题:** NO or VERY MINOR ethics concerns only
- **Paper formatting concerns / 格式问题:** No

### Summary / 摘要

**English:** The paper proposes DADC, which adapts drift models to continuous-control online RL and uses them as probabilistic policy priors. DADC constructs attractive anchors using a conditional flow matching prior and Q-guided Langevin dynamics, while using a critic-based filter to extract low-value actions as repulsive samples. Experiments on 10 DMC tasks and 4 HumanoidBench tasks show higher performance than SOTA models.

**中文：** 本文提出 DADC，将 drift model 适配到 continuous-control online RL，并将其作为策略的概率先验。DADC 使用 conditional flow matching prior 和 Q-guided Langevin dynamics 构造吸引锚点，同时通过 critic-based filter 提取低价值动作作为排斥样本。论文在 10 个 DMC 任务和 4 个 HumanoidBench 任务上实验，显示其性能高于 SOTA 方法。

### Strengths / 优点

**English:**

- Using the attraction and repulsion mechanism of drift models to reduce the impact of suboptimal actions is interesting.
- The paper makes a reasonable adaptation of drift models to online RL, and the engineering implementation appears well executed.
- Experiments show substantial numerical gains on both DMC and HumanoidBench tasks, supporting the main claim.

**中文：**

- 利用 drift models 的 attraction 和 repulsion 机制来减轻 suboptimal actions 的影响是有趣的。
- 作者对 drift model 到 online RL 场景的适配是合理的，工程实践也执行得较好。
- 实验在 DMC 和 HumanoidBench 任务上展示了显著数值提升，支持了论文的主要主张。

### Weaknesses / 缺点

**English:**

- Although the theoretical framework is sound at a high level, the operational assumptions are too optimistic and close to theoretical overextension. Langevin guarantees rely on local basins and bounded critic error. In online RL, the Q-function is continuously updated, so the energy landscape is non-stationary. The paper acknowledges that the repulsion field may mislead the policy early due to noisy Q-values, but does not provide quantitative robustness experiments.
- The method contains many components: prior actor, implicit actor, critic, target network, Langevin iterations, and many hyperparameters such as coefficients, flow steps, and anchor count. This makes the method difficult to tune. The ablations do not sufficiently cover all components, which is important for understanding the true contribution.
- The paper lacks computational complexity analysis, even though the pipeline introduces extra computation.

**中文：**

- 尽管理论框架在高层次上是合理的，但其操作性假设过于乐观，接近理论过度延伸。Langevin 的保证依赖 local basins 和 bounded critic error，而在 online RL 中 Q-function 持续更新，energy landscape 是非平稳的。论文承认早期 noisy Q 可能导致 repulsion field 误导策略，但没有提供定量鲁棒性实验。
- 方法包含许多组件：prior actor、implicit actor、critic、target network、Langevin iterations，以及多个超参数，例如若干系数、flow steps 和 anchor count。这使方法难以调参。消融实验没有充分覆盖所有组件，而这些消融对于理解本文真实贡献非常关键。
- 论文缺少 computational complexity analysis，尽管该 pipeline 引入了额外计算。

### Questions / 问题

**English:**

1. Can the authors provide end-to-end training and inference latency comparisons between DADC and the benchmark methods?
2. Can the authors elaborate best practices for selecting the hyperparameters, such as the coefficients, flow steps, and anchor count? The original review text appears to omit some rendered math symbols.

**中文：**

1. 作者能否提供 DADC 与 benchmark methods 的端到端训练和推理延迟比较？
2. 作者能否详细说明如何选择这些超参数，例如若干系数、flow steps 和 anchor count？原始评审文本中部分数学符号似乎在复制时缺失。

### Limitations / 局限性

**English:** yes

**中文：** 有。

## Reviewer 4kU9

### Metadata / 元信息

- **Review date / 评审日期:** 24 Jun 2026, 15:11; modified 23 Jul 2026, 22:22
- **Quality / 质量:** 1: poor
- **Clarity / 清晰度:** 1: poor
- **Significance / 重要性:** 1: poor
- **Originality / 原创性:** 3: good
- **Rating / 评分:** 2: Reject
- **Confidence / 置信度:** 4
- **Ethical concerns / 伦理问题:** NO or VERY MINOR ethics concerns only
- **Paper formatting concerns / 格式问题:** No major formatting, anonymity, or submission policy concerns.

### Summary / 摘要

**English:** The paper adapts drift models to online reinforcement learning. It derives a constrained policy optimization objective from the drift-model loss, requiring both positive samples for attraction and negative samples for repulsion. High-Q samples are obtained as positives through Langevin dynamics within a conditional flow matching model trained on high-return replay-buffer transitions, while negatives are obtained through Q-value-based filtering.

**中文：** 本文将 drift models 适配到 online reinforcement learning。论文从 drift-model loss 推导出一个 constrained policy optimization objective，该目标同时需要用于 attraction 的正样本和用于 repulsion 的负样本。高 Q-value 样本通过在 conditional flow matching model 中使用 Langevin dynamics 得到，该模型训练于 replay buffer 中的 high-return transitions；负样本则通过基于 Q-value 的 filtering 获得。

### Claimed Contributions / 审稿人总结的贡献

**English:**

- The paper introduces a method for obtaining positive and negative samples when there is no static sampling distribution, which is challenging because the Q-network continuously updates.
- Through a dual-actor mechanism, one actor is dedicated to sampling for constructing positive and negative samples, while the other actor is updated through constrained policy optimization.
- The paper provides convergence analysis for positive sample construction and theoretical analysis of the policy gradient, and empirically validates the method across 14 tasks from two benchmarks.

**中文：**

- 论文提出了一种在没有 static sampling distribution 时获得正负样本的方法，而这个问题由于 Q-network 持续更新而具有挑战性。
- 通过 dual-actor mechanism，一个 actor 专门用于采样并构造正负样本，另一个 actor 则通过 constrained policy optimization 更新。
- 论文提供了 positive sample construction procedure 的 convergence analysis 和 policy gradient 的理论分析，并在来自两个 benchmark 的 14 个任务上进行了经验验证。

### Strengths / 优点

**English:**

- The introduction effectively motivates the method by showing that naively applying a drift model to online RL gives suboptimal outcomes, thereby establishing the need for the proposed dual actor critic algorithm.
- Section 3.2 is a strength because its equations and explanations clarify the meaning of each gradient term and its connection to the underlying drift model.
- A positive originality aspect is that Langevin-refined positive samples from replay-buffer data and filtered negatives, trained under the drift-model objective, yield meaningful online RL gains.
- Motivating decoupling in the introduction and instantiating it through a dual-actor action-sampler design is an original framing.

**中文：**

- 引言通过展示 naive drift model 直接用于 online RL 会得到 suboptimal outcome，有效地建立了提出 dual actor critic algorithm 的必要性。
- Section 3.2 是一个优点，其中的公式和解释澄清了每个 gradient term 的含义及其与底层 drift model 的联系。
- 在原创性方面，一个优点是将 replay-buffer data 中经过 Langevin refinement 的正样本与 filtered negatives 结合，并在 drift-model objective 下训练，能够在 online RL 中产生有意义的收益。
- 在引言中以 decoupling 为动机，并通过 dual-actor action-sampler design 实现这一想法，是一种有原创性的 framing。

### Weaknesses - Theory and Optimization / 缺点 - 理论与优化

**English:**

- Theorem 1 relies on a very strong assumption, namely Assumption 2 in Appendix A. Bounding the action-gradient discrepancy between the current critic and the optimal critic is difficult to accept in online deep RL.
- The bound in Theorem 1 does not establish true convergence. Even when the initial distribution term vanishes, a residual term remains. If that residual is not driven to zero, the result only places the distribution within an error ball around the target rather than converging exactly to it. If the relevant gradient discrepancy is unbounded, the bound does not hold.
- The constrained policy optimization lacks a policy-improvement guarantee, and the exploration interpretation is unconvincing. Following the Q-gradient in Equation 9 is fundamentally local exploitation rather than exploration.
- The surrogate actor objective is not shown to guarantee monotonic improvement. Establishing monotonic improvement would typically require a trust region, conservative update, or lower-bound argument on the true objective.
- Because the critic, positive samples, and negative samples are all derived from the learned critic, the link between reducing actor loss and increasing true return is missing.
- The paper does not show critic convergence through policy evaluation or actor convergence through policy improvement or policy iteration. This weakens Assumption 2 because the paper assumes a bounded gradient error relative to the optimal critic without demonstrating that the learned critic approaches it.

**中文：**

- Theorem 1 依赖一个很强的假设，即 Appendix A 中的 Assumption 2。在 online deep RL 中，要求 current critic 与 optimal critic 之间的 action-gradient discrepancy 有界，是较难接受的。
- Theorem 1 的 bound 并没有建立真正的 convergence。即使 initial distribution term 消失，仍然存在 residual term。如果该 residual 没有被驱动到零，结果只说明分布落在目标附近的 error ball 中，而不是精确收敛到目标。如果相关 gradient discrepancy 无界，该 bound 也不成立。
- constrained policy optimization 缺少 policy-improvement guarantee，且 exploration 解释不令人信服。Equation 9 中沿 Q-gradient 的更新本质上是 local exploitation，而不是 exploration。
- 论文没有证明 surrogate actor objective 保证 monotonic improvement。通常要建立单调改进，需要 trust region、conservative update，或对 true objective 的 lower-bound argument。
- 由于 critic、positive samples 和 negative samples 都来自 learned critic，减少 actor loss 与提升 true return 之间的联系缺失。
- 论文没有展示 critic 通过 policy evaluation 收敛，也没有展示 actor 通过 policy improvement 或 policy iteration 收敛。这进一步削弱了 Assumption 2，因为论文假设相对于 optimal critic 的 gradient error 有界，却没有证明 learned critic 会接近 optimal critic。

### Weaknesses - Decoupling and Negative Sampling / 缺点 - 解耦与负采样

**English:**

- The decoupling motivation conflicts with the actual algorithm. The introduction motivates decoupling by referring to the nonstationarity of the moving Q-target, yet every core component still depends on the current Q-function, including Q-weighted regression for learning the CFM prior and the use of Q in constructing the positive set.
- Separating sampler and actor parameters does not remove Q-function nonstationarity. The authors should clarify in what sense the proposed method is decoupled.
- The negative sampler is heuristic. Bottom-K actions need not correspond to low-return actions.
- Since Q-guidance can push samples out of distribution, the authors should explain why these samples qualify as valid negatives.

**中文：**

- decoupling motivation 与实际算法存在冲突。引言将 decoupling 的动机归因于 moving Q-target 的非平稳性，但每个核心组件仍然依赖当前 Q-function，包括用于学习 CFM prior 的 Q-weighted regression，以及构造 positive set 时使用 Q。
- 分离 sampler 和 actor 参数并不能消除 Q-function 的非平稳性。作者应澄清所提出方法在哪种意义上是 decoupled。
- negative sampler 具有启发式性质。Bottom-K actions 未必对应 low-return actions。
- 由于 Q-guidance 可能把 samples 推出 distribution，作者应解释为什么这些 samples 可以作为 valid negatives。

### Weaknesses - Experiments and Clarity / 缺点 - 实验与清晰度

**English:**

- The empirical comparison lacks strong, contemporary baselines and standardized evaluation. Only DACER is compared, although DACERv2 is cited and recent enough to include. DIME is omitted despite closely related work showing its advantage through comparison against DIME.
- Experiments should be reconstructed with pre-2026 baselines such as DIME and DACERv2, reported using IQM returns because 5 seeds are insufficient. The baseline-selection rationale should be stated explicitly.
- The experimental section is underspecified. The choice of DMC hard tasks is sound, but the subset selection among DMC easy tasks and HumanoidBench tasks is not justified.
- No hyperparameter table is provided, and the absence of a unified table for all baselines makes it impossible to verify comparison fairness. A detailed configuration table should be added.

**中文：**

- 经验比较缺少强的、近期的 baseline，也缺少标准化评估。论文只比较了 DACER，尽管 DACERv2 已被引用且足够近期，应该纳入。DIME 也被省略，而相关工作显示其优势时正是通过与 DIME 比较建立的。
- 实验应使用 2026 年之前已有的 baseline 重新构建，例如 DIME 和 DACERv2，并使用 IQM returns 报告，因为 5 个 seeds 不足。baseline-selection rationale 应明确说明。
- 实验部分说明不足。使用 DMC hard tasks 展示方法是合理选择，但为何只选择部分 DMC easy tasks 和部分 HumanoidBench tasks 没有得到解释。
- 论文没有提供 hyperparameter table，也没有给所有 baselines 一个统一配置表，因此无法验证比较是否公平。应添加详细 configuration table。

### Weaknesses - Originality / 缺点 - 原创性

**English:** The positive-sampling procedure largely combines existing techniques: advantage-weighted replay samples followed by projection appear in prior online-RL work, and Langevin dynamics for higher-quality samples has also been explored. The gap between the decoupling motivation and the actual algorithm further weakens the originality claim.

**中文：** positive-sampling procedure 很大程度上是已有技术的组合：advantage-weighted replay samples followed by projection 已出现在既有 online-RL 工作中，使用 Langevin dynamics 获得更高质量样本也已有探索。decoupling motivation 与实际算法之间的差距进一步削弱了 originality claim。

### Questions / 问题

**English:**

1. Does the constrained policy optimization in Equation 9 guarantee policy improvement?
2. Is it valid to assume that policy iteration guarantees critic convergence and bounded critic-gradient error?
3. Given that the decoupled framework is motivated by Q-function nonstationarity, why is advantage-weighted regression performed using the online-updated Q-function? When the same online Q-function is used in Langevin dynamics, is the resulting sampler nonstationarity empirically shown to cause no issue?
4. For experiment questions, see the weaknesses on baseline selection, standardized evaluation, task subset rationale, and missing hyperparameter tables.

**中文：**

1. Equation 9 中的 constrained policy optimization 是否保证 policy improvement？
2. 假设 policy iteration 保证 critic convergence 并且 critic-gradient error 有界是否合理？
3. 既然 decoupled framework 的动机是 Q-function 的非平稳性，为什么 advantage-weighted regression 仍然使用在线更新的 Q-function？当同一个 online Q-function 用于 Langevin dynamics 时，由此带来的 sampler nonstationarity 是否有经验证据说明不会造成问题？
4. 关于实验问题，请参见上面对 baseline selection、standardized evaluation、task subset rationale 和 missing hyperparameter tables 的批评。

### Limitations / 局限性

**English:** The reviewer says the limitations section is insufficient because it only discusses the negative sampler. The authors should expand it to address theoretical issues, including Assumption 2, absence of policy-improvement or critic-convergence guarantees, and the gap between decoupling motivation and the algorithm. The authors should also acknowledge that adding stronger contemporary baselines such as DIME and DACERv2 may reduce the apparent empirical gains.

**中文：** 审稿人认为 limitations section 不充分，因为它只讨论了 negative sampler。作者应扩展该部分，讨论理论问题，包括 Assumption 2、缺少 policy-improvement 或 critic-convergence guarantee，以及 decoupling motivation 与实际算法之间的差距。作者还应承认，加入更强的近期 baseline，如 DIME 和 DACERv2，可能会降低表面上的经验收益。

## Reviewer MeUK

### Metadata / 元信息

- **Review date / 评审日期:** 23 Jun 2026, 13:32; modified 23 Jul 2026, 22:22
- **Quality / 质量:** 2: not good
- **Clarity / 清晰度:** 3: good
- **Significance / 重要性:** 3: good
- **Originality / 原创性:** 3: good
- **Rating / 评分:** 4: Borderline accept
- **Confidence / 置信度:** 3
- **Ethical concerns / 伦理问题:** NO or VERY MINOR ethics concerns only
- **Paper formatting concerns / 格式问题:** N/A

### Summary / 摘要

**English:** This work studies how to use expressive generative policies, specifically drift models, while exploiting negative samples in online RL. DADC combines an advantage-weighted drift objective, Q-guided Langevin refinement to construct positive anchors, and Q-value filtered actions as explicit repulsive anchors. The paper claims that this decoupled attractive-repulsive construction helps mitigate suboptimal probability residues left by expressive generative policies. DADC shows strong empirical results across DMControl and HumanoidBench tasks, with one-task ablations.

**中文：** 本文研究如何在 online RL 中使用 expressive generative policies，具体是 drift models，同时利用 negative samples。DADC 结合了 advantage-weighted drift objective、用于构造 positive anchors 的 Q-guided Langevin refinement，以及作为 explicit repulsive anchors 的 Q-value filtered actions。论文声称这种 decoupled attractive-repulsive construction 有助于缓解 expressive generative policies 留下的 suboptimal probability residues。DADC 在 DMControl 和 HumanoidBench 任务上展示了强实验结果，并提供了单任务消融。

### Strengths / 优点

**English:**

- The work identifies an important limitation of diffusion or flow-style generative policies: they mainly imitate or reweight high-value behavior but make limited use of explicitly bad actions to steer the policy away from suboptimal regions.
- Probability-fitting generative policies can suffer from suboptimal probability residues, and explicit repulsion from low-value samples may help suppress those regions.
- The empirical performance across evaluated DMControl and HumanoidBench tasks is strong.
- The method appears reasonably robust to several tested design choices on Dog Run, although broader hyperparameter sensitivity is not fully established.

**中文：**

- 该工作指出 diffusion 或 flow-style generative policies 的一个重要局限：它们主要模仿或重加权高价值行为，但很少利用明确的 bad actions 将策略推离 suboptimal regions。
- probability-fitting generative policies 可能受到 suboptimal probability residues 的影响，而来自低价值样本的显式 repulsion 可能有助于抑制这些区域。
- 在所评估的 DMControl 和 HumanoidBench 任务上，实验性能很强。
- 在 Dog Run 上，方法对若干已测试设计选择看起来具有一定鲁棒性，尽管更广泛的 hyperparameter sensitivity 尚未完全建立。

### Weaknesses / 缺点

**English:**

- The main weakness is insufficient component ablations. The authors ablate different types of negative samples, but do not more fundamentally ablate whether negative samples improve performance at all. It is also unclear how the method performs without the positive or negative branches, making it hard to identify whether gains come from the base drift objective, positive Q-guided Langevin dynamics, negative repulsion, or their combination.
- The ablations have limited generality because all are conducted only on Dog Run. Since the method is evaluated on 14 tasks with different dynamics and difficulty, at least one additional ablation task is needed to show whether conclusions generalize.
- The ablation setup could be clearer by explicitly stating which components remain active in each setting. For example, in Figure 4.c it should be clear whether the negative branch still uses Q-filtering; in Figure 4.d it should be clear whether the positive branch still uses Langevin refinement.
- Marking the default setting in each ablation plot would improve readability.

**中文：**

- 主要缺点是 component ablations 不充分。作者消融了不同类型的 negative samples，但没有更根本地消融 negative samples 本身是否提升性能。方法在没有 positive branch 或 negative branch 时表现如何也不清楚，因此很难判断主要提升来自 base drift objective、positive Q-guided Langevin dynamics、negative repulsion，还是它们的组合。
- ablations 的泛化性有限，因为所有消融都只在 Dog Run 上进行。由于方法在 14 个具有不同动力学和难度的任务上评估，至少需要再加入一个任务的消融，以证明结论能够泛化。
- ablation setup 的清晰度可以提升，应明确说明每个设置中哪些组件仍然 active。例如 Figure 4.c 中应说明 negative branch 是否仍使用 Q-filtering；Figure 4.d 中应说明 positive branch 是否仍使用 Langevin refinement。
- 在每个 ablation plot 中标出 default setting 会提升可读性。

### Questions / 问题

**English:**

1. Are the initial positive samples and negative samples from different state pairs? The reviewer suggests making this explicit in the text, for example around line 169 or directly in the equations. The original copied review contains some malformed math.
2. Figure 1 uses "Naive Drift" as a motivating baseline, but its exact implementation is not fully specified. What are the precise differences between Naive Drift and DADC? Are the differences mainly in where positive and negative action samples come from, namely current actor samples versus decoupled flow-prior and actor-based construction?
3. Figures 4.c and 4.d show that removing Q-guided Langevin refinement or replacing Q-filtered negative anchors with random negative anchors still yields reasonably strong performance. This makes it difficult to determine which component does most of the work: base drift objective, decoupled positive/negative sample construction, Q-guided Langevin refinement, Q-filtered repulsion, or their combination.
4. Since Naive Drift in Figure 1 is the main motivation, the paper should include a precise description of its objective and sample-construction procedure, either in the main text or as a short preliminary-experiment paragraph.
5. How do the ablation conclusions transfer to other tasks? At least one more task should be used for ablation to evaluate generalization.
6. For ablations, which components remain active? In Figure 4.c, is repulsion still active? In Figure 4.d, is Q-guided Langevin refinement still active?
7. The reviewer wants an ablation on the negative branch itself, such as turning off the lowest-25% negative samples entirely, or testing a stricter 50% negative-sample threshold. Does this threshold affect the repulsive coefficient? The original review text omits the rendered coefficient symbol.

**中文：**

1. 初始 positive samples 和 negative samples 是否来自不同的 state pairs？审稿人建议在正文中直接写清楚，例如在 line 169 附近，或者直接在公式中表达。原始复制文本中部分公式格式损坏。
2. Figure 1 使用 “Naive Drift” 作为 motivating baseline，但其具体实现没有完全说明。Naive Drift 和 DADC 的精确定义差异是什么？差异是否主要在于 positive 和 negative action samples 的来源，即 current actor samples 与 decoupled flow-prior / actor-based construction 的区别？
3. Figures 4.c 和 4.d 显示，移除 Q-guided Langevin refinement 或用 random negative anchors 替代 Q-filtered negative anchors 后，性能仍然相当强。这使得读者难以判断主要起作用的是 base drift objective、decoupled positive/negative sample construction、Q-guided Langevin refinement、Q-filtered repulsion，还是它们的组合。
4. 由于 Figure 1 中的 Naive Drift 是本文主要动机，论文应在正文或一个简短 preliminary-experiment paragraph 中精确描述它的 objective 和 sample-construction procedure。
5. ablation conclusions 如何迁移到其他任务？至少应增加一个任务进行消融，以评估泛化性。
6. 对于 ablation，每个设置中哪些组件仍然 active？Figure 4.c 中 repulsion 是否仍 active？Figure 4.d 中 Q-guided Langevin refinement 是否仍 active？
7. 审稿人希望看到 negative branch 本身的消融，例如完全关闭 lowest-25% negative samples，或测试更严格的 50% negative-sample threshold。这个 threshold 是否会影响 repulsive coefficient？原始评审文本缺失了该系数的渲染符号。

### Minor Comments / 次要意见

**English:**

- Mark the default values used in ablation plots so readers do not need to search back and forth.
- Make Figures 6, 7, 8, and 9 full width to improve readability.
- The symbol for the repulsive coefficient in the main text is described differently in the hyperparameter table as the flow drift coefficient. The notation should be streamlined.

**中文：**

- 在 ablation plots 中标注 default values，避免读者来回查找默认设置。
- 将 Figures 6、7、8、9 做成 full width，以提高可读性。
- 主文中某个符号被写作 repulsive coefficient，但在 hyperparameter table 中被写作 flow drift coefficient。应统一符号和术语。

### Limitations / 局限性

**English:** yes

**中文：** 有。

## Cross-Reviewer Themes / 三位审稿人的共同关注点

### 1. Theory assumptions and policy improvement / 理论假设与策略改进保证

**English:** Reviewer qUFY and Reviewer 4kU9 both worry that the theory relies on optimistic assumptions about critic quality, bounded gradient error, and stable Langevin behavior under a non-stationary online Q-function. Reviewer 4kU9 specifically asks whether Equation 9 guarantees policy improvement and whether critic convergence is established.

**中文：** Reviewer qUFY 和 Reviewer 4kU9 都担心理 论依赖过于乐观的假设，包括 critic quality、bounded gradient error，以及 non-stationary online Q-function 下 Langevin behavior 的稳定性。Reviewer 4kU9 特别询问 Equation 9 是否保证 policy improvement，以及是否建立了 critic convergence。

### 2. Decoupling versus Q nonstationarity / 解耦叙事与 Q 非平稳性

**English:** Reviewer 4kU9 challenges the decoupling claim because the CFM prior, positive samples, negative samples, and Langevin refinement still depend on the online-updated Q-function. Reviewer qUFY similarly notes that a continuously updated Q-function makes the energy landscape non-stationary and may mislead the repulsion field early in training.

**中文：** Reviewer 4kU9 质疑 decoupling claim，因为 CFM prior、positive samples、negative samples 和 Langevin refinement 仍依赖在线更新的 Q-function。Reviewer qUFY 也指出持续更新的 Q-function 使 energy landscape 非平稳，并可能在训练早期误导 repulsion field。

### 3. Ablations and component attribution / 消融实验与组件归因

**English:** Reviewer MeUK's main concern is insufficient component ablation. qUFY also notes that many components and hyperparameters are not sufficiently covered. Reviewers want ablations that isolate the base drift objective, positive Langevin branch, negative repulsion branch, Q-filtering, random negatives, and different negative thresholds.

**中文：** Reviewer MeUK 的主要担忧是 component ablation 不充分。qUFY 也指出许多组件和超参数没有被充分覆盖。审稿人希望看到能够分离 base drift objective、positive Langevin branch、negative repulsion branch、Q-filtering、random negatives 和不同 negative thresholds 的消融。

### 4. Computational overhead / 计算开销

**English:** Reviewer qUFY asks for end-to-end training and inference latency comparisons, while Reviewer 4kU9 and MeUK raise concerns that the added sampler, Langevin iterations, and multiple actors may introduce meaningful compute overhead. A rebuttal should quantify latency, wall-clock return, and possibly memory cost.

**中文：** Reviewer qUFY 要求端到端 training 和 inference latency comparison；Reviewer 4kU9 和 MeUK 也关注新增 sampler、Langevin iterations 和 multiple actors 可能带来的计算开销。rebuttal 应量化 latency、wall-clock return，并尽可能报告 memory cost。

### 5. Baselines and evaluation protocol / Baseline 与评估协议

**English:** Reviewer 4kU9 strongly criticizes missing contemporary baselines, especially DIME and DACERv2, and requests standardized IQM reporting because 5 seeds may be insufficient. The same reviewer also asks for justification of the selected DMC and HumanoidBench task subsets.

**中文：** Reviewer 4kU9 强烈批评缺少近期强 baseline，尤其是 DIME 和 DACERv2，并要求使用标准化的 IQM reporting，因为 5 个 seeds 可能不足。同一审稿人还要求解释为什么选择特定 DMC 和 HumanoidBench 任务子集。

### 6. Hyperparameter sensitivity and reproducibility / 超参数敏感性与可复现性

**English:** Reviewer qUFY asks for best practices for choosing coefficients, flow steps, and anchor count. Reviewer MeUK asks for clearer ablation settings and default-value markers. Reviewer 4kU9 requests a unified hyperparameter table for all baselines to verify fairness.

**中文：** Reviewer qUFY 要求说明如何选择各类系数、flow steps 和 anchor count。Reviewer MeUK 要求更清楚地说明 ablation settings 并标注默认值。Reviewer 4kU9 要求提供所有 baselines 的统一 hyperparameter table，以验证公平性。

### 7. Negative sampler validity / 负样本有效性

**English:** Reviewers question whether bottom-K or Q-filtered actions are valid negatives. 4kU9 notes that bottom-K actions may not correspond to truly low-return actions and that Q-guided samples can go out of distribution. MeUK asks for direct ablations that turn the negative branch off or change the negative-sample threshold.

**中文：** 审稿人质疑 bottom-K 或 Q-filtered actions 是否是 valid negatives。4kU9 指出 bottom-K actions 未必对应真实 low-return actions，而且 Q-guided samples 可能 out of distribution。MeUK 要求直接消融 negative branch，例如关闭负样本分支或改变 negative-sample threshold。

