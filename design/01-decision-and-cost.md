# Slice 01 — external contract

## Responsibility
Define the four-output contract the system exposes and the cost of each wrong answer.

## Reads
The failure report (which test, which branch), the test's pass/fail history, system and
network logs, and the code diff.

## Emits
Exactly one of four outputs per red build, plus a confidence level:

| Output | Engineer action |
|---|---|
| real defect | hold the release, go to code review, get the change fixed |
| flaky | rerun or quash the flake, lean toward shipping |
| infrastructure | rerun on healthy infra, fix the runner, then proceed |
| abstain | engineer investigates manually (rerun, quick infra check, history), then decides |

Each output earns its place because it triggers a different action. If two led to the
same action, we wouldn't need both.

## Refuses
When evidence is too weak to separate causes, the system emits ABSTAIN rather than
forcing a confident label. Refusing here is an output, not silence.

## Constraint
The system must never make the ship/hold decision itself. It must never emit a confident
cause label when the evidence does not support it.

## Connects to
Depends on slice 00 (system boundary). Consumed by slice 02 (evaluation component).
