# AI ledger — phase 06

## Rejected proposal

**Proposal:** Report the random 5-fold number, 0.7569. It is the higher figure, it is what
almost every tabular paper reports, its standard deviation is ten times tighter (0.0099
against 0.1299), and cross-validation is standard practice.

**Verdict:** Rejected.

**Reason:** Deployment sees projects the model has never trained on, so a split that lets
rows from the same project sit on both sides measures something the system will never be
asked to do. The tight standard deviation is not a point in its favour — it is the clearest
symptom of the problem. Fold-to-fold agreement under a random split comes from every fold
containing the same projects; genuine cross-project performance varies by project, and the
random split conceals that variance as well as the level.

Cost of rejecting it: 0.069 AUC of reportable performance. What that buys is a number that
survives contact with an unseen project.

## Narrowed proposal

**Proposal (mine, in phase 04):** Keep six `hIndexModificationsPerCoveredLine_*` columns,
dropping only `window5` and `window10` on a ≥80% project-mode rule, and accept a
git-history dependency into the system boundary.

**Verdict:** Reversed by measurement.

**Reason:** The ≥80% mode-share rule caught only the two most extreme project-constants. It
was a proxy for the thing that actually matters — whether a feature carries project identity
— and it was too weak. Measured directly on the deployment split, all 8 project-scale
features cost **0.039 AUC** on held-out projects while returning **0.005** on a random
split. Helping within a project and hurting across it is what a project identifier does.

Phase 04 recorded this as the open item phase 06 would settle, and it settled against the
original decision. The git-history dependency accepted then is cancelled as a side effect.

## Order violation, disclosed

TASK step 2 requires the deployment question to be answered **before** looking at which
split gives a nicer number. It was answered after: phase 00 had not fixed the deployment
context, and by the time the question was put the numbers were already on screen.

The argument given for unseen projects does not depend on the numbers, but that is a claim
about reasoning neither party can audit. Recorded as a contaminated decision rather than
presented as a clean one. The mitigation available in future phases is to fix the
deployment context in the design file before any model is fitted.

## Gap in the harness

`evaluate_split` originally averaged whatever folds it could score. With `jimfs` and
`commons-exec` carrying zero positives, that silently produced a mean over 23 folds while a
reader would assume 25. The fix is disclosure rather than repair: skipped folds are returned
with the held-out project and the reason, counted separately, and
`tests/test_splits.py::test_single_class_fold_is_reported_not_silently_dropped` fails if a
fold is dropped without being reported.
