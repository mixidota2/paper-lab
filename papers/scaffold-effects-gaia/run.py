"""同じ60件で再試行の上限を変える。論文のモデルやGAIAは実行しない。"""
import json
from pathlib import Path
import re
import sys

p = Path(__file__).resolve().parent
sys.path.insert(0, str(p.parent))
from _toy_common import compute

LAB_ID = "scaffold-effects-gaia"


def example():
    result = compute(LAB_ID)
    result["note"] = "同じ60件の作例で、再試行の上限を変えて完了件数を数える。論文のモデルやGAIAの成績ではない。"
    result["experiments"][0]["name"] = "同じ60件を、再試行の上限だけ変えて比べる"
    result["explorer"]["label"] = "最初に失敗した後で、やり直せる回数"
    for frame in result["explorer"]["frames"]:
        old, new = re.search(r"([0-9]+) → ([0-9]+) 回", frame["note"]).groups()
        frame["note"] = (f"60件の作例で、再試行しないとツールを{old}回呼ぶ。この上限では{new}回呼ぶ。"
                         "成功したタスクはそこで止める。何回目に成功するかは、作例であらかじめ決めた。")
    return result


if __name__ == "__main__":
    result = example()
    (p / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"再試行の上限を変えた{len(result['explorer']['frames'])}条件を計算しました。")
