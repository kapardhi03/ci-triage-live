"""Slice 11: the decision layer. Five strategies, and the rules for comparing them.

Reads Evidence AFTER slice 10 has collapsed it by cause_group. Un-collapsed records let one
physical cause vote twice -- the coupling measured at AUC 0.6987 between observers 1 and 3.

A strategy that cannot run on every frozen case is `incomplete`: unranked, not a loss.
See experiments/11-fusion-comparison.md and decisions/11-arbiter-rules.md.
"""

import hashlib
import json
import os
from pathlib import Path

import numpy as np

from ci_triage.contracts import Evidence, State, Verdict, collapse_correlated

INCOMPLETE = "incomplete"


def js_divergence(p, q, eps=1e-12):
    """Jensen-Shannon divergence between two Bernoulli beliefs, in bits. Range [0, 1].

    Chosen over KL because observers have no privileged order (JS is symmetric; KL is not)
    and because KL is unbounded -- one observer at 0.0 against another at 1.0 gives infinity,
    which no ranking can use. JS is bounded, so divergences are comparable across pairs and
    a threshold on it means the same thing everywhere.

    Total variation was the other candidate; it is also symmetric and bounded but is linear
    in the gap, so it cannot distinguish disagreement near the extremes (0.05 vs 0.15) from
    disagreement in the middle (0.45 vs 0.55). Those are very different disagreements.
    """
    p, q = float(np.clip(p, eps, 1 - eps)), float(np.clip(q, eps, 1 - eps))
    m = 0.5 * (p + q)

    def kl(a, b):
        return a * np.log2(a / b) + (1 - a) * np.log2((1 - a) / (1 - b))

    return float(0.5 * kl(p, m) + 0.5 * kl(q, m))


def max_divergence(probs):
    """Largest pairwise JS divergence among the surviving observers."""
    vals = [p for p in probs if p is not None]
    if len(vals) < 2:
        return 0.0
    return max(js_divergence(a, b)
               for i, a in enumerate(vals) for b in vals[i + 1:])


def distinct_voices(records):
    """How many genuinely distinct opinions -- cause_groups, not records.

    Three records from one cause_group are one opinion. Reporting them as consensus is the
    false-consensus failure.
    """
    return len({r.cause_group for r in records if r.state is not State.NO_EVIDENCE})


def is_false_consensus(records):
    """True when records agree but are not distinct. Unanimity from one voice is not consensus."""
    usable = [r for r in records if r.state is State.OBSERVED and r.probability is not None]
    if len(usable) < 2:
        return False
    agree = max(r.probability for r in usable) - min(r.probability for r in usable) < 0.1
    return agree and distinct_voices(usable) < 2


# --- the strategies ----------------------------------------------------------------------

def _probs(records):
    c = collapse_correlated(records)
    return [r.probability for r in c
            if r.state is State.OBSERVED and r.probability is not None], c


def strategy_most_confident(records, **_):
    """A: the observer furthest from 0.5 wins."""
    p, c = _probs(records)
    if not p:
        return None
    return max(p, key=lambda x: abs(x - 0.5))


def strategy_mean(records, **_):
    """B: average the collapsed probabilities."""
    p, _ = _probs(records)
    return float(np.mean(p)) if p else None


def strategy_threshold(records, threshold=0.5, **_):
    """C: a fixed cutoff -- hard 0/1, no intermediate belief."""
    p, _ = _probs(records)
    if not p:
        return None
    return 1.0 if float(np.mean(p)) >= threshold else 0.0


def strategy_escalate_on_disagreement(records, divergence_threshold=0.1, **_):
    """D: agree -> use the mean; disagree -> ABSTAIN. Returns None when abstaining."""
    p, _ = _probs(records)
    if not p:
        return None
    if max_divergence(p) > divergence_threshold:
        return None            # ABSTAIN: a human decides
    return float(np.mean(p))


# --- strategy E: the arbiter -------------------------------------------------------------
#
# design/11 forbids it from seeing the label, the test/class/project identity, or any other
# strategy's output; and from manufacturing a probability, moving a case toward SHIP, or
# citing evidence absent from the record. The category it returns is mapped to the same
# hard 0/1-or-abstain shape C and D already have, so it is scored on the identical metric
# implementation without inventing a confidence.

AGREE_FLAKY, AGREE_REAL_DEFECT, ESCALATE = "AGREE_FLAKY", "AGREE_REAL_DEFECT", "ESCALATE"
ARBITER_MODEL = "gpt-4o-mini"


def load_env(path=".env"):
    """Read KEY=value lines. The key never enters source or a command line."""
    env = {}
    p = Path(path)
    if p.exists():
        for line in p.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def make_openai_client(env=None):
    from openai import OpenAI
    key = (env or load_env()).get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not key:
        return None
    return OpenAI(api_key=key)


