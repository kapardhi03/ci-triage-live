# Prior work, located by doubt

Not a literature review. Five specific doubts about **this** design came first; each search
was run to resolve one of them. "Nothing changed" appears below and is written as such.

Caveat on method: these are search results and one fetched paper summary. Where a paper's
claims are reported below I have read the abstract/summary, not the full text, and that is
stated rather than implied.

---

## Doubt 1 — Is `ExecutionTime` a legitimate feature or is it leaking the outcome?

**Where the doubt came from:** `experiments/07-execution-time-leak.md`, pre-registered during
phase 04. Dropping it takes LOPO AUC from 0.6765 to 0.5577, so the observer is effectively
one column — and a flaky test often runs longer *because* it timed out or retried.

**Search:** *flaky test prediction execution time feature leakage label*

**Found:** Execution time is a **standard, accepted predictor** in this literature, named
alongside coverage and third-party library usage. Nobody treats it as leakage. Separately,
the field does audit for "label leakage (tests labelled flaky purely because of
infrastructure outages)" — which is the phase 05 concern, not this one.

**What changed: nothing.** The doubt is not resolved, it is relocated. The field's
acceptance of the feature is not evidence it does not leak; it is evidence nobody has
asked. The decisive test remains the one `experiments/07-execution-time-leak.md` names and
this dataset cannot answer: whether `ExecutionTime` was measured on runs that include
failures. Still open, and I now know it is open in the literature too.

---

## Doubt 2 — Is the random/grouped split gap real, or an artifact of 25 small projects?

**Where the doubt came from:** phase 06. Random 5-fold 0.7621, leave-one-project-out 0.6490.
`knowns/06` records 61% of that gap as unexplained.

**Search:** *FlakeFlagger cross-project evaluation flaky test prediction generalization unseen
projects*, then fetched **"How Far Are We from Detecting Flaky Tests? On the Limits of
Code-Based Detection"** (arXiv 2607.09345).

**Found:** The project-disjoint setting is the one the field considers realistic. And that
paper reports, on published detectors, that performance **"collapsed when evaluated
project-disjoint but recovered dramatically under standard cross-validation on identical
data, suggesting the model exploited within-project patterns rather than learning
transferable flakiness signals."**

**What changed:** Confidence, substantially. The gap is **not** a small-subset artifact —
it is the central finding of independent work on the same problem, on different detectors.
Phase 06's mechanism claim ("base rate is project-level") is the same mechanism that paper
names. The 61% still-unexplained portion is unaffected and stays open.

---

## Doubt 3 — Is the one-sided contamination of `not flaky` labels a real concern or my invention?

**Where the doubt came from:** `experiments/03-rerun-bias.md`. A flip is a proof; no flip is
a budget. Phase 04 partly refuted the magnitude once N turned out to be 10,000.

**Search:** *rerun-based flaky test labels false negatives contamination how many reruns needed*

**Found:** Standard and named. **"A limited number of reruns can still result in an incorrect
'non-flaky' label"** — the exact asymmetry phase 03 derived from first principles. And the
rerun counts in practice are small: one study reran **20 times**.

**What changed:** The phase 04 refutation is **strengthened**, not weakened. FlakeFlagger's
N = 10,000 is two to three orders of magnitude above typical practice, so this corpus's
negative class is far cleaner than the field's norm. Phase 03's argument was right about the
mechanism and right to be partly refuted here — and it would be *correct and unrefuted* on a
dataset built with 20 reruns. The scope note in `knowns/03` now has evidence behind it.

---

## Doubt 4 — Does anyone else find the cost table makes the task degenerate?

**Where the doubt came from:** phase 07. With 40:3 asymmetry at a 3.19% base rate the
cost-optimal threshold is p > 0.930, the calibrated model's maximum is 0.2362, and the model
is indistinguishable from "always hold the release" to four decimals.

**Search:** *cost-sensitive evaluation asymmetric misclassification cost degenerate optimal
policy rare class*

**Found:** The threshold derivation is **textbook** — "the optimal prediction minimises total
expected cost" and "an optimal threshold that yields the minimum expected cost can be
calculated from misclassification costs." Confirms the arithmetic in `decisions/07-the-pivot.md`
was standard rather than novel.

**What changed: nothing, and the gap is the interesting part.** I did not find work naming
the consequence — that at sufficient asymmetry and rarity the cost-optimal policy becomes
*constant*, and a model with real discrimination is then worthless without the metric ever
saying so. The literature optimises thresholds under asymmetric cost; it does not appear to
ask when that optimisation makes the model irrelevant. Either I searched badly or this is
underexamined. Recorded as unresolved rather than claimed as novel.

