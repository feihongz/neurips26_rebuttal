# Submission 10722 — Author Response Framework

> **Internal working draft. Do not paste this note into OpenReview.**
>
> - Post each reviewer section separately using that review's **Rebuttal** button.
> - Keep each posted response below 10,000 characters.
> - Remove every `[TO FILL]`, `[VERIFY]`, and internal note before posting.
> - Do not include links, attachments, identities, institutions, repository details, or promises to revise/upload the paper.
> - Use the response to clarify the original submission and report verified numerical results directly in text or Markdown tables.
> - Prefer “we clarify,” “the intended scope is,” and “we acknowledge” over “we revised/added.”

---

## Rebuttal to Reviewer qUFY

Thank you for the careful review and for recognizing the motivation of using attractive and repulsive drift fields, the adaptation to online RL, and the strong numerical results on both DMC and HumanoidBench. We address the concerns about critic non-stationarity, component complexity, hyperparameter selection, and computational cost below.

### 1. Scope of the Langevin analysis and robustness to a non-stationary critic

We agree that the learned critic is non-stationary across online RL training and can be inaccurate early in training. Theorem 1 is not intended as a convergence result for the complete online actor–critic process. Its scope is conditional and local: for a fixed state and a local basin, assuming bounded critic-gradient error, it shows geometric contraction of the initialization-dependent term toward a residual neighborhood. In particular, the nonzero terms involving the critic-gradient error and the finite Langevin step size mean that the theorem does **not** establish exact \(W_2\to0\) convergence under fixed nonzero error and step size.

During each finite Langevin refinement inner loop, the critic parameters are held fixed. Across outer online updates, the critic changes, so the theorem should be interpreted as characterizing a single local refinement step rather than a stationary global target throughout training. We therefore do not use it to claim convergence of the full online RL procedure.

The practical question is whether critic noise makes the positive or negative guidance unreliable. We will answer this directly with quantitative robustness results in the discussion:

**[TO FILL — critic robustness results]**

| Setting | Task(s) | Return / IQM | Relative change |
|---|---:|---:|---:|
| Default DADC | [ ] | [ ] | — |
| Longer/shorter critic warm-up | [ ] | [ ] | [ ] |
| Target critic for anchor ranking/guidance | [ ] | [ ] | [ ] |
| Added critic-value/gradient noise | [ ] | [ ] | [ ] |
| Delayed activation of the repulsive branch | [ ] | [ ] | [ ] |

**[TO FILL — one or two sentences interpreting whether degradation is gradual and whether early-training instability is observed.]**

### 2. Number of components and what is used at inference

The prior network, anchor generation, Q-filtering, and Langevin refinement are training-time mechanisms. Environment interaction and evaluation use only the learned actor. Thus, the additional components increase training cost but do not require iterative flow or Langevin sampling at deployment.

The roles of the principal quantities are:

- \(\alpha\): strength of the drift-imitation constraint relative to local Q maximization;
- \(\omega\): relative strength of negative-anchor repulsion;
- number of flow steps: fidelity/cost trade-off for the positive prior;
- number of candidate anchors: coverage of candidate action modes;
- Langevin step size and number of steps: magnitude and cost of local positive-anchor refinement.

**[VERIFY before posting: Were the same default hyperparameters used for every reported task? Were any task-specific exceptions used?]**

Our selection protocol was **[TO FILL: e.g., one shared configuration across all tasks / a small predefined sweep on specified development tasks]**. The final reported defaults were **[TO FILL with verified values]** and were not selected independently from each test seed.

**[TO FILL — sensitivity results]**

| Hyperparameter | Values tested | Task(s) | Main observation |
|---|---|---|---|
| \(\alpha\) | [ ] | [ ] | [ ] |
| \(\omega\) | [ ] | [ ] | [ ] |
| Flow steps | [ ] | [ ] | [ ] |
| Candidate anchors | [ ] | [ ] | [ ] |
| Langevin step size/steps | [ ] | [ ] | [ ] |

