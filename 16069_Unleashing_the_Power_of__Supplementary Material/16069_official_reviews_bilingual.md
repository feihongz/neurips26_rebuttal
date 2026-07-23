# Submission 16069 Official Reviews - Bilingual Notes

本文档整理 Submission 16069 三位审稿人的官方评审意见，采用中英对照格式，便于撰写 rebuttal。

## Reviewer tShQ

### Metadata / 元信息

- **Review date / 评审日期:** 26 Jun 2026, 18:29; modified 23 Jul 2026, 22:57
- **Quality / 质量:** 4: excellent
- **Clarity / 清晰度:** 4: excellent
- **Significance / 重要性:** 4: excellent
- **Originality / 原创性:** 4: excellent
- **Rating / 评分:** 6: Strong Accept
- **Confidence / 置信度:** 3
- **Ethical concerns / 伦理问题:** NO or VERY MINOR ethics concerns only

### Summary / 摘要

**English:** This paper introduces GENIEO, a method that replaces standard Gaussian policies with generative models in off-policy RL, motivated by the ability of generative models to represent complex, multimodal action distributions. The core contribution is a principled approach to maximum entropy RL using generative policies, centered on exact intrinsic entropy estimation for efficient exploration, addressing a key challenge since entropy computation is typically intractable for expressive generative models. The paper introduces a doubled dummy action-space technique that enables invertible updates, providing a clean mathematical foundation for the approach.

**中文：** 本文提出 GENIEO，一种在 off-policy RL 中用生成模型替代标准高斯策略的方法。其动机在于生成模型能够表示复杂的、多模态的动作分布。核心贡献是提出了一种使用生成式策略进行最大熵强化学习的原则性方法，重点在于通过精确的内在熵估计来实现高效探索。由于对于表达能力强的生成模型而言，熵计算通常是不可 tractable 的，因此该工作解决了一个关键挑战。论文还引入了 doubled dummy action-space 技术，使更新过程可逆，并为该方法提供了清晰的数学基础。

### Strengths / 优点

**English:**

- The paper is well-supported by theory, with Theorems 2 and 3 providing non-heuristic justification for the approach. This elevates the contribution beyond empirical tricks and gives confidence that the method's benefits are principled rather than incidental.
- Despite tackling a technically rich topic, the paper is clearly written and easy to follow, making the contribution accessible without sacrificing rigor.
- The doubled dummy action-space trick is a clever and interesting mechanism that enables invertible updates, addressing a real technical challenge in working with generative policies for entropy-driven exploration.
- The paper evaluates across 14 environments spanning diverse domains, with baseline selection that appropriately represents generative model-based policies. The authors carefully match hyperparameters across methods to ensure fair comparison, a detail that strengthens confidence in the reported improvements. The method clearly outperforms baselines, with especially strong results on H-Bench, which appears to represent the most challenging task set.
- All major components of the method are validated through ablation, supporting the design choices and clarifying which elements drive performance gains.

**中文：**

- 论文有扎实的理论支撑，其中 Theorem 2 和 Theorem 3 为方法提供了非启发式的论证。这使得贡献超越了经验技巧，并增强了读者对方法收益具有原则性而非偶然性的信心。
- 虽然论文处理的是技术上较复杂的主题，但写作清晰、易于理解，使贡献在不牺牲严谨性的前提下具有较好的可读性。
- doubled dummy action-space 技巧是一个巧妙且有趣的机制，它使更新可逆，并解决了生成式策略在熵驱动探索中面临的真实技术挑战。
- 论文在覆盖多个不同领域的 14 个环境上进行了评估，baseline 的选择能够恰当地代表基于生成模型的策略。作者仔细匹配了不同方法的超参数以保证公平比较，这一细节增强了对实验改进结果的信心。该方法明显优于 baseline，尤其是在 H-Bench 上表现很强，而 H-Bench 似乎代表了最具挑战性的任务集合。
- 方法的所有主要组件都通过 ablation 得到了验证，支持了设计选择，并澄清了哪些因素驱动了性能提升。

### Weaknesses / 缺点

**English:** I want to be upfront that my background in generative policy-based RL is limited, so I may be missing nuances that a specialist would catch. That said, after careful reading, I did not identify major weaknesses. The paper appears to comprehensively address what's needed for a strong RL contribution: principled theory, a clear technical innovation, and thorough experimental validation across diverse environments and baselines.

