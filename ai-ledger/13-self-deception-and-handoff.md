# AI ledger — phase 13

## Rejected proposal

**Proposal:** Write `FAILURES.md` around the three failures this repository actually had —
the inverted cost mapping, the circular leak test, the unsatisfiable criterion. They are
real, documented, and each has a fix. That is a stronger register than speculation.

**Verdict:** Rejected.

**Reason:** TASK is explicit — *"Write it as a prediction. If you find yourself writing up
something that already happened, that is a different document."* A register of past failures
is a changelog. Its value is that the fixes are already in; its cost is that it teaches
nothing about the next one, because a failure you have already survived is not the one that
will fool you.

The three are kept, marked `ALREADY HAPPENED`, as **evidence that the class is real** — the
calibrator-collapse family is more credible because `kevinsawicki`/200 actually produced AUC
0.5000 with one distinct value. But every entry in the register is forecast, and the
instrument column is what makes each one falsifiable rather than a worry.

## Narrowed proposal

**Proposal:** Do a literature review of flaky-test prediction, then note where this project
agrees and differs.

**Verdict:** Narrowed to five doubt-first searches, per TASK step 2.

**Reason:** A general review finds what the field talks about. A doubt-first search finds
whether **a specific thing I am unsure about** has been settled. The ordering is the method,
and it paid off unevenly in exactly the way that ordering predicts:

- two doubts changed nothing (`ExecutionTime` leak; degenerate cost-optimal policy) —
  recorded as "nothing changed", not dressed up;
- one strengthened a refutation (rerun counts: typical practice is ~20, this corpus used
  10,000, so phase 04's partial refutation of phase 03 is *more* defensible, and phase 03's
  argument would be unrefuted on a normal dataset);
- one confirmed a mechanism (project-disjoint collapse);
- **one found a named remedy for a conceded deficiency** — the double-fault measure and Q
  statistic are established instruments for exactly the correlation `cause_group` assigns by
  hand, and they are cheap enough to have been used.

A general review would have surfaced the fourth at best incidentally.

## What the searches found that outranks the searches

arXiv 2607.09345 independently reproduces **four** of this repository's conclusions on
different detectors: models matching an always-flaky baseline, collapse under project-disjoint
evaluation, data leakage in published evaluations, and detector collapse once non-flaky labels
are rebuilt from repeated execution. It goes further than this repo did, stating that
*"flakiness is not a static property of test code."*

That is the deep version of what phases 07–09 kept hitting. This project found the symptom
— three observers, three free alternatives, zero wins — and stopped at "≈20 failure modes and
one dominant cause." The paper names the cause.

**Recorded as the single most valuable outcome of the honest-reporting discipline:** it is
now much more likely that these negative results are *correct* than that they are an artifact
of working on three projects. Reported with the caveat that I have read the paper's summary,
not its full text.

## What I got wrong across the project, collected

Three things of mine failed silently and none was caught by review:

1. **The inverted cost mapping** (slice 02) — and the test I wrote encoded the same
   misreading in its comments, so it passed while being wrong, for five phases.
2. **The circular leak test** (slice 04) — graded `X.columns` against the module's own
   exclusion dict, so deleting an entry made both sides agree.
3. **The "keep the wide windows" rule** (slice 04) — intuition presented as a finding;
   measured within-project variance is not monotonic in window size.

All three were caught by **deliberately trying to break something**, never by reading. That
is why mutation runs are in slice 13's constraint rather than its nice-to-haves, and why
Family 4.4 of the register predicts this class will recur.

## The uncomfortable summary this phase has to state

Three observers were built. Three were matched or beaten by a free alternative. Fusion added
nothing — four strategies, one decision rule. The fine-tune was gated out on evidence. The
shipped component is a dictionary lookup that abstains on 17.8% of cases.

**The system does not work, and the repository says so in every file.** That is the
deliverable. A version of this project that reported 0.7569 and a working three-observer
ensemble would have been easier to write, more impressive to read, and wrong.
