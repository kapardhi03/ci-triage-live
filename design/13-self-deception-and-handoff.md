# Slice 13 — operations layer

## Responsibility
Catch the failures the other twelve slices cannot report about themselves.

## Reads
The artefacts every other slice already produces: `Evidence` records, run manifests,
`artifacts/results/*.json`, and the frozen constants recorded alongside each result. It
reads no raw data and trains nothing — an operations layer that recomputed the system's
numbers would be a fourteenth slice with its own silent failures.

## Emits
Pass/fail per invariant, with the value observed and the value expected. A failing invariant
names the slice, the expected constant, and the measurement that contradicted it — a bare
red test tells an on-call engineer that something broke, not what.

Also an **append-only evidence store**: every verdict with the records that produced it.
Append-only because a system that can rewrite its own history cannot be audited, and the
failures in this register are exactly the ones a retrospective edit would hide.

## Refuses
It refuses to pass an invariant it could not evaluate. A skipped check reports `SKIPPED` with
the reason, never `PASSED` — absence of evidence is not evidence, which is the phase 03
error and would be the worst possible place to repeat it.

It refuses to compare a result against a constant recomputed by the code under test. Every
frozen number is hardcoded in the test file, independent of the module it grades.

## Constraint
**Every silent slice has an instrument, and every instrument fails when the failure occurs.**

A test that cannot fail is a wish with a green tick. This repository has produced three of
them — the inverted cost mapping (slice 02, five phases green), the circular leak test
(slice 04), and the unsatisfiable keep criterion (slice 08). **None was caught by a passing
test. All three were caught by deliberately trying to break something.** Mutation is
therefore part of the constraint, not a nicety.

## The hard question: which slices would tell me, and which would lie quietly

**Loud — they announce themselves, and need no instrument.** They throw, return empty, or
crash. The failure is the symptom.

| slice | how it announces |
|---|---|
| 00 boundary | crash or missing input, visible immediately |
| 01 external contract | malformed verdict or a cost-table shape change breaks consumers |
| 03 ground-truth source | a missing or unreadable source fails at read |
| 10 integration contract | a schema mismatch throws when a record does not fit |

**Silent — they keep emitting a plausible number.** Each needs an invariant that fires on
the failure the slice cannot self-report.

| slice | the silent failure | instrument |
|---|---|---|
| **02** evaluation | inverted cost mapping — *already happened*, five phases green | cost of a known-wrong verdict exceeds a known-right one, against **hardcoded** expected costs, not the mapping under test |
| **04** ingestion | circular leak test — *already happened*, green either way | `MUST_NEVER_APPEAR` frozen independently of the module; an un-excluded leak column must turn a test red |
| **05** trust gate | a mis-parse still returns a verdict | the ground-truth cross-check frozen: gate's always-failing set == `test_results.csv` deterministic set, Jaccard 1.000 |
| **06** splits | a leaky split still yields an AUC | no project on both sides of any fold; zero-positive folds **skipped, not scored** |
| **07** observer 1 | a broken observer still emits probabilities | max probability ≤ 0.1609, and its removal flips no case-level verdict |
| **08** observer 2 | unsatisfiable keep criterion — *already happened* | the keep/throw margin rule frozen as an executable check, not prose |
| **09** observer 3 | silently answers cases it should decline | coverage reported with every accuracy; abstained cases return ABSTAIN, never a guess |
| **11** fusion | A/B/C emit identical labels while looking like three strategies | reported voice count is post-de-duplication; agreement across a shared `cause_group` collapses to one |
| **12** explanation | a fluent account of a wrong verdict cannot self-detect | every field maps to an `Evidence` field; thin and split evidence flagged as such — structural, since correctness cannot be checked at emit time |

Slice 12's instrument is structural on purpose. The explanation layer's own design forbids it
from asserting the verdict, so the only checkable property is that it said nothing the record
does not contain.

## Connects to
Depends on every earlier slice and is depended on by none — which is why it is last and why
it must not be optional. Consumed by the on-call engineer and by whoever inherits this
repository.
