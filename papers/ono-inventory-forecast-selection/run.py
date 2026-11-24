"""Calculate comparisons of selected reported values, and a separate toy example."""
import json
from pathlib import Path

REPORTED = (
    (1, 21657, 22041),
    (5, 27830, 28104),
    (12.5, 39193, 39471),
    (25, 58098, 58415),
)
TOY = (
    ("欠品を1回にまとめる", (10,) * 9 + (6,)),
    ("欠品を4回に分ける", (10,) * 6 + (9,) * 4),
)


def compare(penalty, selection, baseline):
    return {
        "shortage_pct": penalty,
        "cfms": selection,
        "ses": baseline,
        "difference": baseline - selection,
        "reduction_pct": round(100 * (baseline - selection) / baseline, 2),
    }


def service(label, served):
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
