# Experiment 11 — five fusion strategies

**Written 2026-09-23, before any strategy was implemented.** Appended to after the run,
never edited.

## The frozen case set

202 `square-okhttp` tests — every test all three observers can speak about.
**`sha256[:16] = 305d8ece8a0fa240`**, 100 flaky / 102 deterministic, base rate **0.495**.

Every ranked strategy must run on all 202, with the same labels and the same metric
implementation from slice 02. A strategy that does not is `incomplete` and unranked.

## The strategies

| | strategy |
|---|---|
| A | most-confident-wins — take the observer furthest from 0.5 |
| B | mean of the probabilities |
| C | threshold rule |
| D | escalate-on-disagreement — agree → use it; disagree → ABSTAIN |
| E | LLM arbiter |

**E is `incomplete` before the run.** No `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` or
`GEMINI_API_KEY` is set and no SDK is installed. Its predicted position is recorded below
and will never be checked — which is the honest outcome, not a gap to be filled by
inference or by substituting `precomputed/fusion-comparison.json`.

## The prediction

**Accuracy, best → worst:**  `C > D > A > B`   *(E predicted 2nd, between C and D)*

**Calibration, best → worst:**  `B > D > A > C`   *(E predicted near-worst)*

### The committed claim

**The two rankings nearly invert.** C tops accuracy and bottoms calibration; B mirrors it,
bottoming accuracy and topping calibration. If that holds, **a single scoreboard is
dishonest here** — reporting one number would pick a winner by choosing a metric rather than
by measuring.

This is falsifiable: if the orderings turn out to agree, the claim is refuted and one
scoreboard would have been fine.

### Reported alongside

- **Coverage for D**, next to its accuracy. A strategy that abstains buys accuracy on the
  cases it keeps, and an accuracy figure without coverage is not comparable to one from a
  strategy that answered everything.
- **Both metrics for every strategy.** No composite.

### Base-rate caveat, stated before the result

These 202 cases are **49.5%** positive. Deployment is **3.16%**. Whichever strategy wins
here is likely flattered relative to deployment, and the gap is not a constant offset — a
threshold tuned at 49.5% can invert at 3.16%.

## What would refute the reasoning

1. **The two rankings agree.** The committed claim is wrong and a single scoreboard was
   adequate.
2. **B wins accuracy outright.** Averaging correlated evidence would be beating the
   alternatives on the metric it was predicted to lose — and slice 10 forbids B at case
   level on cost grounds, so it would force that decision to be re-argued.
3. **D's advantage disappears once coverage is accounted for.** If D answers far fewer cases
   for the same accuracy, its ranking is bought, not earned.
4. **Every strategy lands within noise of every other.** With 202 cases and ~19 distinct
   failure messages, the effective sample is small enough that this is a live possibility,
   and it would mean the fusion question is unanswerable on this data rather than answered.

## Divergence

Disagreement is measured between **distributions, not labels** — two observers can emit the
same label from completely different beliefs. Measure and justification recorded in
`decisions/11-arbiter-rules.md`.

---

## Result

*(appended after the run — empty at the time of prediction)*

**Appended 2026-09-23 after the run. Nothing above this line was edited.**

## The result

| strategy | accuracy | ECE | coverage | n |
|---|---|---|---|---|
| A most-confident | 0.9554 | 0.0435 | 100% | 202 |
| B mean | 0.9554 | 0.0914 | 100% | 202 |
| C threshold | 0.9554 | 0.0446 | 100% | 202 |
| **D escalate-on-disagreement** | **0.9940** | **0.0071** | **82.2%** | 166 |
| E LLM arbiter | — | — | — | **incomplete, unranked** |

```
ACCURACY    predicted  C > D > A > B      actual  D > A = B = C   (A,B,C tied exactly)
CALIBRATION predicted  B > D > A > C      actual  D > A > C > B
```

## The committed claim is refuted

> *"The two rankings nearly invert. C tops accuracy and bottoms calibration, B mirrors it."*

**Wrong, and there is no ordering left to invert.** A, B and C tie on accuracy to four
decimal places. D tops *both* rankings and A is second in *both* — they agree. B, predicted
best on calibration, came **last** (0.0914). C, predicted best on accuracy, is tied last.

So a single scoreboard would have picked D on either metric. The claim that reporting one
number would be dishonest is not supported by this data — though reporting D's accuracy
without its coverage still would be, for the reason below.

## Two refutation conditions fired

**Condition 4 — "every strategy lands within noise of every other."** Fired, and harder than
predicted. A, B and C do not merely score similarly; they emit **identical labels on
202/202 cases**. They are one decision rule wearing three probability shapes, which is
exactly why their ECE differs and their accuracy cannot.

**Condition 3 — "D's advantage disappears once coverage is accounted for."** Fired
decisively:

```
                on all 202      on D's covered 166
  A               0.9554              0.9940
  B               0.9554              0.9940
  C               0.9554              0.9940
  D                  —                0.9940
```

On the same 166 cases every strategy scores **identically**. D's entire advantage is *which
cases it declines*, not how it decides them — and it declines exactly the 36 where the
lookup has no entry. Its 0.9940 is phase 09's `MessageLookup` result, reproduced.

## Why fusion had nothing to fuse

```
tabular    min 0.0065   max 0.1609   152 distinct   calibrated
sequence   min 0.0000   max 1.0000    14 distinct
lookup     min 0.0000   max 1.0000     8 distinct   (166/202 covered)
```

**The tabular observer's maximum probability across all 202 cases is 0.1609.** It never
crosses 0.5, so it cannot change a single decision at that cutoff — phase 07's finding
arriving inside the fusion layer.

And slice 10 collapses `tabular` with `lookup` (shared `cause_group: ssl-jvm`), so fusion
runs over **two voices, never three** — mean 2.00, max 2, with 166 records de-duplicated
away. The lookup wins that collapse 161 times of 202.

Two voices, one of which is inert. There was never three-way evidence to combine.

## Not invented

E is `incomplete`. No API key, no SDK, nothing ran. Its predicted position — 2nd on
accuracy, near-worst on calibration — stands recorded and **unchecked**. It is not ranked
last, not interpolated, and `precomputed/fusion-comparison.json` was not substituted for it.

The prompt it would have received is rendered and audited in `decisions/11-arbiter-rules.md`
anyway, because TASK step 5's requirement to read every character is the only way to check
the forbidden-to-see rules against an artefact rather than an intention.

## The base-rate caveat, still standing

These 202 cases are 49.5% positive; deployment is 3.16%. Every number above is flattered,
and D's abstention economics in particular invert: phase 07 measured abstention as a loser
at 1.5h/row against 0.0957h/row of error at the deployment base rate.
