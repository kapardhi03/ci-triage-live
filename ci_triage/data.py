"""Ingestion: three source CSVs -> one feature matrix that cannot contain the label.

Source: FlakeFlagger, Zenodo record 4450723, CC-BY-4.0. See decisions/04-dataset-choice.md.
Fetch and verify with scripts/fetch_raw.sh before calling anything here.
"""

import hashlib
import json
from pathlib import Path

import pandas as pd

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

CHECKSUMS = {
    "Project_Info.csv": "5b3392a4f7367b2a566b919a98989a97",
    "test_features.csv": "63306c05fafcc6446911ab7000f85ae0",
    "test_results.csv": "fcd2674ab42068de627ec6afce4f6d1a",
}

LABEL = "IsFlaky"

# Every column denied from the feature matrix, with the reason it is denied.
# design/04-data-and-licence.md is the argument; this is the enforcement.
EXCLUDED = {
    "FirstFailingRunID": "label_derived",
    "FirstPassingRunID": "label_derived",
    "UniqueFailingExceptionTypes": "label_derived",
    "NumFailingRuns": "label_derived",
    "NumPassingRuns": "label_derived",
    "flaky": "alternate_label",
    "flaky_source": "label_derived",
    "hIndexModificationsPerCoveredLine_window5": "project_constant",
    "hIndexModificationsPerCoveredLine_window10": "project_constant",
    # Added in phase 06. Deployment is unseen projects, and on leave-one-project-out
    # these 8 cost 0.039 AUC while giving back 0.005 on a random split -- they help
    # within-project and hurt across it. See decisions/06-split-choice.md.
    "projectSourceLinesCovered": "project_scale",
    "projectSourceClassesCovered": "project_scale",
    "hIndexModificationsPerCoveredLine_window25": "project_scale",
    "hIndexModificationsPerCoveredLine_window50": "project_scale",
    "hIndexModificationsPerCoveredLine_window75": "project_scale",
    "hIndexModificationsPerCoveredLine_window100": "project_scale",
    "hIndexModificationsPerCoveredLine_window500": "project_scale",
    "hIndexModificationsPerCoveredLine_window10000": "project_scale",
    "test_name": "identifier",
    "project": "identifier",
    "testClassName": "identifier",
    "testMethodName": "identifier",
    "Project": "identifier",
    "Test": "identifier",
    "": "identifier",
    "Unnamed: 0": "identifier",
    LABEL: "label",
}


def _md5(path):
    return hashlib.md5(path.read_bytes()).hexdigest()


def verify_checksums(raw=RAW):
    """Refuse to proceed on any source file that is not the one we recorded."""
    for name, want in CHECKSUMS.items():
        path = raw / name
        if not path.exists():
            raise FileNotFoundError(f"{path} missing — run scripts/fetch_raw.sh")
        got = _md5(path)
        if got != want:
            raise ValueError(f"checksum mismatch for {name}: got {got}, expected {want}")


def _project_map(feature_projects, result_projects):
    """test_results uses `owner-repo`; test_features uses `repo`. Match by suffix."""
    mapping = {}
    for rp in result_projects:
        hits = [fp for fp in feature_projects if rp == fp or rp.endswith("-" + fp)]
        if len(hits) == 1:
            mapping[rp] = hits[0]
    return mapping


def load_joined(raw=RAW, verify=True):
    """Join the two CSVs into one row per test. Returns (frame, join_report)."""
    if verify:
        verify_checksums(raw)

    features = pd.read_csv(raw / "test_features.csv")
    results = pd.read_csv(raw / "test_results.csv")

    results_raw = len(results)
    mapping = _project_map(set(features["project"]), set(results["Project"]))

    # Capture what the mapping could not place BEFORE those rows are dropped, or the
    # manifest reports a clean join that silently lost projects.
    unmapped = sorted(set(results["Project"]) - set(mapping))
    unused_feature_projects = sorted(set(features["project"]) - set(mapping.values()))
    dropped_unmapped = int((~results["Project"].isin(mapping)).sum())

    results = results.assign(
        project=results["Project"].map(mapping),
        test_name=results["Test"].str.replace("#", ".", regex=False).str.lower(),
    ).dropna(subset=["project"])

    # 8 case-folding collisions exist in results; keep the first and record the loss.
    before = len(results)
    results = results.drop_duplicates(subset=["project", "test_name"], keep="first")

    joined = features.merge(results, on=["project", "test_name"], how="inner")

    report = {
        "features_rows": len(features),
        "results_rows": results_raw,
        "results_after_project_map": before,
        "results_after_dedupe": len(results),
        "case_folding_collisions": before - len(results),
        "unmapped_result_projects": unmapped,
        "rows_dropped_unmapped_project": dropped_unmapped,
        "unused_feature_projects": unused_feature_projects,
        "joined_rows": len(joined),
        "features_rows_unjoined": len(features) - len(joined),
        "join_key": "(suffix-matched project, lowercase(Test with '#'->'.'))",
    }
    return joined, report


def feature_matrix(raw=RAW, verify=True):
    """The only function that returns features. The leak guard is inside it.

    X is built from an allowlist of columns that survived, never by subtracting a
    blocklist from whatever arrived — a column added upstream later is denied by default.
    """
    joined, report = load_joined(raw, verify=verify)

    joined = joined.dropna(subset=[LABEL])
    y = joined[LABEL].astype(int)
    groups = joined["project"]

    kept = [c for c in joined.columns if c not in EXCLUDED and not c.startswith("Unnamed")]
    X = joined[kept].copy()

    # The guard, after every merge and rename. Not reachable around.
    leaked = sorted(set(X.columns) & set(EXCLUDED))
    if leaked:
        raise AssertionError(f"excluded columns reached the feature matrix: {leaked}")

    manifest = {
        **report,
        "label": LABEL,
        "rows": len(X),
        "n_features": X.shape[1],
        "features": list(X.columns),
        "excluded": [
            {"column": c, "reason": EXCLUDED[c]}
            for c in sorted(set(joined.columns) & set(EXCLUDED))
        ],
        "positives": int(y.sum()),
        "positive_rate": float(y.mean()),
        "n_projects": int(groups.nunique()),
        "checksums": CHECKSUMS,
        "source": "FlakeFlagger, Zenodo 4450723, CC-BY-4.0",
    }
    return X, y, groups, manifest


def main():
    X, y, groups, manifest = feature_matrix()
    out = Path("artifacts/results/eda.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"rows={manifest['rows']}  features={manifest['n_features']}  "
          f"positives={manifest['positives']} ({manifest['positive_rate']:.4%})  "
          f"projects={manifest['n_projects']}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
