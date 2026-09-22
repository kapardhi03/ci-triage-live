# Phase 04

First phase with real data. Every number below came from a command; the command is named.

| Was | Now | Statement | Evidence |
|---|---|---|---|
| unknown | known | FlakeFlagger (Zenodo 4450723) is **CC-BY-4.0** — usable, attribution obligatory | decisions/04-dataset-choice.md |
| unknown | known | IDoFT has **no licence at all** — no LICENSE file, no badge, only a citation request | decisions/04-dataset-choice.md, ai-ledger/04 |
| assumed | known | **empty ≠ unrestricted**: copyright is automatic, so no licence means all rights reserved; GitHub ToS grants view/fork only | ai-ledger/04-data-and-licence.md |
| **known-unknown** | **known** | **N = 10,000.** 26,034 of 26,765 tests were run exactly 10,000 times (some 20k/30k, a tail fewer) — phase 03's central open unknown, closed | derived from `NumFailingRuns + NumPassingRuns` |
| assumed | known | `IsFlaky` is exactly `NumFailingRuns > 0 AND NumPassingRuns > 0` — all 828 flaky rows flipped, **zero** non-flaky rows did | scan of test_results.csv |
| unknown | known | the join key is `(suffix-matched project, lowercase(Test with '#'→'.'))` — neither project nor test name matches across files as published | ci_triage/data.py, artifacts/results/eda.json |
| unknown | known | joined shape: **26,134 rows, 825 positives, 3.1568%, 25 projects, 21 features** | artifacts/results/eda.json |
| unknown | known | two candidate labels disagree on **904 tests**; **763 of 825** rerun-proven flaky tests (92%) are invisible to the tool label | cross-tab, decisions/04-dataset-choice.md |
| unknown | known | `IsFlaky` (rerun-observed) chosen as ground truth over `flaky` (tool-labelled) | decisions/04-dataset-choice.md |
| unknown | known | four label-derived columns found by single-column AUC scan: `FirstFailingRunID` (**1.000**), `UniqueFailingExceptionTypes` (0.998), `NumFailingRuns` (0.994), `NumPassingRuns` (0.993) | leak scan, this session |
| unknown | known | the general method: a leaking column is one that could not exist before the answer was known, and shows up as a single column separating the classes almost perfectly | tests/test_data.py::test_no_column_predicts_the_label_alone |
| unknown | known | `hIndex...window5` takes 1.8 distinct values per project with 89.0% of rows at the project mode — a project identifier in numeric costume | constancy measurement, this session |
| unknown | known | the 8 history features require git history the dataset does not ship (Project_Info.csv = 24 rows of URL+SHA, one revision each) | artifacts/results/eda.json, design/04 |
| unknown | known | exclusion policy: 4 rerun columns + `flaky` + `flaky_source` + `window5` + `window10` dropped; 6 history columns kept | design/04-data-and-licence.md |
| unknown | known | strongest surviving feature is `ExecutionTime` at AUC 0.76; everything else ≤0.65 | leak scan |
| assumed | known | a leak test graded against the module's own exclusion list is **circular** and passes when an entry is deleted | ai-ledger/04-data-and-licence.md |
| unknown | known | row accounting: 469 results rows dropped (3 unmapped projects), 8 case-folding collisions, 485 feature rows unjoined | artifacts/results/eda.json |

## Phase 03 predictions, checked

| Prediction | Outcome |
|---|---|
| positive rate under 10% | **held** — 3.16% joined (0.77% tool label, 3.09% rerun label) |
| true flaky rate higher than published | **held, in an unexpected form** — the rerun label is 4× the tool label on the same corpus |
| contamination of the negative class is material | **substantially refuted** — at N=10,000 a hidden flake must flip rarer than ~1-in-3,000 to survive |
| one-way error direction, no reverse errors | **held for `IsFlaky`** (0 non-flaky rows flipped); **false for the tool label** (141 tool-flaky tests never flipped in 10,000 runs) |

The contamination argument was correct but belonged to the other column. For `IsFlaky` the
negative class is about as clean as money can buy; for `flaky` it hides 92% of the true
positives. Same argument, opposite verdict, decided entirely by the label choice.

## Open

| Statement | Why it is still open |
|---|---|
| whether keeping 6 history columns was right | phase 06's held-out-project gap is the test; revisit if it stays large |
| the 80% mode-share threshold is a chosen number | no natural break in the gradient; written down so it can be argued with |
| the git-history dependency is unbuilt | accepted into the phase 00 boundary, not yet designed or costed |
| 469 + 485 rows excluded by the join | not investigated per-project; a systematic loss in one project would bias `groups` |
| 8 case-folding collisions kept-first | arbitrary tie-break; unexamined whether the discarded twin differed in label |
| `ExecutionTime` at AUC 0.76 is suspiciously strong | not yet established whether it is a real signal or an artifact of how long failing tests run |
| no model has been trained | every number here describes data, not performance |
