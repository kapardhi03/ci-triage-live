# Decision 05 — the trust gate

## Why a run-level gate exists at all

Phase 04 confirmed the labelling rule empirically: `IsFlaky = NumFailingRuns > 0 AND
NumPassingRuns > 0`. One poisoned run is therefore enough to flip a clean test to flaky —
a build that never compiles reports the whole suite as failing, and every test in it
acquires both a pass and a fail.

That also punctures the phase 03 conclusion that a flip is a proof. **A flip is only a
proof if the run that produced it was real.** The positive class, which phase 03 treated as
clean, had never been audited.

## The five verdicts

| Verdict | Meaning |
|---|---|
| `TRUSTED` | outcomes may contribute evidence |
| `BUILD_FAILED` | the build never succeeded; nothing meaningfully ran |
| `LOG_TRUNCATED` | the log is cut off, or the process died before finishing |
| `MASS_FAILURE` | an implausible fraction failed at once |
| `UNKNOWN` | something is off and the cause cannot be established |

`UNKNOWN` is derived, not assumed, for the same reason `ABSTAIN` was in phase 01: two
verdicts had nowhere to put a run that is clearly odd but whose cause cannot be shown.

**A sixth verdict was considered and rejected.** The genuinely new thing found in this
phase is a *test-level* property (deterministic-failing), not a run state. Adding a run
verdict for it would smuggle a test-level fact into run-level vocabulary and blur the
distinction phase 03 drew. Five verdicts, plus a test-level exclusion set.

## Precedence: `BUILD_FAILED` → `LOG_TRUNCATED` → `MASS_FAILURE` → `TRUSTED`, `UNKNOWN` last

Two arguments, and the weaker one is recorded as secondary.

**Feasibility (load-bearing).** `MASS_FAILURE` requires `failed / total`. The denominator
appears only on the Results summary lines, which Maven emits last; tail-truncation removes
them. The numerator is then partial with no bound on how partial, because the line that
would have bounded it is the line that was cut. The fraction is **undefined, not
approximate**, and any improvised denominator makes the verdict depend on where the log
happened to be cut rather than on what the run did. This is not contestable, which is why
it outranks the second argument.

**Cause before symptom (secondary).** A run that never compiled matches both
`BUILD_FAILED` and `MASS_FAILURE`. `BUILD_FAILED` tells a future engineer *no tests ran*;
`MASS_FAILURE` would tell them *many tests failed*, which is false and sends them hunting a
test problem that does not exist. The reason string is the audit trail, and a symptom-first
order fabricates it.

**A consequence worth naming:** the build end-marker also sits at the end of the log, so it
dies in the same cut. A log missing its Results summary is ambiguous between "the archiver
truncated this" and "the process died partway." The gate refuses to assert truncation it
cannot demonstrate, and the reason string says so explicitly rather than picking one.

## The mass-failure threshold: 30%, and it is undefended by evidence

**Reasoning for the number:** below roughly a third, a failing cluster is squarely in the
range ordinary correlated breakage produces — one shared fixture, one bad dependency, one
flaky setup method taking a group of tests down together. That is real failure under phase
03's definition and must be preserved, not discarded. Once a third or more of a suite goes
red in a single run, independent test-level causes stop being a plausible explanation and
something run-wide is more likely.

I deliberately did not anchor on run 6947. Its 9.2% is a reason to keep the threshold
*high*: it has a coherent cluster and a `BUILD SUCCESS`, which is the profile of a genuine
flaky-cluster failure the label should keep. A threshold near 9% would use `MASS_FAILURE`
to discard precisely what this system exists to study.

**What the measurement did to it.** Over 7,905 runs of `kevinsawicki-http-request`:

```
exactly 0%   7700 (97.41%)
     0-2%       0
     2-5%       0
    5-10%     205 ( 2.59%)
   10-100%      0
```

Bimodal. Maximum failure fraction in the project: **9.20%**. Predicted "a thin tail
climbing up, and a gap before the run-wide catastrophes" — first clause right, rest wrong.
There is no climbing tail and no catastrophes.

So 30% is not *wrong*; it is **untested**. Every threshold from ~10% to 100% behaves
identically on this data, and `MASS_FAILURE` fires zero times across both gated projects.
Recorded as a number chosen by argument and unvalidated by evidence. What would be needed
to choose better: a project that actually contains run-wide failures.

## The deterministic threshold: 90% of a project's archived runs

A test red in nearly every run is a deterministic failure on the pinned revision, not
infrastructure noise, and must not inflate any single run's failure fraction.

**This one is validated, exactly.** On `square-okhttp` the gate found **102** such tests
from `maven.log` text alone. `test_results.csv` defines deterministic failure independently
as `NumFailingRuns > 0 AND NumPassingRuns == 0`, and contains **102** such tests. The sets
are identical — intersection 102, gate-only 0, CSV-only 0, Jaccard 1.000. The gate had no
access to the CSV; a fault in module summing, the failed-test regex or the nested-archive
reader would have broken the match.

## The correlated-flake case, and a hypothesis of mine that died

`kevinsawicki-http-request` has 205 failing runs, 15 distinct failing tests, and only **3
distinct failure-set signatures** — 129 runs share an identical 15-test set, 75 share an
identical 13-test set. Eleven tests fail in 100% of the runs where anything fails. The names
cluster by function: every query-param test, plus SSL and proxy tests.

I argued this was a deterministic failure gated by a precondition, and that the exclusion
rule's denominator was therefore wrong — it should be "runs where the cause could manifest,"
not all 7,905 runs.

**Refuted by timing.** Failing runs per 1000-id block: 2.32%, 2.70%, 2.60%, 2.90%, 2.40%,
2.90%, 2.30%, 2.60%. Mean gap between failing runs 37.5 against 38.6 expected under uniform
scatter; 7 adjacent pairs. That is a Poisson process at ~2.6%, not a precondition window.
A transient cause is by definition not reproducible on a schedule — but a *correlated* one
is: one shared fixture flaking 2.6% of the time and taking 15 dependents with it.

So those tests genuinely flip and are genuinely flaky. The all-runs denominator was
correct, and the exclusion set reporting empty for this project was right rather than
myopic.

**What survives is better than the original claim:** those 15 tests are one cause wearing
15 labels. Not contamination in the phase 03 sense, but the positive class counts 15
independent flaky tests where there is plausibly one flaky mechanism. That is an
over-counting problem and it is handed to phase 10, whose job is stopping observers from
treating shared evidence as independent evidence.

## What it cost

Nothing measurable, in this subset. 15,813 runs gated, 36 rejected, and **zero** distinct
failing tests lost. The bill for this gate is paid entirely in the possibility that a
project outside the subset behaves differently.
