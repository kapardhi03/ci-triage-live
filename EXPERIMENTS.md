# Experiments

Index of `experiments/*.md`. Each entry was written **before** its run.

| Phase | Hypothesis | Prediction | Result | Verdict |
|---|---|---|---|---|
| 03 | Label noise is one-directional: positives clean, negatives contaminated with uncaught flakes | Positive rate <10%; true flaky rate above published; model-flagged FPs flip more than random negatives | Rate 3.16% ✓. Rerun label is 4× the tool label ✓. Direction held for `IsFlaky` (0 reverse errors) | **partly refuted** — N=10,000 means a hidden flake must flip rarer than ~1-in-3,000; the magnitude braced for is not there. Kept unedited |
| 03 | (same) — reverse-direction errors are impossible | No mechanism produces a spurious `flaky` mark | True for `IsFlaky`; **false** for the tool label — 141 tool-flaky tests never flipped in 10,000 runs | **refuted for the alternate label** |
| 07 | `ExecutionTime` (AUC 0.760, alone above the pack) is partially label-derived — failing runs take longer | Dropping it costs less held-out AUC than 0.76 implies; its edge shrinks disproportionately under the grouped split | — | **pre-registered 2026-09-22**, not yet run |

Verdict is one of: supported, refuted, inconclusive. A refuted hypothesis that was kept is
worth more here than a supported one that was edited after the fact.