**中文：** 审稿人坦诚表示自己在 generative policy-based RL 方面的背景有限，因此可能会遗漏专家能够注意到的细节。不过，在仔细阅读后，审稿人没有发现主要缺点。论文似乎全面满足了一篇强 RL 论文所需的要素：原则性的理论、清晰的技术创新，以及在多样环境和 baseline 上的充分实验验证。

### Questions / 问题

**English:**

1. How does training and inference time for GENIEO compare to baseline methods? Specifically, does doubling the latent dimensionality via the dummy action-space trick introduce meaningful computational overhead?
2. The paper mentions in Future Work that handling extremely sparse reward settings remains challenging. Do you believe this limitation is intrinsic to the maximum entropy RL paradigm itself, since exploration under this framework is not explicitly targeted toward uncertain regions, or is it specific to your method's implementation?
3. Could you include additional experiments providing direct evidence that GENIEO explores more effectively than baselines? For instance, visualizing or quantifying state space coverage would strengthen the exploration claims beyond final task performance.

**中文：**

1. GENIEO 的训练时间和推理时间与 baseline 方法相比如何？具体来说，通过 dummy action-space 技巧将 latent dimensionality 加倍是否会带来显著的计算开销？
2. 论文在 Future Work 中提到，处理极端稀疏奖励设定仍然具有挑战性。你们认为这个限制是最大熵 RL 范式本身固有的吗？因为该框架下的探索并不是显式地指向不确定区域；还是说这是你们方法实现层面的具体限制？
3. 你们能否加入额外实验，直接证明 GENIEO 比 baseline 探索得更有效？例如，可视化或量化 state space coverage 将能加强探索方面的主张，而不仅仅依赖最终任务性能。

### Limitations / 局限性

**English:** yes

**中文：** 有。

## Reviewer 4ynL

### Metadata / 元信息

- **Review date / 评审日期:** 26 Jun 2026, 00:28; modified 23 Jul 2026, 22:57
- **Quality / 质量:** 3: good
- **Clarity / 清晰度:** 3: good
- **Significance / 重要性:** 3: good
- **Originality / 原创性:** 2: not good
- **Rating / 评分:** 3: Borderline reject
- **Confidence / 置信度:** 3
- **Ethical concerns / 伦理问题:** NO or VERY MINOR ethics concerns only
- **Paper formatting concerns / 格式问题:** Manuscript is well-structured and complies with submission guidelines.

### Summary / 摘要

**English:** This paper introduces GENIEO, a novel generative reinforcement learning framework designed to unlock the untapped potential of generative models in maximum entropy RL. By designing a structurally invertible affine dual-variable flow, GENIEO bypasses the numerical approximations of traditional ODE solvers to calculate the policy's exact intrinsic entropy. Directly integrating this exact entropy formulation into the learning objective drives principled and highly effective exploration. Evaluated across 14 complex, high-dimensional tasks, GENIEO achieves state-of-the-art performance, successfully bridging the gap between highly expressive generative models and maximum entropy RL.

**中文：** 本文提出 GENIEO，一个新颖的生成式强化学习框架，旨在释放生成模型在最大熵 RL 中尚未被充分利用的潜力。通过设计结构上可逆的 affine dual-variable flow，GENIEO 绕过了传统 ODE solver 的数值近似，从而计算策略的精确内在熵。将这种精确熵形式直接整合进学习目标中，能够驱动原则性且高效的探索。在 14 个复杂、高维任务上的评估显示，GENIEO 达到了 state-of-the-art 性能，成功弥合了高表达能力生成模型与最大熵 RL 之间的差距。

### Strengths / 优点

**English:**

- The proposed policy design successfully bridges maximum entropy RL and generative RL, supported by a rigorous mathematical foundation.
- The empirical results presented in the paper are well-executed and convincingly demonstrate the overall effectiveness of the proposed method across the evaluated environments.

**中文：**

- 所提出的策略设计成功连接了最大熵 RL 和生成式 RL，并由严谨的数学基础支撑。
- 论文中的实验结果执行良好，并且令人信服地展示了该方法在所评估环境中的整体有效性。

### Weaknesses / 缺点

**English:**

