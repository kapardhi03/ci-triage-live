"""Trust gate: may this run's outcomes contribute evidence at all?

A run where the build never compiled reports every test as failing. A truncated run
reports everything that had not executed yet as failing. Both look, in the raw counts,
exactly like a run where hundreds of tests genuinely failed -- and under phase 03's rule
(IsFlaky = a pass and a fail were both observed) a single poisoned run manufactures a
flaky label for every clean test in the suite.

See design/05-infra-gate.md for the slice and decisions/05-infra-gate.md for the numbers.
"""

import io
import re
import tarfile
from collections import Counter

# Results-summary lines: one per module, emitted last, WITHOUT "Time elapsed".
# Lines WITH "Time elapsed" are per-test-class and double-count if summed.
RESULTS = re.compile(r"Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)\s*$", re.M)
FAILED_TEST = re.compile(r"^(\w+)\(([\w.$]+)\)\s+Time elapsed: \S+ sec\s+<<< (?:FAILURE|ERROR)!", re.M)

TRUSTED, BUILD_FAILED, LOG_TRUNCATED, MASS_FAILURE, UNKNOWN = (
    "TRUSTED", "BUILD_FAILED", "LOG_TRUNCATED", "MASS_FAILURE", "UNKNOWN",
)

# Fraction of a suite failing at once that is implausible as independent test-level causes.
# Chosen at 30% and NOT validated by kevinsawicki-http-request, where the observed maximum
# is 9.2% and every threshold from ~10% to 100% behaves identically. See decisions/05.
MASS_FAILURE_THRESHOLD = 0.30

# A test failing in at least this fraction of a project's archived runs is a deterministic
# failure on the pinned revision, not infrastructure noise, and is excluded from the
# mass-failure fraction so it cannot drag borderline runs over the threshold.
DETERMINISTIC_THRESHOLD = 0.90


def parse_log(text):
    """Extract the counts a verdict is allowed to be built from."""
    results = RESULTS.findall(text)
    return {
        "modules": len(results),
        "total": sum(int(r[0]) for r in results),
        "failed": sum(int(r[1]) + int(r[2]) for r in results),
        "failed_tests": {f"{cls.split('.')[-1]}.{name}" for name, cls, in
                         ((m[0], m[1]) for m in FAILED_TEST.findall(text))},
        "build_success": "BUILD SUCCESS" in text,
        "build_failure": "BUILD FAILURE" in text,
        "bytes": len(text),
    }


def classify(text, deterministic=frozenset(), threshold=MASS_FAILURE_THRESHOLD):
    """One run in, one verdict plus a reason built from what was actually found.

    Precedence: BUILD_FAILED -> LOG_TRUNCATED -> MASS_FAILURE -> TRUSTED, UNKNOWN last.
    Feasibility first, cause before symptom second.
    """
    if text is None:
        return {"verdict": UNKNOWN, "reason": "no maven.log in the run archive",
                "evidence": {}}

    f = parse_log(text)
    has_marker = f["build_success"] or f["build_failure"]

    if f["build_failure"]:
        return {"verdict": BUILD_FAILED,
                "reason": f"log contains BUILD FAILURE; {f['total']} tests summarised "
                          f"across {f['modules']} module(s)",
                "evidence": f}

    # Truncation before mass-failure: the Results summaries and the end-marker are both
    # emitted last, so a tail cut removes the denominator AND the completeness signal.
    if f["modules"] == 0 or not has_marker:
        missing = []
        if f["modules"] == 0:
            missing.append("no Results summary line")
        if not has_marker:
            missing.append("no BUILD SUCCESS/FAILURE marker")
        return {"verdict": LOG_TRUNCATED,
                "reason": f"{' and '.join(missing)} ({f['bytes']} bytes read); the failure "
                          f"fraction is undefined without a total, and truncation cannot be "
                          f"distinguished from abnormal termination because both markers "
                          f"sit at the end of the log",
                "evidence": f}

    counted = f["failed_tests"] - deterministic
    excluded = len(f["failed_tests"] & deterministic)
    # Fall back to the summary count when per-test lines are unavailable.
    failed = len(counted) if f["failed_tests"] else max(0, f["failed"] - excluded)
    fraction = failed / f["total"] if f["total"] else 0.0
    f = {**f, "fraction": fraction, "excluded_deterministic": excluded,
         "failed_after_exclusion": failed}

    if f["total"] == 0:
        return {"verdict": UNKNOWN,
                "reason": f"{f['modules']} Results line(s) present but 0 tests summarised; "
                          f"cannot tell a suite that ran nothing from one that reported nothing",
                "evidence": f}

    if fraction >= threshold:
        return {"verdict": MASS_FAILURE,
                "reason": f"{failed}/{f['total']} tests failed = {fraction:.1%}, at or above "
                          f"the {threshold:.0%} threshold"
                          + (f" ({excluded} deterministic failure(s) excluded)" if excluded else ""),
                "evidence": f}

    return {"verdict": TRUSTED,
            "reason": f"{f['modules']} module(s), {f['total']} tests, {failed} failed "
                      f"= {fraction:.1%}, below the {threshold:.0%} threshold"
                      + (f" ({excluded} deterministic failure(s) excluded)" if excluded else ""),
            "evidence": f}


