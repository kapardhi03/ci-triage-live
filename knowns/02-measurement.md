# Phase 02

| Was | Now | Statement | Evidence |
|---|---|---|---|
| unknown | known | evaluation is a separate component, not a model method, so every model is scored by identical code — this is what makes phase 07's control a control | design/02-measurement.md, decisions/02-metric-ladder.md |
| unknown | known | at a 3% positive rate the constant "never flaky" model scores 0.97 accuracy and 0.0 recall on the same input | tests/test_metrics.py::test_constant_high_accuracy_zero_recall |
| unknown | known | equal-width ECE reports **0.000** for a model that predicts the base rate for every case; equal-frequency reports **0.042** on the same array | decisions/02-metric-ladder.md |
| unknown | known | equal-width bins carve the probability axis, equal-frequency bins carve the samples — under imbalance all predictions land in one equal-width bin where confidence equals accuracy by construction | decisions/02-metric-ladder.md |
| unknown | known | **ECE alone selects the useless model**: base-rate model ECE 0.000 vs perfect ranker ECE 0.105, while recall is 0.0 vs 1.0 and cost is 1.20 vs 0.00 | decisions/02-metric-ladder.md, tests/test_metrics.py::test_ece_alone_prefers_the_useless_model |
| unknown | known | calibration must never be read without a discrimination metric beside it | ai-ledger/02-measurement.md |
| unknown | known | the constant and base-rate models have ROC AUC = None, not 0.5 — a single-valued predictor cannot be ranked at all | tests/test_metrics.py::test_constant_model_auc_is_undefined_not_good |
| unknown | known | cost-weighted risk for both useless models is 1.20 engineer-hours/build; a perfect model is 0.00 | decisions/02-metric-ladder.md |
| assumed | known | the phase 01 cost asymmetry was **not** enforced by any test until this phase — flattening 40h to 3h left the suite green | ai-ledger/02-measurement.md |
| unknown | known | the suite is mutation-checked: symmetric costs, free abstain, abstain-costlier-than-hold, and equal_freq-collapsed-to-equal_width each fail exactly one test | this session's mutation runs |
| known-unknown | known-unknown | equal-frequency ECE is tie-order dependent when probabilities are identical (0.042 vs 0.048 by positive placement) — it is *not flattering*, but it is not *correct* on a single-valued predictor either | decisions/02-metric-ladder.md |
| known-unknown | known-unknown | every number above is from a 100-row hand-typed toy array; nothing has touched real CI data yet | — |
| known-unknown | known-unknown | how many ECE bins is right for the real dataset — 10 is a default, not a decision | — |
| known-unknown | known-unknown | the abstain threshold is still not derived; risk–coverage can now measure it but has not chosen it | — |
| known-unknown | known-unknown | whether the ~40h / ~3h / ~1.5h guesses survive contact with real incident data | knowns/01-decision-and-cost.md |

## Correction (phase 07)

| Was | Now | Statement | Evidence |
|---|---|---|---|
| known | **wrong** | "cost-weighted risk for both useless models is 1.20 engineer-hours/build" — the cost mapping was inverted against `IsFlaky`; the corrected figure is **0.09** | decisions/02-metric-ladder.md (correction) |
| unknown | known | an inverted cost table does not merely misreport magnitude — it makes "call it flaky" look cheap and points the system at the 40h error | decisions/02-metric-ladder.md (correction) |
| assumed | known | the phase 02 asymmetry test encoded the same misreading in its comments, so it passed while being wrong — the circular-test failure again | tests/test_metrics.py |
| unknown | known | direction is now pinned: `y=0` predicted `1` charges 40h, `y=1` predicted `0` charges 3h; flipping the mapping fails two tests | tests/test_metrics.py::test_the_expensive_error_is_calling_a_real_defect_flaky |