- Insufficient clarity regarding technical novelty. The concepts of space expansion and triangular affine coupling have been extensively explored in prior literature, notably in works such as Real NVP. The specific technical advancements and unique contributions of the proposed method over these established techniques remain unclear. The authors should explicitly articulate these differences and highlight their method's specific advantages in both the methodology and related work sections.
- Incomplete baseline comparisons and evaluation scope. While the authors claim state-of-the-art performance, several recent and highly relevant strong baselines, such as SimbaV2, MAD-TD, and BRO, are absent from the experiments. Omitting these comparisons undermines the SOTA claim and may introduce evaluation bias. Furthermore, to comprehensively assess robustness, evaluation on the DeepMind Control suite should ideally incorporate the more challenging DMC Hard suite.
- Lack of empirical evidence supporting improved exploration. A primary motivation of this work is to enhance policy exploration, particularly within generative RL. However, the paper lacks sufficient empirical evidence to substantiate this claim. The authors should provide concrete evidence, such as exploration statistics, state-visitation heatmaps, or related visualizations, to clearly demonstrate the exploratory benefits of the proposed approach.

**中文：**

- 技术新颖性的阐述不够清晰。space expansion 和 triangular affine coupling 的概念已经在既有文献中被广泛探索，尤其是 Real NVP 等工作。与这些成熟技术相比，本文方法的具体技术进步和独特贡献仍不清楚。作者应在方法和相关工作部分明确说明这些差异，并突出本文方法的具体优势。
- baseline 比较和评估范围不完整。尽管作者声称达到了 SOTA 性能，但实验中缺少若干近期且高度相关的强 baseline，例如 SimbaV2、MAD-TD 和 BRO。省略这些比较会削弱 SOTA 主张，并可能引入评估偏差。此外，为了全面评估方法的鲁棒性，DeepMind Control suite 上的评估理想情况下应包含更具挑战性的 DMC Hard suite。
- 缺乏支持改进探索能力的实验证据。该工作的主要动机之一是增强策略探索，尤其是在生成式 RL 语境下。然而，论文缺少足够的实验证据来支撑这一主张。作者应提供具体证据，例如 exploration statistics、state-visitation heatmaps 或相关可视化，以清楚展示所提出方法的探索收益。

### Questions / 问题

**English:**

1. What are the distinct methodological advantages of the proposed approach over existing space-expansion and affine-coupling techniques, specifically in the context of generative RL?
2. Could the authors provide a detailed analysis of the computational overhead associated with the proposed method during both training and inference, particularly in comparison to a standard or vanilla policy?
3. To what extent does the proposed method actually improve policy exploration in practice? Furthermore, does enforcing higher policy entropy consistently translate to better meaningful exploration in the evaluated tasks, or are there scenarios where it becomes detrimental?

**中文：**

1. 特别是在生成式 RL 的语境下，与现有 space-expansion 和 affine-coupling 技术相比，本文方法有哪些明确的方法论优势？
2. 作者能否提供对该方法在训练和推理阶段计算开销的详细分析，尤其是与标准或 vanilla policy 相比？
3. 所提出方法在实践中到底在多大程度上改善了策略探索？此外，强制提高策略熵是否总能在评估任务中转化为更有意义的探索，还是在某些场景中会产生负面影响？

### Limitations / 局限性

**English:** The authors should more explicitly discuss the inherent trade-offs of maximum-entropy-based methods. Specifically, these methods often penalize highly deterministic and stable behaviors in favor of encouraging exploration. However, tasks requiring high-precision control or fine-grained manipulation, such as robotic grasping, typically rely on such stable, low-variance behaviors. Therefore, the authors are encouraged to critically analyze and define the valid scope of environments where their proposed method is most applicable and beneficial.

**中文：** 作者应更明确地讨论基于最大熵方法的内在权衡。具体而言，这类方法通常会为了鼓励探索而惩罚高度确定且稳定的行为。然而，诸如 robotic grasping 这样的高精度控制或精细操作任务通常依赖稳定、低方差的行为。因此，审稿人建议作者批判性地分析并界定所提出方法最适用、最有收益的环境范围。

### References Mentioned / 提到的参考文献

**English:**

- Real NVP: Laurent Dinh, Jascha Sohl-Dickstein, Samy Bengio. Density estimation using Real NVP. ICLR 2017.
- SimbaV2: Hojoon Lee, Youngdo Lee, Takuma Seno, Donghu Kim, Peter Stone, Jaegul Choo. Hyperspherical Normalization for Scalable Deep Reinforcement Learning. ICML 2025.
- MAD-TD: Claas A. Voelcker et al. MAD-TD: Model-Augmented Data stabilizes High Update Ratio RL. ICLR 2025.
- BRO: Michal Nauman, Mateusz Ostaszewski, Krzysztof Jankowski, Piotr Milos, Marek Cygan. Bigger, Regularized, Optimistic: scaling for compute and sample-efficient continuous control. NeurIPS 2024.