def iter_runs(archive_path):
    """Yield (run_id, maven.log text or None) from the nested project archive.

    The project .tgz holds one .tgz per run; maven.log lives inside that inner archive.
    Nothing is extracted to disk.
    """
    with tarfile.open(archive_path, "r:gz") as outer:
        for member in outer:
            if not member.name.endswith(".tgz"):
                continue
            run = member.name.split("/")[-1][:-4]
            try:
                blob = outer.extractfile(member).read()
                with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as inner:
                    logs = [n for n in inner.getnames() if n.endswith("maven.log")]
                    yield run, (inner.extractfile(logs[0]).read().decode("utf-8", "replace")
                                if logs else None)
            except (tarfile.TarError, EOFError, OSError):
                yield run, None


def deterministic_tests(parsed_runs, threshold=DETERMINISTIC_THRESHOLD):
    """Tests failing in >= threshold of a project's archived runs, computed once.

    A test red in nearly every run is a deterministic failure on the pinned revision, not
    a random infrastructure symptom, and must not inflate any run's failure fraction.
    """
    seen, n = Counter(), 0
    for f in parsed_runs:
        n += 1
        seen.update(f["failed_tests"])
    return {t for t, c in seen.items() if n and c / n >= threshold}, n


def gate_project(archive_path, threshold=MASS_FAILURE_THRESHOLD,
                 deterministic_threshold=DETERMINISTIC_THRESHOLD):
    """Two passes: identify deterministic tests once, then verdict every run."""
    parsed = {}
    for run, text in iter_runs(archive_path):
        parsed[run] = parse_log(text) if text is not None else None

    present = [f for f in parsed.values() if f is not None]
    excluded, n_scanned = deterministic_tests(present, deterministic_threshold)

    verdicts, all_failing, trusted_failing = Counter(), set(), set()
    reasons, runs_out = {}, {}
    for run, f in parsed.items():
        text_present = f is not None
        r = classify(_reconstruct(f) if text_present else None, excluded, threshold) \
            if not text_present else _classify_parsed(f, excluded, threshold)
        verdicts[r["verdict"]] += 1
        reasons.setdefault(r["verdict"], r["reason"])
        runs_out[run] = r["verdict"]
        if text_present:
            all_failing |= f["failed_tests"]
            if r["verdict"] == TRUSTED:
                trusted_failing |= f["failed_tests"]

    return {
        "project": str(archive_path).split("/")[-1].replace(".tgz", ""),
        "runs": len(parsed),
        "mass_failure_threshold": threshold,
        "deterministic_threshold": deterministic_threshold,
        "verdicts": dict(verdicts),
        "example_reason_per_verdict": reasons,
        "deterministic_tests_excluded": sorted(excluded),
        "distinct_failing_tests_all_runs": len(all_failing),
        "distinct_failing_tests_trusted_runs": len(trusted_failing),
        "tests_lost_to_gating": sorted(all_failing - trusted_failing),
        "runs_scanned_for_deterministic": n_scanned,
    }


def _reconstruct(_f):
    return None


def _classify_parsed(f, excluded, threshold):
    """classify() on already-parsed counts, so the archive is read once."""
    has_marker = f["build_success"] or f["build_failure"]
    if f["build_failure"]:
        return {"verdict": BUILD_FAILED,
                "reason": f"log contains BUILD FAILURE; {f['total']} tests summarised "
                          f"across {f['modules']} module(s)", "evidence": f}
    if f["modules"] == 0 or not has_marker:
        missing = ([] if f["modules"] else ["no Results summary line"]) + \
                  ([] if has_marker else ["no BUILD SUCCESS/FAILURE marker"])
        return {"verdict": LOG_TRUNCATED,
                "reason": f"{' and '.join(missing)} ({f['bytes']} bytes read); the failure "
                          f"fraction is undefined without a total, and truncation cannot be "
                          f"distinguished from abnormal termination because both markers "
                          f"sit at the end of the log", "evidence": f}
    counted = f["failed_tests"] - excluded
    n_excl = len(f["failed_tests"] & excluded)
    failed = len(counted) if f["failed_tests"] else max(0, f["failed"] - n_excl)
    frac = failed / f["total"] if f["total"] else 0.0
    f = {**f, "fraction": frac, "excluded_deterministic": n_excl}
    if f["total"] == 0:
        return {"verdict": UNKNOWN,
                "reason": f"{f['modules']} Results line(s) present but 0 tests summarised; "
                          f"cannot tell a suite that ran nothing from one that reported nothing",
                "evidence": f}
    tail = f" ({n_excl} deterministic failure(s) excluded)" if n_excl else ""
    if frac >= threshold:
        return {"verdict": MASS_FAILURE,
                "reason": f"{failed}/{f['total']} tests failed = {frac:.1%}, at or above the "
                          f"{threshold:.0%} threshold{tail}", "evidence": f}
    return {"verdict": TRUSTED,
            "reason": f"{f['modules']} module(s), {f['total']} tests, {failed} failed = "
                      f"{frac:.1%}, below the {threshold:.0%} threshold{tail}", "evidence": f}
