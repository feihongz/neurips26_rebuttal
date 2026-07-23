# Submission 15978 Official Reviews - Bilingual Notes

本文档整理 Submission 15978 四位审稿人的官方评审意见，采用中英对照格式，便于撰写 rebuttal。

## Reviewer Gdko

### Metadata / 元信息

- **Review date / 评审日期:** 27 Jun 2026, 18:36; modified 23 Jul 2026, 22:57
- **Quality / 质量:** 3: good
- **Clarity / 清晰度:** 3: good
- **Significance / 重要性:** 3: good
- **Originality / 原创性:** 3: good
- **Rating / 评分:** 4: Borderline accept
- **Confidence / 置信度:** 4
- **Ethical concerns / 伦理问题:** NO or VERY MINOR ethics concerns only
- **Paper formatting concerns / 格式问题:** N/A

### Summary / 摘要

**English:** The paper proposes Self-Adjoint Flow Policy Optimization (SAFLOW), a likelihood-tractable generative policy with a self-adjoint structure. SAFLOW parameterizes the policy as an invertible flow in a doubled action space and uses a Verlet-style self-adjoint composition for generation. This structure makes the inverse map obtainable by step-size reversal, aligning forward sampling and backward likelihood evaluation under the same time-symmetric numerical rule. It also provides second-order approximation accuracy to the learned continuous flow, improving the numerical consistency of likelihood and policy-ratio computation.

**中文：** 本文提出 Self-Adjoint Flow Policy Optimization (SAFLOW)，一种具有 self-adjoint 结构且 likelihood tractable 的生成式策略。SAFLOW 将策略参数化为 doubled action space 中的可逆 flow，并使用 Verlet-style self-adjoint composition 进行生成。该结构使得 inverse map 可以通过反转 step size 获得，从而在同一个 time-symmetric numerical rule 下对齐 forward sampling 和 backward likelihood evaluation。它还为学习到的连续 flow 提供二阶近似精度，提升 likelihood 和 policy-ratio 计算的数值一致性。

### Strengths / 优点

**English:**

- The paper presents an interesting idea and targets an important gap between expressive generative policies and likelihood-based policy optimization.
- The motivation that generative policies are not only samplers but also define likelihoods used in PPO ratios, entropy, and KL-related quantities is compelling and clearly presented.
- The self-adjoint Verlet-style construction is a meaningful methodological contribution. Compared with merely requiring invertibility, the paper emphasizes time-symmetric consistency between sampling and likelihood evaluation, and connects this structure theoretically to second-order approximation of the learned continuous flow.
- The experiments are comprehensive, covering locomotion, manipulation, dexterous control, and aerial control in IsaacLab.
- SAFLOW achieves the best reported mean return across all eight tasks, and the ablation study further supports the claim.

**中文：**

- 论文提出了一个有趣的想法，并瞄准 expressive generative policies 与 likelihood-based policy optimization 之间的重要缺口。
- 论文清楚且有说服力地阐述了一个动机：生成式策略不仅是 sampler，也定义了 PPO ratio、entropy 和 KL 相关量中使用的 likelihood。
- self-adjoint Verlet-style construction 是有意义的方法贡献。相比仅仅要求 invertibility，论文强调了 sampling 和 likelihood evaluation 之间的 time-symmetric consistency，并通过理论分析将该结构与 learned continuous flow 的二阶近似联系起来。
- 实验较全面，覆盖 IsaacLab 中的 locomotion、manipulation、dexterous control 和 aerial control。
- SAFLOW 在全部八个任务上取得了最高 reported mean return，ablation study 进一步支持了论文主张。

### Weaknesses / 缺点

**English:**

