"""Tests for ci_triage.infra — the reason must match what was found.

The load-bearing tests here are the reason-correspondence ones. A verdict can be correct
while its audit trail is fabricated, and that bug passes every test that only checks
verdicts. A future engineer asking why 400 runs vanished reads the reason.
"""

import pathlib
import re

import pytest

from ci_triage.infra import (
    BUILD_FAILED, LOG_TRUNCATED, MASS_FAILURE, TRUSTED, UNKNOWN,
    classify, deterministic_tests, parse_log,
)

ARCHIVE = pathlib.Path("data/raw/archives/kevinsawicki-http-request.tgz")


def log(modules, marker="BUILD SUCCESS", failed_tests=()):
    """Build a maven.log in the real format: per-class lines WITH Time elapsed,
    Results summary lines WITHOUT it, one per module."""
    out = []
    for total, fails, errs in modules:
        out.append(f"Tests run: {total}, Failures: {fails}, Errors: {errs}, "
                   f"Skipped: 0, Time elapsed: 1.2 sec")
        for name, cls in failed_tests:
            out.append(f"{name}({cls})  Time elapsed: 0.006 sec  <<< FAILURE!")
        out.append(f"Tests run: {total}, Failures: {fails}, Errors: {errs}, Skipped: 0")
    if marker:
        out.append(marker)
    return "\n".join(out)


# --- the constraint: reason matches what was found -------------------------------------

def test_trusted_reason_reports_the_real_counts():
    """Every number in the reason must appear in the evidence it claims to describe."""
    r = classify(log([(163, 0, 0)]))
    assert r["verdict"] == TRUSTED
    assert "163 tests" in r["reason"]
    assert "1 module(s)" in r["reason"]
    assert r["evidence"]["total"] == 163


def test_multi_module_reason_reports_the_summed_total_not_one_module():
    """square-okhttp emits 5 Results lines summing to 826. The reason must say 826."""
    r = classify(log([(400, 0, 0), (200, 0, 0), (150, 0, 0), (70, 0, 0), (6, 0, 0)]))
    assert r["evidence"]["total"] == 826
    assert r["evidence"]["modules"] == 5
    assert "826 tests" in r["reason"] and "5 module(s)" in r["reason"]
    assert "400" not in r["reason"], "reported one module's count as the whole build"


def test_mass_failure_reason_percentage_matches_the_evidence():
    """The stated percentage must equal failed/total, not a plausible-looking number."""
    r = classify(log([(100, 50, 10)]))
    assert r["verdict"] == MASS_FAILURE
    pct = float(re.search(r"= (\d+\.\d)%", r["reason"]).group(1))
    assert pct == pytest.approx(r["evidence"]["fraction"] * 100, abs=0.05)
    assert "60/100" in r["reason"]


def test_build_failed_reason_does_not_claim_tests_failed():
    """A run that never compiled must not be described as a test problem."""
    r = classify(log([(163, 163, 0)], marker="BUILD FAILURE"))
    assert r["verdict"] == BUILD_FAILED
    assert "BUILD FAILURE" in r["reason"]
    assert "threshold" not in r["reason"], "reported a mass-failure reason for a build failure"


def test_truncated_reason_admits_it_cannot_distinguish_truncation_from_death():
    """Both the Results summary and the end-marker sit at the end, so both die together."""
    r = classify("Tests run: 40, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 1.0 sec")
    assert r["verdict"] == LOG_TRUNCATED
    assert "no Results summary line" in r["reason"]
    assert "no BUILD SUCCESS/FAILURE marker" in r["reason"]
    assert "abnormal termination" in r["reason"], "asserted truncation it cannot demonstrate"
    assert "fraction" not in r["evidence"], "computed a fraction on a truncated log"


# --- precedence -------------------------------------------------------------------------

def test_build_failure_outranks_mass_failure():
    """100% failed AND never compiled -> the cause, not the symptom."""
    assert classify(log([(163, 163, 0)], marker="BUILD FAILURE"))["verdict"] == BUILD_FAILED


def test_truncation_outranks_mass_failure():
    """Feasibility: the fraction cannot be computed, so it must not be reported."""
    r = classify("Tests run: 140, Failures: 140, Errors: 0, Skipped: 0, Time elapsed: 1s")
    assert r["verdict"] == LOG_TRUNCATED


def test_unparseable_run_is_not_trusted():
    """Absence of evidence of a problem is not evidence of a sound run (phase 03)."""
    assert classify(None)["verdict"] == UNKNOWN
    assert classify(log([(0, 0, 0)]))["verdict"] == UNKNOWN


# --- deterministic exclusion ------------------------------------------------------------

def test_deterministic_tests_do_not_inflate_the_mass_failure_fraction():
    """A test red in nearly every run must not drag a borderline run over the threshold."""
    failures = [(f"t{i}", "com.x.T") for i in range(35)]
    text = log([(100, 35, 0)], failed_tests=failures)

    without = classify(text)
    with_excl = classify(text, deterministic={f"T.t{i}" for i in range(30)})

    assert without["verdict"] == MASS_FAILURE
    assert with_excl["verdict"] == TRUSTED
    assert with_excl["evidence"]["excluded_deterministic"] == 30
    assert "30 deterministic failure(s) excluded" in with_excl["reason"]


def test_deterministic_set_uses_the_all_runs_denominator():
    """Fails in >= 90% of a project's runs. A 2.6% correlated flake must not qualify."""
    always = [{"failed_tests": {"T.always"}} for _ in range(95)]
    never = [{"failed_tests": set()} for _ in range(5)]
    flaky = [{"failed_tests": {"T.correlated"}} for _ in range(3)]
    found, n = deterministic_tests(always + never + flaky[:0])
    assert found == {"T.always"} and n == 100

    # the kevinsawicki case: 15 tests failing in 2.59% of runs are flakes, not deterministic
    runs = [{"failed_tests": {"T.a", "T.b"}} for _ in range(26)] + \
           [{"failed_tests": set()} for _ in range(974)]
    found, n = deterministic_tests(runs)
    assert found == set(), "correlated flakes were misclassified as deterministic"


# --- parsing ----------------------------------------------------------------------------

def test_per_class_lines_are_not_summed_into_the_total():
    """Lines WITH 'Time elapsed' are per-test-class; summing all lines double-counts."""
    f = parse_log(log([(161, 0, 0), (2, 0, 0)]))
    assert f["total"] == 163, "summed per-class lines as well as Results lines"


# --- against the real archive -----------------------------------------------------------

@pytest.mark.skipif(not ARCHIVE.exists(), reason="run scripts/fetch_archives.sh")
def test_real_archive_matches_the_recorded_scan():
    """Guards the parser against the actual data. Recorded in artifacts/results/infra.json."""
    from ci_triage.infra import iter_runs
    seen = 0
    for run, text in iter_runs(ARCHIVE):
        r = classify(text)
        assert r["verdict"] == TRUSTED
        assert r["evidence"]["total"] == 163
        seen += 1
        if seen >= 50:
            break
    assert seen == 50
