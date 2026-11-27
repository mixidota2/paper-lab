"""面積弾力性の21条件で、2部門に面積を配る教材を実行する。"""
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _toy_common import compute

LAB_ID = "whole-foods-shelf"
BAR_LABELS = ("50ずつ配る案", "点数が最も高い案")


def example():
    """同じ点数を使い、教材と実売上を区別できるように表示する。"""
    result = compute(LAB_ID)
    result["note"] = (
        "教材は、架空の2部門に売場面積を配る。点数を計算する式も教材用で、"
        "論文のモデルや実際の売上は再現していない。"
    )
    explorer = result["explorer"]
    explorer["label"] = "A部門の面積弾力性 β"
    explorer["metric"] = "教材の点数"
    for frame in explorer["frames"]:
        line = frame["lines"][0]
        # 最大点が同じなら、共通の計算と同様に最初の候補を採る。
        a = max(range(10, 91), key=lambda n: 20 * n ** frame["value"] + 18 * (100 - n) ** 0.5)
        for bar, label in zip(frame["bars"], BAR_LABELS):
            bar["label"] = label
        frame["note"] = (
            f"点数が最も高い案はA部門が{a}、B部門が{100 - a}。"
            "面積は合計100で、どちらも10以上。点数は20×A^β＋18×B^0.5で求める。"
            "この式は、他部門の面積が販売に及ぼす影響や、購買後の長期効果を表さない。"
        )
        line["label"] = "A部門の面積を10から90まで変えた場合の点数"
    test = result["experiments"][0]
    test["name"] = "同じ面積制約で等分案と最高点の案を比べる"
    test["dataset"] = "教材用の固定データ"
    test["metrics"] = dict(zip(BAR_LABELS, test["metrics"].values()))
    return result


if __name__ == "__main__":
    result = example()
    (HERE / "results.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"A部門の面積弾力性を変えた{len(result['explorer']['frames'])}条件を計算しました。")