- The introduction could be clearer, especially in notation. Variables such as T, z, h, and K are used before formal definition, making the self-adjoint flow idea harder to follow.
- The paper mainly compares SAFLOW with Gaussian-policy baselines and recent generative-policy methods. The reviewer suggests adding RN-D, which has a similar motivation of providing a more flexible alternative to Gaussian policies and also evaluates PPO/TRPO-style optimization. This would clarify whether gains come from the self-adjoint flow design or from using a more expressive policy class.
- Although the paper includes several IsaacLab tasks, analysis on harder high-dimensional environments could be strengthened. The reviewer specifically asks for more discussion of Isaac-Velocity-Rough-H1-v0, Isaac-Velocity-Rough-Unitree-Go2-v0, and Isaac-Repose-Cube-Shadow-Direct-v0, especially regarding computational efficiency compared with PPO.
- The paper reports that SAFLOW requires around 23-32% more training time than GenPO in additional efficiency experiments. While performance-versus-time curves remain competitive, the method's practical value depends on whether the return improvement justifies the extra cost, especially for large-scale robotic training or limited parallel simulation.
- SAFLOW introduces several important design choices, including flow steps, compression coefficient, time embedding dimension, and time embedding hidden size. The reviewer suggests adding discussion of hyperparameter sensitivity.
- SAFLOW is conceptually close to prior doubled-action invertible generative policy methods, especially GenPO. The paper should more clearly separate the novelty of the numerical integrator from other implementation choices and discuss when the added second-order structure is expected to matter most in practice.

**中文：**

- 引言可以更清晰，尤其是符号说明。T、z、h、K 等变量在正式定义前已经被使用，这使 self-adjoint flow 的想法更难跟随。
- 论文主要将 SAFLOW 与 Gaussian-policy baselines 和近期 generative-policy methods 比较。审稿人建议加入 RN-D，因为它同样具有提供比 Gaussian policies 更灵活替代方案的动机，并且也评估 PPO/TRPO-style optimization。这有助于澄清性能提升究竟来自 self-adjoint flow design，还是仅仅来自更 expressive 的 policy class。
- 虽然论文包含多个 IsaacLab 任务，但对于更难的高维环境的分析还可以加强。审稿人特别希望看到对 Isaac-Velocity-Rough-H1-v0、Isaac-Velocity-Rough-Unitree-Go2-v0 和 Isaac-Repose-Cube-Shadow-Direct-v0 的更多讨论，尤其是与 PPO 相比的计算效率。
- 论文在额外效率实验中报告 SAFLOW 比 GenPO 需要约 23-32% 更多训练时间。尽管 performance-versus-time curves 仍然具有竞争力，但该方法的实际价值取决于 return improvement 是否足以证明额外成本合理，尤其是在大规模机器人训练或并行仿真受限的场景中。
- SAFLOW 引入了若干重要设计选择，包括 flow steps、compression coefficient、time embedding dimension 和 time embedding hidden size。审稿人建议加入关于 hyperparameter sensitivity 的讨论。
- SAFLOW 在概念上接近已有 doubled-action invertible generative policy methods，尤其是 GenPO。论文应更清楚地区分 numerical integrator 的新颖性与其他实现选择，并讨论附加的二阶结构在实践中何时最重要。

### Questions / 问题

**English:**

1. Why is there no related work discussion about flow policies for RL, such as ReinFlow, SAC Flow, or other flow-based methods such as MeanFlow?
2. How would the authors choose the compression coefficient nu in practice?

**中文：**

1. 为什么 related work 中没有讨论 RL 中的 flow policy，例如 ReinFlow、SAC Flow，或其他 flow-based methods，如 MeanFlow？
2. 作者在实践中如何选择 compression coefficient nu？

### Limitations / 局限性

**English:** See Weakness.

**中文：** 见 Weakness 部分。

### Reference Mentioned / 提到的参考文献

**English:** Bian et al. RN-D: Discretized Categorical Actors for On-Policy Reinforcement Learning, ICML 2026.

**中文：** Bian et al. RN-D: Discretized Categorical Actors for On-Policy Reinforcement Learning, ICML 2026.

## Reviewer sTxw

### Metadata / 元信息

- **Review date / 评审日期:** 26 Jun 2026, 19:52; modified 23 Jul 2026, 22:57
- **Quality / 质量:** 3: good
- **Clarity / 清晰度:** 3: good
- **Significance / 重要性:** 3: good
- **Originality / 原创性:** 3: good
- **Rating / 评分:** 4: Borderline accept
- **Confidence / 置信度:** 4
- **Ethical concerns / 伦理问题:** NO or VERY MINOR ethics concerns only
- **Paper formatting concerns / 格式问题:** no

### Summary / 摘要

