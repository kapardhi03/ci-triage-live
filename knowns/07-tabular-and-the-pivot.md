# Phase 07

Scope: 25 projects, 13 features, leave-one-project-out (23 evaluable folds). TASK describes
23 features; phase 06 removed 8. Not comparable to `precomputed/`.

| Was | Now | Statement | Evidence |
|---|---|---|---|
| unknown | known | GBT calibrated scores **0.6781 ±0.159** LOPO — **worse** than phase 06's logistic regression at 0.6878 | artifacts/results/tabular.json |
| unknown | known | calibration moved AUC **+0.0016** (sigmoid) and **−0.0116** (isotonic); both monotonic, so ties and the internal refit are doing the work, not the mapping | experiments/07-calibration-tradeoff.md |
| unknown | known | ECE improved only 6.6% (equal-width) and 2.5% (equal-frequency) — "much better" was refuted | experiments/07-calibration-tradeoff.md |
| unknown | known | **cost-weighted risk halved, 0.5440 → 0.2708**, while AUC and ECE barely moved | artifacts/results/tabular.json |
| unknown | known | **the model IS the constant baseline**: both cost 0.0957 h/row to four decimals | artifacts/results/tabular.json |
| unknown | known | the cost-optimal threshold from the phase 01 table is **p > 0.930**; the calibrated model's maximum probability over 25,867 rows is **0.2362** | decisions/07-the-pivot.md |
| unknown | known | **no threshold beats the constant**, calibrated or uncalibrated; the best found flags zero rows | artifacts/results/tabular.json |
| unknown | known | the uncalibrated model's **top-10 most confident predictions are 0/10 correct**; precision peaks at 10% against a 93% requirement | artifacts/results/tabular.json |
| unknown | known | **the pivot to abstention is refuted**: abstention costs 1.5h/row to avoid 0.0957h/row; optimal qualifier threshold is 0.00 | decisions/07-the-pivot.md |
| unknown | known | an **oracle** qualifier saves **2.7%**, abstaining on one project (`alluxio`) — the ceiling, not the qualifier, is the limit | artifacts/results/tabular.json |
| unknown | known | qualifier correlates weakly and correctly: Spearman vs cost **−0.357**, vs AUC **+0.323** | artifacts/results/tabular.json |
| unknown | known | **the observer is effectively one feature**: dropping `ExecutionTime` takes LOPO from 0.6765 to **0.5577** | experiments/07-execution-time-leak.md |
| unknown | known | `ExecutionTime` drives **39.4%** of the alien-project distance — the coupling predicted in design/07 before measurement holds | design/07, tests/test_tabular.py |
| assumed | **wrong** | phase 02's `cost_weighted_risk` had the cost mapping **inverted** against `IsFlaky`, making "call it flaky" look cheap — the 40h error | ai-ledger/07, decisions/02 (correction) |
| unknown | known | a qualifier fitted on all projects cannot detect the held-out one as alien | tests/test_tabular.py::test_qualifier_is_fitted_without_the_held_out_project |

## Predictions, checked

| Prediction | Outcome |
|---|---|
| AUC unchanged after calibration | **right for sigmoid** (+0.0016), wrong for isotonic (−0.0116) |
| ECE much better | **refuted** — 6.6% / 2.5% |
| refutation 1: AUC moves >0.01 | **fires for isotonic** |
| refutation 4: methods disagree in direction | **fires** — the named mechanism was too coarse |
| `ExecutionTime` is partially label-derived | **inconclusive** — it holds its contribution across projects, which argues against; but a uniform leak would too |
| (design/07) `ExecutionTime` dominates the distance metric | **confirmed** — 39.4%, 3× the next feature |

All kept unedited.

## Open

| Statement | Why it is still open |
|---|---|
| **the `ExecutionTime` leak is unresolved** | A leak present in both train and test transfers fine, so strong cross-project contribution is consistent with both readings. Decisive evidence is whether it was measured on runs including failures — the dataset does not ship it. |
| the 40/3/1.5 cost numbers dominate every result here | Flagged as guesses in `knowns/01`. **Deliberately not revisited** — changing them because the model looks bad is the dishonest option. Any change must be argued from the organisation, not the metric. |
| 61% of the phase 06 split gap is still unexplained | Carried forward untouched; this phase added no evidence either way. |
| can the observer contribute **in combination**? | This phase only shows it cannot act alone. Phase 11's question, now open rather than assumed. |
| will three observers be independent? | Sharper than expected: this one reduces to a single column, so three observers are three observers only if they do not all rest on the same signal. Phase 10. |
| the qualifier is built and unused | Its design survives — distance, not model confidence — but the economics give it nothing to buy here. It may matter when a component exists that is worth gating. |
| LOPO fold spread remains enormous | ±0.159. `assertj-core` scores AUC 0.255, `Achilles` 0.881. A mean over 23 such folds may be the wrong summary. |
