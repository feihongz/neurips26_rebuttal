# 15978 Self-Adjoint Flow Policy Optimization — Rebuttal Outline

> Internal working document. Each reviewer section below is a separate response to be submitted through that reviewer's **Rebuttal** button. Keep each final response below 10,000 characters. Use plain text/Markdown only; do not upload files, include links, reveal identities, or imply that the submitted paper/supplement has been revised. The HTML comments mark places that should remain blank until new experimental results are available and must not be pasted into OpenReview.

## Technical guardrails shared by all responses

- Be precise about the numerical claim: an exactly inverted discrete GenPO map has a valid likelihood for its **own discrete policy**. SAFLOW's proved advantage is time symmetry and second-order fidelity to the corresponding learned continuous flow, not that GenPO's discrete likelihood is invalid.
- Describe augmented-space PPO control as **valid and conservative**, not pointwise equivalent to projected-action clipping.
- Distinguish evidence levels: Appendix C.4 establishes numerical order on a known system; Appendix C.2 compares first- and second-order rules in the same SAFLOW implementation; Appendix C.3 reports ratio dispersion. None alone proves that second-order accuracy necessarily causes higher return.
- When citing the eight-task table, say “highest reported mean,” not “statistically significant on every task.”

---

## Reviewer Gdko

### Opening

We thank the reviewer for recognizing the importance of bridging expressive generative policies and likelihood-based policy optimization, the methodological value of the self-adjoint Verlet construction, and the breadth of our eight-task IsaacLab evaluation. We also appreciate the specific suggestions on notation, related methods, high-dimensional efficiency, computational cost, sensitivity, and positioning relative to GenPO. We address each weakness and question in turn below.

### W1. Notation in the introduction: \(T,z,h,K\)

**Response outline**

- Acknowledge that the compact motivation paragraph introduces these symbols too early.
- Define them immediately in the response: \(z=(x,y)\in\mathbb R^{2d}\) is the augmented flow state, \(T\) is the integration horizon, \(K\) is the number of flow steps, and \(h=T/K\) is the step size; the experiments use \(T=1\).
- Clarify that “self-adjoint” refers to the time-indexed one-step identity \(\Psi_{h,t}^{-1}=\Psi_{-h,t+h}\), with the clock reversed during likelihood evaluation.

### W2. Missing RN-D comparison

**Response outline**

- Agree that RN-D is relevant as another expressive on-policy actor and that it tests whether gains over Gaussian PPO can arise from a richer policy family more generally.
- Explain the difference in scope: RN-D uses a discretized categorical actor, whereas SAFLOW studies a continuous, invertible generative policy and finite-step likelihood ratios.
- Point out that Appendix C.2 already provides the most direct isolation of the integrator: it keeps the SAFLOW architecture, objective, and training setup fixed and replaces only the second-order self-adjoint rule with the first-order alternating rule.
- Do not claim that this makes an RN-D comparison unnecessary; frame RN-D as complementary rather than an integrator-matched control.

**Additional RN-D result, if available**

<!-- EXPERIMENT RESULTS: leave blank until the RN-D comparison is complete. -->

### W3. Hard high-dimensional tasks and efficiency relative to PPO

**Response outline**

- Make explicit that the main evaluation already includes the three requested environments: H1 (state/action dimensions 256/19), Go2 (235/12), and Shadow Hand (157/20), and SAFLOW obtains the highest reported mean on each.
- Avoid implying that these returns answer the efficiency question. The submitted wall-clock study covers Ant and Humanoid, not the three requested tasks.
- Separate final return, sample efficiency, wall-clock time-to-threshold, throughput, and memory; only claim the quantities actually reported.
- State candidly that broader wall-clock and memory profiling is a limitation of the submitted evidence.

**High-dimensional wall-clock, memory, and time-to-threshold results**

<!-- EXPERIMENT RESULTS: leave blank until these measurements are complete. -->

### W4. Does the return gain justify the 23–32% overhead over GenPO?

**Response outline**

