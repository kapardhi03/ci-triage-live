"""Tests for ci_triage.fusion.

The load-bearing test is false consensus: the pipeline must not report unanimity when the
observers agreeing are not distinct. Three records from one cause_group are one opinion, and
reporting them as three is how a shared cause manufactures confidence.
"""

import numpy as np
import pytest

from ci_triage.contracts import Evidence, State, Verdict
from ci_triage.fusion import (
    INCOMPLETE, distinct_voices, evaluate_strategy, freeze_cases, is_false_consensus,
    js_divergence, max_divergence, rank, strategy_escalate_on_disagreement,
    strategy_llm_arbiter, strategy_mean, strategy_most_confident, strategy_threshold,
)

FROZEN_HASH = "305d8ece8a0fa240"   # 202 square-okhttp cases, phase 11


def ev(observer, cause, p, test="T.a", calibrated=True):
    return Evidence(observer=observer, test=test, state=State.OBSERVED,
                    verdict=Verdict.FLAKY, reads=frozenset({observer}),
                    cause_group=cause, probability=p, calibrated=calibrated)


# --- TASK step 7: false consensus --------------------------------------------------------

def test_unanimity_from_one_cause_group_is_not_consensus():
    """Three observers, one voice. The pipeline must not call this agreement."""
    records = [ev("tabular", "ssl-jvm", 0.90),
               ev("retrieval", "ssl-jvm", 0.92),
               ev("echo", "ssl-jvm", 0.91)]
    assert distinct_voices(records) == 1
    assert is_false_consensus(records) is True


def test_unanimity_from_distinct_causes_is_consensus():
    records = [ev("tabular", "ssl-jvm", 0.90), ev("sequence", "run-history", 0.92)]
    assert distinct_voices(records) == 2
    assert is_false_consensus(records) is False


def test_disagreement_is_never_false_consensus():
    records = [ev("a", "ssl-jvm", 0.1), ev("b", "ssl-jvm", 0.9)]
    assert is_false_consensus(records) is False


def test_correlated_agreement_cannot_move_a_fused_probability():
    """Adding correlated records that agree must not change the answer at all."""
    two = [ev("tabular", "ssl-jvm", 0.9), ev("sequence", "run-history", 0.5)]
    five = two + [ev(f"echo{i}", "ssl-jvm", 0.9) for i in range(3)]
    assert strategy_mean(two) == pytest.approx(strategy_mean(five))
    assert strategy_most_confident(two) == pytest.approx(strategy_most_confident(five))


# --- divergence: distributions, not labels -----------------------------------------------

def test_same_label_can_hide_a_large_divergence():
    """Both say 'flaky' at a 0.5 cutoff, and they believe completely different things."""
    a, b = 0.51, 0.99
    assert (a >= 0.5) == (b >= 0.5), "same label"
    assert js_divergence(a, b) > 0.2, "and a large divergence the label hides"


def test_js_is_symmetric_and_bounded():
    assert js_divergence(0.2, 0.8) == pytest.approx(js_divergence(0.8, 0.2))
    assert 0.0 <= js_divergence(0.0, 1.0) <= 1.0
    assert js_divergence(0.7, 0.7) == pytest.approx(0.0)


def test_js_distinguishes_what_total_variation_cannot():
    """|0.45-0.55| == |0.05-0.15|, but they are not the same disagreement."""
    middle = js_divergence(0.45, 0.55)
    extreme = js_divergence(0.05, 0.15)
    assert abs(0.55 - 0.45) == pytest.approx(abs(0.15 - 0.05)), "TV calls these equal"
    assert extreme > middle * 2, "JS does not"


# --- the strategies ------------------------------------------------------------------------

def test_escalate_abstains_on_disagreement_and_answers_on_agreement():
    agree = [ev("a", "g1", 0.85), ev("b", "g2", 0.88)]
    disagree = [ev("a", "g1", 0.10), ev("b", "g2", 0.90)]
    assert strategy_escalate_on_disagreement(agree) is not None
    assert strategy_escalate_on_disagreement(disagree) is None


def test_threshold_returns_a_hard_label_not_a_belief():
    assert strategy_threshold([ev("a", "g1", 0.99)]) == 1.0
    assert strategy_threshold([ev("a", "g1", 0.51)]) == 1.0
    assert strategy_threshold([ev("a", "g1", 0.49)]) == 0.0


def test_most_confident_takes_the_extreme_not_the_average():
    r = [ev("a", "g1", 0.95), ev("b", "g2", 0.55)]
    assert strategy_most_confident(r) == pytest.approx(0.95)
    assert strategy_mean(r) == pytest.approx(0.75)


# --- incomplete strategies are unranked, not ranked last ----------------------------------

def test_llm_arbiter_without_a_client_is_incomplete():
    with pytest.raises(RuntimeError, match="incomplete"):
        strategy_llm_arbiter([ev("a", "g1", 0.9)])

    out = evaluate_strategy(strategy_llm_arbiter, [[ev("a", "g1", 0.9)]], [1])
    assert out["status"] == INCOMPLETE