**中文：**

- Real NVP：Laurent Dinh, Jascha Sohl-Dickstein, Samy Bengio. Density estimation using Real NVP. ICLR 2017.
- SimbaV2：Hojoon Lee, Youngdo Lee, Takuma Seno, Donghu Kim, Peter Stone, Jaegul Choo. Hyperspherical Normalization for Scalable Deep Reinforcement Learning. ICML 2025.
- MAD-TD：Claas A. Voelcker et al. MAD-TD: Model-Augmented Data stabilizes High Update Ratio RL. ICLR 2025.
- BRO：Michal Nauman, Mateusz Ostaszewski, Krzysztof Jankowski, Piotr Milos, Marek Cygan. Bigger, Regularized, Optimistic: scaling for compute and sample-efficient continuous control. NeurIPS 2024.

## Reviewer BXmK

### Metadata / 元信息

- **Review date / 评审日期:** 04 Jun 2026, 17:07; modified 23 Jul 2026, 22:57
- **Quality / 质量:** 3: good
- **Clarity / 清晰度:** 4: excellent
- **Significance / 重要性:** 3: good
- **Originality / 原创性:** 3: good
- **Rating / 评分:** 4: Borderline accept
- **Confidence / 置信度:** 4
- **Ethical concerns / 伦理问题:** NO or VERY MINOR ethics concerns only
- **Paper formatting concerns / 格式问题:** NA

### Summary / 摘要

**English:** This paper presents an invertible flow-based mechanism so that the log-likelihood of flow-based policies can be computed exactly, and the entropy can be estimated with little or no approximation bias as a consequence. This leads to a more accurate solution to perform maximum entropy reinforcement learning over previous diffusion or flow-based policies. The authors develop a new MaxEnt RL algorithm setup to accommodate their new flow-architecture, and show in their ablations that entropy estimation is near-exact up to numerical precision and Monte Carlo approximation error. The authors perform informative ablations on the key hyperparameters of the new RL algorithm, and compare against a variety of previous diffusion and flow-based RL algorithms, against which GENIEO performs quite well.

**中文：** 本文提出了一种基于可逆 flow 的机制，使得 flow-based policy 的 log-likelihood 可以被精确计算，并因此使熵估计只有很小或几乎没有近似偏差。与以往 diffusion 或 flow-based policy 相比，这为最大熵强化学习提供了更准确的解法。作者开发了一套新的 MaxEnt RL 算法设置以适配新的 flow 架构，并通过 ablation 表明，在数值精度和 Monte Carlo 近似误差范围内，熵估计接近精确。作者还对新 RL 算法的关键超参数进行了有信息量的消融实验，并与多种已有 diffusion 和 flow-based RL 算法进行了比较，GENIEO 表现相当好。

### Overall Assessment / 总体评价

**English:** This is a technically solid paper that identifies an important gap for making flow-based policies better suited in a common reinforcement learning setting, namely MaxEnt RL. The approach is straightforward, and although the building blocks of the method are not new, for example normalizing flows, and the reviewer has reservations about the authors' motivation and narrative, the contribution is expected to be generally useful for researchers who want to use flow-based models for SAC-based RL or PPO-like algorithms.

**中文：** 这是一篇技术上扎实的论文，指出了让 flow-based policy 更适合常见强化学习设置，即 MaxEnt RL 的一个重要缺口。方法本身比较直接，尽管其构件并不新颖，例如 normalizing flows，并且审稿人对作者的动机和叙事方式有一些保留意见，但审稿人认为该贡献对于希望将 flow-based model 用于 SAC-based RL 或 PPO 类算法的研究者来说会具有普遍实用价值。

**English:** There are still a few issues that need to be ironed out. If properly addressed, the reviewer is willing to raise quality from 3 to 4 and rating from 4 Borderline Accept to 5 Accept.

**中文：** 仍有一些问题需要解决。如果这些问题得到妥善回应，审稿人愿意将 quality 从 3 提高到 4，并将 rating 从 4 Borderline Accept 提高到 5 Accept。