- Confirm rather than minimize the reported overhead: on Ant and Humanoid, SAFLOW takes approximately 32% and 23% more training time than GenPO, respectively.
- Attribute the overhead to the additional velocity-network evaluations in the palindromic update and likelihood computation.
- Refer to the already submitted performance-versus-normalized-time curves as the relevant evidence that the final-return advantage is not solely an artifact of comparing at unequal wall-clock budgets.
- Distinguish the use cases: SAFLOW targets settings where an expressive on-policy policy and improved finite-step continuous-flow fidelity are worth extra computation; Gaussian PPO remains preferable when wall-clock cost is the overriding constraint.
- Do not generalize the Ant/Humanoid trade-off to every task or claim that the overhead is universally justified.

### W5. Sensitivity to \(K\), \(\nu\), time embedding dimension, and hidden size

**Response outline**

- Clarify that Figure 4 in the submitted paper already studies all four requested choices on Ant:
  - \(K\in\{1,3,5,7,10\}\);
  - \(\nu\in\{0,0.01,0.1,0.5,1\}\);
  - time-embedding dimension in \(\{4,8,16,32\}\);
  - hidden size in \(\{32,64,128,256\}\).
- Summarize the qualitative conclusion only as strongly as the figure permits: performance is comparatively stable over the tested ranges, while very strong compression can reduce expressivity; \(\nu=0.01\) is used subsequently.
- Acknowledge that this sensitivity study is single-task and therefore does not establish cross-task robustness.

### W6. Novelty relative to GenPO and when second order matters

**Response outline**

- Scope the claim carefully. SAFLOW inherits the doubled-action augmented-MDP idea and likelihood-based on-policy framework from GenPO; classical Verlet integration itself is also not claimed as a new numerical method.
- Identify the paper-specific contribution as their combination: a palindromic kick-drift-kick policy map, the correct reverse-clock/negative-step inverse, second-order finite-step approximation of the learned continuous flow, propagation of that error order to continuous-flow likelihood ratios and the fixed-buffer PPO surrogate, and its controlled RL evaluation.
- Explain when the structure should matter most: coarse step sizes/small \(K\), rapidly varying or nonlinear learned velocity fields, and policy updates for which ratio/clipping behavior is sensitive to finite-step continuous-flow bias.
- Cite Appendix C.2 as the same-implementation first- versus second-order RL control and Appendix C.4 as the numerical-order verification.
- Acknowledge the task dependence: Figure 4(a)'s modest variation across \(K\) suggests that Ant is not strongly step-limited throughout the tested range.

### Q1. ReinFlow, SAC Flow, and MeanFlow

**Response outline**

- Thank the reviewer and position the methods directly, without links.
- ReinFlow is relevant as an invertible/normalizing-flow policy approach with tractable densities; its policy parameterization and training target differ from SAFLOW's doubled-action self-adjoint discretization for PPO.
- SAC Flow studies flow policies in an off-policy SAC-style setting, where likelihoods enter a different objective and the old/new on-policy ratio is not the central issue.
- MeanFlow is relevant to efficient generative action construction; although it is cited in the submission, the response should give it an explicit conceptual comparison rather than treating the citation as sufficient.
- State that these works broaden the landscape but do not provide the same controlled first- versus second-order comparison addressed here.

### Q2. Practical selection of the compression coefficient \(\nu\)

**Response outline**

- Explain its role: it discourages drift along projection fibers by encouraging \(x\) and \(y\) to remain close, but an overly large value can suppress useful policy expressivity.
- Report the submitted protocol: select \(\nu=0.01\) from the Ant sensitivity study and then keep it fixed across tasks rather than tuning per environment.
- Give a practical rule consistent with the evidence: start from a small positive value on a log scale, monitor the compression loss relative to the PPO objective and projected-action performance, and choose the smallest value that controls fiber drift without degrading return.
- State that an adaptive schedule was not evaluated and should not be presented as an established result.

---

## Reviewer sTxw

### Opening

We thank the reviewer for recognizing the importance of likelihood-tractable flow policies, the clarity of the presentation, the overall empirical support, and the numerical-order evidence from the time-varying toy system. We especially appreciate the questions about whether the toy advantage transfers to nonlinear RL, the precise novelty over GenPO, theoretical economy, and compute-matched comparisons. We address each point below.

### W1. Linear 2D toy versus high-dimensional nonlinear systems; small gap in Figure 4(a)

**Response outline**

