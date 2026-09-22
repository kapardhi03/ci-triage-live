# Decisions

Index of `decisions/*.md`. One line each: what was decided, and what it cost.

A decision with no cost was not a decision — it was a preference. If you cannot name what
you gave up, the interview for that phase is not finished.

| Phase | Decision | What it cost |
|---|---|---|
| 00 | The decision at 02:47 is what a human *does* with a red build — stop the release, isolate, rerun, or escalate — not the prediction "flaky or not" | Ruled out framing the system as a classifier with a score as its output |
| 01 | Four outputs, not three: real defect, flaky, infrastructure, **abstain** | ABSTAIN is not free (~1.5h); the system must earn the right to use it rather than hiding behind it |
| 01 | Objective is cost-weighted expected cost, not accuracy | Gave up a single legible headline number; every result now needs the cost table attached |
| 02 | Evaluation is its own component, never a method on a model | More plumbing — every model must be handed to an external scorer instead of reporting its own number |
| 02 | Equal-frequency is the trustworthy ECE binning; equal-width may be reported but never read alone | Equal-frequency is tie-order dependent on single-valued predictors, so neither number is trustworthy there |
| 02 | ECE is a diagnostic, never a selection criterion | Cannot rank models on calibration alone — every calibration number needs a discrimination number beside it |
| 03 | `not flaky` is treated as a budget, not a fact | Every negative label must carry its basis and sample size; consumers can no longer read a bare label |
| 03 | A false positive is a candidate, not a verdict — FPs get reran before counting against a model | Costs rerun budget and slows evaluation; precision stays a lower bound until that budget is spent |
| 04 | FlakeFlagger (CC-BY-4.0) over IDoFT | Gave up 300+ projects and Python coverage for ~25 Java projects, purely on licensing |
| 04 | `IsFlaky` (rerun-observed, 825 positives) over `flaky` (tool-labelled, 205) | Gave up the label the original paper's features were engineered around |
| 04 | Keep 6 history features, drop `window5` and `window10` at a ≥80% project-mode threshold | Accepts a **git-history dependency** into the phase 00 system boundary — unbuilt and uncosted |
