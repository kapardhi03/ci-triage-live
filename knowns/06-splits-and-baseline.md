# Phase 06

Scope: 25 projects from the full FlakeFlagger CSVs, 26,134 rows, 825 positives. Not
comparable to `precomputed/` (17 projects).

| Was | Now | Statement | Evidence |
|---|---|---|---|
| unknown | known | deployment sees **unseen projects**, so leave-one-project-out is the reported split | decisions/06-split-choice.md |
| unknown | known | random 5-fold **0.7621**, grouped 5-fold 0.6060, LOPO **0.6490** on 21 features — gap **0.1131** | artifacts/results/baseline.json |
| unknown | known | the random split's std is **0.0127** against LOPO's **0.1295** — it reports a falsely *stable* number, not only a falsely high one | artifacts/results/baseline.json |
| unknown | known | fold-to-fold agreement under a random split comes from every fold containing the same projects; real cross-project performance varies enormously | decisions/06-split-choice.md |
| unknown | known | dropping the 8 project-scale features costs the random split **0.005** and gains LOPO **+0.039** — the fingerprint of a project identifier in disguise | experiments/06-split-comparison.md |
| unknown | known | the base-rate mechanism is **supported**: the gap collapses 38.8% (0.1131 → 0.0692) when those features go | experiments/06-split-comparison.md |
| unknown | known | **phase 04's history-column decision is reversed.** All 8 project-scale features excluded, matrix is now **13 features** | ci_triage/data.py, artifacts/results/eda.json |
| unknown | known | the git-history dependency accepted into the phase 00 boundary in phase 04 is **cancelled** | decisions/06-split-choice.md |
| unknown | known | **reported baseline: LOPO AUC 0.6878 ± 0.1299** over 23 evaluable folds, 13 features | artifacts/results/baseline.json |
| unknown | known | majority baseline is **96.84% accurate with AUC 0.500** — phase 02's lesson on real data | artifacts/results/baseline.json |
| unknown | known | `jimfs` and `commons-exec` have **zero positives**, so LOPO has 23 evaluable folds, not 25 | artifacts/results/baseline.json |
| unknown | known | the positive rate spans ~4,000× by project (`alluxio` 62.0% → `assertj-core` 0.016%), and `assertj-core` is 24% of rows with 1 positive | this session's scan |
| unknown | known | a project on both sides of a fold is invisible in the metrics and fatal to the claim; checked per fold, and the detector is proven capable of failing | tests/test_splits.py |
| unknown | known | **0.6878 is the number later phases must beat**, not 0.7569 | decisions/06-split-choice.md |

## Predictions, checked

| Prediction | Outcome |
|---|---|
| random 0.85 | **wrong** — 0.7621, over by 0.09 |
| LOPO 0.65 | **right within 0.001** — 0.6490 |
| gap 0.20 | **wrong** — 0.1131, about half |
| refutation 1: gap < 0.05 | not met |
| refutation 2: LOPO ≤ 0.50 | not met |
| refutation 3: LOPO > random | not met |
| refutation 4: gap survives feature removal | **not met — mechanism supported** |

Kept unedited. The error was in the optimistic number, not the pessimistic one.

## Open

| Statement | Why it is still open |
|---|---|
| **61% of the gap is unexplained** | Removing project-scale features closed 38.8%. Project identity travels by a route not yet named. The prime suspect is test-level features correlating with project, but nothing has been measured. Carried to phase 07. |
| the deployment question was answered **after** seeing the numbers | TASK step 2 requires the reverse order. Phase 00 had not fixed the deployment context. The decision is contaminated and disclosed as such; the argument does not appear to depend on the numbers, but that is unauditable. |
| LOPO std is 0.1299 — folds disagree violently | A mean over 23 wildly varying folds may not be the right summary. Per-project results are recorded in `baseline.json` but not analysed. |
| 8 of 25 projects have <5 positives | Their folds are near-meaningless individually yet weighted equally in the mean. An alternative weighting has not been considered. |
| logistic regression is a floor, not a model | Phase 07 builds the real tabular observer. Whether the gap behaves the same under a stronger model is unknown — a higher-capacity model may memorise projects *harder*. |
| the test-set ledger has never been used | It records access; nothing has accessed it yet. Its value is untested. |
