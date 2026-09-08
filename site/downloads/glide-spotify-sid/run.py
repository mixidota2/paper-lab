"""CPU teaching counterexample: candidate channel share does not identify lift.

All probabilities are invented toy assumptions, not Spotify measurements.
Run with uv run papers/glide-spotify-sid/run.py. No dependencies or network.
"""
import json
from pathlib import Path


def channel_case(new_probability, overlap, new_count=34, slots=100):
    """Hold the final slate's channel label count fixed; vary incremental value.

    overlap counts GLIDE-labeled slots that also existed in baseline retrieval.
    Baseline has identical 0.1 discovery probability in every slot. Shared
    candidates keep that outcome; only genuinely replaced slots change it.
    Expected events are sums of Bernoulli expectations, not sampled outcomes.
    """
    if not 0 <= overlap <= new_count <= slots or not 0 <= new_probability <= 1:
        raise ValueError("invalid slate assumptions")
    baseline = slots * 0.1
    incremental_slots = new_count - overlap
    treatment = (slots - incremental_slots) * 0.1 + incremental_slots * new_probability
    return {
        "channel_share_percent": round(100 * new_count / slots, 4),
        "overlap_slots": overlap,
        "incremental_slots": incremental_slots,
        "new_candidate_discovery_probability": new_probability,
        "baseline_expected_events": baseline,
        "treatment_expected_events": round(treatment, 4),
        "relative_lift_percent": round(100 * (treatment / baseline - 1), 4),
    }


def token_budget(old_events, recent_events=20, text_tokens_per_event=30):
    """Illustrative input accounting; excludes common instructions/metadata.

    Four SID tokens and one soft token follow GLIDE's representation. History
    lengths and average text length here are assumptions, not paper facts.
    Equal token count does NOT mean equal information or measured latency.
    """
    return {
        "old_events": old_events,
        "recent_events": recent_events,
        "text_history_tokens": (old_events + recent_events) * text_tokens_per_event,
        "sid_history_tokens": (old_events + recent_events) * 4,
        "soft_plus_recent_sid_tokens": 1 + 4 * recent_events,
    }


def compute():
    cases = {
        "同じ価値": channel_case(0.1, 0),
        "新候補の価値が高い": channel_case(0.2, 0),
        "新候補の価値が低い": channel_case(0.05, 0),
        "候補がすべて重複": channel_case(0.2, 34),
        "半数が重複": channel_case(0.2, 17),
    }
    return {
        "note": "合成の期待値計算。34%は説明上固定した経路比率で、論文の効果量を再現した値ではない。",
        "verification": {"mechanism": "PARTIAL", "performance": "NOT TESTED", "scaling": "NOT TESTED", "production_applicability": "NOT TESTED"},
        "experiments": [
            {"name": "同じ経路比率でも増分は変わる", "dataset": "仮想100推薦枠", "metrics": cases},
            {"name": "履歴の入力枠を数える", "dataset": "1件30 text tokens・直近20件を仮定", "metrics": {str(n): token_budget(n) for n in (0, 20, 100, 1000)}},
        ],
    }


if __name__ == "__main__":
    result = compute()
    Path(__file__).with_name("results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
