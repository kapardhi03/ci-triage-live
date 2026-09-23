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
