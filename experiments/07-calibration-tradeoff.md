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

**Appended 2026-09-23 after the run. Nothing above this line was edited.**

| | AUC | ECE_ew | ECE_ef | Brier | cost |
|---|---|---|---|---|---|
| GBT uncalibrated | 0.6765 ±0.163 | 0.0907 | 0.0925 | 0.0909 | 0.5440 |
| GBT + sigmoid | 0.6781 ±0.159 | 0.0847 | 0.0902 | 0.0855 | **0.2708** |
| GBT + isotonic | 0.6650 ±0.153 | 0.0853 | 0.0911 | 0.0859 | 0.2724 |
| *phase 06 logistic regression* | *0.6878* | | | | |

## The prediction, checked

**AUC unchanged — correct for sigmoid.** ΔAUC +0.0016, inside the stated 0.01 band.

**ECE much better — refuted.** −0.0060 equal-width and −0.0023 equal-frequency: 6.6% and
2.5% relative. Real, but not "much."

### Refutation conditions

| # | Condition | Outcome |
|---|---|---|
| 1 | AUC moves materially (>0.01) | **fires for isotonic** (−0.0116), not for sigmoid (+0.0016) |
| 2 | ECE gets worse | not met — both improved |
| 3 | ECE improves on equal-width only | not met, but equal-width improved 2.6× more than equal-frequency |
| 4 | isotonic and sigmoid disagree in direction | **fires** — +0.0016 against −0.0116 |

Condition 4 is the one that matters. Both methods are monotonic, so "a monotonic map
preserves ranking" cannot account for a 0.013 spread between them. Isotonic's ties are
moving the ranking, and `CalibratedClassifierCV` refits the base estimator on internal
folds — so the calibrated object is an ensemble, not the same model with a rescaled output.
The predicted *direction* was right for sigmoid; the *mechanism* named was too coarse.

## The unpredicted result

**Cost-weighted risk halved: 0.5440 → 0.2708.** Neither AUC nor ECE moved meaningfully, and
the metric taken from the phase 01 cost table dropped 50%. Calibration pulls probabilities
toward the 3.19% base rate, so far fewer rows cross 0.5 and each one avoided is the 40h
error.

That number is only visible because the inverted cost mapping was found and fixed earlier in
this phase. On the old table it would have moved the other way.

## What it does not survive

The cost improvement is real and it is not enough. See `decisions/07-the-pivot.md`: at no
threshold does the model beat the constant "always hold the release" policy. The calibrated
model's maximum probability is **0.2362** against a cost-optimal threshold of **0.930**.