- Clarify that Appendix C.4 and Figure 4(a) answer different questions. Appendix C.4 holds a known time-varying vector field fixed and measures first- versus second-order convergence to a continuous reference. Figure 4(a) retrains the second-order SAFLOW policy at different \(K\), so the learned field can adapt and no first-order curve appears there.
- Agree that the toy example establishes numerical order, not universal high-dimensional RL improvement.
- Point to Appendix C.2 as the closer practical test: within the same SAFLOW implementation, replacing only the second-order rule with the first-order alternating rule reduces return on Ant and Humanoid.
- Interpret Figure 4(a) conservatively: Ant appears not to be strongly flow-step-limited across the tested \(K\) range. Likelihood fidelity is therefore one factor, not necessarily the sole bottleneck.
- Avoid claiming that a dramatic asymptotic toy-error ratio should translate proportionally into return.

**Nonlinear high-dimensional reference-solver or degradation-curve results**

<!-- EXPERIMENT RESULTS: leave blank until these experiments are complete. -->

### W2. Modest novelty over GenPO; classical symmetric integration; Corollary 6

**Response outline**

- Agree on the proper scope: the augmented action construction and on-policy framework are inherited from GenPO, and the Verlet formula is classical.
- State that the contribution is not “inventing Verlet,” but constructing a usable self-adjoint generative policy around it and analyzing the consequences of this construction for a time-dependent learned flow, its likelihood ratio, and a fixed-buffer PPO objective.
- Highlight the controlled first-order substitution experiment as evidence specific to this algorithmic change.
- Agree that Corollary 6 is a central bridge, while avoiding a stronger claim than it proves: it gives an \(O(h^2)\) approximation to the corresponding continuous-flow ratio/surrogate under its assumptions; it does not by itself guarantee higher return.
- Explicitly avoid saying that GenPO's likelihood for its own discrete invertible map is incorrect.

### W3. Theorem 3 is nearly immediate from the definition

**Response outline**

- Agree that the algebraic proof is short because each shear is explicitly invertible and the composition is palindromic.
- Explain why the statement is still useful: exact reversibility is the prerequisite for tractable likelihood evaluation, and writing it separately distinguishes exact discrete inversion from the separate asymptotic approximation result in Theorem 4.
- Give the precise nonautonomous identity, \(\Psi_{h,t}^{-1}=\Psi_{-h,t+h}\), to make clear that reverse clock indexing—not theorem length—is the substantive detail.
- Do not portray Theorem 3 itself as a deep convergence result.

### Q1. Is likelihood accuracy a bottleneck on Ant? Requested degradation curves

**Response outline**

- Answer directly: the weak dependence on \(K\) in Figure 4(a) suggests that discretization accuracy is not the dominant bottleneck for Ant over that tested range; it does not show that accuracy is irrelevant in general.
- Explain that performance also depends on representation, optimization, rollout noise, clipping, and the learned field's ability to adapt to the solver.
- Note that the exact symbol following “when” is absent from the review text; interpret the request as varying solver difficulty/coarseness or rollout difficulty, and state this interpretation briefly.

**SAFLOW-versus-GenPO degradation curves**

<!-- EXPERIMENT RESULTS: leave blank until the requested curves are complete. -->

### Q2. GenPO with doubled flow steps and computational cost

**Response outline**

- Agree that equal nominal \(K\) is not a compute-matched comparison. Before implementation effects, one SAFLOW step uses three velocity evaluations, whereas a first-order alternating GenPO step uses two.
- Separate three comparisons: equal integration steps, equal velocity-network evaluations, and equal wall-clock time.
- Use the submitted Table 4 only for the comparison it supports: SAFLOW is approximately 32%/23% slower than GenPO on Ant/Humanoid at the reported settings.
- Do not infer the outcome of doubled-step GenPO without data.

**Doubled-step and compute-matched GenPO results**

<!-- EXPERIMENT RESULTS: leave blank until these comparisons are complete. -->

---

## Reviewer pw8T

### Opening

We thank the reviewer for recognizing the importance of the problem, the elegance and motivation of the self-adjoint update, the breadth of the theoretical and empirical evaluation, and the usefulness of the ablations. We agree that the augmented/projected policy relationship, GenPO++, computational cost, compression, and the link from numerical consistency to RL optimization deserve especially precise answers. We address each concern and question individually below.

