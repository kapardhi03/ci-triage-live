# Decision 02 — the metric ladder and the binning choice

## Why evaluation is not a method on the model

If `model.score()` owns the measurement, every model grades its own homework on its own
terms. Then "the tabular model beats the constant baseline" is not a claim anyone can
check, because the two numbers were produced by two different rulers.

The evaluation component is separate so that a constant, a heuristic, a tabular model, a
sequence model and a retrieval observer can all be handed the same `(predictions, truth)`
pair and scored by identical code. That is what makes phase 07's control possible at all:
the control is only a control if nothing about the measurement changed when the model did.

## The ladder, and what each rung is for

| Measurement | The question it answers | Source |
|---|---|---|
| accuracy | almost nothing at a 3% positive rate | sklearn |
| ROC AUC | does it rank flaky above not-flaky | sklearn |
| precision / recall @ threshold | of what we flagged, how much was right; of what was there, how much did we catch | sklearn |
| Brier | squared error on the probabilities themselves | sklearn |
| ECE (selectable binning) | when it says 80%, is it right 80% of the time | written here |
| cost-weighted risk | the phase 01 objective, in engineer-hours | written here |
| risk–coverage | what happens once the system may abstain | written here |

Only the last three are hand-written. Anything sklearn already does is imported.

## The binning decision

**Decision: equal-frequency is the trustworthy binning on this problem. Equal-width may
be reported alongside it but is never read alone.**

The reasoning was class imbalance — flaky events are rare, so predictions crowd into the
bottom of the [0,1] range instead of spreading across it. Equal-width bins carve the
*probability axis* into ten fixed slices; equal-frequency bins carve the *samples* into
ten equal groups. When every prediction is small, the first arrangement puts them all in
one slice and the second still has to split them.

Evidence — the base-rate model (outputs 0.03 for all 100 rows, 3 of which are flaky):

| Binning | ECE |
|---|---|
| equal-width, 10 bins | **0.0** |
| equal-frequency, 10 bins | **0.042** |

Equal-width reports *perfect calibration* for a model that catches nothing. Every
prediction falls in bin 0, where average confidence (0.03) equals average accuracy (0.03)
by construction. There is nothing left for the metric to disagree with.

One caveat found while running it: when every probability is identical, the
equal-frequency bins are split by tie-order, and the number wobbles (0.042 vs 0.048
depending on where the positives sit). So equal-frequency is not *right* here either — it
is merely not flattering. Neither number is trustworthy on a single-valued predictor.

## The bigger finding: calibration without discrimination

Running the full ladder on three models on the same array:

| | constant 0.0 | base-rate 0.03 | perfect ranker |
|---|---|---|---|
| accuracy | 0.97 | 0.97 | 1.00 |
| recall | 0.0 | 0.0 | 1.00 |
| ROC AUC | None | None | 1.00 |
| **ECE (equal-width)** | 0.030 | **0.000** | **0.105** |
| cost-weighted risk | 1.20 | 1.20 | **0.00** |

**A model selected on ECE alone picks the useless one.** The base-rate model scores a
perfect 0.0 calibration error; the perfect ranker scores 0.105 and looks ten times worse.
The metrics that get it right are recall, AUC, and cost-weighted risk.

So ECE is a *diagnostic*, not a selection criterion. Nothing in this system may be chosen
on calibration without a discrimination number beside it.

## What the ladder is allowed to decide

Nothing. It measures. Threshold selection, abstention policy, and model choice happen in
later phases and read these numbers — they are not computed here.

---

## Correction (phase 07): the cost mapping was inverted

`cost_weighted_risk` charged the wrong cost to each error. The label is `IsFlaky`, so
`y == 1` is **flaky** and `y == 0` is **not flaky — a real defect**. Phase 01's table prices
*real defect called flaky* at ~40h (the bug ships) and *flaky called real defect* at ~3h
(a needless hold). `ci_triage/metrics.py` had them the other way round, and its comment
asserted `y == 1` meant "real defect."

It survived phase 02 because that phase only ran the function on toy arrays where nothing
pinned `y = 1` to a meaning, and the asymmetry test encoded the same misreading in its own
comments — so it passed while being wrong. The same self-referential failure as phase 04's
circular leak test, in a different module.

**It is worse than a factor of 13.** Inverted, the table makes missing a flaky test
expensive and shipping a defect cheap, so any threshold or model tuned against it optimises
*toward* calling things flaky — which is the 40h error phase 01 priced highest. The bug did
not only misreport cost; it aimed the system at the wrong mistake.

The `cost_weighted_risk` row in the table above is therefore wrong. Corrected:

| | constant 0.0 | base-rate 0.03 | perfect ranker |
|---|---|---|---|
| cost_weighted_risk **(as reported)** | 1.20 | 1.20 | 0.00 |
| cost_weighted_risk **(corrected)** | **0.09** | **0.09** | **0.00** |

Every other number in this file is unaffected — AUC, recall, ECE and Brier do not read the
cost table. The conclusion that ECE alone selects the useless model stands unchanged, and
so does the cost column's *ranking*: the useless models still cost more than the perfect
one. Only the magnitude was wrong.

`tests/test_metrics.py::test_the_expensive_error_is_calling_a_real_defect_flaky` now pins
the direction explicitly, and flipping the mapping back fails two tests.