**English:** This paper presents SAFlow, a likelihood-tractable generative policy structure through self-adjoint composition. It adapts generative policies to popular likelihood-based policy optimization. Specifically, it uses a Verlet-style decomposition to ensure that the augmented MDP is time-symmetric invertible, in contrast to GenPO, which is asymmetric. The authors prove theoretically and empirically that their decomposition achieves second-order accuracy. Experiments on IsaacLab tasks demonstrate better performance over Gaussian policies, FPO, and GenPO. The first-order substitution ablation and 2D toy example analysis support the claim that the self-adjoint form brings better likelihood accuracy.

**中文：** 本文提出 SAFlow，一种通过 self-adjoint composition 实现 likelihood-tractable 的生成式策略结构。该方法使生成式策略适配流行的 likelihood-based policy optimization。具体而言，方法使用 Verlet-style decomposition 来保证 augmented MDP 具有 time-symmetric invertibility，与 asymmetric 的 GenPO 形成对比。作者从理论和经验上证明其 decomposition 达到了二阶精度。IsaacLab 任务上的实验显示，SAFlow 相比 Gaussian policies、FPO 和 GenPO 表现更好。将 SAFlow 替换为一阶更新规则的 ablation，以及 2D toy example 分析，支持 self-adjoint form 带来更好 likelihood accuracy 的主张。

### Strengths / 优点

**English:**

- The paper studies an important topic where existing flow RL methods are not good enough in likelihood estimation.
- The paper is well formatted and the proof sketch is easy to follow.
- The claim is overall well supported by empirical results.
- SAFlow benefits from environment parallelization and is easier to scale up compared with GenPO.
- The toy validation on a 2D time-variant system further supports the second-order error advantage.

**中文：**

- 论文研究了一个重要主题：已有 flow RL methods 在 likelihood estimation 上仍不够好。
- 论文格式良好，proof sketch 容易跟随。
- 论文主张整体上得到了实验结果的较好支持。
- 与 GenPO 相比，SAFlow 受益于环境并行化，更容易扩展。
- 2D time-variant system 上的 toy validation 进一步支持了二阶误差优势。

### Weaknesses / 缺点

**English:**

- The toy example is a linear 2D time-variant system, which does not ensure applicability to high-dimensional nonlinear systems. Given that the accuracy gap in Appendix C.4 is dramatic, the reviewer does not observe a corresponding gap in Figure 4(a), where SAFlow with different flow steps differs only slightly.
- Overall, the construction differs only modestly from GenPO. It follows classical symmetric integrators in eliminating odd-order terms and assuring at least second-order accuracy. The reviewer sees the core novelty as the propagation of accuracy to the PPO objective, namely Corollary 6.
- As a minor concern, the theoretical part feels somewhat redundant. For example, Theorem 3 is basically implied by the definition itself.

**中文：**

- toy example 是线性的 2D time-variant system，不能保证方法适用于高维非线性系统。考虑到 Appendix C.4 中 accuracy gap 非常明显，审稿人并没有在 Figure 4(a) 中观察到相应差距，其中不同 flow steps 的 SAFlow 结果差别很小。
- 总体而言，该构造与 GenPO 的差异并不大。它遵循经典 symmetric integrators，通过消除奇数阶项来保证至少二阶精度。审稿人认为核心新颖性在于将 accuracy 传播到 PPO objective，即 Corollary 6。
- 作为次要问题，理论部分略显冗余。例如 Theorem 3 基本上可以由定义本身推出。

### Questions / 问题

**English:**

1. Related to Weakness 1, does this imply that likelihood accuracy is not the performance bottleneck on Ant? Could the authors provide degradation curves of SAFlow versus GenPO as the relevant difficulty or rollout parameter increases? The original review text appears to omit the exact symbol after "when".
2. Related to Weakness 2, how does SAFlow perform compared to GenPO with doubled flow steps? What about computational cost?

**中文：**

1. 关于 Weakness 1，这是否意味着 likelihood accuracy 不是 Ant 任务上的性能瓶颈？作者能否提供当某个参数增大时 SAFlow 与 GenPO 的 degradation curves？用户提供的原始评审文本中 “when” 后的具体符号似乎缺失。
2. 关于 Weakness 2，与 doubled flow steps 的 GenPO 相比，SAFlow 表现如何？计算成本如何？

### Limitations / 局限性

