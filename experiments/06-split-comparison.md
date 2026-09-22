# Experiment 06 — random split versus held-out projects

**Written 2026-09-22, before any model was fitted.** Nothing below the line marked
*Result* existed when the prediction was made. This file is appended to, never edited.

## Setup

- Model: logistic regression, standardised. The cheapest thing that could work; phase 07
  builds the real tabular observer.
- Features: the 21 surviving phase 04's exclusion policy. Label: `IsFlaky`, 825 positives
  in 26,134 rows across 25 projects.
- Split A: 5-fold random, rows shuffled.
- Split B: leave-one-project-out. Only 23 of 25 projects are evaluable — `jimfs` and
  `commons-exec` contain zero positives, so AUC is undefined on those folds.

Known before predicting: the positive rate is strongly project-dependent, from `alluxio`
at 62.0% to `assertj-core` at 0.016%, a spread of roughly 4,000×. `assertj-core` alone is
6,261 rows — 24% of the corpus — with a single positive.

## What each split measures

**Random row-wise split.** Rows from the same project land on both sides. The model sees
some of `hbase` in training and the rest of `hbase` in test. It can therefore score a test
row using anything it learned about that row's *project*, including the project's base
rate, which is a property of the project rather than of the test. This measures performance
on tests drawn from projects the model has already seen.

**Leave-one-project-out.** Every row of the held-out project is unseen, so nothing
project-specific transfers. Whatever the model learned about `hbase` being 33.6% flaky is
unavailable when `hbase` *is* the test set. This measures performance on a project the
model has never seen.

## The prediction

| | AUC |
|---|---|
| **Random split** | **0.85** |
| **Leave-one-project-out** | **0.65** |
| **Gap** | **0.20** |

**Reasoning, in the builder's words: "base rate is project-level."**

The random split lets the model exploit a project's base rate as if it were a feature of
the test. Since base rate varies ~4,000× across projects and project identity is recoverable
from project-scale columns (`projectSourceLinesCovered`, `projectSourceClassesCovered`, and
the surviving history features), a model can score well by identifying the project and
predicting its prevalence — without learning anything about flakiness. Grouped splitting
removes that route, so the number should fall substantially. 0.65 still leaves room for
genuine test-level signal.

## What would show this reasoning was wrong

*Derived from the stated reasoning during the write-up; correct it if it misstates the
intent.*

1. **The two AUCs come out close** (gap < 0.05). Base-rate memorisation would then not be
   doing meaningful work, and the random split would be roughly honest — the opposite of
   the claim.
2. **Grouped AUC lands at or below 0.50.** That would be worse than the claim, not better:
   it would mean the features carry essentially no transferable test-level signal at all,
   and "0.65 leaves room for genuine signal" was wrong.
3. **Grouped AUC exceeds random-split AUC.** The direction itself would be refuted and the
   mechanism would need rethinking entirely.
4. **The gap survives removal of the project-scale features.** If dropping
   `projectSourceLinesCovered`, `projectSourceClassesCovered` and the history columns leaves
   the gap intact, then project identity is not travelling through the route named above and
   the explanation is wrong even if the number is right.

Condition 4 is the one that tests the *mechanism* rather than the outcome, and is the
strongest of the four.

## Scope

25 projects from the full CSVs, not the 3-project archive subset. Comparable to phase 04's
numbers, not to `precomputed/`.

---

## Result

*(appended after the run — empty at the time of prediction)*

**Appended 2026-09-22 after the run. Nothing above this line was edited.**

| | predicted | actual (21 features) |
|---|---|---|
| random 5-fold | 0.85 | **0.7621** ± 0.0127 |
| leave-one-project-out | 0.65 | **0.6490** ± 0.1295 |
| gap | 0.20 | **0.1131** |

LOPO predicted within **0.001**. The random split was overestimated by 0.09, so the gap is
about half what was predicted. Direction correct, magnitude wrong — and the error sits in
the optimistic number, not the pessimistic one.

**Unpredicted:** the random split's std is 0.0127 against LOPO's 0.1295. It reports a
falsely *stable* number as well as a falsely high one. Fold-to-fold agreement under a random
split comes from every fold containing the same projects; real cross-project performance
varies enormously.

## Refutation conditions, checked

| # | Condition | Outcome |
|---|---|---|
| 1 | gap < 0.05 → base-rate memorisation not doing real work | **not met** — gap 0.1131 |
| 2 | LOPO ≤ 0.50 → no transferable signal at all | **not met** — 0.6490 |
| 3 | LOPO > random → direction refuted | **not met** — direction held |
| 4 | gap survives removal of project-scale features → mechanism wrong | **not met — mechanism supported** |

**Condition 4 in detail.** Dropping the 8 project-scale features shrank the gap from 0.1131
to 0.0692, a 38.8% collapse. The shape is the fingerprint: the random split lost 0.005, LOPO
gained **+0.039**. Features that help within a project and hurt across it are project
identifiers in disguise.

But **61% of the gap survives**. The stated mechanism is supported and incomplete: project
identity also travels by a route not named in the prediction. Open, carried to phase 07.

## Consequence

Deployment is unseen projects, so the 8 features are dropped and phase 04's history-column
decision is reversed. Final reported baseline on 13 features, leave-one-project-out:
**AUC 0.6878 ± 0.1299** over 23 evaluable folds. Majority baseline: 96.84% accuracy, AUC
0.500. See `decisions/06-split-choice.md` and `artifacts/results/baseline.json`.
