# Slice 09 — observer 3, retrieval

## Responsibility
Answer "has this failure been seen before, and how did those turn out?" by retrieving the
most similar past failures and voting over their outcomes.

## Reads
The **failure text** of the query test — exception type and message, stack frames dropped —
and the index. Nothing else.

It does not read the 13 tabular features, the run sequence, any other observer's output, or
the query's own label.

### What it reads that observers 1 and 2 do not
Observer 1 reads static per-test properties. Observer 2 reads the temporal sequence of
outcomes. Neither has ever seen **the text of the failure itself**. All three input sets are
mutually disjoint.

Why that might matter here: a trained model compresses 26,134 rows into weights, and at a
3.16% positive rate the gradient is dominated by the majority class, so rare cases are
averaged into the noise floor — which is how phase 07's model ended up making decisions
identical to a constant. An index averages nothing. A single flaky test with a distinctive
stack trace remains retrievable as itself.

## Emits

```
{
  probability:   fraction of the top-k neighbours whose test is flaky
  neighbours:    [{test, label, distance}, ...]
  k:             neighbours requested
  n_distinct:    how many DISTINCT tests those k neighbours represent
  index_state:   { n_documents, n_flaky, n_deterministic, built_at, project }
}
```

`n_distinct` is emitted because five neighbours that are the same test retrieved five times
are one opinion, not five. `index_state` travels with every answer because this observer's
output is meaningless without knowing what was in the index when it answered.

## Refuses
**It refuses to answer from a single-class index.** If every document carries the same label,
every vote returns that label and precision@k is 1.0 by construction — a measurement of the
index's composition, not of retrieval. This is the phase's bug and it is a hard refusal, not
a warning.

**It refuses to let a query retrieve itself.** A test's own document is excluded from its own
neighbour set. Checked, not assumed.

It refuses to answer when fewer than k distinct tests are available to retrieve.

## Constraint
**The index must contain real text from both label classes, and a query may never retrieve
its own document.**

Both are invisible in the metric — each inflates precision@k while everything looks
healthy — and both are asserted in `tests/test_retrieval.py` rather than checked by reading.

## The stateful dependency

Observers 1 and 2 are functions. This one has a thing that gets built, goes stale, and has
contents somebody chose.

**Who builds it:** the ingestion path, from archived failure text of runs slice 05 marked
`TRUSTED`. Not the observer at query time.

**When it refreshes:** whenever new trusted runs land. A stale index is not a degraded
answer, it is an answer about a codebase that no longer exists — and unlike a stale model it
degrades silently, because retrieval always returns *something*.

**What is in it:** one document per test — its most frequent failure message, exception type
and message only.

**What is deliberately excluded, and why:** the **test name and class name**. Every
`HttpOverSpdy3Test.*` in `square-okhttp` is deterministic, so embedding the class name lets
retrieval recover the label by class membership without reading the failure at all. That is
the phase 04 `flaky_source` leak in different clothes — a column that encodes the answer
rather than evidence for it. Also excluded: stack frames (paths and line numbers identify
the test), the label, and any tabular feature.

## Connects to
Depends on slice 05 (only `TRUSTED` runs contribute text) and on the archives directly.
Consumed by slice 11 (fusion). Slice 10 tests whether its evidence is independent of
observers 1 and 2 — disjoint inputs are necessary and not sufficient, and the failure text
observed here shows why: the same `NoSuchMethodError` appears under both labels, so text
similarity and outcome can come apart.

## Scope limit
Only `square-okhttp` has both classes (102 deterministic, 100 flaky).
`kevinsawicki-http-request` (15 tests) and `tootallnate-java-websocket` (23) are **entirely
flaky**. Cross-project evaluation is therefore not performable in any direction and is
recorded unscored rather than invented.
