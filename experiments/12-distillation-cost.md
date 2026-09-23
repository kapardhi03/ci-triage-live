# Experiment 12b — pricing the distillation corpus

**Written 2026-09-23, before any API call was made.** No distillation was run. This file
records the price and the decision, per TASK step 4b.

## One fully rendered real prompt

Not a synthetic stub. Case `ResponseCacheTest.cacheCanUseCriteriaBesidesVariantObeyed` from
the frozen list, with its actual evidence record and its actual failure message, verbatim:

```text
You are generating a training example for an explanation layer in a CI triage system.

Given the evidence record below, write a template-bound account of the BASIS for the
verdict. You are forbidden from justifying the verdict, from asserting the test is flaky or
is a real defect, and from citing anything absent from the record.

EVIDENCE RECORD
  verdict: FLAKY
  fused_probability: 1.0000
  strategy: escalate_on_disagreement

  observer: tabular
    state: OBSERVED   probability(flaky): 0.0427   calibrated: true
    reads: ExecutionTime, testLength, numAsserts, numCoveredLines, num_third_party_libs,
           assertion-roulette, conditional-test-logic, eager-test, fire-and-forget,
           indirect-testing, mystery-guest, resource-optimism, test-run-war
    cause_group: ssl-jvm
    note: this observer's maximum probability across the evaluation set is 0.1609;
          it never crosses the 0.5 decision threshold

  observer: sequence
    state: OBSERVED   probability(flaky): 1.0000   calibrated: false
    reads: ordered pass/fail outcomes of the first 200 trusted runs
    cause_group: run-history

  observer: lookup
    state: OBSERVED   probability(flaky): 1.0000   calibrated: false
    reads: failure message text
    matched_message: java.lang.AssertionError: java.net.UnknownHostException: ip-172-31-60-164: ip-172-31-60-164: Temporary failure in name resolution
    cause_group: ssl-jvm

  de-duplication: observers `tabular` and `lookup` share cause_group `ssl-jvm`
    (ExecutionTime predicts the lookup's input at AUC 0.6987, p=1.06e-06).
    1 record suppressed. distinct voices after collapse: 2.

OUTPUT FORMAT (fill the slots; do not add prose)
  basis:
  calibrated:
  corroborated_by:
  contradicted_by:
  voices:
  suppressed:
  inert:
  evidence_level:   one of CONFIDENT | THIN | SPLIT
  trace:            each line above -> the record field it came from
```

**1,895 characters.** Token estimate by density:

| assumption | est. input tokens |
|---|---|
| prose, ~4.0 chars/token | 474 |
| mixed code/logs, ~3.2 | 592 |
| **dense/structured, ~2.8 (used)** | **677** |

**Estimated, not counted.** `messages.count_tokens` is the correct tool and it requires
credentials this environment does not have. The conservative 2.8 chars/token figure is used
throughout, so the prices below are upper bounds on the input side. **This may be wrong** —
stated rather than hidden, per the rule recorded in `experiments/12-gpu-path.md`.

## The rate I am standing in

From the `claude-api` skill's model table, **cached 2026-06-24**. Cited, not recalled. If
that table has drifted since, every number below drifts with it.

| model | input $/MTok | output $/MTok |
|---|---|---|
| Claude Opus 5 | $5.00 | $25.00 |
| Claude Sonnet 5 | $2.00 | $10.00 |
| Claude Haiku 4.5 | $1.00 | $5.00 |

## Output tokens — the line that bites

The template is ~250 tokens. But **adaptive thinking bills thinking as output, and Opus 5
thinks by default**, so the naive estimate is the one that goes wrong. `12-gpu-path.md`
recorded this in advance: *"models that think adaptively emit far more output than you
expect."* Three scenarios are priced rather than one.

## The budget

| teacher | out=250 | out=1500 | out=4000 |
|---|---|---|---|
| **Opus 5** | **$1.95** | **$8.26** | $20.88 |
| Sonnet 5 | $0.78 | $3.30 | $8.35 |
| Haiku 4.5 | $0.39 | $1.65 | $4.18 |

*All 202 cases. At 2,000 cases, Opus 5 at modest thinking is $81.77 — **$40.88** with the
Batch API, which applies since distillation is not latency-sensitive. Prompt caching adds
little here: the fixed instruction block is ~120 tokens and the variable evidence record
dominates.*

## The number that would have made me stop

None was reached. **~$8 is not a budget question.** The memory ledger already showed 1.92
GiB fits a free Kaggle T4, so compute is free too.

That overturns the expectation recorded in `experiments/12-gpu-path.md` during phase 05 —
*"the real cost is the distillation API calls, not the GPU."* **On this corpus it is
neither.** Nothing in this phase is gated by cost, which forces the gate to fire on evidence
instead. That is the harder place to stop, because the honest reason becomes *we measured
that it would not help* rather than *we could not afford it*.

## The label distribution — which is the majority baseline

`12-gpu-path.md` flagged this as the thing easiest to skip: **the labeller corpus's class
balance is the majority baseline, and it is not 50%.**

- **Raw balance:** 100 flaky / 102 deterministic across 202 cases — base rate **0.4950**.
- **Under the grouped split actually used: 0.2474.** Held-out test classes are homogeneous
  (every `HttpOverSpdy3Test.*` is deterministic), so the training majority systematically
  mispredicts the entire held-out fold. The majority baseline is **worse than chance**, not
  at it.

Both are recorded because reading either alone misleads. "Base rate 0.495" understates how
structured the corpus is; "baseline 0.247" suggests a hard task when the opposite is true.

## Decision

**Priced and not run.** The corpus was never purchased: the gate in
`experiments/12-finetune-vs-tfidf.md` fired on the baselines, so there was nothing for a
distilled corpus to train. Recorded in `artifacts/results/distill-corpus.json` as a priced,
unrun decision.