### C1 / Q2. Does dummy-action control imply meaningful real-action control?

**Response outline**

- First concede the key distinction: the augmented and projected likelihood ratios are not pointwise equal, and Theorem 1's optimal-value equivalence alone does not prove equivalence of PPO clipping.
- Give the exact relationship. With old augmented policy \(P\), new augmented policy \(Q\), projection \(M\), and \(r_{\widetilde{\mathcal A}}=dQ/dP\), the executed-action ratio satisfies
  \[
  r_{\mathcal A}(a)=\mathbb E_P\!\left[r_{\widetilde{\mathcal A}}(\tilde a)\mid M(\tilde a)=a\right].
  \]
- State the consequence from data processing: KL, total variation, and general \(f\)-divergences cannot increase under \(M\). Thus a genuine augmented-space trust region conservatively controls the projected policy.
- Explain that the unclipped importance-weighted surrogate is exactly preserved because reward, transition, and the exact augmented advantage depend on \(\tilde a\) only through \(M(\tilde a)\).
- For clipping, state the precise limitation and conservative result. The clipped PPO integrand is concave in the ratio, so conditional Jensen gives \(L_{\mathrm{clip}}^{\mathrm{aug}}\le L_{\mathrm{clip}}^{\mathrm{proj}}\) under the fiber-constant advantage. Augmented clipping can therefore penalize fiber-only changes that do not alter the executed action.
- Conclude with the correct claim: augmented clipping is valid and conservative, not pointwise equivalent; the compression term is intended to reduce null-fiber drift but does not eliminate the Jensen gap by theorem.

**Projected/augmented KL, clip fraction, and fiber-change measurements**

<!-- EXPERIMENT RESULTS: leave blank until these measurements are complete. -->

### C2 / Q1. Missing GenPO++ comparison and positioning

**Response outline**

- Treat GenPO++ as highly relevant concurrent work and make no priority claim.
- Compare the mechanisms directly: SAFLOW uses two full action registers, explicit volume-preserving shears, and a fixed second-order palindromic rule; GenPO++ targets reversible/high-order likelihood-ratio computation in the original action dimension without dummy-action augmentation.
- Clarify SAFLOW's distinct focus: a simple explicit self-adjoint policy map, an augmented-MDP PPO construction, second-order continuous-flow/ratio analysis, and a controlled replacement of GenPO's first-order integrator.
- Acknowledge GenPO++'s attractive axes—no doubled action representation and potentially higher order—rather than implying dominance without evidence.
- If a faithful, compute-matched implementation is unavailable during rebuttal, keep the response conceptual and say so; do not invent an empirical comparison.

**SAFLOW-versus-GenPO++ results, if available**

<!-- EXPERIMENT RESULTS: leave blank until a fair comparison is complete. -->

### C3 / Q4. Wall-clock and memory trade-off

**Response outline**

- Surface the existing numbers: Table 4 reports approximately 32% and 23% wall-clock overhead over GenPO on Ant and Humanoid; the submitted performance-versus-time curves show the corresponding return trajectories.
- Explain the source of overhead in velocity-network evaluations and distinguish it from environment-simulation cost.
- State that the submitted evidence does not report memory or a GenPO++ timing comparison and covers only two tasks.
- Present the practical trade-off conditionally: SAFLOW is aimed at cases where return/sample-efficiency gains justify additional actor computation; it is not a universal replacement for low-cost Gaussian PPO/TRPO.

**Memory, throughput, and GenPO++ timing results**

<!-- EXPERIMENT RESULTS: leave blank until these measurements are complete. -->

### C4 / Q5. Does second-order consistency improve RL optimization?

**Response outline**

- Separate the submitted evidence into three levels:
  1. Appendix C.4 verifies first- versus second-order convergence to a continuous reference on a known time-varying system.
  2. Appendix C.2 changes only the integrator within the same SAFLOW implementation and reports higher Ant/Humanoid return for the second-order rule.
  3. Appendix C.3 reports lower likelihood-ratio dispersion during training.
- State the limitation explicitly: lower ratio standard deviation is not itself an accuracy certificate or a causal explanation of return, and Corollary 6 does not guarantee policy improvement.
- Clarify the conceptual target: both exactly inverted schemes have valid likelihoods for their own discrete policies; SAFLOW reduces finite-step bias relative to the corresponding continuous flow and imposes time symmetry.
- Avoid claiming a demonstrated correlation unless the requested statistics have actually been computed.