**English:** yes

**中文：** 有。

## Reviewer pw8T

### Metadata / 元信息

- **Review date / 评审日期:** 26 Jun 2026, 18:58; modified 23 Jul 2026, 22:57
- **Quality / 质量:** 3: good
- **Clarity / 清晰度:** 3: good
- **Significance / 重要性:** 3: good
- **Originality / 原创性:** 3: good
- **Rating / 评分:** 5: Accept
- **Confidence / 置信度:** 4
- **Ethical concerns / 伦理问题:** NO or VERY MINOR ethics concerns only
- **Paper formatting concerns / 格式问题:** no

### Summary / 摘要

**English:** This paper proposes SAFLOW, an on-policy reinforcement learning method for expressive generative policies. The method constructs an invertible flow policy in an augmented, doubled action space and uses a self-adjoint reversible numerical update. Because the inverse map can be obtained by applying the same update with a negative step size, the method enables tractable augmented-action likelihood evaluation for PPO-style policy optimization. The self-adjoint update also provides a second-order approximation to the underlying continuous flow. The paper provides theoretical results on exact inversion, likelihood consistency, policy-ratio consistency, and optimality preservation in the augmented MDP. Empirically, it evaluates SAFLOW on several IsaacLab continuous-control tasks against PPO, TRPO, FPO, and GenPO.

**中文：** 本文提出 SAFLOW，一种面向 expressive generative policies 的 on-policy reinforcement learning 方法。该方法在 augmented, doubled action space 中构造可逆 flow policy，并使用 self-adjoint reversible numerical update。由于 inverse map 可以通过对同一 update 使用负 step size 得到，该方法能够为 PPO-style policy optimization 提供 tractable augmented-action likelihood evaluation。self-adjoint update 还为底层 continuous flow 提供二阶近似。论文给出了关于 exact inversion、likelihood consistency、policy-ratio consistency 以及 augmented MDP 中 optimality preservation 的理论结果。实验方面，论文在多个 IsaacLab continuous-control tasks 上将 SAFLOW 与 PPO、TRPO、FPO 和 GenPO 进行了比较。

### Strengths / 优点

**English:**

- The paper addresses an important problem in likelihood-based on-policy reinforcement learning with generative policies: how to obtain stable and accurate likelihood ratios for expressive flow or diffusion-style policies.
- The proposed self-adjoint reversible update is elegant and technically well motivated.
- Compared with GenPO's first-order alternating update in a doubled action space, SAFLOW introduces a second-order time-symmetric update. This provides a clear numerical advantage: inversion is obtained by reversing the step size, and discretization error is theoretically improved from first order to second order.
- The theoretical analysis is useful. The paper proves exact inversion, second-order flow approximation, second-order consistency of likelihoods and PPO-style ratios, and preservation of optimal control value in the augmented action space.
- The empirical evaluation is reasonably broad, covering locomotion, manipulation, dexterous control, and aerial control tasks in IsaacLab.
- Comparisons with PPO, TRPO, FPO, and GenPO are relevant, and ablations on flow steps, compression coefficient, and time embedding help explain some design choices.

**中文：**

- 论文解决了 generative policies 在 likelihood-based on-policy reinforcement learning 中的一个重要问题：如何为 expressive flow 或 diffusion-style policies 获得稳定且准确的 likelihood ratios。
- 所提出的 self-adjoint reversible update 优雅且技术动机充分。
- 与 GenPO 在 doubled action space 中的一阶 alternating update 相比，SAFLOW 引入了二阶 time-symmetric update。这提供了清晰的数值优势：通过反转 step size 获得 inversion，并且 discretization error 在理论上从一阶提升到二阶。
- 理论分析有用。论文证明了 exact inversion、second-order flow approximation、likelihoods 与 PPO-style ratios 的 second-order consistency，以及 augmented action space 对 optimal control value 的保持。
- 实验评估范围较广，覆盖 IsaacLab 中的 locomotion、manipulation、dexterous control 和 aerial control tasks。
- 与 PPO、TRPO、FPO 和 GenPO 的比较是相关的，对 flow steps、compression coefficient 和 time embedding 的 ablation 有助于解释部分设计选择。

### Concerns / 主要问题

**English:**

