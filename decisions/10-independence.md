# Decision 10 — independence, derived rather than assumed

## The failure mode the rules come from

Three observers agree that a failure is flaky. The system reports high confidence. If two of
them reached that conclusion from the same underlying event, the confidence is
manufactured — one observation counted twice, arithmetic doing work that evidence did not.

So the question the rules must answer is: **what has to be true for two observers agreeing
to count as two pieces of evidence?**

## The rules, and the failure each prevents

**1. Their inputs must not overlap.**
*Prevents:* two observers reading the same column and reporting it as two findings.
*Status:* holds. The intersection of the three `Reads` lists is **empty**, checked by
`input_overlap`, not asserted.

**2. Their inputs must not share a cause.**
*Prevents:* the failure rule 1 does not catch — disjoint columns driven by one physical
event.
*Status:* **violated, and measured.** `ExecutionTime` predicts whether observer 3 sees the
SSL `NoSuchMethodError` at **AUC 0.6987, p = 1.06e-06**, against observer 1's own
label-prediction AUC of **0.6765**. Observer 1's dominant feature predicts observer 3's
*input* better than it predicts the label observer 1 exists to predict. One JVM/SSL
incompatibility drives both.

This is the rule that matters, and rule 1 passing is precisely why it is easy to miss.
Disjointness of inputs is necessary and **not sufficient**, and this repository now has the
number proving it rather than the principle hoping it.

**3. No observer may read another's output.**
*Prevents:* an echo — observer B agreeing with A because it was told what A said.
*Status:* holds by construction; each observer's `Reads` excludes other observers.

**4. Every probability must declare whether it is calibrated.**
*Prevents:* combining "80% of these turn out flaky" with "this scored 0.8 on something" as
though they were the same quantity. Phase 07 showed how far apart those can be — a model
with AUC 0.678 whose maximum probability was 0.2362.
*Status:* enforced; `Evidence` refuses a probability with `calibrated=None`.

**5. "No evidence" and "evidence points equally" must stay distinct.**
*Prevents:* a coverage gap being read as ambiguity in the world. Phase 09's lookup abstains
on 17.8% of tests because it has never seen the message — that is a gap to fix, not a
finding about those tests.
*Status:* enforced; `NO_EVIDENCE` may not carry a probability.

**6. The case-level decision may not be a statistic over run-level probabilities.**
*Prevents:* the cost asymmetry being inverted by arithmetic. Derived below.

## Why rule 6 is not a style preference

One build produced 197 failures: 196 flaky, one a real defect.

| rule | result | cost |
|---|---|---|
| mean `p_real` | ~0.01 → **SHIP** | ships a defect, **~40h** |
| majority vote | 1 of 197 → **SHIP** | ships a defect, **~40h** |
| **hold-if-any-credibly-real** | **HOLD** | needless hold on 196, **~3h** |

The mean is dominated by the 196 cheap cases while the decision is dominated by the one
expensive case. That is not a rounding error, it is a 13× cost inversion, and it is
*confident* — nothing in the number reveals the problem.

**196 flaky tests do not cancel one real defect.** An averaging rule cannot express that;
hold-if-any-credibly-real can. Both naive implementations are mutation-tested: replacing the
rule with a mean, or with a majority vote, fails `tests/test_contracts.py`.

## How correlated observers are de-duplicated

Every `Evidence` record carries a `cause_group`. Records sharing one collapse to a **single
voice** before anything is aggregated — the most informative record in the group survives,
the rest are counted and dropped, and `deduplicated` is reported alongside the verdict.

Never averaged within a group. Averaging two correlated records still lets one event
contribute twice to the confidence; only collapsing prevents it. Adding a third, fourth and
fifth correlated record leaves the result **identical** — asserted directly in
`test_agreement_from_a_shared_cause_cannot_inflate_confidence`.

Observer 1 and observer 3 are assigned the same `cause_group` on the strength of the
measurement above. That assignment is a judgement about the world, and it is recorded as one:
if the SSL incompatibility were fixed and the coupling disappeared, the grouping should be
revisited, and the frozen constant in the tests is what would force that conversation.

## What this contract does and does not establish

It makes combining observers meaningful. It does not make the observers good.

Three were built and three were matched or beaten by a free alternative — a constant tied
the tabular model, a `sum()` beat the sequence model, one `if`-statement tied retrieval. The
contract is correct machinery around components whose individual value is, on this data,
unproven. Recorded here so phase 11 does not read a working contract as evidence of working
observers.
