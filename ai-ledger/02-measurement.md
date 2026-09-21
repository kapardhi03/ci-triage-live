# AI ledger — phase 02

## Rejected proposal

**Proposal:** Report ECE as the headline calibration number and use it to select between
models. It is the standard calibration metric, it is one number, and it is easy to put in
a dashboard next to accuracy.

**Verdict:** Rejected.

**Reason:** It picks the wrong model, and we ran the numbers to prove it. On the 100-row
toy array at a 3% positive rate:

- base-rate model (predicts 0.03 for everything, catches zero flaky tests): ECE = **0.000**
- perfect ranker (AUC 1.0, recall 1.0, zero cost): ECE = **0.105**

A selection rule that reads ECE alone prefers the model that does nothing, because a model
that never commits is never wrong about its confidence. Calibration measures whether the
stated confidence matches reality; it says nothing about whether the model can tell the two
classes apart. ECE stays in the ladder as a diagnostic, but it may never be read without a
discrimination metric (AUC, recall) beside it.

## Narrowed proposal

**Proposal:** The AI-drafted test for the binning trap asserted
`ece_ew <= ece_ef or ece_ew == pytest.approx(ece_ef, abs=0.01)`.

**Verdict:** Narrowed.

**Reason:** That assertion passes whether the trap is real or not — if both binnings
returned the same value, or if equal-width came out higher but within 0.01, the test still
goes green. It confirmed the code executed; it did not confirm the invariant. Narrowed to
assert the actual observed behaviour: `ece_ew == 0.0` exactly, `ece_ef > 0.01`, and
`ece_ef > ece_ew`. Verified by mutation — collapsing `equal_freq` back into `equal_width`
(the bug that shipped in the original build) now fails the test; under the old assertion it
passed.

## Gap found in review

The cost table's ~13x asymmetry — the single thing carried over from phase 01 — was not
tested at all. Flattening `false_flaky` from 40.0 to 3.0 left all nine tests green. Two
tests added (`test_cost_table_asymmetry_is_enforced`,
`test_abstain_is_cheap_but_not_free`); each of the three cost mutations now kills exactly
one test.
