# AI ledger — phase 03

## Rejected proposal

**Proposal:** Since the negative class is contaminated and the positive class is not, drop
the negatives from model selection entirely. Choose models on the trustworthy positives
only — the labels you can actually defend.

**Verdict:** Rejected.

**Reason:** It over-corrects by an enormous margin. The negative class is ~97% of the rows,
and the contamination in it is plausibly a few percent of that class. Discarding all of it
to avoid a minority error leaves almost nothing to train or select on, and it throws away
every clean negative — which is most of them — along with the hidden flakes.

The contamination is a reason to *read* the negatives carefully, not a reason to delete
them. Targeted reruns fix the specific rows that are wrong; deleting the class destroys the
rows that are right.

## Narrowed proposal

**Proposal:** Adopt "precision is always reported as a lower bound, never a point value" as
the constraint carried into lab 05.

**Verdict:** Narrowed — demoted from primary constraint to corollary.

**Reason:** As a competing option it is too weak. It only annotates data already in hand;
it never produces a better number, and a lab that only ever reports bounds stops being able
to compare models. The primary constraint is targeted reruns, which generate new
information and are affordable.

But it cannot be rejected outright either, which is where my own first instinct was wrong.
It is not a strategy competing with the reruns — it is a **fact about the data** that holds
regardless of which strategy is chosen. Until a given false positive has actually been
reran, its true status is unknown and precision over that set genuinely is a bound. So it
stands as the condition that holds while the rerun budget is unspent.

## Corrected during the phase

My first reading of the two rerun outcomes was inverted: I treated the consistent
(no-flip) result as settled and the mixed (60/40) result as the ambiguous one needing the
phase 01 abstain treatment.

It is the other way round. A flip is a witnessed contradiction and proves flakiness
outright; a run of no-flips proves only that no flip occurred within a budget. The abstain
instinct was correct and was pointed at the wrong branch — thin evidence for a confident
call is the *no-flip* case.

Related slip: I reached for "we get more accurate results" as a justification, having
already rejected accuracy in writing in ai-ledger/01-decision-and-cost.md for exactly the
reason that applies here.
