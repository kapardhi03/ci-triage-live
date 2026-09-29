"""Run strategy E (the LLM arbiter) and E0 (the null control) on the frozen 202 cases.

    uv run python -m ci_triage.arbiter_run

Reads artifacts/results/fusion-inputs.json, verifies the frozen hash, and appends both
strategies to artifacts/results/fusion.json. Every raw model response is stored, because an
LLM breaks this repository's run_id reproducibility and an auditable record is the mitigation
recorded in experiments/11-fusion-comparison.md.
"""

import json
from pathlib import Path

import numpy as np

from ci_triage.contracts import Evidence, State, Verdict
from ci_triage.fusion import (
    ARBITER_MODEL, evaluate_strategy, freeze_cases, make_openai_client, null_arbiter,
    strategy_llm_arbiter,
)
from ci_triage.metrics import ece

INPUTS = Path("artifacts/results/fusion-inputs.json")
FUSION = Path("artifacts/results/fusion.json")
RESPONSES = Path("artifacts/results/arbiter-responses.json")
FROZEN_HASH = "305d8ece8a0fa240"


def build_records(d):
    """Observers 1 and 3 share cause_group ssl-jvm -- the phase 10 coupling, AUC 0.6987."""
    per_case = []
    for i, test in enumerate(d["cases"]):
        recs = []
        if d["p_tab"][i] is not None:
            recs.append(Evidence("tabular", test, State.OBSERVED, Verdict.FLAKY,
                                 frozenset({"ExecutionTime"}), "ssl-jvm",
                                 probability=d["p_tab"][i], calibrated=True))
        recs.append(Evidence("sequence", test, State.OBSERVED, Verdict.FLAKY,
                             frozenset({"run_outcome_sequence"}), "run-history",
                             probability=d["p_seq"][i], calibrated=False))
        if d["p_look"][i] is not None:
            recs.append(Evidence("lookup", test, State.OBSERVED, Verdict.FLAKY,
                                 frozenset({"failure_text"}), "ssl-jvm",
                                 probability=d["p_look"][i], calibrated=False))
        else:
            recs.append(Evidence("lookup", test, State.NO_EVIDENCE, Verdict.ABSTAIN,
                                 frozenset({"failure_text"}), "ssl-jvm"))
        per_case.append(recs)
    return per_case


def score(out, y_all):
    if out.get("status") != "complete" or not out["p"]:
        return out
    y, p = np.array(out["y"]), np.array(out["p"])
    out["accuracy"] = float(((p >= 0.5).astype(int) == y).mean())
    out["ece"] = float(ece(y, p, n_bins=10, strategy="equal_freq"))
    return out


def main():
    d = json.loads(INPUTS.read_text())
    h = freeze_cases(d["cases"])
    if h != FROZEN_HASH:
        raise SystemExit(f"frozen hash {h} != {FROZEN_HASH}; the run is void")
    print(f"frozen hash {h} verified, {len(d['cases'])} cases")

    per_case, y = build_records(d), d["labels"]

    null = score(evaluate_strategy(null_arbiter, per_case, y), y)
    print(f"  E0 null control   acc {null['accuracy']:.4f}  ECE {null['ece']:.4f}  "
          f"coverage {null['coverage']:.1%}")

    client = make_openai_client()
    if client is None:
        raise SystemExit("no OPENAI_API_KEY in .env or environment")
    stats = {}
    arb = score(evaluate_strategy(strategy_llm_arbiter, per_case, y,
                                  client=client, model=ARBITER_MODEL, stats=stats), y)
    if arb.get("status") == "complete":
        print(f"  E  arbiter        acc {arb['accuracy']:.4f}  ECE {arb['ece']:.4f}  "
              f"coverage {arb['coverage']:.1%}")
    else:
        print(f"  E  arbiter        INCOMPLETE -- {arb.get('reason')}")

    n = len(d["cases"])
    clamped = stats.get("clamped", 0)
    print(f"\n  ship-direction clamp fired {clamped}/{n} = {clamped/n:.1%} "
          f"(abandonment threshold ~5%)")
    RESPONSES.write_text(json.dumps(
        {"model": ARBITER_MODEL, "temperature": 0, "frozen_hash": h,
         "cases": d["cases"], "raw": stats.get("raw", []),
         "clamped": clamped, "unparseable": stats.get("unparseable", 0)}, indent=2) + "\n")
    print(f"  wrote {RESPONSES}")

    fusion = json.loads(FUSION.read_text())
    for key, out in (("E0_null_arbiter", null), ("E_llm_arbiter", arb)):
        fusion["strategies"][key] = {
            k: out[k] for k in ("status", "accuracy", "ece", "coverage", "n_covered",
                                "n_total") if k in out}
    fusion["arbiter"] = {
        "status": arb.get("status"), "model": ARBITER_MODEL, "temperature": 0,
        "checked": True, "ranked": arb.get("status") == "complete",
        "clamp_fired": clamped, "clamp_rate": clamped / n,
        "unparseable": stats.get("unparseable", 0),
        "responses": str(RESPONSES),
        "predicted_position": "2nd on accuracy, near-worst on calibration",
        "reproducibility": "an LLM has no seed guarantee; temperature 0, model string "
                           "pinned, every raw response stored. Auditable, not re-derivable.",
    }
    FUSION.write_text(json.dumps(fusion, indent=2) + "\n")
    print(f"  wrote {FUSION}")


if __name__ == "__main__":
    main()