---

## Doubt 5 — Is hand-assigning `cause_group` the best available method?

**Where the doubt came from:** `.ci-lab/interviews/10.md`, conceded in review. One correlation
measured, on one project, between two of three observers, and the grouping typed in by hand.
The contract *enforces* a grouping; it does not *detect* one.

**Search:** *ensemble diversity correlated errors shared cause detecting non-independent
classifiers*

**Found:** There is an established literature with named instruments for exactly this —
**Q statistic, the double-fault measure, disagreement measure, correlation coefficient**, and
non-pairwise measures including Kohavi-Wolpert variance and interrater agreement. The
**double-fault measure** is specifically motivated by the case here: *"it is more important
to detect when simultaneous errors are being committed than when both classifiers are
correct."*

**What changed: the most of any of the five.** The hand-assigned `cause_group` is weaker than
standard practice, and standard practice is cheap — double-fault is a count over the
confusion of two classifiers' errors, computable from outputs this repo already stores. The
honest position in `knowns/10` ("enforces a grouping, does not detect one") is confirmed as a
real deficiency with a known remedy that was not applied.

**Concrete consequence, recorded as unbuilt:** `cause_group` should be *derived* from
pairwise double-fault or Q statistic over observer outputs on a held-out set, not typed in.
That would also close the gap phase 10 left open — no coupling involving observer 2 was ever
computed, and these measures would have computed all three pairs for free.

---

## The finding that outranks all five

arXiv 2607.09345 reports, independently and on different detectors, **four conclusions this
repository reached from scratch**:

| this repo | that paper |
|---|---|
| phase 07: the GBT ties a constant policy (0.0957 vs 0.0957) | both Flakify and FlakyQ **matched the "always-flaky" baseline**, F1 0.80 vs 0.80 |
| phase 06: 0.7621 random → 0.6490 project-held-out | performance **collapsed project-disjoint, recovered under standard CV on identical data** |
| phase 04: leaking columns found by single-column AUC scan | **data leakage in published evaluations**; fixing it dropped weighted F1 0.95 → 0.88 |
| phase 03: rerun-based negatives are a budget, not a fact | rebuilt non-flaky labels from **500 repeated executions** and the detectors collapsed |

And it goes one step further than this repo did, stating that **"flakiness is not a static
property of test code,"** making code-based detection ill-posed for many flakiness types.

That is the deep version of what phases 07–09 kept bumping into: three observers, three free
alternatives, zero wins. This repo found the symptom empirically and stopped at "the data has
~20 failure modes and one dominant cause." The paper names the cause.

**What changed:** the confidence that this project's negative results are *correct* rather
than *a consequence of working on three projects*. That is worth more than any positive
result in the repository, and it is the single strongest argument that the honest reporting
discipline paid for itself.

## Sources

- [How Far Are We from Detecting Flaky Tests? On the Limits of Code-Based Detection](https://arxiv.org/html/2607.09345)
- [FlakeFlagger: Predicting Flakiness Without Rerunning Tests](https://www.jonbell.net/preprint/icse21-flakeflagger.pdf)
- [Empirically evaluating flaky test detection techniques combining test case rerunning and machine learning models](https://link.springer.com/article/10.1007/s10664-023-10307-w)
- [Just-in-Time Flaky Test Detection via Abstracted Failure Symptom Matching](https://arxiv.org/pdf/2310.06298)
- [Practical Flaky Test Prediction using Common Code Evolution and Test History Data](https://arxiv.org/pdf/2302.09330)
- [Cost-Sensitive Evaluation for Binary Classifiers](https://arxiv.org/html/2510.22016v1)
- [Maximum Likelihood in Cost-Sensitive Learning](https://jmlr.org/papers/volume11/dmochowski10a/dmochowski10a.pdf)
- [Measures of Diversity in Classifier Ensembles and Their Relationship with the Ensemble Accuracy](https://www.researchgate.net/publication/220344230_Measures_of_Diversity_in_Classifier_Ensembles_and_Their_Relationship_with_the_Ensemble_Accuracy)
- [Ensemble diversity (Kuncheva)](https://lucykuncheva.co.uk/ensemble_diversity.html)
- [Understanding and Improving Flaky Test Classification](https://dl.acm.org/doi/10.1145/3763098)
