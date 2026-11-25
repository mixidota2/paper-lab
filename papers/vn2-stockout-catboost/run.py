"""8週分の架空の需要で、在庫数によって販売の平均がどう変わるかを計算する。"""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _toy_common import compute as compute_teaching

ID = "vn2-stockout-catboost"
LABELS = {
    "合成の潜在需要：平均": "8週に設定した需要の平均",
    "観測販売：平均": "8週に売れた数の平均",
    "非欠品日のみ：平均": "在庫を使い切らなかった週だけの販売数の平均",
    "合成の潜在需要": "各週に設定した需要",
    "観測販売": "各週に売れた数",
}


def compute():
    result = compute_teaching(ID)
    result["note"] = "これは架空の需要を使った計算です。VN2のモデルを学習させたり、競技の費用を測ったりしていません。"
    experiment = result["experiments"][0]
    experiment["name"] = "在庫の上限で販売数の平均がどう変わるか"
    experiment["dataset"] = "架空の需要を設定した8週"
    experiment["metrics"] = {LABELS[k]: v for k, v in experiment["metrics"].items()}
    result["explorer"]["label"] = "毎週の在庫の上限"
    result["explorer"]["metric"] = "需要と販売数の平均（個）"
    for frame in result["explorer"]["frames"]:
        for series in frame["bars"] + frame["lines"]:
            series["label"] = LABELS[series["label"]]
        rule = "売れる数は、需要と用意した在庫のうち少ない方です。"
        if frame["bars"][-1]["value"] is None:
            detail = "在庫を使い切った週を除くと1週も残らないため、平均は計算できません。"
        else:
            detail = "在庫を使い切った週を除いた平均は、残った週だけの販売数を表します。8週すべての需要を表すとは限りません。"
        frame["note"] = rule + detail
    return result


if __name__ == "__main__":
    output = Path(__file__).resolve().with_name("results.json")
    result = compute()
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(ID + ": " + str(len(result["explorer"]["frames"])) + "通りの在庫上限で計算しました。")
