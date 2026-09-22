# AI ledger — phase 05

## Rejected proposal

**Proposal:** Read the last `Tests run:` line in the log as the suite total. It is the
final summary, it is what a human reads, and it saves parsing every module.

**Verdict:** Rejected, and it would have silently corrupted every fraction in the phase.

**Reason:** `square-okhttp` emits **5** Results lines summing to **826** tests. Reading the
last one treats a single module as the whole build, so the failure fraction is divided by a
denominator several times too small — which inflates it and trips `MASS_FAILURE` on healthy
runs. The verdict would be wrong *and* its reason would confidently state a total that was
never the suite size.

A second trap sits underneath: lines **with** `Time elapsed` are per-test-class and lines
**without** it are the per-module Results summaries. Summing all `Tests run:` lines
double-counts — 161 + 2 + 163 = 326 for a 163-test suite. The rule is to sum the lines
without `Time elapsed`, one per module. `tests/test_infra.py` asserts both.

## Narrowed proposal

**Proposal (builder's):** The deterministic-exclusion rule keys on the wrong denominator.
The 15 correlated tests in `kevinsawicki-http-request` fail in 100% of the runs where they
fail at all, and only look rare because the denominator is all 7,905 runs rather than "runs
where the cause could manifest." Add a second trigger: an identical reproducible signature
across every run in which it appears.

**Verdict:** Narrowed to nothing by measurement — the hypothesis was good and the data
killed it.

**Reason:** The proposal requires a precondition window: some stretch of runs where the
cause was present. Run IDs are sequential, so that is directly observable. Failing runs per
1000-id block came out at 2.32%, 2.70%, 2.60%, 2.90%, 2.40%, 2.90%, 2.30%, 2.60% — flat.
Mean gap between failing runs 37.5 against 38.6 expected under uniform scatter, with 7
adjacent pairs. Uniform Poisson scatter at ~2.6%, no window.

So the failures are correlated but genuinely intermittent: one shared fixture flaking 2.6%
of the time across all runs. Those tests flip, so under phase 03's definition they are
flaky and must stay in the positive class. The all-runs denominator was right and the
empty exclusion set was correct.

The finding that survives is better than the proposal: 15 labels, one mechanism. Recorded
as an over-counting concern for phase 10 rather than an exclusion rule.

## Corrected during the phase

The builder's stated verdict on the 205-run cluster arrived as `MASS_FAILURE` in the
headline and `TRUSTED` in the argument below it, which explicitly ruled `MASS_FAILURE` out
(9.2% never trips a defensible threshold, and the other 148 tests pass cleanly every time).
The argument was taken. Recorded because the reasoning was right and only the label was
stale.

## Where my own framing was wrong

I opened this phase with the premise that a poisoned run manufactures flaky labels by
reporting unexecuted tests as failed, and that a single compile failure could create 800 of
them. That is the phase's stated rationale and I repeated it as fact.

**It does not happen in this data.** The 36 truncated runs in `square-okhttp` report
`total=127` of 826 and **zero failing tests** — they terminate early rather than marking
unexecuted tests as failed. Across 15,813 runs in two projects, poisoned runs manufactured
**zero** flaky labels. The gate is correct insurance that has never paid out here, and the
motivating story should not be repeated as though the subset demonstrated it.