- The main theoretical concern is the augmented dummy-action formulation. SAFLOW optimizes likelihoods over the augmented action a_tilde=(x,y), while the environment only observes the projected action a=(x+y)/2. The paper proves that the augmented MDP preserves the optimal control value, which is valid at a broad control level. However, PPO relies on clipped likelihood ratios and trust-region-like constraints. A trust region in dummy-action space need not correspond to a meaningful trust region in the original action space.
- The second concern is the lack of comparison with GenPO++ or detailed discussion of it, assuming it is contemporaneous and available to the authors. GenPO++ also targets reversible generative policy optimization and claims high-order reversible ODE-based likelihood-ratio computation without dummy-action augmentation. Since SAFLOW's main novelty over GenPO is the second-order self-adjoint update, GenPO++ appears to be a highly relevant baseline or at least related work.
- Computational cost is under-emphasized. SAFLOW is slower than GenPO and much slower than Gaussian PPO/TRPO. The reported performance gains may justify the cost on some tasks, but the paper should present wall-clock performance and memory usage more prominently, especially because the method targets large-scale parallel simulation.
- The empirical validation of the central numerical claim could be tied more directly to RL performance. The first-order versus second-order ablation is useful, but additional evidence connecting likelihood-ratio stability, real-action policy change, clipping fraction, and return improvement would make the optimization story more convincing.

**中文：**

- 主要理论担忧是 augmented dummy-action formulation。SAFLOW 在 augmented action a_tilde=(x,y) 上优化 likelihood，而环境只观察 projected action a=(x+y)/2。论文证明 augmented MDP 保持 optimal control value，这在宏观控制层面是成立的。然而 PPO 不仅关心最优值保持，它依赖 clipped likelihood ratios 和 trust-region-like constraints。dummy-action space 中的 trust region 未必对应 original action space 中有意义的 trust region。
- 第二个担忧是缺少与 GenPO++ 的比较或详细讨论，前提是 GenPO++ 与本文同期且作者可以获得。GenPO++ 同样关注 reversible generative policy optimization，并声称在没有 dummy-action augmentation 的情况下实现 high-order reversible ODE-based likelihood-ratio computation。由于 SAFLOW 相比 GenPO 的主要新颖性是二阶 self-adjoint update，GenPO++ 似乎是高度相关的 baseline，至少也应作为 related work 讨论。
- computational cost 被弱化了。SAFLOW 比 GenPO 慢，也比 Gaussian PPO/TRPO 慢得多。报告的性能提升在某些任务上可能足以证明成本合理，但论文应更突出 wall-clock performance 和 memory usage，尤其是因为该方法面向 large-scale parallel simulation。
- 对核心数值主张的实验验证可以更直接地与 RL performance 绑定。first-order versus second-order ablation 是有用的，但如果能进一步连接 likelihood-ratio stability、real-action policy change、clipping fraction 和 return improvement，optimization story 会更有说服力。

### Questions / 问题

**English:**

1. How does SAFLOW compare with GenPO++? GenPO++ also uses reversible generative policy optimization and claims high-order reversible likelihood-ratio computation without doubled action augmentation. A comparison or detailed discussion would help clarify the novelty and practical advantage of SAFLOW.
2. Does a trust region in the augmented dummy-action space correspond to a meaningful trust region in the original action space? Since the environment only observes a=(x+y)/2, PPO clipping on a_tilde=(x,y) may penalize changes that do not affect the executed action. Could the authors provide theoretical or empirical evidence that the dummy-action likelihood ratio is well aligned with real-action policy change?
3. How sensitive is SAFLOW to the compression coefficient? The compression term seems important for controlling the projection null space, but it also changes the optimization objective. Would an adaptive schedule or a stronger analysis of this regularizer improve robustness?
4. What is the computational trade-off compared with GenPO and GenPO++? The paper reports that SAFLOW is slower than GenPO due to self-adjoint likelihood evaluation. It would be useful to report performance per wall-clock time and memory cost more prominently, especially since the method targets large-scale parallel simulation.
5. Does the second-order likelihood consistency translate into better policy optimization in practice, beyond smoother likelihood-ratio statistics? A controlled experiment comparing first-order versus second-order updates under the same architecture is useful; further reporting the correlation between likelihood-ratio variance and return improvement would strengthen the claim.

