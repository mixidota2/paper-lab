"""候補経路の比率と、見つけられる番組の増分が別であることを合成例で確かめる。"""
import json
from pathlib import Path


def channel_case(new_probability, overlap, new_count=34, slots=100):
    """同じ経路に34枠を割り当て、重複数と新候補の確率を変える。

    既存方式は各枠で同じ0.1の確率とする。重複する候補の結果は固定する。
    各枠の確率を足して期待件数を出す。利用者の反応を抽選する計算ではない。
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
    """共通の指示と補助情報を除き、履歴に必要なトークン数を数える。

    論文に合わせ、SID1件は4トークン、長期の好みは1トークンとする。
    履歴件数と文章の長さは合成例の仮定。情報量や処理時間は測らない。
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
        "note": "Labは追加経路が占める割合を34%に固定して、発見の期待件数を計算します。Spotifyで測った増分を再現した数値ではありません。",
        "verification": {"mechanism": "PARTIAL", "performance": "NOT TESTED", "scaling": "NOT TESTED", "production_applicability": "NOT TESTED"},
        "experiments": [
            {"name": "追加経路の割合を固定し、重複と新候補の価値を変える", "dataset": "仮想100推薦枠", "metrics": cases},
            {"name": "履歴を渡すのに必要なトークン数を比べる", "dataset": "文章は1件30トークン、直近の履歴は20件と仮定", "metrics": {str(n): token_budget(n) for n in (0, 20, 100, 1000)}},
        ],
    }


if __name__ == "__main__":
    result = compute()
    Path(__file__).with_name("results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
