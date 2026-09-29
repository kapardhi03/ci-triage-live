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

---

# Extension: the arbiter, with real evidence

**Written 2026-09-29, before any arbiter code existed.** The 90-minute challenge. Appended
to after the run, never edited.

## What changed since the phase 11 run

Nothing about the experiment. An API key became available, so strategy E can complete on
the same frozen 202 cases. **The case list, the labels, the metric implementation and the
four completed strategies are untouched** — `sha256[:16] = 305d8ece8a0fa240` must come out
identical or the run is void.

## The hypothesis is not written now

It was written at commit **`99516bd`**, before any strategy was implemented:

> **E predicted 2nd on accuracy, between C and D. Near-worst on calibration.**

That prediction stands as recorded. Writing a fresh one now, with the other four results on
screen, would be prediction after the fact wearing a timestamp.

## Setup

- **Model:** `gpt-4o-mini`, temperature 0, pinned model string in the `run_id`.
- **Cost:** 202 calls × 677 input tokens ≈ **$0.023** at $0.15/$0.60 per 1M
  ([developers.openai.com/api/docs/pricing](https://developers.openai.com/api/docs/pricing),
  fetched 2026-09-29). Cost is not a constraint, so this decides on evidence or not at all.
- **Output mapping:** `AGREE_FLAKY → 1.0`, `AGREE_REAL_DEFECT → 0.0`, `ESCALATE → abstain`.
  The same shape `C_threshold` and `D_escalate_on_disagreement` already have, scored on the
  identical metric implementation. Scoring a categorical choice is not inventing a
  confidence; `design/11`'s ban on manufacturing a probability is intact.
- **Ship-direction rule, absolute:** where collapsed evidence points `REAL_DEFECT`, the
  arbiter may confirm or escalate, **never** move toward `FLAKY`. The wrapper refuses; the
  refusal is counted.

## Recorded limitation, accepted in advance

**An LLM breaks this repository's reproducibility standard.** `run_id` hashes split,
estimator, features, label, seed and data digest; a model has no seed guarantee, so an
identical `run_id` no longer implies identical numbers.

Mitigation: temperature 0, the model string inside the `run_id`, and **every raw response
stored per case**, so the run is *auditable* even when it is not *re-derivable*. This is
weaker than every other result in the repository and is recorded as such rather than
presented as equivalent.

## The controls

1. **Strategy D** — the current best, 0.9940 at 82.2% coverage.
2. **The null arbiter** — a stub returning the most-confident collapsed voice. No model, no
   cost, no network. **This is the control that matters**, and the one the record says will
   win: a constant tied the tabular model, a `sum()` beat the GRU, one `if`-statement tied
   MiniLM.

## Abandonment condition

**Withdraw the arbiter if any of these fire:**

1. **It ties the null control.** Accuracy and ECE within fold noise of the stub → it added
   nothing, the phases 07/08/09 finding a fourth time, and it ships as `withdrawn` rather
   than as a strategy.
2. **It cannot complete all 202.** Timeouts, refusals, or unparseable output on any case →
   `incomplete` and unranked, the same rule that kept it out of the phase 11 table.
3. **The ship-direction clamp fires on more than ~5% of cases.** The arbiter is then
   **unsafe regardless of its accuracy** — it is repeatedly trying to relax caution, and the
   only thing stopping it is a guard it does not know exists.

Condition 3 is the one that earns its place. Accuracy could look healthy while the model
systematically pushes toward the expensive error, and nothing in the accuracy number would
show it. **The clamp rate is therefore a reported result, not merely a safety mechanism.**

---

## Result

*(appended after the run — empty at the time of writing)*

**Appended 2026-09-29 after the arbiter run. Nothing above this line was edited.**

## The result

| strategy | accuracy | ECE | coverage | n |
|---|---|---|---|---|
| A most-confident | 0.9554 | 0.0435 | 100% | 202 |
| B mean | 0.9554 | 0.0914 | 100% | 202 |
| C threshold | 0.9554 | 0.0446 | 100% | 202 |
| D escalate-on-disagreement | 0.9940 | 0.0071 | 82.2% | 166 |
| **E0 null arbiter** (control) | **0.9554** | **0.0435** | 100% | 202 |
| **E LLM arbiter** (`gpt-4o-mini`) | **0.9904** | **0.0096** | **51.5%** | 104 |

Frozen hash **`305d8ece8a0fa240`** verified — the inputs were rebuilt from the raw archives
by `ci_triage/evidence.py` and reproduce the case list exactly.

**Read naively, E has the second-best accuracy and the second-best calibration in the
table.** It is withdrawn anyway.

## Both abandonment conditions fired

### Condition 1 — it ties the null control

```
arbiter    on its own 104 covered cases:  0.9904
null stub  on the SAME 104 cases:         0.9904
```

**Identical.** A stub that returns the most-confident collapsed voice — no model, no
network, no cost — decides those cases exactly as well. The phases 07/08/09 finding for the
fourth time: a constant tied the tabular model, a `sum()` beat the GRU, one `if`-statement
tied MiniLM, and now a free stub ties an LLM.

### Condition 3 — the ship-direction clamp fired on 24.3%

**Threshold was ~5%. Measured: 49 of 202.**

The model's raw output distribution: **`AGREE_FLAKY` 121, `ESCALATE` 49,
`AGREE_REAL_DEFECT` 32.** It wants to say flaky.

```
model said AGREE_FLAKY against REAL_DEFECT evidence :   49   (24.3%)
  of those, genuine REAL DEFECTS                    :   44
  unclamped: 44 x ~40h  =  1,760 engineer-hours of shipped bugs, on 202 cases
```

**The only thing preventing that was a guard the model could not see.**

And the coverage is not what it looks like. Reported 51.5%, but of the 98 abstentions
**exactly half are the clamp, not the model's judgement** — 49 escalations it chose, 49
refusals imposed on it. Its willingness to decline is overstated by a factor of two.

## Why this is the result the condition was written for

Condition 3 was recorded before the run as:

> *"Accuracy could look healthy while the model systematically pushes toward the expensive
> error, and nothing in the accuracy number would show it."*

That is precisely what happened. **Accuracy 0.9904 and ECE 0.0096 are the second-best
figures in the table, and they are produced by a component that tried to ship 44 real
defects.** No metric on the phase 02 ladder would have revealed it. The clamp rate is the
only instrument that sees it, and it exists only because the rule was written down first.

## The pre-registered prediction was wrong, and it does not matter

`99516bd` predicted **2nd on accuracy, near-worst on calibration.** Measured, E would rank
**1st or 2nd on both** if the headline numbers were read at face value. The prediction is
kept unedited and recorded as wrong.

It does not change the outcome, because the strategy is withdrawn on **safety**, not on
rank — which is itself the finding. A ranking table would have promoted it.

## Reproduction

```bash
uv run python -m ci_triage.evidence        # rebuild frozen inputs from data/raw, verify hash
uv run python -m ci_triage.arbiter_run     # run E0 and E, write results + every raw response
uv run pytest tests/test_fusion.py -q      # the clamp invariant, no network
```

`gpt-4o-mini`, temperature 0, 202 calls ≈ **$0.023**. Every raw response is stored in
`artifacts/results/arbiter-responses.json`.

## What this does not prove

- **One model, one prompt, one temperature.** A different model, or a prompt that argued
  harder for caution, might clamp less. Untested.
- **49.5% base rate, not deployment's 3.16%.** The ship-direction rule is *more* important at
  3.16%, not less, so the concern does not shrink — but the numbers do not transfer.
- **The clamp is a wrapper, not a property of the model.** Nothing here shows the arbiter
  could be made safe; it shows that this one, unguarded, was not.
- **Non-reproducible by construction.** Temperature 0 and a pinned model string reduce
  variance; they do not guarantee identical output. The stored responses make the run
  auditable, not re-derivable.

---

# Extension 2: does the clamp rate survive a cautious prompt?

**Written 2026-09-29, before the variant ran.** One variable.

## The question this settles

Extension 1 left it open: *"Does the 24.3% clamp rate drop with a prompt that argues for
caution, or is it a property of the model?"* It decides whether "LLM arbiter" is a **bad
idea** or a **badly-prompted one**, and the first run cannot tell them apart.

## The one variable

Identical: the evidence-record rendering byte for byte, the `cause_group` note,
`gpt-4o-mini`, temperature 0, `max_tokens` 8, the same 202 frozen cases
(`305d8ece8a0fa240`), and the clamp and how it is counted.

Changed: the instruction block now carries the phase 01 cost table and names `AGREE_FLAKY`
as the expensive error — ~40h against ~3h and ~1.5h, roughly 13× and 27× — and tells the
model that escalating is cheap and is not a failure.

Nothing else. Cost ≈ $0.03.

## The prediction

**Clamp rate falls below 5%.**

Reasoning: the baseline prompt never told the model that `AGREE_FLAKY` is the expensive
error. It was choosing between three words with no stated consequences. Given the costs
explicitly, it should become appropriately cautious.

**If it holds:** the verdict is *badly-prompted, not a bad idea* — and the arbiter is worth
a second look with the cost table baked in, rather than withdrawn outright.

## What each outcome means, fixed in advance

| measured clamp rate | verdict |
|---|---|
| **< 5%** | prompting fixes it. The tendency was an instruction gap, not a model property. |
| 5–15% | partly instructable, partly intrinsic. The clamp stays mandatory either way. |
| 15–25% | the pull toward FLAKY survives being told it is 13× costlier — a model property. "Bad idea", not "badly prompted". |
| > 25% | naming the costs made it **worse**. Least expected, most interesting. |

## What it still will not prove

One model, one cautious phrasing, one temperature. A drop would show *this* wording helps on
*this* model — not that the arbiter is safe, and not that the clamp could be removed. The
clamp is what makes the measurement possible; it is not a result about whether the clamp is
needed.

**Appended 2026-09-29 after the cautious variant ran. Nothing above this line was edited.**

## The result

```
E0 null control   acc 0.9554   ECE 0.0435   coverage 100.0%   clamp   n/a
E  baseline       acc 0.9901   ECE 0.0099   coverage  50.0%   clamp 43/202 = 21.3%
Ec cautious       acc   n/a    ECE   n/a    coverage   0.0%   clamp  0/202 =  0.0%
```

**The cautious variant output `ESCALATE` 202 times out of 202.** Not one decision.

```
baseline raw:  AGREE_FLAKY 111 | ESCALATE 58 | AGREE_REAL_DEFECT 33
cautious raw:  ESCALATE 202
```

## The prediction's number was right and its verdict was wrong

Predicted **< 5%**. Measured **0.0%**. The band was hit exactly — **by total abstention.**

The pre-registered interpretation said *"< 5% → prompting fixes it. The tendency was an
instruction gap, not a model property."* **Refuted.** Nothing was fixed. A component that
escalates on every case has zero coverage and decides nothing; it is the
**ESCALATE-everything constant**.

Phase 02's lesson for the fifth time: the safe-looking policy scores perfectly on the safety
metric by refusing to do the job. A constant predictor was 96.84% accurate in phase 04, the
tabular model *was* the constant in phase 07, and now the "cautious" arbiter is a constant
too.

## The interpretation rule had the flaw it was written to catch

The rule measured **only the clamp rate**. It had no coverage floor, so a policy that never
decides anything satisfies it perfectly.

That is the fourth instance in this repository of a check that can be passed without the
thing it checks being true — after the circular leak test (phase 04), the self-referential
cost test (phase 07), and the unsatisfiable keep criterion (phase 08). **This one was
written during the phase whose entire subject is that failure mode**, and it still happened.

The rule should have read: *clamp rate < 5% **at coverage ≥ 50%**.*

## The baseline is not a stable measurement

Three runs, identical configuration — `gpt-4o-mini`, temperature 0, same prompt, same 202
frozen cases:

| run | clamp |
|---|---|
| 1 | 49/202 = **24.3%** |
| 2 | 36/202 = **17.8%** |
| 3 | 43/202 = **21.3%** |

**Mean 21.1%, sd 3.3, range 6.5 points.**

Extension 1's headline 24.3% was **over-precise** and should be read as **~21% ± 3**. The
limitation recorded before that run — *"temperature 0 reduces variance; it does not
guarantee identical output"* — is now measured rather than asserted, and it is larger than
I expected.

## What this settles, and what it does not

**It does not settle the question it was written to answer.** "Bad idea or badly prompted"
remains open, because **neither prompt produces a usable component**: the unsafe one tries to
ship real defects on ~21% of cases, and the safe one does no work at all.

What it does establish is narrower and worth more: **the two failure modes are reachable
from a single sentence of prompt text**, and the metrics cannot tell them apart. Accuracy and
ECE were excellent for the dangerous variant and undefined for the useless one.

Untested: a prompt between these two, a coverage floor in the instruction, a different model,
and whether any of it survives at deployment's 3.16% base rate.