def test_an_incomplete_strategy_is_excluded_from_the_ranking_not_placed_last():
    results = {
        "A": {"status": "complete", "accuracy": 0.7},
        "B": {"status": "complete", "accuracy": 0.9},
        "E": {"status": INCOMPLETE, "reason": "no client"},
    }
    order, incomplete = rank(results, "accuracy")
    assert order == ["B", "A"]
    assert "E" not in order, "an unavailable strategy was ranked"
    assert incomplete == ["E"]


# --- the frozen case list -----------------------------------------------------------------

def test_case_list_hash_is_stable_and_order_sensitive():
    names = ["T.a", "T.b", "T.c"]
    assert freeze_cases(names) == freeze_cases(list(names))
    assert freeze_cases(names) != freeze_cases(["T.c", "T.b", "T.a"])


def test_coverage_is_reported_so_abstention_cannot_buy_accuracy():
    """A strategy that answers 2 of 4 must not be compared on accuracy alone."""
    cases = [[ev("a", "g1", 0.9), ev("b", "g2", 0.9)],
             [ev("a", "g1", 0.1), ev("b", "g2", 0.9)],
             [ev("a", "g1", 0.2), ev("b", "g2", 0.9)],
             [ev("a", "g1", 0.8), ev("b", "g2", 0.8)]]
    out = evaluate_strategy(strategy_escalate_on_disagreement, cases, [1, 1, 0, 1])
    assert out["coverage"] < 1.0
    assert out["n_covered"] < out["n_total"]


# --- the arbiter: the ship-direction clamp ------------------------------------------------

from ci_triage.fusion import (
    AGREE_FLAKY, AGREE_REAL_DEFECT, ESCALATE, arbiter_decide, null_arbiter,
    render_arbiter_prompt, strategy_llm_arbiter,
)


class StubClient:
    """Returns a fixed word. No network. The point is what the wrapper does with it."""

    def __init__(self, word):
        self.word = word
        self.prompts = []
        outer = self

        class _Completions:
            def create(self, model, temperature, max_tokens, messages):
                outer.prompts.append(messages[0]["content"])
                msg = type("M", (), {"content": outer.word})()
                return type("R", (), {"choices": [type("C", (), {"message": msg})()]})()

        self.chat = type("Chat", (), {"completions": _Completions()})()


def real_defect_records():
    """Collapsed evidence points REAL_DEFECT: the surviving voice is p(flaky)=0.05."""
    return [ev("tabular", "ssl-jvm", 0.05), ev("sequence", "run-history", 0.30)]


def test_arbiter_cannot_move_a_case_toward_ship():
    """THE invariant. A fluent model saying FLAKY against REAL_DEFECT evidence is refused.

    Under the phase 01 table a wrong "flaky" costs ~40h against ~3h for a needless hold, so
    the arbiter may confirm or escalate and never relax caution. Without the clamp the
    wrapper would return 1.0 here and the expensive error would ship.
    """
    stats = {}
    out = arbiter_decide(real_defect_records(), StubClient(AGREE_FLAKY), stats=stats)
    assert out == ESCALATE, "the arbiter moved a case toward SHIP"
    assert stats["clamped"] == 1, "the clamp fired but was not counted"

    # and the strategy wrapper abstains rather than emitting a flaky score
    assert strategy_llm_arbiter(real_defect_records(), client=StubClient(AGREE_FLAKY),
                                stats={}) is None


def test_arbiter_may_confirm_the_safe_direction():
    """The clamp must be directional, not a blanket refusal, or it proves nothing."""
    stats = {}
    out = arbiter_decide(real_defect_records(), StubClient(AGREE_REAL_DEFECT), stats=stats)
    assert out == AGREE_REAL_DEFECT
    assert "clamped" not in stats

    flaky_evidence = [ev("lookup", "ssl-jvm", 0.95)]
    assert arbiter_decide(flaky_evidence, StubClient(AGREE_FLAKY), stats={}) == AGREE_FLAKY


def test_arbiter_prompt_leaks_no_identity_or_label():
    """design/11's forbidden-to-see list, asserted against the rendered artefact."""
    prompt = render_arbiter_prompt(real_defect_records())
    for forbidden in ("T.a", "okhttp", "IsFlaky", "label", "HttpOverSpdy",
                      "A_most_confident", "D_escalate"):
        assert forbidden not in prompt, f"prompt leaked {forbidden!r}"


def test_arbiter_refuses_unparseable_output_rather_than_guessing():
    stats = {}
    with pytest.raises(ValueError, match="unparseable"):
        arbiter_decide(real_defect_records(), StubClient("I think it's probably flaky?"),
                       stats=stats)
    assert stats["unparseable"] == 1


def test_null_arbiter_needs_no_client():
    """The control must be free, or it is not a control."""
    assert null_arbiter(real_defect_records()) == pytest.approx(0.05)
    assert null_arbiter([ev("a", "g", 0.95)]) == pytest.approx(0.95)


def test_escalate_is_reported_as_coverage_not_dropped():
    out = evaluate_strategy(strategy_llm_arbiter,
                            [real_defect_records(), real_defect_records()], [0, 1],
                            client=StubClient(ESCALATE), stats={})
    assert out["n_covered"] == 0 and out["coverage"] == 0.0