### Strengths / 优点

**English:**

- Figure 1 provides a simple and useful overview that presents the authors' contributions at a glance. Figure 2 is also very clear in showing what the algorithm does.
- The preliminary section is clean and to the point, ending with a concrete problem statement in lines 94-96 that logically flows into the proposed method.
- The theoretical analysis in Section 3.2 leads to generally useful and straightforward results in Theorems 2 and 3: exact likelihoods, not accounting for numerical precision, and a much improved entropy estimator, although not exact. This formalization should benefit practitioners who want to use SAC-based RL with flow policies.
- DMC-average performance in Figure 3 is a strong result showing that the method works. Figure 4 shows a clear ablation on how well the new method approximates policy entropy on a non-trivial example compared to a near-exact value. Figure 5 is also insightful regarding the most important hyperparameters of the new method.

**中文：**

- Figure 1 提供了一个简单且有用的总览，能够一眼展示作者的贡献。Figure 2 也非常清楚地说明了算法在做什么。
- preliminary section 简洁且切中要点，并在 L94-96 以一个具体的问题陈述结束，自然引出所提出的方法。
- Section 3.2 的理论分析导出了 Theorem 2 和 Theorem 3 中一般有用且直接的结果：在不考虑数值精度的情况下，likelihood 是精确的；熵估计器有大幅改进，但并非完全精确。该形式化应当有益于希望将 flow policy 用于 SAC-based RL 的实践者。
- Figure 3 中 DMC 平均性能是一个强结果，说明方法有效。Figure 4 也清楚地展示了新方法在一个非平凡例子上相对于近似精确值能够多好地近似 policy entropy。Figure 5 对新方法最重要的超参数也给出了有洞察力的结果。

### Weaknesses - Intro and Motivation / 缺点 - 引言与动机

**English:** The paper's motivation relies too strongly on the claim that maximum entropy improves exploration, including in the title. This statement is too strong. Entropy regularization helps keep exploration alive, but it is not a direct exploration method like UCB or Bayes-adaptive methods. Maximum entropy methods preserve stochasticity in the policy but do not directly attempt to reduce epistemic uncertainty about the generative parameters. Geist et al. (2019) provides a direction for understanding maximum entropy methods through regularized MDPs, for example by smoothing the optimization landscape.

**中文：** 论文的动机过度依赖“最大熵提升探索”这一主张，包括标题也体现了这一点。审稿人认为该说法过强。熵正则化确实有助于保持探索的持续性，但它不是像 UCB 或 Bayes-adaptive methods 那样的直接探索方法。最大熵方法保留了策略中的随机性，但并不直接试图减少生成参数上的 epistemic uncertainty。Geist et al. (2019) 从 regularized MDPs 的角度提供了理解最大熵方法的方向，例如最大熵可能平滑优化景观。

**English:** The title and exploration framing would be more appropriate if the paper estimated the entropy of the state occupancy of the current policy and used that for informed exploration, but that would be a different paper. The copied review text appears to omit the exact formula for state occupancy entropy.

**中文：** 如果论文估计当前策略的 state occupancy entropy 并将其用于有信息的探索，那么标题和探索叙事会更贴切，但这将是另一篇论文。用户提供的评审文本中似乎缺失了对应的公式。

**English:** The first contribution in lines 62-64 is slightly too strong. The reviewer believes Equation 9 and Equation 13 imply exact log-likelihood evaluation, and entropy has an improved form as a consequence. However, entropy still requires marginalization over a variable in Equation 13, so a better term may be "unbiased" because the integrand error, namely inversion error sketched in Equation 7, has been removed.

**中文：** L62-64 中的第一项贡献表述略强。审稿人认为根据 Equation 9 和 Equation 13，log-likelihood evaluation 是精确的，而 entropy 因此获得了改进形式。然而，entropy 仍然需要对 Equation 13 中的某个变量做 marginalization，因此更好的术语可能是 “unbiased”，因为 Equation 7 中所示的 integrand error，即 inversion error，已经被消除了。

### Weaknesses - Method / 缺点 - 方法

**English:** The invertible affine transform trick through space expansion is core to the well-established normalizing flow framework, but normalizing flows are not mentioned in the manuscript. The reviewer points to Rezende and Mohamed (2015), Variational Inference with Normalizing Flows.

