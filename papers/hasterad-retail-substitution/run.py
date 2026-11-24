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
        (PRODUCTS, "全4商品を並べると、どちらのモデルでも、顧客は各商品と「何も買わない」を20%ずつの確率で選びます。"),
        (("A2", "B1", "B2"), "A1を外すと、階層なしのモデルよりも、ブランド別のモデルのほうが、同じブランドに残るA2を選ぶ確率が高くなります。"),
        (("B1", "B2"), "ブランドAの全品を外すと、ブランドAには代わりの商品が残りません。この例では、残ったブランドBの商品と非購入の予測が両モデルで一致します。"),
        (("A1", "A2"), "2品を残す案①では、同じブランドのA1とA2を並べます。"),
        (("A1", "B1"), "2品を残す案②では、二つのブランドからA1とB1を1品ずつ並べます。"),
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
            "note": f"{note} 来店1回当たりに見込む粗利（架空の単位）：{estimates}。",
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
                "dataset": "Labが作った、4品と非購入を比べる例です。実店舗のデータは使っていません。",
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
