# AI ledger — phase 08

## Rejected proposal

**Proposal:** Feed the test's full run sequence to an LSTM and predict `IsFlaky`. It is the
obvious formulation, it is what a sequence model is for, and the AUC will be excellent.

**Verdict:** Rejected before any code was written.

**Reason:** `IsFlaky` is *"both a pass and a fail were observed"* — verified empirically in
phase 04. A model handed the whole sequence and asked for `IsFlaky` computes a property of
its own input: *does this list contain both a 0 and a 1?* A regex answers it. The AUC would
be 1.0 by construction and an engineer would learn nothing.

The phase README predicts this gets built first and the number is so good nobody questions
it. It was named instead, which is the only reason the rest of the phase means anything.

## Narrowed proposal

**Proposal (builder's):** Predict whether a sequence is *interleaved* (`P P F P F P`,
genuine non-determinism) or *blocked* (`F F F F P P P P`, broken then fixed), since both
satisfy `IsFlaky` and only the arrangement separates them.

**Verdict:** Narrowed — rejected as a task, kept as a finding.

**Reason:** It has the identical defect. "Is this sequence interleaved" is also a
deterministic function of the sequence being fed in; there is no external source for the
label. Different function, same AUC 1.0.

But the observation underneath is correct and load-bearing: **`IsFlaky` conflates two
different phenomena.** A test broken for 5,000 runs and then fixed is deterministic at every
point in time and is labelled flaky anyway. Phase 03 established the label is a procedure;
this says the procedure has a failure mode nobody has measured. Carried to phase 13.

## Withdrawn criterion — mine to flag, the builder's to fix

The first keep/throw rule proposed was *"beat the control by 0.05 in every cell."*

**Withdrawn as unsatisfiable.** Three of six cells have less headroom than the margin:
`kevinsawicki` sits at 1.0000 at both prefix lengths and `tootallnate`/2000 at 0.9992. Run
as stated, the model would be dropped by arithmetic rather than by evidence — a
predetermined outcome wearing the costume of a test.

That is the **third** instance of the same structural flaw in this repository: the circular
leak test in phase 04, the self-referential cost-table test in phase 07, and now a criterion
that cannot fire. The pattern is a check whose reference is derived from the thing it
checks. Worth stating as a class, because it has not been caught by review any of the three
times — only by deliberately trying to break it.

Replaced with: judge on `square-okhttp`/200 alone, the only cell where the control is dead,
with the exclusion of the saturated cells declared in advance rather than discovered
afterwards.

## What the result was

The GRU never wins. Control wins 4 cells, ties 2, loses 0. The pre-registered criterion
required 0.5467 on the decision cell; the model scored 0.4975. **Withdrawn.**

The bootstrap adds the part the means hide: in that cell the control's 95% CI is
[0.4647, 0.5331], which contains 0.5. Neither predictor beats chance there. The cell was
chosen because the control was dead in it; it turns out nothing works in it.

## Why `n_distinct` mattered

TASK requires raw AUC, calibrated AUC and the count of distinct calibrated probabilities,
because a calibrated AUC of 0.5 is ambiguous. The ambiguity materialised on the first cell:
`kevinsawicki`/200 reports calibrated AUC **0.5000** with **one** distinct value — the model
collapsed to a constant and has no ranking at all. Its raw AUC is **0.0000**, perfectly
inverted rather than random; isotonic calibration is monotonic non-decreasing, so it could
not un-invert the ranking and flattened it instead.

A report of "0.5" without the other two numbers would have looked like an unremarkable
chance result.
