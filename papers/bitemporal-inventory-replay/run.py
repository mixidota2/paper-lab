"""報告を受け取った時点ごとに、同じ過去と将来予定を計算する合成例。"""
import json
from pathlib import Path


REPORTS = [
    # event_id, revision, event_day, received_day, kind, qty
    ("A", 1, 1, 1, "demand", 5),
    ("C", 1, 3, 3, "demand", 1),
    ("B", 1, 2, 4, "receipt", 4),
    ("A", 2, 1, 5, "demand", 1),
    ("C", 2, 5, 6, "demand", 1),
]
SCHEDULE = [(4, "demand", 3), (5, "receipt", 2), (6, "demand", 1)]
TARGET = 3
INITIAL = 2


def select(reports, target, cutoff):
    """受領で絞り、訂正版を選び、それから発生日で絞る。"""
    latest = {}
    for row in reports:
        event, revision, day, received, _, _ = row
        if received <= cutoff and (event not in latest or latest[event][1] < revision):
            latest[event] = row
    return sorted((row for row in latest.values() if row[2] <= target),
                  key=lambda row: (row[2], row[0]))


def replay(stock, events):
    loss, first_loss = 0, -1
    trail = []
    for day, kind, quantity in events:
        missed = 0
        before = stock
        if kind == "receipt":
            stock += quantity
        elif kind == "demand":
            missed = max(0, quantity - stock)
            stock -= quantity - missed
            loss += missed
            if missed and first_loss < 0:
                first_loss = day
        else:
            raise ValueError(kind)
        trail.append([day, kind, quantity, before, stock, missed])
    return stock, loss, first_loss, trail


def calculate(cutoff):
    selected = select(REPORTS, TARGET, cutoff)
    stock, loss, _, past = replay(INITIAL, [(d, k, q) for _, _, d, _, k, q in selected])
    future_stock, future_loss, first_future_loss, future = replay(stock, SCHEDULE)
    return dict(cutoff=cutoff, selected=[list(row) for row in selected], past=past, future=future,
                answer=[stock, loss, future_stock, future_loss, first_future_loss])


def main():
    cases = [calculate(c) for c in (2, 4, 6)]
    assert [case["answer"] for case in cases] == [[0, 3, 1, 3, 4], [3, 3, 1, 0, -1], [5, 0, 3, 0, -1]]
    assert [row[0] for row in cases[-1]["selected"]] == ["A", "B"]
    for case in cases:
        stock, _, end, loss, _ = case["answer"]
        assert end - loss == stock - 2
    output = {
        "note": "Labが決めた1商品の合成例です。モデルの呼び出し、需要予測、実店舗データは使っていません。",
        "experiments": [{"name": "報告を受け取った時点による5項目の違い", "metrics": {
            f'{case["cutoff"]}日目': dict(zip(
                ("3日目の在庫（個）", "過去の売り逃し（個）", "6日目の最終在庫（個）",
                 "将来の売り逃し（個）", "最初の売り逃し（将来）"),
                [*case["answer"][:4], "なし" if case["answer"][-1] == -1
                 else f'{case["answer"][-1]}日目']))
            for case in cases}}],
        "initial_stock": INITIAL,
        "target_day": TARGET,
        "reports": REPORTS,
        "schedule": SCHEDULE,
        "cases": cases,
    }
    Path(__file__).with_name("results.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
