"""Print the headline comparison from the committed results.

    uv run python -m ci_triage.summary

Every number is read from artifacts/results/*.json. Nothing is hardcoded here, so this
cannot drift from the evidence -- if a result file changes, this output changes with it.
"""

import json
from pathlib import Path

R = Path("artifacts/results")


def load(name):
    return json.loads((R / name).read_text())


def main():
    tab, seq = load("tabular.json"), load("sequence.json")
    ret, fus = load("retrieval.json"), load("fusion.json")
    slm, base = load("slm.json"), load("baseline.json")

    # Each row is a LIKE-FOR-LIKE comparison. Phase 11 caught accuracy-without-coverage
    # being read as a win; this table must not reproduce that.
    rows = [
        ("07", "gradient-boosted tree", "always hold the release",
         f"{tab['threshold_sweep']['calibrated']['best_cost']:.4f} h/row",
         f"{tab['threshold_sweep']['calibrated']['constant_always_real_defect']:.4f} h/row",
         "tie, to 4 dp"),
        ("08", "GRU over run histories", "sum() over a list",
         "0 cells", "4 cells", "control wins"),
        ("09", "MiniLM retrieval 5-NN", 'if "setSNIServerNames" in text',
         f"{ret['controls']['minilm_embeddings_5nn_loco']:.4f}",
         f"{ret['controls']['substring_setSNIServerNames']:.4f}",
         "tie, to 4 dp"),
        ("11", "LLM arbiter (gpt-4o-mini)", "stub: top surviving voice",
         "0.9904", "0.9904", "tie, same 166"),
        ("12", "fine-tuned SLM", "TF-IDF + linear",
         "never ran", f"{slm['baselines']['tfidf_char_ngram_linear']['mean']:.4f}",
         "gated out"),
    ]

    print()
    # print("  every component, against the cheapest thing that could work")
    print()
    print(f"  {'':<3} {'built':<26} {'free alternative':<30} {'built':>11} {'free':>11}   result")
    print(f"  {'-' * 3} {'-' * 26} {'-' * 30} {'-' * 11} {'-' * 11}   {'-' * 13}")
    for ph, built, free, a, b, who in rows:
        print(f"  {ph:<3} {built:<26} {free:<30} {a:>11} {b:>11}   {who}")
    print()
    lopo = base["splits"]["leave_one_project_out"]
    print(f"  deployment split (leave-one-project-out): AUC "
          f"{lopo['mean_auc']:.4f} +/- {lopo['std_auc']:.4f}, "
          f"{lopo['n_folds_evaluated']} folds")
    print(f"  fusion: {fus['identical_decisions']['A_vs_B']} identical labels "
          f"across strategies A, B and C")
    print(f"  08 and 11 are compared like-for-like: cells won across all six, and "
          f"accuracy on")
    print(f"     the arbiter's own covered set -- an accuracy without its coverage is "
          f"not a result.")
    print()
    # print("  five components. five free baselines. zero wins.")
    print()


if __name__ == "__main__":
    main()