The intended practical rule is to choose the smallest flow/anchor configuration whose performance is stable, because these quantities affect training cost but not actor inference cost. **[TO FILL with the empirically supported stable ranges and selection recommendation.]**

### 3. Computational complexity, training throughput, and inference latency

Let \(M_+\) and \(M_-\) denote the positive- and negative-candidate counts, \(L\) the number of flow integration steps, and \(J\) the number of Langevin refinement steps. The additional training work scales linearly with \(M_+L\), \(M_-\), and \(J\) through batched flow/critic evaluations. These operations are parallelized over anchors. Inference uses one actor forward pass and is independent of \(M_+\), \(M_-\), \(L\), and \(J\).

**[TO FILL — measured cost on identical hardware and software settings]**

| Method | Training steps/s | Wall-clock per run | Peak GPU memory | Inference latency, batch 1 | Inference latency, batch [ ] |
|---|---:|---:|---:|---:|---:|
| DADC | [ ] | [ ] | [ ] | [ ] | [ ] |
| FlowRL | [ ] | [ ] | [ ] | [ ] | [ ] |
| SAC | [ ] | [ ] | [ ] | [ ] | [ ] |
| [other requested benchmark] | [ ] | [ ] | [ ] | [ ] | [ ] |

**[TO FILL — time-to-return comparison if available.]**

In short, the method trades additional batched training computation for a direct actor at inference. We appreciate the reviewer’s request because both sides of this trade-off are important for assessing practical usefulness.

---

## Rebuttal to Reviewer 4kU9

Thank you for the detailed and technically careful review. We appreciate the positive assessment of the motivating Naive Drift comparison, the clarity of the gradient decomposition, and the originality of constructing positive and negative anchors through separate actor/prior roles. We address the theoretical scope, policy-improvement question, meaning of decoupling, negative-anchor validity, and empirical protocol point by point.

### 1. What Theorem 1 does and does not establish

We agree that Assumption 2 is a strong conditional assumption in online deep RL. The theorem does not derive bounded critic-gradient error from policy iteration, nor do we assume that generic nonlinear off-policy policy iteration automatically guarantees critic convergence. Rather, the bounded-error condition is explicit: **if** the learned critic gradient remains within that error level in a local basin, the bound quantifies how this error affects the positive-anchor refinement.

The reviewer is also correct that the residual terms do not vanish for fixed nonzero critic error and Langevin step size. The intended conclusion is geometric contraction of the initialization-dependent term **to a residual neighborhood**, not exact convergence to the target distribution. As \(k\) grows, the bound approaches a radius controlled by critic-gradient error and discretization error. The theorem therefore analyzes a conditional finite/local sampler refinement, not global convergence of online DADC, the critic, or the optimal policy.

During each Langevin inner loop the critic is fixed; its non-stationarity occurs across outer training updates. Consequently, the theorem should not be read as asserting a single stationary energy landscape throughout online training. A full time-varying actor–critic convergence theorem is outside the claim supported by this analysis.

**[OPTIONAL TO FILL — empirical measurement of critic/target drift or anchor-Q improvement over Langevin steps.]**

| Measurement | Early training | Mid training | Late training |
|---|---:|---:|---:|
| Mean Q before refinement | [ ] | [ ] | [ ] |
| Mean Q after refinement | [ ] | [ ] | [ ] |
| Critic/target disagreement | [ ] | [ ] | [ ] |
| Anchor displacement | [ ] | [ ] | [ ] |

### 2. Does Equation 9 guarantee policy improvement?

No monotonic policy-improvement guarantee is claimed by Equation 9 itself. It is a practical surrogate combining local critic-based value ascent with a stop-gradient drift target. Theorem 2 decomposes the resulting update direction into local Q guidance, positive-anchor attraction, and negative-anchor repulsion; it does not prove monotonic improvement of the true return \(J(\pi)\), critic convergence, or convergence of the complete actor–critic iteration.

