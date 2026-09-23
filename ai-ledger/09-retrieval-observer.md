# AI ledger — phase 09

## Rejected proposal

**Proposal:** Ship the retrieval observer. MiniLM embeddings with a 5-NN vote score
precision **0.9851** against a majority baseline of **0.5050** on `square-okhttp` — the
first component in this project to clear its baseline by a wide margin, after a tabular
observer that tied a constant and a sequence observer that lost to `sum()`.

**Verdict:** Rejected. The number is real and the component is redundant.

**Reason:** A single substring check —

```python
0 if "setSNIServerNames" in text else 1
```

— scores **0.9851**. Identical to four decimal places. TF-IDF character n-grams with 5-NN
also score 0.9851, and an exact-message dictionary lookup scores **0.9940** where it has a
match. The 384-dimensional transformer, the cosine index and the top-k vote are exactly
equalled by one `if`.

The structure explains it: **100 of 102 deterministic tests share one failure message**, and
the corpus holds **19 distinct messages across 202 tests**. There is one decision boundary
and every method finds it. Shipping a sentence transformer to perform a substring match adds
an embedding dependency, a model download, and an index that can go stale — for nothing.

## What ships instead

`MessageLookup`: exact failure-message lookup, **abstaining on any message it has not seen**.
Leave-one-class-out on `square-okhttp`: **82.2% coverage, 0.9940 precision on covered, 36
abstentions.**

Abstention is the honest handling of the 36 tests whose message has no precedent. The
earlier 0.9940 figure for exact matching was scored on 166 of 202 — the other 36 were
silently dropped. As a shipped component they must be answered, and `ABSTAIN` is the
answer phase 01 priced at ~1.5h against ~40h for a wrong "flaky" call.

The stateful dependency `design/09` was built around — an index that gets built, goes stale,
and has contents somebody chose — **disappears**. The table is the state, and an unseen
message abstains rather than silently returning a stale neighbour.

## Retained deliberately

`build_index` and `query` stay in `ci_triage/retrieval.py` with their invariants tested.
They are the measured control, and TASK requires a test that fails when an index carries one
class. Deleting them would delete the evidence for the decision.

## The pattern, now three phases deep

| phase | component | free alternative | outcome |
|---|---|---|---|
| 07 | gradient-boosted tree | constant "always hold" | tie, to 4 decimals |
| 08 | GRU over run sequences | `sum()` over a list | control wins 4–0 |
| 09 | MiniLM retrieval + 5-NN | one `if`-statement | tie, to 4 decimals |

Three components, three free alternatives, zero wins for the trained thing. This is not
three coincidences — it is what a corpus with roughly twenty real failure modes and one
dominant cause does to every method pointed at it. Recorded as a finding about the data,
not as three separate disappointments.

## Not invented

Cross-project retrieval is **not performable** and is recorded unscored. Holding out
`square-okhttp` leaves an index of 38 entirely-flaky tests, which the observer refuses;
holding out either other project leaves a single-class *query* set, where precision@k is 1.0
whatever retrieval does. Both directions measure class composition. No cross-project number
is reported and `precomputed/retrieval-eval.json` was not substituted for one.