**Ratio error, projected KL, clipping, and return-correlation results**

<!-- EXPERIMENT RESULTS: leave blank until these analyses are complete. -->

### Q3. Compression sensitivity and an adaptive schedule

**Response outline**

- Explain that \(\nu\) controls a real trade-off: it discourages changes in the projection null space, but in a finite parameterized policy and clipped PPO update it also changes the optimization objective.
- Point to the submitted Ant sweep \(\nu\in\{0,0.01,0.1,0.5,1\}\), with \(0.01\) selected and then fixed across all tasks.
- Give the idealized theoretical qualification: over unrestricted stochastic policies, a nonnegative compression penalty does not lower the optimal control value because every original policy has a zero-penalty diagonal lift \((a,a)\); this does not establish equivalence for a finite SAFLOW class or each PPO update.
- Describe an adaptive schedule as a plausible future direction, not an evaluated solution.

**Cross-task sensitivity or adaptive-schedule results**

<!-- EXPERIMENT RESULTS: leave blank until these experiments are complete. -->

---

## Reviewer h1HA

### Opening

We thank the reviewer for recognizing the strength and diversity of the experiments, the significance of numerical structure for likelihood-based generative policy optimization, and the clarity of the overall problem and method. We especially appreciate the careful scrutiny of Theorems 1 and 4 and the question of whether doubling the action space is necessary. These comments identify places where assumptions and scope were stated too tersely. We address each concern below.

### T1-a. The averaging projection may leave the action space

**Response outline**

- Agree that the arithmetic projection requires \(M(\mathcal A\times\mathcal A)\subseteq\mathcal A\); convexity is sufficient and midpoint closure is the minimal relevant condition.
- Give the more general theorem form: the value-equivalence argument only requires a measurable surjection \(M:\widetilde{\mathcal A}\to\mathcal A\) with a measurable right inverse \(i\), where \(M\circ i=\mathrm{id}\). For averaging, \(i(a)=(a,a)\).
- State exactly which space the practical flow and environment mapping use—pre-squash, bounded box, clipping, or squashing—so that the support of the Gaussian-generated \(\mathbb R^{2d}\) variable is not conflated with \(\mathcal A\times\mathcal A\).

<!-- IMPLEMENTATION DETAIL TO VERIFY: specify the exact action squashing/clipping convention before finalizing. -->

### T1-b. The theorem does not account for compression regularization

**Response outline**

- Agree on scope: Theorem 1, as stated, concerns the unregularized control problem over all stochastic policies; it does not prove that the practical clipped update is unchanged by compression.
- Give the limited ideal result that is available. For a regularized return \(\widetilde J_\nu=J-\nu\mathbb E\sum_t\gamma^t\|x_t-y_t\|^2\), the supremum over unrestricted augmented policies still equals the original optimum: the penalty is nonnegative and every original policy has the zero-cost diagonal lift \((a,a)\).
- State the limitation: the diagonal lift can be singular and need not lie exactly in the finite diffeomorphic SAFLOW family; compression can therefore affect the attainable marginal policy and training dynamics in practice.
- Do not use optimal-value preservation to claim equivalence of every finite-parameter PPO update.

### T4-a. Time-dependent velocity, BCH, and missing time conditioning

**Response outline**

- Agree that suppressing the time index made both inversion and the convergence argument incomplete as written.
- State the precise inverse identity:
  \[
  \Psi_{h,t}^{-1}=\Psi_{-h,t+h},
  \]
  so the reverse pass starts at \(t_{k+1}\) and evaluates the same field at endpoint/midpoint times in reverse order.
- Make the nonautonomous analysis autonomous by introducing \(u=(x,y,t)\) and
  \[
  X=(v_\theta(y,t;s),0,0),\qquad
  Y=(0,v_\theta(x,t;s),0),\qquad
  D=(0,0,1).
  \]
- Explain that Equation (3) is the five-stage palindromic splitting
  \[
  X_{h/2}D_{h/2}Y_hD_{h/2}X_{h/2}.
  \]
  The two clock subflows generate the midpoint and endpoint time conditioning used by the algorithm.
