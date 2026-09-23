# Decision 07 — the pivot, and its refutation

## The number that forced the decision

Gradient-boosted tree, 13 features, leave-one-project-out, calibrated:
**AUC 0.6781 ± 0.159.**

Phase 06's logistic regression scored **0.6878** on the same split. **The stronger model is
worse.** Two hundred boosting iterations bought less than nothing on unseen projects.

## Every honest response, and what happened to it

TASK lists four. All four were tested rather than argued.

| Option | Outcome |
|---|---|
| accept it and ship a weak component | it **loses money at every threshold** — see below |
| get better features | phase 06 already dropped 8 that were actively harmful; the remaining 13 peak at 10% precision |
| get more data | oracle abstention caps the available gain at **2.7%**; there is nothing there to find |
| **change the question** | **chosen, run, and refuted** |

## The pivot, chosen from PROBLEM.md

The argument was not from the metric. Phase 01 gave this system four outputs, one of which
is ABSTAIN at ~1.5h against ~40h for a wrong "flaky" call, and phase 02 built a
`risk_coverage` function that nothing had yet called. So: **stop asking this observer to
classify every red build. Abstain on alien projects and report risk–coverage.**

## Why it failed

Abstention is charged at 1.5h on **every** covered row. The model's errors cost **0.0957
h/row** on average. The pivot pays 1.5 to avoid 0.096.

| qualifier threshold | coverage | cost/row |
|---|---|---|
| 0.00 (no abstention) | 100.0% | **0.0957** |
| 0.25 | 90.7% | 0.2153 |
| 0.55 | 88.4% | 0.2332 |
| 0.72 | 66.4% | 0.5507 |
| 1.01 (abstain everything) | 0.0% | 1.5000 |

**The optimum is not to abstain at all.** And the ceiling is not much better: an oracle
qualifier that knows each project's true cost abstains on exactly one project (`alluxio`,
the only one where covering costs more than 1.5h) and saves **0.0026 h/row — 2.7%**.

The qualifier itself is weakly informative in the right direction — Spearman(qualifier,
cost) = **−0.357**, Spearman(qualifier, AUC) = **+0.323** — and far too weak to act on. It
abstains on `activiti` (2,044 rows, cost 0.047) while covering `hector` (cost 0.697,
qualifier 0.825). But fixing it would not help, because the ceiling is 2.7%.

**The design was sound and the opportunity was absent.** Building the qualifier on
distributional distance rather than model confidence was the right call — a model on an
unseen project is most confident where it is least entitled to be — and it remains right.
There was simply nothing for it to buy.

## The deeper finding: the model is the constant baseline

```
"always say real defect"  :  825/25867 = 3.1894%  ->  0.0957 h/row
the calibrated GBT        :                          0.0957 h/row
```

Identical to four decimals. The model has AUC 0.678 and at threshold 0.5 it **never once
predicts flaky**, so its decisions are indistinguishable from a constant.

Work the boundary from the phase 01 table. Predict flaky only when it is cheaper:

```
40 × (1 − p)  <  3 × p     →     p > 0.930
```

**The cost-optimal threshold is 0.930.** The calibrated model's maximum probability across
25,867 rows is **0.2362**. It never comes close.

Swept exhaustively, neither model beats the constant at any threshold:

| | max p | rows ≥ 0.93 | best threshold | beats constant? |
|---|---|---|---|---|
| calibrated | 0.2362 | 0 | 0.2365 → flags 0 rows | **no** |
| uncalibrated | 0.9765 | 10 | 0.9770 → flags 0 rows | **no** |

The uncalibrated model *can* reach 0.93, and doing so costs **+0.0155 h/row (≈ +401h)** —
consistent with ten false "flaky" calls at 40h each.

## Precision is the whole story

| top-k most confident "flaky" | truly flaky |
|---|---|
| 10 | **0/10 — 0.0%** |
| 25 | 1/25 — 4.0% |
| 50 | 3/50 — 6.0% |
| 100 | 10/100 — 10.0% |
| *base rate* | *3.19%* |

The ten predictions the model is most certain about are **all wrong**. Precision peaks near
10% — genuinely 3× base rate, so the signal is real — against a cost table demanding 93%.

**The observer has information and cannot act on it.** AUC 0.678 is not a lie and is not
worth anything here. The gap between "beats chance" and "beats doing nothing" is a factor
of nine in precision.

## What was not done, and why

The cost table could be revisited. The 40/3/1.5 numbers were guesses, `knowns/01` flagged
them as needing real incident data, and they now dominate every result in this phase.

**Not touched.** Revisiting them now, because the model looks bad, is the dishonest option
the phase README warns about. Any change to those numbers has to be argued from the
organisation and its incidents, not from a metric it would improve. Recorded as an open
item, not exercised.

## What this decision costs

A component that does not work, reported as a component that does not work.

It is also the strongest argument the project has yet produced **for** its own architecture.
One weak observer cannot clear a 93% precision bar. That is the reason phases 08–11 exist,
and it is now an empirical claim with a number attached rather than a design intuition.

Slice 10's independence question is sharper than expected: removing `ExecutionTime` drops
the model from 0.6765 to **0.5577**, so this observer is effectively one feature. Three
observers are only three observers if they do not all reduce to the same column.