**中文：** 通过 space expansion 实现的可逆 affine transform 技巧是成熟 normalizing flow 框架的核心，但稿件中没有提到 normalizing flows。审稿人指出应参考 Rezende and Mohamed (2015) 的 Variational Inference with Normalizing Flows。

**English:** The explanation of the GENIEO algorithm in Section 3.3 is clear, but it buries or obscures the paper's contribution. The contribution revolves around the improved approximation of the flow policy, so it is unclear why a new algorithm setup is needed. The authors should modify Section 3.3 to guide the reader into why a new algorithm is derived.

**中文：** Section 3.3 对 GENIEO algorithm 的解释是清楚的，但它埋没或模糊了论文的贡献。该贡献围绕 flow policy 的改进近似展开，因此不清楚为什么需要一个新的算法设置。作者应修改 Section 3.3，引导读者理解为什么需要推导一个新算法。

### Weaknesses - Experiments / 缺点 - 实验

**English:** The presentation of Table 1 using bold face for the best GENIEO results is misleading and often wrong. The table reports mean plus or minus one standard deviation over 5 seeds. Even without accounting for multiple comparisons, most results do not show statistical significance by visual inspection; only AVG. DMC Suite seems statistically significant at about the 95% confidence level over the population. This posture is maintained throughout the main experiment section, for example lines 212-226.

**中文：** Table 1 用加粗表示 GENIEO 最优结果的呈现方式具有误导性，而且经常是不正确的。该表报告的是 5 个 seed 的均值加减一个标准差。即使不考虑 multiple comparisons，大多数结果从视觉上看也没有统计显著性；只有 AVG. DMC Suite 似乎在总体上达到约 95% 置信水平的统计显著性。主实验部分，如 L212-226，也持续使用了这种表达姿态。

**English:** The empirical results do not match the strength of the claims in the text. The results presentation and wording should be revised to be more honest. Depending on the authors' intended claim, they should either run more seeds, show proper confidence intervals, and clearly define what "best" means, or weaken the claims.

**中文：** 实验结果与正文中的强主张并不匹配。结果呈现和措辞应修改得更加诚实。根据作者希望达到的主张，应该要么运行更多 seeds、展示恰当的 confidence intervals，并清楚定义 “best” 的含义；要么削弱相关主张。

**English:** The conclusion in lines 227-230 on the main results has incorrect causality. The authors assume that the method explores better and therefore achieves better performance. A better statement would be: "our method that approximates the entropy better achieved higher performance."

**中文：** L227-230 关于主要结果的结论存在错误的因果表述。作者假设方法探索得更好，因此获得了更好性能。更合适的表述是：“我们更好地近似 entropy 的方法获得了更高性能。”

**English:** The ablation in Figure 4 misses comparison to the naive Euler inversion sketched in Equation 7, and also misses comparison to one or two comparative baselines used in the main results.

**中文：** Figure 4 的 ablation 缺少与 Equation 7 中 naive Euler inversion 的比较，也缺少与主结果中使用的一两个对比 baseline 的比较。

### Neutral Comments / 中性意见

**English:**

- The proof for Lemma 1 is nice to have but not really needed because it is a well-known result.
- The Section 3.3 title "generative MaxEnt RL and ..." is tautological because RL is already generative.
- Please enlarge the font sizes of Figure 3 plot ticks to make them comparable to the paper font size.
- Figure 3 is missing a non-flow MaxEnt baseline such as SAC with Gaussian policies. This would improve the empirical claim that flow-based modeling with improved entropy estimation helps over a simpler method.
- At some points, such as related work lines 271-273, the authors compare to Gaussian policies that admit exact entropy. However, in most continuous domains, the action domain is bounded. It is important to mention that the common tanh-squashed Gaussian does not admit exact entropy. Neither does the clipped Gaussian; only the truncated normal admits it, but that distribution is less commonly used.

**中文：**

- Lemma 1 的证明有当然更好，但并非真正必要，因为这是一个众所周知的结果。
- Section 3.3 的标题 “generative MaxEnt RL and ...” 有些同义反复，因为 RL 本身已经是 generative 的。
- 请放大 Figure 3 中坐标轴刻度的字号，使其与论文正文字号相当。
- Figure 3 缺少非 flow 的 MaxEnt baseline，例如带 Gaussian policies 的 SAC。这将加强经验主张，即带改进熵估计的 flow-based modeling 相比更简单的方法确实有帮助。
- 在论文某些位置，例如 related work L271-273，作者将方法与可精确计算熵的 Gaussian policies 进行比较。然而在大多数连续控制领域中，动作域是有界的。应当提到常见的 tanh-squashed Gaussian 并不具有 exact entropy，clipped Gaussian 也没有；只有 truncated normal 具有这一性质，但它并不那么常用。

