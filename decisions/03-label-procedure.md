# Decision 03 — how a label is produced, and what it is worth

## The procedure

No human judged these tests. No engineer read `testUserSessionTimeout` and ruled on its
character. Every label in the dataset came out of a machine running this:

1. Take a test and one commit. The code does not change.
2. Run the test N times.
3. If the test both passed **and** failed across those N runs, write `flaky`.
4. Otherwise, write `not flaky`.

**N is currently unknown.** It is not recorded anywhere I have looked, and I am being asked
to trust every row in the file without it. Finding N is carried into phase 04 as a required
question, not an optional one. Until it is known, `detectable_floor` is null for every
negative row in the corpus.

## The asymmetry

The two branches of step 3/4 do not prove the same kind of thing.

**It flipped.** Identical code produced two different outcomes, and the procedure witnessed
it directly. There is no explanation for that except non-determinism — a race, a timeout, a
clock, a port, a shared fixture. This is a proof. It required no inference and no sample
size argument. Caught in the act.

**It did not flip.** The honest statement of what happened is: *no flip occurred in N runs.*

That is not the same sentence as *this test cannot flip.* Nothing was observed. An event
failed to occur within a budget, and then `not flaky` was written into a CSV as though a
property had been established.

So the labels are one-sided:

| CSV value | What actually happened | Worth |
|---|---|---|
| `flaky` | a contradiction was witnessed | **proof** |
| `not flaky` | a search ended without finding one | **bound** |

## What N actually buys

A rerun count never buys "not flaky." If a test flips with probability `p`, the chance of
catching it in N runs is:

```
P(catch) = 1 - (1 - p)^N
```

So N buys one sentence: *not flakier than roughly 1-in-N.* It is not a confidence level.
It is a choice about **which flip rate you have agreed to ship.**

Worked on a 1-in-500 race:

| N | P(catch) | consequence |
|---|---|---|
| 100 | 18% | **82% chance it is mislabelled `not flaky`** |
| 1,500 | 95% | caught |

## Pricing the truth

My sign-off number: **250–500 reruns** before I would personally accept `not flaky`. It is
budget-dependent and I would raise it for a release-critical suite.

Costed at N = 500. All inputs are guesses and all are arguable:

| input | value |
|---|---|
| suite size | 3,000 tests |
| suite wall-clock | 20 min |
| CI runner | ~$0.008/min |

- **One project, one commit:** 500 runs × 20 min = 10,000 runner-minutes ≈ 167 runner-hours
  ≈ **$80**. Seven days serial, ~3 hours across 50 runners.
- **25-project corpus:** ≈ **$2,000**, ~4,200 runner-hours, ~174 days of serial CI.

$2,000 is not a shocking number, and I am not going to pretend it is. Cloud CI is cheap.
The bill is not where this hurts. Three other things are:

1. **What the money bought is narrower than it sounds.** $2,000 certifies *no test flips
   more often than about 1-in-500, on this exact commit.* A 1-in-5,000 race walks through
   untouched — and those are precisely the ones that surface under production load rather
   than under CI, at 02:47. Excluding 1-in-5,000 needs N ≈ 15,000: **≈ $60,000** and ~5,200
   days of serial CI. Excluding 1-in-50,000 costs thirty times that again.
2. **It is stale on the next commit.** The label was only ever valid for the code it ran
   against. Merge anything and every negative row becomes an extrapolation.
3. **No finite N finishes the job.** Every budget buys a threshold, never a proof. The
   negative class cannot be made clean at any price. Its contamination can only be pushed
   down to rarer and rarer flakes.

## The decision

**`not flaky` is not a label. It is a budget, written down as if it were a fact.**

Every negative row is therefore carried with its basis attached (slice 03), and the
evaluation consequences are recorded in experiments/03-rerun-bias.md.

## Alternative considered

Trusting the negative class more than the positive class, on the grounds that it is the
class the system mostly has to get right and the one I care about operationally.

Rejected. That confuses *which class matters* with *which label was proven*. The concern
about the negative class is correct and worth keeping — it is ~97% of the rows — but the
reason to look at it is that it is **contaminated**, not that it is trustworthy. Those two
readings point at the same column and lead to opposite conclusions.
