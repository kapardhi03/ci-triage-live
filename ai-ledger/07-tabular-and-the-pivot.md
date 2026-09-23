# AI ledger — phase 07

## Rejected proposal

**Proposal:** Report AUC 0.678 as the observer's result and move on. It beats chance, it is
in the range tabular flaky-test papers report, and a component that ranks is a component
that contributes — fusion in phase 11 can decide what to do with it.

**Verdict:** Rejected.

**Reason:** AUC measures ranking; the system takes actions. At every threshold, calibrated
or not, the observer fails to beat "always hold the release" — cost 0.0957 h/row against
0.0957 h/row, identical to four decimals. Reporting 0.678 without that sentence would let a
reader infer the component is useful, which the same evidence refutes.

The honest form is both numbers together: it ranks at 0.678 and it cannot act. Phase 02
built the ruler that can tell those apart, and this is the first time the distinction has
had consequences.

## Narrowed proposal

**Proposal (builder's):** Change the question — abstain on alien projects and report
risk–coverage.

**Verdict:** Run and refuted, kept as chosen.

**Reason:** The reasoning was right and the opportunity was absent. Abstention is charged at
1.5h on every covered row while the model's errors cost 0.0957 h/row, so the pivot pays 1.5
to avoid 0.096. The cost-minimising qualifier threshold is 0.00 — abstain on nothing.

The ceiling is what settles it: an oracle qualifier that knows each project's true cost
abstains on one project and saves **2.7%**. The qualifier is not underperforming; there was
nothing to find. Recorded as refuted rather than rescoped into a smaller success.

## Corrected during the phase — a bug of mine from phase 02

`cost_weighted_risk` had the cost mapping **inverted** against the label. `IsFlaky == 1` is
flaky; `== 0` is a real defect. Phase 01 prices *real defect called flaky* at 40h and *flaky
called real defect* at 3h. The module charged them the other way round, and its comment
asserted `y == 1` meant "real defect."

It survived because phase 02 only ran the function on toy arrays where nothing pinned
`y = 1` to a meaning, and the asymmetry test I wrote encoded the same misreading in its own
comments — passing while wrong. The same self-referential failure as phase 04's circular
leak test, in a different module. Two of these now.

Worse than a factor of 13: inverted, the table makes missing a flaky test expensive and
shipping a defect cheap, so anything tuned against it optimises *toward* the 40h error. It
did not merely misreport cost, it aimed the system at the wrong mistake. Fixed, direction
pinned by a test, and flipping it back now fails two tests. `decisions/02` and `knowns/02`
carry appended corrections.

## What the builder got right before the measurement

Two things, both recorded in `design/07` before any model was fitted.

**The qualifier must not be the model's own confidence.** A model on an unseen project does
not know it is on an unseen project; it is most confident exactly where it is least
entitled to be, so gating abstention on self-reported confidence abstains on the cases it
is unsure about and waves through the cases it is wrong about. This held up — and the
design survives the pivot's refutation, because what failed was the economics, not the
reasoning.

**The `ExecutionTime` coupling.** Predicted unprompted: distance is computed on standardised
features, `ExecutionTime` will dominate it, and it is also the pre-registered leak suspect —
so if it leaks, the observer and its own safeguard fail in the same direction. Measured:
`ExecutionTime` drives **39.4%** of the distance, three times the next feature. The coupling
is real.

## Not done, deliberately

The 40/3/1.5 cost numbers dominate every result in this phase and were flagged in
`knowns/01` as guesses needing real incident data. They were **not** revisited. Changing
them now, because the model looks bad, is the dishonest option the phase README names.
Recorded as open.