### Questions / 问题

**English:**

1. Why is the coupled action called a "dummy" action? The term sounds like a placeholder value, which confused the reviewer because they initially thought it would be thrown away later, but it is not. Could the authors consider a better term?
2. For empirical validation, why did the authors not directly plug the new flow method into a well-known RL method like SAC or PPO? In other words, why is the new algorithm setup needed?
3. Could the authors modify Algorithm 1 with color coding, or through a side-by-side comparison, to contrast the new algorithm with SAC?

**中文：**

1. 为什么 coupled action 被称为 “dummy” action？这个术语听起来像是一个占位值，使审稿人一开始感到困惑，以为之后会把它丢弃，但实际上并没有。作者能否考虑一个更好的术语？
2. 在经验验证方面，为什么作者没有直接把新的 flow 方法接入一个众所周知的 RL 方法，如 SAC 或 PPO？换句话说，为什么需要新的算法设置？
3. 作者能否通过颜色标注或并排比较的方式修改 Algorithm 1，以突出新算法与 SAC 的对比？

### Limitations / 局限性

**English:** yes

**中文：** 有。

## Cross-Reviewer Themes / 三位审稿人的共同关注点

### 1. Computational overhead / 计算开销

**English:** Reviewer tShQ and Reviewer 4ynL both explicitly ask about training and inference overhead, especially whether doubling the latent or dummy action space creates meaningful computational cost.

**中文：** Reviewer tShQ 和 Reviewer 4ynL 都明确询问训练和推理阶段的计算开销，尤其是 latent 或 dummy action space 加倍是否会带来显著计算成本。

### 2. Exploration evidence and wording / 探索证据与表述

**English:** All three reviewers touch on exploration. tShQ asks for direct exploration evidence such as state space coverage. 4ynL asks for statistics or heatmaps and whether higher entropy reliably leads to meaningful exploration. BXmK argues that the paper overstates the link between maximum entropy and exploration, and suggests weakening causal language.

**中文：** 三位审稿人都涉及探索问题。tShQ 要求提供直接探索证据，例如 state space coverage。4ynL 要求提供统计量或 heatmaps，并询问更高 entropy 是否可靠地转化为有意义的探索。BXmK 则认为论文过度强调最大熵与探索之间的关系，并建议削弱因果表述。

### 3. Novelty relative to normalizing flows / 相对于 normalizing flows 的新颖性

**English:** Reviewer 4ynL and Reviewer BXmK both ask the authors to clarify novelty relative to space expansion, affine coupling, Real NVP, and normalizing flows. BXmK specifically notes that normalizing flows are not mentioned.

**中文：** Reviewer 4ynL 和 Reviewer BXmK 都要求作者澄清相对于 space expansion、affine coupling、Real NVP 和 normalizing flows 的新颖性。BXmK 特别指出稿件没有提到 normalizing flows。

### 4. Baselines and evaluation scope / Baseline 与评估范围

**English:** Reviewer 4ynL requests comparisons against SimbaV2, MAD-TD, BRO, and DMC Hard. Reviewer BXmK requests a non-flow MaxEnt baseline such as SAC with Gaussian policies, more careful statistical reporting, and additional comparisons in Figure 4.

**中文：** Reviewer 4ynL 要求与 SimbaV2、MAD-TD、BRO 和 DMC Hard 进行比较。Reviewer BXmK 要求加入非 flow 的 MaxEnt baseline，例如 Gaussian policy SAC，并希望更谨慎地报告统计结果，以及在 Figure 4 中增加额外比较。

### 5. Algorithm positioning / 算法定位

**English:** Reviewer BXmK asks why a new algorithm setup is needed instead of directly plugging the flow method into SAC or PPO, and suggests revising Section 3.3 and Algorithm 1 to better contrast with SAC.

**中文：** Reviewer BXmK 询问为什么需要新的算法设置，而不是直接将 flow 方法接入 SAC 或 PPO，并建议修改 Section 3.3 和 Algorithm 1，以更清楚地与 SAC 对比。

