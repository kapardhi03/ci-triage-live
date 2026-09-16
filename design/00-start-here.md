# Slice 00 — system boundary

## Responsibility
Classify a red CI build by likely cause and present evidence to the on-call engineer.

## Reads
The failure report (which test, which branch), the test's pass/fail history, and logs
around the failure.

## Emits
A triage report containing: the likely cause (real defect, flaky test, or infrastructure),
a confidence level, and the evidence and reasoning behind the judgment.

## Refuses
When evidence is too weak or confidence is below a threshold, it reports that it cannot
determine the cause rather than guessing.

## Constraint
The system must never take a release action (ship, hold, rollback). The final call
always belongs to the on-call engineer.

## Connects to
First slice. Consumed by slice 01 (external contract — the output space).
