"""Rebuild the frozen fusion inputs from the raw archives and CSVs.

The phase 11 observer probabilities previously existed only in a scratchpad, so the fusion
comparison was not reproducible from this repository. This module regenerates them from
data/raw/, writes artifacts/results/fusion-inputs.json, and verifies the frozen case hash.

    uv run python -m ci_triage.evidence
"""

import csv
import io
import json
import re
import tarfile
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

from ci_triage.data import feature_matrix
from ci_triage.infra import (
    TRUSTED, _classify_parsed, deterministic_tests, iter_runs, parse_log,
)
from ci_triage.retrieval import ABSTAIN, MessageLookup
from ci_triage.tabular import make_calibrated

PROJECT = "square-okhttp"
ARCHIVE = Path("data/raw/archives") / f"{PROJECT}.tgz"
OUT = Path("artifacts/results/fusion-inputs.json")
FROZEN_HASH = "305d8ece8a0fa240"
PREFIX_K = 200

FAILURE_BLOCK = re.compile(
    r"^(\w+)\(([\w.$]+)\)\s+Time elapsed: \S+ sec\s+<<< (?:FAILURE|ERROR)!\s*\n(.*?)(?=\n\S|\Z)",
    re.M | re.S)


def scan_archive(archive=ARCHIVE):
    """One pass: trusted-run outcomes per test, and each test's most frequent message."""
    parsed, texts = {}, defaultdict(Counter)
    for run, log in iter_runs(archive):
        f = parse_log(log) if log is not None else None
        parsed[run] = f
        if f is None or f["modules"] == 0 or not (f["build_success"] or f["build_failure"]):
            continue
        for name, cls, body in FAILURE_BLOCK.findall(log):
            lines = [l.strip() for l in body.strip().splitlines() if l.strip()]
            msg = " ".join(l for l in lines[:2] if not l.startswith("at "))
            if msg:
                texts[f"{cls.split('.')[-1]}.{name}"][msg[:300]] += 1

    excluded, _ = deterministic_tests([f for f in parsed.values() if f])
    trusted = sorted((int(r), f["failed_tests"]) for r, f in parsed.items()
                     if f and _classify_parsed(f, excluded, 0.30)["verdict"] == TRUSTED)
    return trusted, {t: c.most_common(1)[0][0] for t, c in texts.items()}, set(excluded)


def suite_tests(project=PROJECT):
    out = set()
    with open("data/raw/test_results.csv", encoding="utf-8", errors="replace") as fh:
        for r in csv.DictReader(fh):
            if r["Project"] == project:
                cls, meth = (r["Test"].split("#", 1) if "#" in r["Test"]
                             else (r["Test"], ""))
                out.add(f"{cls.split('.')[-1]}.{meth}")
    return out


def build(archive=ARCHIVE, out=OUT):
    trusted, messages, deterministic = scan_archive(archive)
    cases = sorted(set(messages) & suite_tests())
    labels = [0 if t in deterministic else 1 for t in cases]

    # observer 2: prefix failure count over the first k trusted runs (the phase 08 control)
    counts = {t: sum(1 for _, failed in trusted[:PREFIX_K] if t in failed) for t in cases}
    hi = max(counts.values()) or 1
    p_seq = {t: 1.0 - c / hi for t, c in counts.items()}

    # observer 1: calibrated GBT, this project fully held out
    X, y, groups, manifest = feature_matrix()
    Xn = X.apply(lambda c: pd.to_numeric(c, errors="coerce")).values
    held = groups.values == "okhttp"
    model = make_calibrated("sigmoid").fit(Xn[~held], y.values[~held])
    rows = [r for r in csv.DictReader(open("data/raw/test_features.csv", encoding="utf-8",
                                           errors="replace")) if r["project"] == "okhttp"]
    names = [f"{r['testClassName'].split('.')[-1]}.{r['testMethodName']}" for r in rows]
    p_tab = dict(zip(names, model.predict_proba(Xn[held])[:, 1]))

    # observer 3: exact-message lookup, leave-one-class-out
    def cls_of(n):
        return n.split(".")[0]

    p_look = {}
    for t in cases:
        block = {m for m in cases if cls_of(m) == cls_of(t)}
        keep = [m for m in messages if m not in block]
        lk = MessageLookup().fit([messages[m] for m in keep],
                                 [0 if m in deterministic else 1 for m in keep])
        r = lk.predict(messages[t])
        p_look[t] = None if r["verdict"] == ABSTAIN else r["probability"]

    payload = {
        "project": PROJECT, "n_trusted_runs": len(trusted), "prefix_k": PREFIX_K,
        "cases": cases, "labels": labels,
        "p_tab": [float(p_tab[t]) if t in p_tab else None for t in cases],
        "p_seq": [float(p_seq[t]) for t in cases],
        "p_look": [None if p_look[t] is None else float(p_look[t]) for t in cases],
        "messages": {t: messages[t] for t in cases},
        "data_digest": {k: manifest[k] for k in ("rows", "positives", "n_features")},
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n")
    return payload


def main():
    from ci_triage.fusion import freeze_cases
    p = build()
    h = freeze_cases(p["cases"])
    print(f"{p['project']}: {len(p['cases'])} cases, {sum(p['labels'])} flaky, "
          f"{p['n_trusted_runs']} trusted runs")
    print(f"frozen hash {h}  expected {FROZEN_HASH}  "
          f"{'MATCH' if h == FROZEN_HASH else 'MISMATCH -- the run is void'}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
