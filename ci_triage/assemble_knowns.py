"""Rebuild KNOWNS.md from the per-phase knowns/ files.

    uv run python -m ci_triage.assemble_knowns

A document assembled by hand drifts from its sources. This makes it a command, so a new
phase or a challenge extension shows up by re-running rather than by remembering.
"""

import pathlib

KNOWNS = pathlib.Path("knowns")
OUT = pathlib.Path("KNOWNS.md")

FOOTER = """
---

## The five that matter most to whoever inherits this

1. **`ExecutionTime` may be partially label-derived, and it is the whole tabular observer.**
   Dropping it takes LOPO AUC 0.6765 -> 0.5577. The decisive evidence -- whether it was
   measured on runs including failures -- is not in the dataset. Pre-registered in
   `experiments/07-execution-time-leak.md` during phase 04, still open.
2. **`cause_group` is hand-assigned, and no coupling involving observer 2 was ever
   computed.** `docs/prior-work.md` names the standard remedy (double-fault measure, Q
   statistic), computable from outputs already stored, and records that it was not applied.
3. **The 40/3/1.5 cost numbers are guesses that dominate every result**, and were
   deliberately not revisited, because changing them when the model looks bad is the
   dishonest move. The arbiter extension showed how much they dominate: put them in a
   prompt and the model stops deciding anything at all.
4. **The explanation layer is designed, minimally implemented, and never evaluated.** Its
   own prediction -- that explanations will be unimpressive, and that sounding smart is the
   alarm -- has never been checked.
5. **Everything after phase 05 rests on three projects, and much of it on one.** The
   dominant signal is a single JVM/SSL incompatibility on the host that produced these
   archives.

## What the system is, stated plainly

Three observers were built and **three were matched or beaten by a free alternative** -- a
constant tied the gradient-boosted tree, a `sum()` beat the GRU, one `if`-statement tied
MiniLM embeddings, and a stub tied an LLM arbiter. Fusion adds nothing: four strategies
reduce to one decision rule. The fine-tune was gated out on evidence, not cost. The shipped
component is a dictionary lookup that abstains on 17.8% of cases.

**The system does not work, and the repository says so in every file.**

## What independent work says about that

arXiv 2607.09345 reports the same four conclusions this repository reached from scratch --
models matching an always-flaky baseline, collapse under project-disjoint evaluation, data
leakage in published evaluations, and rerun-based label reconstruction changing the result.
See `docs/prior-work.md`. The negative results here are most likely correct rather than an
artifact of a small subset.
"""


def collect():
    known, open_rows = [], []
    for path in sorted(KNOWNS.glob("[0-9]*.md")):
        phase, in_open = path.name[:2], False
        for line in path.read_text().splitlines():
            s = line.strip()
            if s.startswith("#"):
                in_open = "open" in s.lower()
                continue
            if not s.startswith("|") or set(s) <= set("|- :"):
                continue
            cells = [c.strip() for c in s.strip("|").split("|")]
            if cells[0].lower() in ("was", "statement", "prediction"):
                continue
            if in_open and len(cells) == 2:
                open_rows.append((phase, *cells))
            elif not in_open and len(cells) == 4:
                known.append((phase, *cells))
    return known, open_rows


def render(known, open_rows):
    lines = [
        "# KNOWNS", "",
        "Assembled from `knowns/00`-`knowns/13` plus the challenge extensions. Every row's",
        "evidence column names a file or a command; nothing here is asserted without one.", "",
        "**The known-unknowns table is longer than it is comfortable for it to be. That is",
        "the point.** A short one would mean the register was dishonest, not that the system",
        "was understood.", "",
        "Regenerate with:", "", "```bash",
        "uv run python -m ci_triage.assemble_knowns", "```", "",
        f"## What moved ({len(known)} rows)", "",
        "| Phase | Was | Now | Statement | Evidence |", "|---|---|---|---|---|",
        *(f"| {a} | {b} | {c} | {d} | {e} |" for a, b, c, d, e in known), "",
        f"## What remains unknown ({len(open_rows)} rows)", "",
        "| Phase | Statement | Why it is still open |", "|---|---|---|",
        *(f"| {a} | {b} | {c} |" for a, b, c in open_rows),
    ]
    return "\n".join(lines) + "\n" + FOOTER


def main():
    known, open_rows = collect()
    OUT.write_text(render(known, open_rows))
    print(f"wrote {OUT}: {len(known)} known rows, {len(open_rows)} known-unknowns")
    if len(open_rows) < 20:
        print("  WARNING: the known-unknowns column looks short. That usually means the "
              "register is dishonest, not that the system is understood.")


if __name__ == "__main__":
    main()
