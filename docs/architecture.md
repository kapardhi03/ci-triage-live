# Architecture

Assembled from `design/00`–`design/13`. This file states the thing none of the individual
slices can: how the levels fit together, and why combining observers is not averaging them.

## The two questions

They are different questions, with different consumers, and answering one while claiming to
answer the other is the central architectural mistake this design guards against.

| | **Run level** | **Case level** |
|---|---|---|
| **Question** | Is *this test's* failure flaky, a real defect, or infrastructure? | Does the 09:00 release ship? |
| **Unit** | one test in one build | one build |
| **Consumer** | the engineer triaging a specific test; the quarantine list; the flaky-test backlog | the on-call release engineer at 02:47, making a ship/hold call |
| **Produced by** | observers 1–3, collapsed by the integration contract | the case-level rule, over collapsed run-level verdicts |
| **Output** | `real defect \| flaky \| infrastructure \| abstain` + evidence | `SHIP \| HOLD \| ESCALATE` |

## What goes wrong if you answer one with the other

**One build produced 197 failures.** That is one question, not 197.

The tempting arithmetic is to take 197 per-test probabilities and average them, or take a
majority vote. Both are wrong here, and the phase 01 cost table says why.

Suppose 196 tests are flaky and one is a real defect. The mean flakiness probability is
~0.99. A majority vote says "flaky". Both ship a broken release, at ~40h, to avoid a ~3h
hold. The arithmetic is *confidently* wrong, and it is wrong in the expensive direction —
the mean is dominated by the 196 cheap cases while the decision is dominated by the one
expensive case.

The asymmetry is the whole point: **196 flaky tests do not cancel one real defect.** A rule
that averages cannot express that. A rule that holds if any test is credibly real can.

The reverse error matters too. Answering the run-level question with a case-level decision —
telling an engineer "we held the release" when they asked "is `testUserSessionTimeout`
flaky" — gives them nothing to act on. Different consumer, different artefact.

## Why observers are not averaged

Three observers agreeing is three pieces of evidence **only if they looked at three
different things.**

Their inputs are literally disjoint — the intersection of the three `Reads` lists is empty.
That is necessary and not sufficient, and this repository has the measurement to prove it:

```
ExecutionTime predicting "does observer 3 see the SSL NoSuchMethodError"
    AUC 0.6987    p = 1.06e-06

observer 1 predicting the actual label (leave-one-project-out)
    AUC 0.6765
```

Observer 1's dominant feature predicts observer 3's *input* better than it predicts the
label observer 1 exists to predict. One JVM/SSL incompatibility drives both. So when those
two agree, the agreement is substantially one observation reported twice, and averaging
their confidence would make the system more certain on the basis of nothing new.

The contract therefore collapses evidence by `cause_group` **before** anything is
aggregated. Records sharing a cause contribute one voice, not several.

## Three states, not two

`NO_EVIDENCE` and `INDETERMINATE` are different and must not be merged:

- **`NO_EVIDENCE`** — the observer could not look. The retrieval lookup has no entry for
  this message; the sequence observer has no history of length *k*. It has nothing to say.
- **`INDETERMINATE`** — the observer looked and its evidence points equally in all
  directions. That is a finding.

A uniform probability encodes both identically, which erases the distinction exactly when it
matters: one is a gap in coverage to be fixed, the other is genuine ambiguity in the world.

## The case-level rule

**Hold if any test is credibly a real defect.** Not a mean, not a vote.

Formally: after per-test collapse, if any test's real-defect evidence exceeds the credibility
threshold, the build is `HOLD` and that test is named as the driver. If none does and
coverage is adequate, `SHIP`. If coverage is inadequate — too many `NO_EVIDENCE` records —
`ESCALATE` to a human, which phase 01 priced at ~1.5h.

`ESCALATE` is not a hedge. It is the case-level form of the same abstention derived in slice
01, and it costs less than either wrong answer.

## What this architecture has actually established

Three observers were built. **Three were matched or beaten by a free alternative** (phase 07
tie with a constant, phase 08 loss to `sum()`, phase 09 tie with one `if`-statement). The
integration contract is therefore correct machinery around components whose individual value
is, on this data, unproven. That is recorded here rather than papered over: the contract is
worth having, and it is not evidence that the observers are.