- BCH now applies to autonomous Lie operators on the extended state, giving a local \(O(h^3)\) defect; stability plus a discrete Grönwall argument over \(K=T/h\) steps gives global \(O(h^2)\), rather than merely multiplying local errors without a stability bound.
- List the required scope assumptions: a common compact trajectory neighborhood, uniformly bounded sufficiently high derivatives of \(v_\theta\) in state and time, and uniform stability over the fixed horizon.

### T4-b. Extension to the local Jacobian

**Response outline**

- Supply the missing construction rather than saying “the same argument applies.” For any extended vector field \(G\), use its tangent lift
  \[
  \widehat G(u,\Xi)=(G(u),DG(u)\Xi).
  \]
  The derivative of each split subflow is exactly the corresponding tangent-lift flow.
- Apply the same palindromic splitting and stability argument to \(\widehat X,\widehat Y,\widehat D\) to obtain the global \(C^1\) error \(O(h^2)\), under the stronger derivative bounds required by the lift.
- Add the SAFLOW-specific simplification relevant to likelihood: every discrete shear has a block-triangular Jacobian with unit diagonal, and the continuous crossed field has zero divergence. Hence both maps have determinant one exactly. The likelihood-consistency result can therefore be obtained from the inverse-state error and local Lipschitz continuity of \(\log p_0\); the tangent-Jacobian result is a stronger separate statement, not the only route to likelihood consistency.

### Core theoretical claim: what is and is not established

**Response outline**

- State narrowly that the repaired extended-time/tangent-lift argument establishes second-order approximation to the corresponding learned continuous flow on compact sets under the stated smoothness assumptions.
- State that Corollary 6 transfers this finite-step order to the continuous-flow likelihood ratio and a fixed-buffer PPO surrogate under uniform boundedness assumptions.
- Do not infer monotonic return improvement or claim that an asymmetric but exactly invertible discrete GenPO policy has an invalid likelihood.
- Frame the empirical first-/second-order ablation as supporting evidence, not a substitute for the mathematical assumptions.

### Q2-a. Is a \(2d\) augmented action space necessary?

**Response outline**

- Answer directly: it is not mathematically necessary for every possible self-adjoint flow. It is a sufficient design choice for the specific construction in this paper.
- Explain its benefits without claiming uniqueness: two full \(d\)-dimensional registers let every shear update an entire action-sized vector conditioned on another entire action-sized vector; the update is explicit, invertible without an implicit solve, symmetric between registers, and works uniformly for \(d=1\) and odd \(d\).
- Explain the projection choice: averaging the two registers preserves exchange symmetry and maps a diagonal pair \((a,a)\) back to \(a\).
- Acknowledge the cost: augmentation introduces a null fiber and motivates compression; it also increases actor representation and computation.

### Q2-b. Why not split the original \(d\)-dimensional action into two blocks?

**Response outline**

- Agree that block-split additive coupling can also form reversible/self-adjoint maps; do not state that it is impossible.
- Explain the design trade-offs: it creates unequal or empty blocks for small/odd dimensions, gives each substep only a coordinate subset, introduces partition asymmetry, and may require permutations/multiple masks to communicate across all coordinates.
- Contrast this with SAFLOW's two full registers and shared action-sized velocity field, while acknowledging that the submission does not prove this choice optimal.
- Separate intuition from performance attribution: the current experiments compare integration rules within the augmented construction but do not isolate doubled augmentation against a well-tuned non-augmented block-split alternative.

**No-augmentation or block-split ablation results**

<!-- EXPERIMENT RESULTS: leave blank until this comparison is complete. -->

### Originality relative to GenPO

**Response outline**

- Agree with the reviewer's attribution: the augmented control formulation and much of the likelihood-based flow-policy framework build directly on GenPO, and Verlet is classical numerical analysis.
- State the scoped originality: instantiating a palindromic self-adjoint policy map in this framework; handling the reverse clock for a time-conditioned learned field; proving second-order continuous-flow, ratio, and fixed-buffer-surrogate consistency under explicit assumptions; and empirically isolating the first- versus second-order update.
- Avoid describing every component of SAFLOW as new or claiming that time symmetry alone proves the observed return gains.

