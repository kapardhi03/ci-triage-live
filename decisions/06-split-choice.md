# Decision 06 — the split, and what it cost

## The deployment question

**The system is deployed against projects it has never seen. Leave-one-project-out is the
honest number.**

There is a genuine tension in `PROBLEM.md`. It describes one organisation's release
process — "the on-call release engineer", "the 09:00 release" — and a system shipped inside
one company will, within months, have trained on every repo it meets. Under that reading a
random split is close to honest and LOPO is needlessly pessimistic.

Rejected, because `design/00` puts no boundary on which repos the system serves, and a
triage system that degrades the first time a team spins up a new service is one that fails
at exactly the moment it is being adopted. Onboarding a repo must not require retraining
before the system is trustworthy on it. Deployment therefore includes unseen projects, and
the number reported for the rest of this lab is the one measured on unseen projects.

**Order disclosure.** TASK step 2 asks for this answer *before* looking at which split gives
a nicer number. It was answered after. Phase 00 did not fix the deployment context, the
numbers were already on screen, and the answer is therefore contaminated by knowing that
LOPO scores lower. It is recorded here rather than presented as though the order had been
clean. The argument above does not depend on the numbers, but that is a claim about my
reasoning that neither of us can audit.

## The result

Prediction, recorded in `experiments/06-split-comparison.md` and committed as `08b1c35`
before any model was fitted: **random 0.85, LOPO 0.65, gap 0.20.**

Measured on the 21-feature matrix:

| Split | AUC | std | folds |
|---|---|---|---|
| random 5-fold | **0.7621** | 0.0127 | 5 |
| grouped 5-fold | 0.6060 | 0.1653 | 5 |
| leave-one-project-out | **0.6490** | 0.1295 | 23 eval, 2 skipped |

**LOPO was predicted within 0.001.** The random split was overestimated by 0.09, so the gap
came out at 0.1131 — about half the predicted 0.20. Direction right, magnitude wrong, and
the error was in the *optimistic* number rather than the pessimistic one.

**The unpredicted finding is the spread.** The random split's standard deviation is 0.0127
against 0.1295 for LOPO — an order of magnitude tighter. The random split does not merely
report a higher number, it reports a **falsely stable** one: fold-to-fold agreement that
comes from every fold containing the same projects. Cross-project performance genuinely
varies enormously by project, and the random split hides that variance as well as the level.

## The mechanism test

Refutation condition 4 was the strongest of the four, because it tests the stated mechanism
rather than the outcome: if the gap survives removal of the project-scale features, project
identity is not travelling by the named route and the explanation is wrong even if the
number is right.

| features | random | LOPO | gap |
|---|---|---|---|
| all 21 | 0.7621 | 0.6490 | 0.1131 |
| 8 project-scale removed | 0.7569 | 0.6878 | **0.0692** |

The gap collapses by **38.8%**, and the shape is the mechanism's fingerprint: removing those
features costs the random split **0.005** and gains LOPO **+0.039**. They help within a
project and hurt across projects, which is what a project identifier disguised as a feature
does.

So the reasoning — *base rate is project-level* — is **supported**. But 61% of the gap
survives, so project identity also travels by a route that was not named. The claim is
supported and incomplete, and the unnamed route is an open question.

## What it cost: phase 04's decision is reversed

`knowns/04` recorded the open item: *"whether keeping 6 history columns was right — phase
06's held-out-project gap is the test; revisit if it stays large."*

It was not right. **The 8 project-scale features are dropped**: `projectSourceLinesCovered`,
`projectSourceClassesCovered`, and all six surviving `hIndexModificationsPerCoveredLine_*`
columns. `ci_triage/data.py` carries them with reason code `project_scale`, and the feature
matrix is now **13 features**, down from 21.

Two consequences worth naming:

- **The git-history dependency is gone.** Phase 04 accepted it into the phase 00 system
  boundary as a bill to be paid later. Dropping the history features cancels it — the
  system no longer needs a project's commit history at 02:47. A decision that looked like a
  cost turned out to be a saving.
- **Every number produced before this point used 21 features.** `artifacts/results/eda.json`
  has been regenerated. `decisions/04` and `knowns/04` record what was decided then and have
  not been rewritten; a supersession note points here.

## The reported baseline

On 13 features, the deployment split:

| | AUC | std |
|---|---|---|
| random 5-fold | 0.7569 | 0.0099 |
| grouped 5-fold | 0.6031 | 0.1442 |
| **leave-one-project-out** | **0.6878** | **0.1299** |

Majority-class baseline: 96.84% accuracy, **AUC 0.5 by definition**. Which is phase 02's
lesson arriving on real data — the constant predictor is 96.84% accurate and useless, and
the only reason that is obvious here is that the ruler was built before the model.

**0.6878 is the number every later phase must beat, on this split.** Not 0.7569.

## What it cost to choose this

Reporting 0.6878 instead of 0.7569 gives up 0.069 AUC of reportable performance. That is
the price of a number that survives contact with a project the system has not seen. The
alternative was not a better system; it was the same system with a more flattering
measurement.
