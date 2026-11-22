"""Generate the deterministic synthetic choice and assortment example."""
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
    """Two-level nested logit calibrated to 20% per option in the full set."""
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
        (PRODUCTS, "全4商品：両モデルとも、4商品と何も買わない選択が20%ずつです。"),
        (("A2", "B1", "B2"), "A1を外す：ブランド別モデルでは、残った同じブランドのA2への移動が多くなります。"),
        (("B1", "B2"), "ブランドAをすべて外す：ブランド内に代わりの商品がないため、両モデルの予測は一致します。"),
        (("A1", "A2"), "2品の案①：同じブランドからA1とA2を残します。"),
        (("A1", "B1"), "2品の案②：両ブランドからA1とB1を1品ずつ残します。"),
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
            "note": f"{note} この品ぞろえの期待粗利（来店1回当たり、架空の単位）：{estimates}。",
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
                "name": "A1を外したときの予測",
                "dataset": "4品と非購入の合成例。実店舗データを使わない。",
                "metrics": {"A2の予測割合（階層なし、%）": frames[1]["bars"][2]["value"],
                            "A2の予測割合（ブランド別、%）": frames[1]["bars"][3]["value"]},
            }
        ],
        "explorer": {
            "label": "表示する例（1〜5）", "unit": "", "metric": "選ぶ確率（%）", "default": 0,
            "frames": frames,
        },
    }


if __name__ == "__main__":
    Path(__file__).with_name("results.json").write_text(
        json.dumps(result(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
