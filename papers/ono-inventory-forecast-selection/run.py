"""論文の報告値から費用差を求め、別の架空の例で欠品の指標を比べる。"""
import json
from pathlib import Path

# 表7の各行は、欠品費用の率、CFMSの総費用、SESの総費用の順。
REPORTED = (
    (1, 21657, 22041),
    (5, 27830, 28104),
    (12.5, 39193, 39471),
    (25, 58098, 58415),
)
# どちらも1サイクルに10個の需要がある。各要素は在庫から満たせた個数。
TOY = (
    ("1サイクルで4個欠品する", (10,) * 9 + (6,)),
    ("4サイクルで1個ずつ欠品する", (10,) * 6 + (9,) * 4),
)


def compare(penalty, selection, baseline):
    # SESを基準に、CFMSの費用が何%低かったかを計算する。
    return {
        "shortage_pct": penalty,
        "cfms": selection,
        "ses": baseline,
        "difference": baseline - selection,
        "reduction_pct": round(100 * (baseline - selection) / baseline, 2),
    }


def service(label, served):
    # 欠品がなかったサイクルの割合と、需要を満たした数量の割合を分ける。
    n = len(served)
    assert n and all(0 <= s <= 10 for s in served)
    return {
        "label": label, "demand_per_cycle": 10, "served": served,
        "csl_pct": 100 * sum(s == 10 for s in served) / n,
        "fill_pct": 100 * sum(served) / (n * 10),
    }


def main():
    data = {"reported_table7": [compare(*row) for row in REPORTED],
            "reported_table2": compare(None, 85056, 85093),
            "toy_service": [service(*row) for row in TOY]}
    target = Path(__file__).with_name("results.json")
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