We agree that the Q-gradient term alone is local exploitation/value ascent rather than a formal exploration guarantee. The broader action coverage comes from stochastic multimodal action generation and guidance by anchors generated through a separate prior; it should not be attributed to the local Q-gradient alone.

**[TO FILL — if available, report a conservative-update or step-size sensitivity experiment; otherwise omit this placeholder entirely.]**

### 3. Precise meaning of “decoupled”

“Decoupled” refers to **sample-source and parameter-role decoupling**, not independence from the critic:

- positive candidates are produced by the separately parameterized flow prior trained from replay data and then locally refined;
- negative candidates are drawn from the current environment actor and ranked by the critic;
- the environment actor is optimized against the resulting fixed drift target.

The motivation is to avoid constructing both positive and negative sets from the same current-actor candidate distribution, which can make their empirical fields highly symmetric and weak. The method does not remove the use of \(Q\), and it does not claim that the sampler is statistically independent of online critic non-stationarity. We agree that this distinction is important.

### 4. Meaning and validity of negative anchors; possible OOD guidance

The term “negative” is operational: these are the **critic-ranked lower-value actions among candidates from the current actor for the same state**. They are not asserted to be ground-truth globally low-return actions. Sampling them from the current actor keeps the negative candidates within the current policy’s support, while Q-ranking targets relatively unfavorable modes represented by that actor.

The reviewer is correct that critic mis-ranking can make this signal unreliable, especially early in training. Moreover, Q-guided refinement of positive candidates can move them away from the replay distribution. The safeguards used in the original procedure are **[VERIFY: flow-prior initialization, small finite refinement steps, action-domain clipping/projection, delayed activation, target/twin critic]**; none of these turns learned Q-values into ground truth.

We therefore evaluate the operational validity directly:

**[TO FILL — negative-anchor and OOD diagnostics]**

| Diagnostic | Result |
|---|---:|
| Correlation between critic ranking and rollout/held-out return | [ ] |
| Critic disagreement on selected negatives | [ ] |
| Distance of refined positives from initial flow candidates/replay support | [ ] |
| Full DADC vs no-negative branch | [ ] |
| Q-filtered vs random negatives | [ ] |
| Bottom fraction 0% / 25% / 50% | [ ] |

These results should be interpreted as empirical validation of critic-ranked anchors, not as a guarantee that every selected action is truly suboptimal.

### 5. Contemporary baselines and standardized evaluation

We agree that DACERv2 and DIME are important contemporary comparisons and that aggregate statistics should not rely only on per-task mean and standard deviation.

**[TO FILL — verified new comparison; do not include a method without completed runs under the same protocol.]**

| Method | DMC IQM [95% CI] | HumanoidBench IQM [95% CI] | Seeds | Interaction budget |
|---|---:|---:|---:|---:|
| DADC | [ ] | [ ] | [ ] | [ ] |
| DACERv2 | [ ] | [ ] | [ ] | [ ] |
| DIME | [ ] | [ ] | [ ] | [ ] |
| FlowRL | [ ] | [ ] | [ ] | [ ] |
| SAC | [ ] | [ ] | [ ] | [ ] |

**[TO FILL — whether stratified bootstrap/IQM changes the ranking or uncertainty of the main conclusion.]**

All methods in this comparison use **[TO FILL: identical environment steps, evaluation frequency/episodes, observation/action preprocessing, and seed protocol]**. Hyperparameters were taken from **[TO FILL: official defaults / a common tuning budget]**, with the following fairness controls:

**[TO FILL — concise baseline configuration table or prose, with no links.]**

### 6. Task-subset rationale

The selected DMC tasks were intended to cover multiple morphologies (dog, humanoid, quadruped, and walker) and multiple coordination regimes (standing, walking, trotting, and running). The HumanoidBench subset was intended to add whole-body balance, navigation/sitting, crawling, and reaching.

