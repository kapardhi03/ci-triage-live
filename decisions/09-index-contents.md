# Decision 09 — what goes in the index

The embedding model is not the decision in this phase. The index contents are.

## Why retrieval might beat a trained model here

**In the builder's words: "index keeps the rare cases, gradients average them away."**

At a 3.16% positive rate, 97% of every batch is the same class, so the loss — and therefore
the gradient — is dominated by the majority. Rare cases are averaged into the noise floor.
Phase 07 showed the endpoint: a model whose decisions were identical to a constant to four
decimal places.

An index compresses nothing. One flaky test with a distinctive stack trace stays in there as
itself and remains retrievable even if it is the only one of its kind. That is the property
weights discard.

## The unit: one document per test

One document per test, containing its **most frequent failure message** — exception type and
message.

Rejected alternatives:

- *One document per distinct message.* A test with three failure modes would get three votes
  against a test with one. The index would then be weighted by how varied a test's failures
  are, which is not the question being asked.
- *One document per occurrence.* `HttpOverSpdy3Test.noDefaultContentLengthOnPost` failed
  7,872 times with the identical message. Indexing occurrences would let a handful of
  always-failing tests own the entire neighbourhood of every query.

## What is deliberately excluded

**The test name and class name.** This is the load-bearing exclusion.

Every `HttpOverSpdy3Test.*` in `square-okhttp` is deterministic. Embedding the class name
would let retrieval recover the label by class membership without reading the failure at
all — `HttpOverSpdy3Test.spdyConnectionTimeout` retrieves `HttpOverSpdy3Test.responsesAreCached`
on the strength of a shared prefix, and both are deterministic, so the vote is right for a
reason that has nothing to do with evidence.

That is the phase 04 `flaky_source` leak in different clothes: a field that encodes the
answer rather than evidence for it. It would inflate precision@k while everything looked
healthy.

**Also excluded:** stack frames (file paths and line numbers identify the test as surely as
its name), the label itself, and every tabular feature from slice 04.

## Both classes, by construction

**If the index contained only flaky failures, every neighbour of every query would be
flaky.** Every vote returns "flaky". precision@k = 1.0 — a beautiful number measuring the
index's composition and nothing else. It would not be wrong so much as vacuous, and nothing
in the metric would reveal it.

So the index must contain real text from both classes. Not labels, not placeholders, not
synthetic text — real messages from tests that actually behaved both ways.
`tests/test_retrieval.py` fails if a single-class index is used.

## Query leakage

A test's own document is removed from its own neighbour set. Checked per query, not assumed
— an index built over the same corpus it is queried with will otherwise return the query
itself as its own nearest neighbour at distance 0, with the correct label.

## Distinct tests, not neighbours

`n_distinct` is reported beside k. Five neighbours that are the same test retrieved five
times are one opinion. Without that count, k=5 can silently mean k=1.

## What the corpus actually contains

| project | tests with failure text | deterministic | flaky |
|---|---|---|---|
| `square-okhttp` | 202 | **102** | **100** |
| `kevinsawicki-http-request` | 15 | 0 | 15 |
| `tootallnate-java-websocket` | 23 | 0 | 23 |

Only `square-okhttp` supports a two-class index.

## Cross-project evaluation: not performable

Recorded as unscored rather than invented, per TASK step 5.

- **Hold out `okhttp`** → the index is the other two projects: 38 tests, **all flaky**. A
  single-class index, which this slice refuses to answer from.
- **Hold out `kevinsawicki` or `tootallnate`** → the index has both classes, but the **query
  set is single-class**, so precision@k is 1.0 regardless of what retrieval does.

Both directions produce a number that measures class composition. Neither is reported. The
within-project evaluation on `square-okhttp` is the only measurable claim this observer can
make, and it is scoped that way.

## A problem visible before any measurement

The same failure text appears under both labels:

```
DETERMINISTIC  HttpOverSpdy3Test.noDefaultContentLengthOnPost
   java.lang.NoSuchMethodError: sun.security.ssl.Handshaker.setSNIServerNames   (7872x)

FLAKY          URLConnectionTest.connectViaHttpProxyToHttpsUsingBadProxyAndHttpResponseCache
   java.lang.NoSuchMethodError: sun.security.ssl.Handshaker.setSNIServerNames   (6650x)
```

One JVM/SSL incompatibility produces a test that fails in every run and one that fails in
84% of them. Text similarity cannot separate those, and no embedding model will fix it,
because the distinction is not in the text. Recorded before measurement so the result can be
read against it.