**中文：**

1. SAFLOW 与 GenPO++ 相比如何？GenPO++ 同样使用 reversible generative policy optimization，并声称无需 doubled action augmentation 就可以实现 high-order reversible likelihood-ratio computation。比较或详细讨论将有助于澄清 SAFLOW 的新颖性和实践优势。
2. augmented dummy-action space 中的 trust region 是否对应 original action space 中有意义的 trust region？由于环境只观察 a=(x+y)/2，对 a_tilde=(x,y) 做 PPO clipping 可能会惩罚不影响实际执行动作的变化。作者能否提供理论或实验证据，说明 dummy-action likelihood ratio 与 real-action policy change 良好对齐？
3. SAFLOW 对 compression coefficient 有多敏感？compression term 似乎对控制 projection null space 很重要，但它也改变了优化目标。adaptive schedule 或对该 regularizer 的更强分析是否能改善鲁棒性？
4. 与 GenPO 和 GenPO++ 相比，计算 trade-off 是什么？论文报告 SAFLOW 由于 self-adjoint likelihood evaluation 比 GenPO 慢。鉴于该方法面向 large-scale parallel simulation，更突出地报告 performance per wall-clock time 和 memory cost 会很有帮助。
5. 除了更平滑的 likelihood-ratio statistics，二阶 likelihood consistency 是否在实践中转化为更好的 policy optimization？在相同架构下比较一阶与二阶更新的 controlled experiment 是有用的；进一步报告 likelihood-ratio variance 与 return improvement 之间的相关性会加强该主张。

### Limitations / 局限性

**English:** The authors discuss several limitations, including fixed flow steps, fixed compression coefficient, and evaluation mostly on state-based simulated benchmarks.

**中文：** 作者讨论了若干局限性，包括固定的 flow steps、固定的 compression coefficient，以及评估主要集中在 state-based simulated benchmarks 上。

## Reviewer h1HA

### Metadata / 元信息

- **Review date / 评审日期:** 25 Jun 2026, 07:03; modified 23 Jul 2026, 22:57
- **Quality / 质量:** 2: not good
- **Clarity / 清晰度:** 2: not good
- **Significance / 重要性:** 3: good
- **Originality / 原创性:** 3: good
- **Rating / 评分:** 3: Borderline reject
- **Confidence / 置信度:** 4
- **Ethical concerns / 伦理问题:** NO or VERY MINOR ethics concerns only
- **Paper formatting concerns / 格式问题:** None

### Summary / 摘要

**English:** This paper tackles the likelihood intractability of flow-based models, which cannot be directly applied to on-policy frameworks like PPO. The authors propose SAFLOW, a likelihood-tractable flow policy with a doubled action space that uses a Verlet-style self-adjoint composition for generation. SAFLOW aligns forward sampling and backward likelihood evaluation under the same time-symmetric numerical rule. Experiments in IsaacLab show superior performance compared to Gaussian policies and likelihood-based generative policy baselines.

**中文：** 本文处理 flow-based models 的 likelihood intractability 问题，因为这类模型无法直接应用于 PPO 等 on-policy frameworks。作者提出 SAFLOW，一种 likelihood-tractable flow policy，它使用 doubled action space，并通过 Verlet-style self-adjoint composition 进行生成。SAFLOW 使 forward sampling 和 backward likelihood evaluation 在同一个 time-symmetric numerical rule 下对齐。IsaacLab 实验显示，与 Gaussian policies 和 likelihood-based generative policy baselines 相比，SAFLOW 表现更优。

### Strengths and Concerns / 优点与担忧

**English:**

