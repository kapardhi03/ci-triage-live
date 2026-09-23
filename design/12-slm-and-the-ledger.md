# Slice 12 — explanation layer

## Responsibility
State the basis for a verdict, in a bounded form, without ever asserting the verdict is
right.

## Reads
The **full `Evidence` record** — every observer that spoke, every one that was inert, the
`cause_group` collapses, the calibration flags, the de-duplication count, the coverage.
Never the bare verdict-and-probability.

This is forced rather than preferred. An explainer handed only "flaky, 0.83" has no material
except the number, so the only prose it can produce is confidence-laundering: it dresses a
hash-table hit in the language of reasoning because that is the only language available to
it. Given the whole record it can describe the actual mechanism — *one dictionary entry
matched, two observers were dropped as correlated, one never crossed 0.5* — which is what
happened. **The record is what makes honesty possible.**

It never reads the label, the raw archives, or anything an observer read. It explains the
machine's state, not the world.

## Emits
A **structured, template-bound account of the evidence**. Slots filled from the record, not
sentences composed at will:

```
{
  basis:          which observer produced the verdict, at what confidence
  calibrated:     whether that confidence is calibrated
  corroborated_by: observers that agreed AND were distinct
  contradicted_by: observers that disagreed
  voices:         how many opinions counted after de-duplication
  suppressed:     observers dropped as correlated, and their cause_group
  inert:          observers that never crossed threshold
  evidence_level: CONFIDENT | THIN | SPLIT
  trace:          every emitted claim -> the record field it came from
}
```

Free prose is forbidden. The moment it may write *"this test is flaky because it exhibits
classic non-deterministic timing behaviour"* it has invented a rationale the system never
computed. **Constrain the form and you constrain the lie.**

## Refuses
**It refuses to justify.** It reports what was observed; it does not argue the conclusion.

This is the structural answer to *what happens when the verdict is wrong*, and the system
cannot know that at explanation time. Two forms are available:

- *"This is flaky because…"* — stakes the system's credibility on the verdict. When the
  verdict is wrong, that sentence actively recruits the human into the error, fluently, in a
  form they cannot check.
- *"The message-lookup observer matched a known SSL/JVM signature; the tabular and sequence
  observers did not cross threshold; two voices, one decision."* — **stays true whether or
  not the verdict is correct.**

The second does not collapse when the verdict is wrong, because it never claimed the verdict
was right. The evidence really was there; the human can look at the described basis and
decide the machine over-read it.

**It refuses to hide thin evidence.** A covered case says *matched a known signature*; an
uncovered case must say *no observer had a confident signal — this is a low-evidence
verdict*. Thin evidence is narrated as thin. A system that explains its confident hits and
its coin-flips in the same fluent register is the dangerous one, so `evidence_level` forces
them to read differently.

**It refuses to smooth disagreement.** Where observers split, the split is shown, not
resolved into a unanimous-sounding story. Contradiction is information the human needs
exactly when the verdict is shakiest.

**It refuses any claim absent from the record.** Every statement maps to a field, so a
reviewer can audit the explanation against the machine state that produced it. That is what
makes a wrong explanation *catchable* rather than persuasive.

## Constraint
**The explainer states the basis, never the belief.** You cannot over-trust an explanation
that refuses to tell you what to conclude.

## Connects to
Depends on slice 10 (the `Evidence` record) and slice 11 (the fused verdict). Consumed by
the on-call engineer and by slice 13, which audits whether explanations matched the machine
state.

## What this predicts about the output, before anything is built

**Most of this system's explanations will be unimpressive, and that is correct.** "A
dictionary matched a known error string" is exactly what happened. An explanation layer
doing its job makes the system sound as modest as it actually is.

**If the explanations start sounding smart, that is the alarm.** It means the model has
begun generating reasoning the observers never did. Recorded here before any model runs, so
the measurement can contradict it.
