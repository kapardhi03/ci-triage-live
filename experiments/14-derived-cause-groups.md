# Experiment 14 — derive `cause_group` instead of assigning it

**Written 2026-09-29, before anything was computed.** Closes the #2 open item in
`KNOWNS.md`.

## The deficiency being fixed

`.ci-lab/interviews/10.md` conceded it unprompted:

> *"`cause_group` is a hand-assigned string. You measured one correlation, decided observers
> 1 and 3 share a cause, and typed the same label onto both. The contract does not *detect*
> correlated evidence — it enforces a grouping a human guessed."*

And `docs/prior-work.md`, from the doubt-first search, named the remedy: the **double-fault
measure** and the **Q statistic** are the standard instruments for exactly this, computable
from outputs already stored. They were not applied. This applies them.

**No coupling involving observer 2 has ever been computed at all.** If the sequence observer
shares a cause with either of the others, the contract currently counts them twice and
nothing would reveal it.

## What is computed

Both measures, all three pairs, on the same frozen 202 cases (`305d8ece8a0fa240`):

- **Double-fault** — the fraction of cases where *both* observers are wrong. Kuncheva's
  motivation is precisely this case: *"it is more important to detect when simultaneous
  errors are being committed than when both classifiers are correct."*
- **Q statistic** — `(N11·N00 − N01·N10) / (N11·N00 + N01·N10)`. Q ≈ 0 independent,
  Q → 1 strongly correlated. Normalises for how often each observer is right, which raw
  double-fault does not.

The lookup abstains on 36 of 202, so each pair is computed on its own overlap and the `n`
for each pair is reported rather than averaged away.

## The threshold

> **Q > 0.5 means the same `cause_group`.**

A convention rather than a derivation, and recorded as one. Substantial positive dependence
is the usual reading of Q > 0.5; Q > 0.8 is strong. The 40:3 cost asymmetry argues for
catching coupling early rather than late, so the lower of the two conventional bars is taken.

## The prediction

1. **`tabular` / `lookup` is the most-coupled pair.** This is the hand-assigned grouping and
   the only one with a prior measurement behind it — `ExecutionTime` predicts the lookup's
   input at AUC 0.6987, p = 1.06e-06.
2. **`sequence` is independent of both.** Q below 0.5 against `tabular` and against
   `lookup`.

If both hold, the hand-assignment was correct and phase 11's two-voice fusion stands.

## What would refute it

| outcome | consequence |
|---|---|
| `sequence` couples to either observer at Q > 0.5 | **phase 11 ran over the wrong number of voices.** Its fusion result needs revisiting, and the contract has been double-counting. |
| `tabular`/`lookup` falls below Q 0.5 | The hand-assigned grouping was wrong in the other direction — the contract has been *over*-collapsing, suppressing a genuine second voice. |
| all three pairs above 0.5 | Every observer shares a cause; the architecture's independence claim collapses entirely. |
| all three below 0.5 | No grouping is justified, `collapse_correlated` is a no-op, and phase 10's central finding was an artifact of a single AUC measurement. |

Any of these changes a recorded conclusion, which is what makes the experiment worth running
rather than a confirmation.

## Scope

202 cases, one project, 49.5% base rate. Q and double-fault are computed on hard predictions
at a 0.5 threshold, so they inherit that threshold's arbitrariness. A pair can be coupled in
belief while disagreeing in label, and these measures would not see it.

---

## Result

*(appended after the run — empty at the time of writing)*

**Appended 2026-09-29 after the run. Nothing above this line was edited.**

## The result: both pre-registered instruments are degenerate on this data

| pair | n | acc A | acc B | double-fault | Q |
|---|---|---|---|---|---|
| `lookup`/`sequence` | 166 | 0.9940 | 0.9940 | 0.0060 | **1.0000** |
| `lookup`/`tabular` | 166 | 0.9940 | 0.6024 | 0.0060 | **1.0000** |
| `sequence`/`tabular` | 202 | 0.9901 | 0.5050 | 0.0099 | **1.0000** |

**Q = 1.0000 on all three pairs, including ones that cannot plausibly be perfectly
dependent.** That is arithmetic, not dependence:

```
                  N11   N10   N01   N00
lookup|sequence   165     0     0     1
lookup|tabular    100    65     0     1
sequence|tabular  102    98     0     2
```

**`N01 = 0` in every pair**, so `N01·N10` vanishes and `Q = (N11·N00)/(N11·N00) = 1`
regardless of any real relationship. `N01` is *"A wrong, B right"* — it is empty because the
weak observer's errors strictly **contain** the strong observers' errors. That is nesting,
which is neither independence nor correlation, and Q cannot express it.

Double-fault fails for the adjacent reason: **`N00` is 1, 1 and 2 observations.** Both
measures are computed from a cell that has essentially no data.

## The post-hoc diagnosis, and why it also fails

Computed *after* Q was found degenerate — diagnosis, not a substituted test:

| pair | disagreement | correlation |
|---|---|---|
| `lookup`/`sequence` | **0.0000** | 1.0000 |
| `lookup`/`tabular` | 0.3916 | 0.0958 |
| `sequence`/`tabular` | 0.4851 | 0.1010 |

At first reading this **inverts the hand-assignment**: `lookup` and `sequence` never disagree
on any of their 166 shared cases, while `tabular` is nearly uncorrelated with both.

**It does not survive a significance check.** Two observers at 99.4% accuracy must agree
almost always by arithmetic:

```
lookup|sequence    expected disagreements under INDEPENDENCE: 2.0    observed: 0
                   P(0 disagreements | independent) = 0.135  -> NOT significant

lookup|tabular     expected 66.2   observed 65
sequence|tabular   expected 100.0  observed 98
```

**Every pair's observed disagreement is what independence predicts.** All three are
indistinguishable from independent by every measure computable here.

## The prediction is refuted, in a fifth way nobody wrote down

Four refutation outcomes were recorded in advance. **None of them happened.** The actual
outcome was a fifth: *the instrument is degenerate on this data.*

That is the more useful failure, because it is diagnosable. These measures need cases where
observers are **wrong**, and this corpus supplies one or two.

## What must not be done with this

**The derived grouping is not applied.** It would merge all three observers into one
`cause_group` on the strength of `Q = 1`, which is an artifact. Applying it would collapse
fusion to a single voice for an arithmetic reason, and it would look like a finding.

**The hand-assigned grouping stands — by default, not by validation.** Nothing here confirms
it. Nothing here can refute it either.

## The #2 open item is not closed. It is better characterised.

`KNOWNS.md` said `cause_group` is hand-assigned and the standard remedy was named but not
applied. It has now been applied, and **the remedy does not work on this data.**

Worth noting what *did* work: the phase 10 coupling (`ExecutionTime` predicts the lookup's
input at AUC 0.6987, p = 1.06e-06) was measured on **inputs**, not on errors. That
measurement stands. Error-based agreement measures fail precisely because these observers
rarely err — so the input-based approach had more power here, and the literature's standard
instruments had less.

**What would be needed:** a corpus where the observers are wrong often enough to populate the
both-wrong cell — which means either far more cases, or observers closer to the 50% accuracy
where these measures have power. Neither is available here.
