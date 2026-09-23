# AI ledger — phase 10

## Rejected proposal

**Proposal:** Fuse the observers by averaging their probabilities, weighted by each
observer's validation AUC. It is the standard ensemble move, it is easy to explain, and the
weights make it principled.

**Verdict:** Rejected on two independent grounds, both measured.

**Reason 1 — it double-counts a shared cause.** Averaging assumes the things being averaged
are separate observations. Observer 1 and observer 3 have **zero shared columns** and
`ExecutionTime` predicts whether observer 3 sees the SSL `NoSuchMethodError` at **AUC
0.6987, p = 1.06e-06** — higher than observer 1's own label-prediction AUC of 0.6765. One
JVM/SSL incompatibility drives both. Averaging their agreement makes the system more
confident on the basis of nothing new, and weighting by AUC makes it *worse*, because the
correlated pair are the two highest-AUC observers.

**Reason 2 — it inverts the cost asymmetry at the case level.** With 196 flaky tests and one
real defect, the mean `p_real` is ~0.01 and a majority vote sees 1 of 197. Both **SHIP** a
~40h defect to avoid a ~3h hold, confidently. The mean is dominated by the cheap cases while
the decision is dominated by the expensive one.

Both naive implementations are mutation-tested and fail the suite.

## Narrowed proposal

**Proposal:** Since the inputs are disjoint, the observers are independent; a check that the
three `Reads` lists do not intersect is sufficient.

**Verdict:** Narrowed — the check is kept, its sufficiency is rejected.

**Reason:** The check passes. The intersection is genuinely empty, and that is exactly why
the real coupling was nearly invisible. Disjoint inputs are **necessary and not sufficient**,
and this repository now has a number saying so rather than a principle. `input_overlap` is
retained, and `test_disjoint_inputs_do_not_imply_independent_evidence` asserts both facts
side by side so the insufficiency cannot be forgotten.

## Conceded in review

`cause_group` is **hand-assigned**. One correlation was measured, on one project, between
two of the three observers, and the grouping was typed in by a human. The contract enforces a
grouping; it does not detect one. No pairwise coupling was computed for observer 2 at all,
so if observers 2 and 3 share a cause the contract will happily count them twice.

A design that recomputed groupings from observed output covariance would be strictly better
and is not what was built. What this one buys instead: the grouping is explicit, named in
every record, and the justifying measurement is **frozen as a constant in the tests**. If the
SSL incompatibility is fixed and the coupling vanishes, `SHARED_CAUSE_AUC` fails and forces
the conversation. Weaker than detection, stronger than a principle, and it cannot drift
silently.

## What the contract does not establish

Three observers were built; three were matched or beaten by a free alternative. The contract
makes combination *meaningful*, not *valuable*. Recorded so phase 11 does not mistake a
working contract for working components.