**[VERIFY before posting: Was this task set fixed before observing DADC results? What exact selection rule and compute constraint were used?]**

The selection was **[TO FILL with the truthful pre-specified rationale]** rather than based on choosing tasks where DADC performed best. **[If this cannot be supported, replace this sentence with an explicit acknowledgement of the subset limitation.]**

### 7. Originality and contribution relative to prior components

We agree that advantage weighting and Langevin refinement are individually established tools. The claimed contribution is not either component in isolation. It is the online-RL construction that assigns separate roles to a replay-trained positive prior and current-actor negative candidates, uses critic filtering to construct an explicit repulsive drift field, and trains a direct environment actor against the combined field. The component ablations below are intended to determine whether this combination, especially the negative branch, contributes beyond the constituent techniques.

**[TO FILL — point to the no-positive/no-negative/base/full results reported directly in this response.]**

### 8. Limitations

We acknowledge the following boundaries of the original submission:

- Theorem 1 is conditional and local and yields a residual-neighborhood bound.
- Equation 9 does not guarantee monotonic policy improvement.
- No general convergence result is provided for the nonlinear off-policy critic or the full actor–critic loop.
- Decoupling concerns the construction paths and network roles, not independence from the learned Q-function.
- Bottom-\(K\) actions are critic-ranked relative negatives, and their quality depends on critic calibration.
- Conclusions about empirical superiority should be conditioned on the compared baselines and evaluation protocol.

We appreciate the reviewer for prompting us to make these distinctions explicit.

---

## Rebuttal to Reviewer MeUK

Thank you for the thoughtful review and for recognizing the importance of explicitly using low-value actions, the potential value of repulsive guidance, and the strong performance across DMC and HumanoidBench. We agree that the main empirical question is component attribution: whether the gains come from the base objective, positive-prior construction, Langevin refinement, negative repulsion, or their combination.

### 1. Are positive and negative anchors constructed for the same state?

Yes. For each replay state \(s_i\) in a minibatch, both sets are conditional on that same state:

\[
P_i^+\sim P^+(\cdot\mid s_i),\qquad
P_i^-\sim P^-(\cdot\mid s_i).
\]

They differ in action source, not in conditioning state. Positive candidates are generated by the separate flow prior and refined using Q guidance; negative candidates are sampled from the current actor for \(s_i\) and filtered by their Q-values. This same-state construction makes the attractive and repulsive displacements comparable in the action space associated with \(s_i\).

### 2. Exact definition of the Naive Drift control

The Naive Drift control constructs both sets from the current actor for the same state: it samples current-actor candidate actions and separates relatively high-Q and low-Q subsets to form positive and negative anchors. It does not use the independently trained flow prior or the flow-initialized Q-guided Langevin positive construction. DADC’s intended difference is therefore the decoupled source of positive anchors, together with their refinement, while retaining current-actor low-Q candidates for repulsion.

**[VERIFY before posting: candidate counts, high/low split, whether the actor objective and all other optimization settings were exactly matched.]**

The controlled implementation used **[TO FILL exact candidate counts, split, objective, seeds, and confirmation that all other settings were held fixed]**.

### 3. Direct component attribution

We agree that comparing Q-filtered negatives only with random negatives does not by itself establish that repulsion is beneficial relative to no repulsion. The following factorial ablation isolates each branch:

**[TO FILL — run on Dog Run and at least one additional task with distinct morphology/dynamics.]**

