"""同じ4商品の例で、買い替え先の確率と品ぞろえの期待粗利を計算する。"""
import itertools
import json
from pathlib import Path

GROUPS = (("A1", "A2"), ("B1", "B2"))
PRODUCTS = tuple(itertools.chain.from_iterable(GROUPS))
OPTIONS = PRODUCTS + ("なし",)
MODELS = {"flat": 1.0, "nested": 0.5}
LABELS = {"flat": "階層なし", "nested": "ブランド別"}
MARGINS = {"A1": 5.1, "A2": 4.9, "B1": 4.4, "B2": 2.0}


def shares(available, exponent):
    """全商品が買えるとき、各商品と非購入の確率を20%ずつにそろえる。"""
    top_level = 0.2
    weights = {}
    for group in GROUPS:
        offered = set(group) & set(available)
        mass = len(offered) / len(group)
        group_weight = 0.4 * mass**exponent
        top_level += group_weight
        for product in group:
            weights[product] = group_weight / len(offered) if product in offered else 0.0
    weights["なし"] = 0.2
    return {key: w / top_level for key, w in weights.items()}


def gross_profit(assortment, exponent):
    probabilities = shares(assortment, exponent)
    return sum(probabilities[p] * MARGINS[p] for p in PRODUCTS)


def rank_pairs(exponent):
    return sorted(
        ((pair, gross_profit(pair, exponent)) for pair in itertools.combinations(PRODUCTS, 2)),
        key=lambda item: (-item[1], item[0]),
    )


def percentages(available):
    return {
        model: {key: round(100 * prob, 3) for key, prob in shares(available, exp).items()}
        for model, exp in MODELS.items()
    }


def result():
    scenarios = [
        (PRODUCTS, "全4商品を並べると、二つのモデルとも各商品を選ぶ確率は20%ずつです。「何も買わない」も20%です。"),
        (("A2", "B1", "B2"), "A1を外すと、同じブランドに残るA2を選ぶ確率は、階層なしよりブランド別のモデルのほうが高くなります。"),
        (("B1", "B2"), "ブランドAをすべて外すと、Aから選べる商品はありません。ブランドBの2品を買う確率も、何も買わない確率も、二つのモデルで一致します。"),
        (("A1", "A2"), "この案では、同じブランドのA1とA2だけを残します。"),
        (("A1", "B1"), "この案では、ブランドAからA1、ブランドBからB1を残します。"),
    ]
    frames = []
    for number, (included, note) in enumerate(scenarios, 1):
        data = percentages(included)
        estimates = "、".join(f"{LABELS[m]} {gross_profit(included, e):.3f}" for m, e in MODELS.items())
        frames.append({
            "value": number,
            "bars": [
                {"label": f"{p}｜{LABELS[m]}", "value": data[m][p]}
                for p in OPTIONS for m in MODELS
            ],
            "note": f"{note} 来店1回当たりの期待粗利（架空の単位）：{estimates}。",
        })
    return {
        "margins": MARGINS,
        "models": MODELS,
        "ranks": {
            model: [{"assortment": pair, "gross_profit": round(profit, 6)}
                    for pair, profit in rank_pairs(exp)]
            for model, exp in MODELS.items()
        },
        "experiments": [
            {
                "name": "A1を外すと、A2が選ばれる割合はどう変わるか",
                "dataset": "Labが設定した架空の4商品と、何も買わない場合を比べます。実店舗のデータは使いません。",
                "metrics": {"A2の予測割合（階層なし、%）": frames[1]["bars"][2]["value"],
                            "A2の予測割合（ブランド別、%）": frames[1]["bars"][3]["value"]},
            }
        ],
        "explorer": {
            "label": "確かめる例（1〜5）", "unit": "", "metric": "選択確率（%）", "default": 0,
            "frames": frames,
        },
    }


if __name__ == "__main__":
    Path(__file__).with_name("results.json").write_text(
        json.dumps(result(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
