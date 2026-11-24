"""Deterministic, offline demonstration. No agent, API, signing, or external effects."""
from dataclasses import dataclass
from itertools import product
from pathlib import Path
import json


@dataclass(frozen=True)
class Case:
    artifact_pass: bool
    receipt: str | None
    reviewed_revision: str | None


def evaluate(case: Case, revision: str = "rev-B", *, requirement_verified: bool = True):
    """Three separate predicates. Review is a simulated ID check, not authorization."""
    received = case.receipt == revision
    reviewed = case.reviewed_revision == revision
    return {
        "artifact_pass": case.artifact_pass,
        "receipt_current": received,
        "work_complete": case.artifact_pass and received,
        "review_current": reviewed,
        "toy_change_eligible": requirement_verified and reviewed,
    }


def frame_note(case: Case, result: dict):
    artifact = "成果物の検査は合格" if case.artifact_pass else "成果物の検査は不合格"
    receipt = {None: "受け取ったかは不明", "accepted": "送信側で受理済みだが、受け取ったかは不明", "rev-A": "受け取り記録は旧版", "rev-B": "受け取り記録は現行版"}[case.receipt]
    review = {None: "レビュー記録なし", "rev-A": "レビュー記録は旧版", "rev-B": "レビュー記録は現行版"}[case.reviewed_revision]
    done = "作業の完了条件を満たす" if result["work_complete"] else "作業の完了条件を満たさない"
    change = "変更を採用できる" if result["toy_change_eligible"] else "変更を採用できない"
    return f"{artifact}。{receipt}。{review}。この条件では{done}。変更に必要な根拠は確認済みで、レビューした版が現行版かによって、{change}と判定する。"


def generate():
    cases = [
        Case(True, None, "rev-A"), Case(True, "rev-B", "rev-A"),
        Case(False, "rev-B", "rev-B"), Case(True, "rev-A", "rev-B"),
        Case(True, "rev-B", "rev-B"), Case(False, None, None), Case(True, "accepted", "rev-B"),
    ]
    exhaustive = [evaluate(Case(a, r, s), requirement_verified=q)
                  for a, r, s, q in product((False, True), (None, "accepted", "rev-A", "rev-B"),
                                             (None, "rev-A", "rev-B"), (False, True))]
    columns = [
        ("成果物の検査", "artifact_pass"),
        ("現行成果物の受け取り", "receipt_current"),
        ("作業の完了", "work_complete"),
        ("変更案を採用できる", "toy_change_eligible"),
    ]
    frames = []
    for i, case in enumerate(cases, 1):
        result = evaluate(case)
        frames.append({"value": i, "bars": [{"label": label, "value": int(result[key])}
                                           for label, key in columns],
                       "note": frame_note(case, result), "lines": []})
    return {
        "note": "架空の作業記録から判定を計算する。0は条件を満たさない、1は満たす。論文の得点や人の行動を再現した結果ではない。",
        "verification": {"mechanism": "PARTIAL", "performance": "NOT TESTED",
                         "scaling": "NOT TESTED", "production_applicability": "NOT TESTED"},
        "experiments": [
            {"name": "版と判定条件の全組合せ", "metrics": {
                "判定条件の組合せ": len(exhaustive),
                "成果物の検査に通った組合せ": sum(r['artifact_pass'] for r in exhaustive),
                "検査・受け取りの両方を満たした組合せ": sum(r['work_complete'] for r in exhaustive),
            }},
        ],
        "explorer": {"label": "試す例", "unit": "番", "metric": "条件を満たすと1", "default": 0,
                     "frames": frames},
    }


if __name__ == "__main__":
    target = Path(__file__).with_name("results.json")
    target.write_text(json.dumps(generate(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
