# Decision 11 — the arbiter's rules

## What the arbiter may see, output, and never do

Three rules minimum; five here, each tied to the failure it prevents.

**1. It may not see the label, in any framing.**
*Prevents:* the obvious. Stated because an evidence record assembled by hand is one careless
field away from carrying it.

**2. It may not see the test name, class name or project.**
*Prevents:* the phase 09 leak. Every `HttpOverSpdy3Test.*` in this corpus is deterministic,
so class membership alone recovers the label without reading any evidence. Identity in a
prompt is `flaky_source` wearing different clothes.

**3. It may not see the other strategies' outputs.**
*Prevents:* ranking rather than arbitrating. An arbiter told what four other rules concluded
is doing meta-analysis on a leaderboard, and its agreement with the majority would be
mistaken for independent confirmation.

**4. It may not manufacture a probability.**
*Prevents:* laundering. A number it invents has no calibration, no provenance and no error
bar; slice 10 would have to mark it uncalibrated, and slice 12 would then explain it as
though it meant something. It arbitrates between existing probabilities and emits a
categorical choice.

**5. It may not move a case toward SHIP — only toward HOLD or ABSTAIN.**
*Prevents:* the expensive failure. Under the phase 01 table a wrong "flaky" costs ~40h
against ~3h for a needless hold. An arbiter that can only add caution has a bounded worst
case. One that can relax caution has an unbounded one, and it would be doing so on the
strength of an uncalibrated judgement.

**6. It may not cite evidence absent from the record.**
*Prevents:* slice 12 explaining something that never happened. Everything it says must be
traceable to an `Evidence` record.

## The divergence measure, and why

**Jensen–Shannon divergence between the two Bernoulli beliefs.**

Disagreement is measured between *distributions*, not labels: two observers can emit the
same label from completely different beliefs — 0.51 and 0.99 are both "flaky" and are not
the same claim.

Chosen over **KL** because observers have no privileged order (JS is symmetric, KL is not)
and because KL is unbounded — one observer at 0.0 against another at 1.0 gives infinity,
which no threshold can use.

Chosen over **total variation** because TV is linear in the gap, so it cannot distinguish
disagreement near the extremes from disagreement in the middle. Measured:

```
JS(0.45, 0.55) = 0.0072        JS(0.05, 0.15) = 0.0209
|0.45-0.55| = 0.10             |0.05-0.15| = 0.10      <- TV calls these identical
```

Those are very different disagreements and the measure has to say so.

## The rendered prompt

TASK step 5 requires the fully rendered prompt be printed and read before any arbiter
result is believed. **No arbiter ran** — no API key, no SDK — so nothing consumed this. It
is rendered and pasted anyway, because it is the only way to check rules 1–3 against an
artefact rather than an intention.

Case index 0 of the frozen list, 1,320 characters, verbatim:

```text
You are arbitrating between automated observers that disagree about one CI test failure.

EVIDENCE RECORD
  observer: tabular
    probability that this failure is FLAKY: 0.0976
    calibrated: true
    read: ExecutionTime, testLength, numAsserts, numCoveredLines, num_third_party_libs,
          and 8 test-smell indicators
    cause_group: ssl-jvm

  observer: sequence
    probability that this failure is FLAKY: 0.0000
    calibrated: false
    read: the ordered pass/fail outcomes of the first 200 trusted runs
    cause_group: run-history

  observer: lookup
    state: NO_EVIDENCE
    reason: no entry for this failure message
    calibrated: false
    read: the failure message text
    cause_group: ssl-jvm

NOTE: observers `tabular` and `lookup` share cause_group `ssl-jvm`. One JVM/SSL
incompatibility drives both (measured: AUC 0.6987, p=1.06e-06). Their agreement is ONE
observation, not two.

YOU MAY OUTPUT EXACTLY ONE OF:
  AGREE_FLAKY        - the surviving evidence supports flaky
  AGREE_REAL_DEFECT  - the surviving evidence supports a real defect
  ESCALATE           - a human should decide

YOU MAY NOT:
  - output a probability of your own
  - move this case toward SHIP; you may only add caution
  - overrule the calibrated observer with your own judgement
  - cite any evidence not listed above
```

**Audited against the forbidden-to-see list:**

| forbidden | present? |
|---|---|
| the label | absent |
| test name / class name | absent |
| project name | absent |
| other strategies' outputs | absent |

The prompt does deliberately carry one thing an arbiter would not normally be told: the
`cause_group` collision, stated with its measurement. An arbiter that does not know
observers 1 and 3 share a cause would read their agreement as two confirmations, which is
the failure slice 10 exists to prevent.

## Status

**Incomplete and unranked.** Predicted position — 2nd on accuracy, near-worst on
calibration — is recorded in `experiments/11-fusion-comparison.md` and will never be
checked. `precomputed/fusion-comparison.json` was not substituted for it, and no position
was inferred from the four strategies that did run.