def render_arbiter_prompt(records):
    """Every line comes from an Evidence record. No identity, no label, no strategy output."""
    lines = ["You are arbitrating between automated observers about one CI test failure.",
             "", "EVIDENCE RECORD"]
    for r in sorted(records, key=lambda x: x.observer):
        lines.append(f"  observer: {r.observer}")
        lines.append(f"    state: {r.state.value}")
        if r.probability is not None:
            lines.append(f"    probability(flaky): {r.probability:.4f}")
            lines.append(f"    calibrated: {str(bool(r.calibrated)).lower()}")
        else:
            lines.append("    reason: this observer had no evidence for this case")
        lines.append(f"    reads: {', '.join(sorted(r.reads)) or 'n/a'}")
        lines.append(f"    cause_group: {r.cause_group}")
    groups = {}
    for r in records:
        groups.setdefault(r.cause_group, []).append(r.observer)
    shared = {g: o for g, o in groups.items() if len(o) > 1}
    if shared:
        for g, obs in sorted(shared.items()):
            lines += ["", f"NOTE: {' and '.join(sorted(obs))} share cause_group `{g}`. One "
                          f"underlying cause drives both, so their agreement is ONE "
                          f"observation, not several."]
    lines += ["", "YOU MAY OUTPUT EXACTLY ONE WORD:",
              f"  {AGREE_FLAKY}        - the surviving evidence supports flaky",
              f"  {AGREE_REAL_DEFECT}  - the surviving evidence supports a real defect",
              f"  {ESCALATE}           - a human should decide", "",
              "YOU MAY NOT output a probability, explain yourself, or cite anything absent",
              "from the record. Reply with the single word only."]
    return "\n".join(lines)


def _collapsed_direction(records):
    """P(flaky) of the most informative surviving voice, or None."""
    c = collapse_correlated(records)
    scored = [r for r in c if r.state is State.OBSERVED and r.probability is not None]
    if not scored:
        return None
    return max(scored, key=lambda r: abs(r.probability - 0.5)).probability


def arbiter_decide(records, client, model=ARBITER_MODEL, stats=None):
    """One case. Returns a category, after the ship-direction clamp.

    The clamp is absolute: where collapsed evidence points REAL_DEFECT the arbiter may
    confirm or escalate, never move toward FLAKY. A refused move becomes ESCALATE -- the
    conservative direction -- and is counted, because the clamp rate is a reported result
    and not only a safety mechanism.
    """
    stats = stats if stats is not None else {}
    prompt = render_arbiter_prompt(records)
    resp = client.chat.completions.create(
        model=model, temperature=0, max_tokens=8,
        messages=[{"role": "user", "content": prompt}])
    raw = (resp.choices[0].message.content or "").strip().upper()
    stats.setdefault("raw", []).append(raw)

    if AGREE_REAL_DEFECT in raw:
        choice = AGREE_REAL_DEFECT
    elif AGREE_FLAKY in raw:
        choice = AGREE_FLAKY
    elif ESCALATE in raw:
        choice = ESCALATE
    else:
        stats["unparseable"] = stats.get("unparseable", 0) + 1
        raise ValueError(f"arbiter returned unparseable output: {raw!r}")

    p = _collapsed_direction(records)
    if choice == AGREE_FLAKY and p is not None and p < 0.5:
        stats["clamped"] = stats.get("clamped", 0) + 1
        return ESCALATE
    return choice


def null_arbiter(records, **_):
    """The control: return the most-confident surviving voice. No model, no network."""
    return _collapsed_direction(records)


def strategy_llm_arbiter(records, client=None, model=ARBITER_MODEL, stats=None, **_):
    """E: hand it to a language model. Raises when no client is configured."""
    if client is None:
        raise RuntimeError(
            "no LLM client configured; this strategy is incomplete and must not be ranked")
    choice = arbiter_decide(records, client, model=model, stats=stats)
    if choice == ESCALATE:
        return None                     # abstain -- reported as coverage, not dropped
    return 1.0 if choice == AGREE_FLAKY else 0.0


STRATEGIES = {
    "A_most_confident": strategy_most_confident,
    "B_mean": strategy_mean,
    "C_threshold": strategy_threshold,
    "D_escalate_on_disagreement": strategy_escalate_on_disagreement,
    "E_llm_arbiter": strategy_llm_arbiter,
    "E0_null_arbiter": null_arbiter,
}


# --- comparison --------------------------------------------------------------------------

def freeze_cases(names):
    return hashlib.sha256("\n".join(names).encode()).hexdigest()[:16]


def evaluate_strategy(fn, per_case_records, labels, **kwargs):
    """Run one strategy over every frozen case. Abstentions are reported, not dropped."""
    preds, covered_idx = [], []
    for i, recs in enumerate(per_case_records):
        try:
            p = fn(recs, **kwargs)
        except (RuntimeError, NotImplementedError) as e:
            return {"status": INCOMPLETE, "reason": str(e)}
        if p is None:
            continue
        preds.append(p); covered_idx.append(i)
    y = np.asarray(labels)[covered_idx]
    p = np.asarray(preds)
    return {"status": "complete", "n_total": len(per_case_records),
            "n_covered": len(preds), "coverage": len(preds) / len(per_case_records),
            "y": y.tolist(), "p": p.tolist()}


def rank(results, key):
    """Rank only strategies that completed on every case. Incomplete ones are unranked."""
    ranked = {k: v for k, v in results.items()
              if v.get("status") == "complete" and v.get(key) is not None}
    order = sorted(ranked, key=lambda k: ranked[k][key],
                   reverse=(key == "accuracy"))
    return order, [k for k, v in results.items() if v.get("status") == INCOMPLETE]
