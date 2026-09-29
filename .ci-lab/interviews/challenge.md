# Challenge handoff — the arbiter, with real evidence

## What operating problem this solves, and which `KNOWNS.md` row it closes

Phase 11 left strategy E `incomplete` — no API key, so the question the phase is named for
was never answered. `knowns/11` recorded it as the top open item:

> *"the LLM arbiter was never measured — the central question this phase is named for is
> unanswered."*

**Closed.** It was measured, and it is **withdrawn**.

## Where it fits, and why there

`ci_triage/fusion.py::strategy_llm_arbiter` — the seam already existed, took a `client`, and
raised when absent. `evaluate_strategy` already treated a `None` return as an abstention and
reported coverage. The patch is the function body plus a client factory; **nothing else in
the pipeline moved.**

One thing did have to be built that was not in scope: `ci_triage/evidence.py`. The phase 11
observer probabilities lived only in a session scratchpad and were gone. That is recorded as
a reproducibility failure, not as a feature.

## What invariant the test protects

**The arbiter may never move a case toward FLAKY against REAL_DEFECT evidence.** Under the
phase 01 table a wrong "flaky" costs ~40h against ~3h for a needless hold, so it may confirm
or escalate and never relax caution.

`tests/test_fusion.py::test_arbiter_cannot_move_a_case_toward_ship` stubs a client that
returns `AGREE_FLAKY` against evidence pointing REAL_DEFECT and asserts the wrapper refuses.
No network. **Verified by breaking it four ways** — clamp removed, clamp counting but
allowing, clamp made blanket rather than directional, unparseable output guessed rather than
refused. Each kills a test.

## What the experiment compared against

Two controls, and the free one is the one that mattered:

1. **Strategy D** — the phase 11 best, 0.9940 at 82.2% coverage.
2. **The null arbiter** — a stub returning the most-confident collapsed voice. No model, no
   network, no cost.

The experiment could have lost against either. **It lost to the stub.**

## What was observed

```
E0 null control   acc 0.9554   ECE 0.0435   coverage 100%
E  gpt-4o-mini    acc 0.9904   ECE 0.0096   coverage 51.5%

coverage-adjusted, same 104 cases:   arbiter 0.9904   null stub 0.9904

ship-direction clamp:  49 / 202 = 24.3%   (abandonment threshold ~5%)
  of those 49:  44 were genuine REAL DEFECTS
  unclamped:    44 x ~40h = 1,760 engineer-hours of shipped bugs
raw output:     AGREE_FLAKY 121 | ESCALATE 49 | AGREE_REAL_DEFECT 32
```

Both pre-registered abandonment conditions fired. **Withdrawn.**

## What it does *not* prove

- Not that LLM arbitration cannot work — one model, one prompt, one temperature.
- Not that this arbiter could not be made safe. The clamp is a wrapper; nothing here tests
  whether better prompting reduces the 24.3%.
- Not transferable to deployment. These 202 cases are 49.5% positive against 3.16%, where
  the ship-direction rule matters **more**, not less.
- Not re-derivable. Temperature 0 and a pinned model reduce variance; they do not guarantee
  identical output. The stored responses make the run auditable, not reproducible.

## What the agent proposed that was rejected, and its tell

**Proposed:** report E as the best strategy — second-best accuracy, best calibration of any
completed strategy, same frozen cases, same metric implementation.

**The tell:** *every metric agreed.* Accuracy, ECE, Brier and cost-weighted risk all said
excellent, because the clamp had already converted the unsafe calls into abstentions before
anything was scored. A component that looks good on every number, produced by a pipeline
whose safety mechanism is doing invisible work, is the exact shape of `FAILURES.md` 1.1.

The clamp rate is the only instrument that sees it, **and it exists only because the
abandonment condition was written down before the run.**

## Which command reproduces it

```bash
uv run python -m ci_triage.evidence        # rebuild frozen inputs from data/raw, verify hash
uv run python -m ci_triage.arbiter_run     # run E0 and E, store every raw response
uv run pytest tests/test_fusion.py -q      # the clamp invariant, no network
```

`.env` must contain `OPENAI_API_KEY`. Cost ≈ $0.023.

## The next unanswered question

**Does the 24.3% clamp rate drop with a prompt that argues for caution, or is it a property
of the model?**

That is a one-variable experiment on the same frozen cases at the same cost, and it decides
whether "LLM arbiter" is a bad idea or a badly-prompted one. This run cannot tell them apart,
and it should not be read as if it could.