| Variant | Positive prior | Langevin | Negative repulsion | Max-Q | Dog Run | Additional task: [ ] |
|---|---|---|---|---|---:|---:|
| Full DADC | Yes | Yes | Q-filtered | Yes | [ ] | [ ] |
| No negative branch | Yes | Yes | No | Yes | [ ] | [ ] |
| No positive branch | No | No | Q-filtered | Yes | [ ] | [ ] |
| Max-Q only | No | No | No | Yes | [ ] | [ ] |
| Positive branch only | Yes | Yes | No | [VERIFY] | [ ] | [ ] |
| Negative branch only | No | No | Q-filtered | [VERIFY] | [ ] | [ ] |
| No Langevin | Yes | No | Q-filtered | Yes | [ ] | [ ] |
| Random negatives | Yes | Yes | Random | Yes | [ ] | [ ] |
| Naive Drift | Current actor | No | Q-filtered | [VERIFY] | [ ] | [ ] |

**[TO FILL — mean ± uncertainty, number of seeds, and a concise conclusion identifying which component contributes most.]**

### 4. Generalization of the ablation conclusion

We chose **[TO FILL additional task]** because it differs from Dog Run in **[TO FILL morphology, action dimension, reward structure, or manipulation/locomotion regime]**. The same component ordering is **[TO FILL: preserved / partly preserved / not preserved]**:

- Effect of removing the positive branch: **[ ]**
- Effect of removing the negative branch: **[ ]**
- Effect of removing Langevin refinement: **[ ]**
- Q-filtered versus random negatives: **[ ]**

If the conclusion differs across tasks, we will state that directly rather than generalizing from Dog Run.

### 5. Which components remain active in Figures 4(c) and 4(d)?

**[VERIFY these statements against the exact experimental configurations before posting.]**

- In Figure 4(c), “without Langevin” retains the negative branch with Q-filtering; only positive-anchor Langevin refinement is removed.
- In Figure 4(d), “without Q-value” retains the full positive branch, including Langevin refinement; the four negative anchors are selected randomly rather than by bottom-Q ranking, keeping the negative-anchor count fixed.

Thus, these plots were intended as one-factor comparisons, but we agree that the active components should be stated explicitly in the response.

### 6. Negative-sample fraction and repulsive coefficient

To separate the amount of negative data from the strength of repulsion, the negative fraction should first be varied while holding \(\omega\) fixed, followed by a separate \(\omega\) sensitivity analysis.

**[TO FILL — restore the exact fraction/coefficient requested in the original rendered review before completing this table.]**

| Bottom fraction | Number selected / candidates | Fixed \(\omega\) | Dog Run | Additional task: [ ] |
|---:|---:|---:|---:|---:|
| 0% | 0 / [ ] | [ ] | [ ] | [ ] |
| 25% | [ ] / [ ] | [ ] | [ ] | [ ] |
| 50% | [ ] / [ ] | [ ] | [ ] | [ ] |

**[TO FILL — separate \(\omega\) sensitivity, if available.]**

### 7. Defaults, terminology, and presentation

For clarity, the default values used in the reported ablations are:

- flow integration steps: **[VERIFY: 5]**;
- positive candidates/anchors: **[VERIFY: 16 and clarify whether this is the candidate or final refined count]**;
- negative candidates and selected fraction: **[VERIFY: \(M=16,K=4\)]**;
- Langevin step size and refinement steps: **[VERIFY: \(0.02\), 4]**;
- drift-imitation coefficient \(\alpha\): **[VERIFY: 1.0]**;
- repulsive coefficient \(\omega\): **[VERIFY exact value used in the reported experiments]**.

The symbol \(\omega\) denotes the relative strength of the repulsive field. The phrase “flow drift coefficient” is an imprecise label for this role; the intended meaning in the method is the repulsive coefficient.

We also agree that marking defaults and enlarging the environment-detail figures would improve readability. Because the response period does not permit revised figures or supplementary files, we provide the relevant defaults and experimental controls directly above rather than uploading modified plots.

We appreciate the reviewer’s focus on causal attribution. The no-positive/no-negative factorial ablations are the most direct test of the paper’s central claim, and the additional-task results determine how broadly the Dog Run conclusion generalizes.
