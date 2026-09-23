# Experiment 07 — what calibration costs

**Written 2026-09-23, before any model was fitted.** Appended to after the run, never edited.

## Setup

- Model: `HistGradientBoostingClassifier` over the 13 features surviving slice 04 and 06.
- Split: leave-one-project-out, 23 evaluable folds (`jimfs` and `commons-exec` have zero
  positives). The deployment split, per decisions/06.
- Metrics: slice 02's ruler — AUC, ECE (both binnings), Brier, cost-weighted risk.
- Calibration: `CalibratedClassifierCV`, sigmoid and isotonic, measured on the same folds.

Floor to beat: phase 06's logistic regression, **LOPO AUC 0.6878 ± 0.1299**.

## The prediction

| | direction |
|---|---|
| **ECE** | **much better** |
| **AUC** | **unchanged** |

**Reasoning, in the builder's words: "monotonic map preserves ranking."**

Calibration fits a monotonic score-to-probability mapping. A strictly monotonic transform
cannot reorder any pair of rows, and AUC depends only on the ordering, so AUC should be
untouched. ECE depends on the absolute values, which is exactly what the mapping corrects,
so ECE should improve substantially.

## What would show this was wrong

*Derived from the stated reasoning during write-up; correct it if it misstates the intent.*

1. **AUC moves materially (|Δ| > 0.01).** The monotonic-map account would then be
   incomplete: `CalibratedClassifierCV` refits the base estimator on internal CV folds and
   averages them, so the calibrated object is an ensemble rather than the same model with a
   rescaled output. If AUC moves, that refit — not the mapping — is what moved it, and the
   reasoning named the wrong mechanism even if it named the right direction.
2. **ECE gets worse.** The mapping is fitted on other projects and applied to a held-out
   one. If the score-to-probability relationship is project-specific, calibration learned on
   `hbase` and `spring-boot` may not transfer, and calibrating could make the held-out
   project's probabilities worse rather than better.
3. **ECE improves on equal-width bins but not equal-frequency.** Phase 02 established that
   equal-width ECE reports 0.000 for a model predicting the base rate everywhere. An
   improvement visible only in the flattering binning is not an improvement.
4. **Isotonic and sigmoid disagree in direction.** Both are monotonic; if they move AUC
   opposite ways, ties from isotonic are doing the work and "monotonic preserves ranking"
   is too coarse a statement for what is actually happening.

Condition 1 is the one that tests the *mechanism* rather than the outcome.

## Scope

25 projects from the full CSVs, 13 features. TASK describes 23 features; phase 06 removed
the 8 project-scale columns. Not comparable to `precomputed/`.

---

## Result

*(appended after the run — empty at the time of prediction)*