- **Quality:** The experiments are strong, covering a diverse set of IsaacLab tasks and comparing against both Gaussian and recent generative-policy baselines. However, there are concerns about theoretical soundness.
- **Theorem 1:** The theorem is generally sound, except that the projection M(x,y)=(x+y)/2 could lead to actions outside the action space. The paper needs the assumption that the action space is convex or at least closed under averaging. The theorem also does not account for regularization used in the practical objective.
- **Theorem 4:** The proof is missing important information about why BCH applies to the time-dependent velocity field, and the proof misses time conditioning. The extension to the local Jacobian is also unclear to the reviewer.
- **Core theoretical claim:** Theorem 4 needs extra justification because it is core to the claim that SAFLOW provides second-order approximation accuracy to the learned continuous flow and improves numerical consistency of likelihood and policy-ratio computation.
- **Clarity:** Overall, the problem and method are clearly illustrated, but the reason for constructing a 2d augmented action space is unclear.
- **Augmentation design:** If the 2d augmentation is simply one straightforward way to perform a Verlet-style kick-drift-kick technique, then other designs, such as splitting the original d-dimensional action into two blocks, may also allow Verlet-style updates. Since the method raises the action space to 2d, it introduces extra components such as regularization in the actor loss. Explaining why augmentation is needed intuitively or experimentally would help readers understand this design choice.
- **Significance:** SAFLOW shows that numerical structure matters for likelihood-based generative policy optimization.
- **Originality:** Using a Verlet-style self-adjoint composition enables exact alignment of forward sampling and backward likelihood evaluation, while the rest of the model is largely based on the likelihood-tractable flow policy GenPO.

**中文：**

- **质量：** 实验较强，覆盖多样的 IsaacLab 任务，并与 Gaussian baselines 和近期 generative-policy baselines 进行了比较。不过，审稿人对理论严谨性有一些担忧。
- **Theorem 1：** 该定理总体上成立，但 projection M(x,y)=(x+y)/2 可能导致动作落在 action space 外。因此需要假设 action space 是 convex，或至少在 averaging 下 closed。该定理也没有考虑 practical objective 中使用的 regularization。
- **Theorem 4：** 证明缺少关键信息，例如为什么 BCH 可以应用于 time-dependent velocity field；证明也缺少 time conditioning。向 local Jacobian 的扩展也让审稿人感到不清楚。
- **核心理论主张：** Theorem 4 需要额外论证，因为它是作者声称“SAFLOW 对 learned continuous flow 提供二阶近似精度，并提升 likelihood 和 policy-ratio computation 数值一致性”的核心。
- **清晰度：** 总体而言，问题和方法解释得比较清楚，但为什么构造 2d augmented action space 仍不清楚。
- **augmentation design：** 如果 2d augmentation 只是执行 Verlet-style kick-drift-kick 技术的一种直接方式，那么其他设计，例如将原始 d 维动作拆分为两个 action blocks，也可能允许 Verlet-style update。由于该方法将 action space 提升到 2d，它引入了 actor loss regularization 等额外组件。通过直觉解释或实验说明为什么 augmentation 是必要的，将帮助读者理解这一设计选择。
- **重要性：** SAFLOW 表明 numerical structure 对 likelihood-based generative policy optimization 很重要。
- **原创性：** 使用 Verlet-style self-adjoint composition 使 forward sampling 与 backward likelihood evaluation 精确对齐；其余模型大体上基于 likelihood-tractable flow policy GenPO。

### Questions / 问题

**English:**

1. Please see the concerns around theorems in the strengths and weaknesses section.
2. Is the 2d augmented action space necessary, and how does this augmentation contribute to model performance? Since the Verlet-style kick-drift-kick technique can also be applied to two action blocks whose sizes sum to the original action dimension d, explaining why augmentation is needed intuitively or experimentally would help readers understand this design choice.

**中文：**

1. 请参见 Strengths and Weaknesses 中关于定理的担忧。
2. 2d augmented action space 是否必要？这种 augmentation 如何贡献于模型性能？由于 Verlet-style kick-drift-kick 技术也可以应用于两个 action blocks，且它们的维度之和为原始 action dimension d，因此通过直觉或实验解释为什么需要 augmentation 将帮助读者理解这一设计选择。

### Limitations / 局限性

**English:** The authors have discussed the limitations.

**中文：** 作者已经讨论了局限性。

## Cross-Reviewer Themes / 四位审稿人的共同关注点

### 1. Computational cost and practical value / 计算成本与实际价值

**English:** Reviewer Gdko and Reviewer pw8T both emphasize that SAFLOW is slower than GenPO and much slower than Gaussian PPO/TRPO. They ask for more prominent wall-clock performance, memory usage, performance-per-time reporting, and discussion of whether return gains justify the extra cost, especially in large-scale robotic training.

