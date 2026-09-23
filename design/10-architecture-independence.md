# Slice 10 — integration contract

## Responsibility
Turn many observer opinions about many tests into one release decision, without letting
correlated evidence count twice or flaky mass outvote a real failure.

## Reads
Only `Evidence` records emitted by observers. It never reads features, archives, run
sequences, failure text, or the label — if it could, it would become a fourth observer and
the independence it exists to enforce would be its own to violate.

## Emits
Two outputs at two levels, and they are not the same object.

**Run level** — per test: a collapsed verdict with the evidence that produced it, the
`cause_group`s that contributed, and how many records were de-duplicated away.

**Case level** — per build: `SHIP | HOLD | ESCALATE`, the test that drove it, and the rule
that fired. Never a mean.

## Refuses
It refuses a probability whose `calibrated` flag is unset. Downstream arithmetic depends on
knowing whether 0.8 means "80% of these turn out flaky" or "this scored 0.8 on something",
and that flag is the thing people forget.

It refuses to aggregate two records sharing a `cause_group` as two observations.

It refuses to collapse `NO_EVIDENCE` into `INDETERMINATE`. "I could not look" and "I looked
and it points equally in all directions" are different findings; a uniform distribution
encodes both identically and thereby destroys the distinction.

It refuses to answer the case-level question with a run-level statistic.

## Constraint
**Agreement between correlated observers may not increase confidence**, and **no amount of
flaky evidence may outvote one credibly-real failure.**

Both are measured facts in this repository, not principles:

- Observer 1 and observer 3 have **zero shared columns** and a **shared cause**.
  `ExecutionTime` predicts whether observer 3 sees the SSL `NoSuchMethodError` at
  **AUC 0.6987, p = 1.06e-06** — better than observer 1 predicts the label it is meant to
  predict (0.6765). Disjoint inputs, one physical event.
- The phase 01 table prices a shipped defect at ~40h against ~3h for a needless hold, at a
  3.19% base rate. One real failure among 196 flaky ones must still hold the release.

Both are frozen as constants in `tests/test_contracts.py` and mutation-tested: an
implementation that averages across a `cause_group`, or that lets flaky mass outvote a
credible real failure, must fail.

## Connects to
Consumes slices 07, 08 and 09 through `Evidence`. Consumed by slice 11 (fusion — which may
choose a strategy but may not reintroduce double-counting) and slice 13 (operations, which
audits the evidence record). Depends on slice 01 for the four outputs and the cost table.
