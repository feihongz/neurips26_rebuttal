Dual-ADC (Drift-only) minimal code subset

This repository keeps only the core algorithm modules of Dual Actor Drift Critic (Dual-ADC) for online continuous-control RL.
It is a semi-open release focused on method logic, not a full training pipeline.

Method sketch
- Decoupled sample construction:
  - Positive set P+: sampled from a flow prior, then refined by Q-guided Langevin updates.
  - Negative set P-: sampled from the current actor policy and then Q-filtered to retain low-value repulsive anchors.
- Drift field:
  - Attractive force from high-value positive anchors.
  - Repulsive force from low-value negative anchors.
- Actor objective:
  - Max-Q exploration term + drift-constraint exploitation term.

Code mapping
- Critic and training loop: `model/algo.py`
- Flow prior and multimodal actor: `model/model.py`
- Drift vector field utilities: `model/utils.py`

Implementation note
- This code follows the Dual-ADC design in spirit and mechanism.
- Some components are practical engineering variants (for example, critic buffer/value buffer branches and parameterized Langevin noise), while preserving the same core dynamics: attraction to high-value anchors and repulsion from suboptimal actions.

Files kept
- `model/algo.py`
- `model/model.py`
- `model/utils.py`

What is not included
- Environment wrappers, training entry scripts, logging/plot scripts, and benchmark configs.
- For full reproduction, integrate these modules into your own trainer and environment stack.

Release scope note
- This package is a minimal method release. If a submission checklist claims complete training code and scripts, align that claim with the actual release artifacts.