**中文：** Reviewer Gdko 和 Reviewer pw8T 都强调 SAFLOW 比 GenPO 慢，也比 Gaussian PPO/TRPO 慢得多。他们要求更突出地报告 wall-clock performance、memory usage、performance per time，并讨论 return gains 是否足以证明额外成本合理，尤其是在大规模机器人训练中。

### 2. Novelty relative to GenPO and recent methods / 相对于 GenPO 与近期方法的新颖性

**English:** All reviewers compare SAFLOW to GenPO or related flow-based generative policy methods. Gdko asks to separate the novelty of the numerical integrator from implementation choices. sTxw says the construction differs only modestly from GenPO. pw8T asks for comparison or discussion of GenPO++. h1HA says the rest of the model is largely based on GenPO.

**中文：** 四位审稿人都将 SAFLOW 与 GenPO 或相关 flow-based generative policy methods 联系起来。Gdko 要求区分 numerical integrator 的新颖性和其他实现选择。sTxw 认为该构造与 GenPO 差异不大。pw8T 要求比较或讨论 GenPO++。h1HA 认为模型其余部分很大程度上基于 GenPO。

### 3. Need for augmented/doubled action space / augmented 或 doubled action space 的必要性

**English:** Reviewer pw8T questions whether a trust region in augmented dummy-action space corresponds to a meaningful trust region in the original action space. Reviewer h1HA asks whether 2d augmentation is necessary and whether other block-splitting designs could also support Verlet-style updates. Gdko also asks how to choose the compression coefficient nu, which is tied to the doubled action formulation.

**中文：** Reviewer pw8T 质疑 augmented dummy-action space 中的 trust region 是否对应 original action space 中有意义的 trust region。Reviewer h1HA 询问 2d augmentation 是否必要，以及其他 block-splitting 设计是否也能支持 Verlet-style update。Gdko 也询问 compression coefficient nu 的实践选择，而该问题与 doubled action formulation 直接相关。

### 4. Theoretical rigor and theorem presentation / 理论严谨性与定理表达

**English:** Reviewer h1HA raises the strongest theoretical concerns, especially about Theorem 1 and Theorem 4: convexity or closure of the action space, the practical regularized objective, BCH for time-dependent velocity fields, time conditioning, and local Jacobian arguments. sTxw also considers some theory redundant, while pw8T asks whether augmented-space likelihood ratios are aligned with real-action policy changes.

**中文：** Reviewer h1HA 提出了最强的理论担忧，尤其围绕 Theorem 1 和 Theorem 4：action space 的 convexity 或 closure、practical regularized objective、time-dependent velocity fields 上 BCH 的适用性、time conditioning，以及 local Jacobian 论证。sTxw 也认为部分理论略显冗余，而 pw8T 则询问 augmented-space likelihood ratios 是否与 real-action policy changes 对齐。

### 5. Empirical link between numerical accuracy and RL gains / 数值精度与 RL 收益之间的实验证据

**English:** Several reviewers want stronger evidence that second-order likelihood consistency actually improves policy optimization. sTxw notes that the dramatic toy accuracy gap is not clearly reflected in Figure 4(a). pw8T asks for evidence connecting likelihood-ratio stability, real-action policy change, clipping fraction, and return improvement. Gdko asks when the second-order structure matters most in practice.

**中文：** 多位审稿人希望看到更强证据，说明二阶 likelihood consistency 确实改善了 policy optimization。sTxw 指出 toy example 中巨大的 accuracy gap 并没有在 Figure 4(a) 中明显体现。pw8T 要求提供连接 likelihood-ratio stability、real-action policy change、clipping fraction 和 return improvement 的证据。Gdko 则询问二阶结构在实践中何时最重要。

### 6. Baselines and related work / Baseline 与相关工作

**English:** Reviewers request additional or more explicit discussion of RN-D, ReinFlow, SAC Flow, MeanFlow, GenPO++, and potentially GenPO with doubled flow steps. These requests are important for rebuttal because they target both novelty and empirical positioning.

**中文：** 审稿人要求补充或更明确地讨论 RN-D、ReinFlow、SAC Flow、MeanFlow、GenPO++，以及可能的 doubled flow steps GenPO。这些问题对 rebuttal 很重要，因为它们同时涉及 novelty 和 empirical positioning。

