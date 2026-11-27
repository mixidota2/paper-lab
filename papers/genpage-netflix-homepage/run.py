"""架空の作品を、候補の制約を守って前から選ぶ場合と、残りをまとめて選ぶ場合で比べる。"""
import json
from pathlib import Path

ITEMS = {"A": ("comedy", 9), "B": ("comedy", 8), "C": ("comedy", 7),
         "D": ("drama", 8), "E": ("drama", 7), "F": ("drama", 6),
         "OUT": ("comedy", 100)}
CANDIDATES = {"comedy": ["A", "B", "C"], "drama": ["D", "E", "F"]}

def score(item, prefix):
    # この例では、Aを選ぶとCの点数が上がり、Bより先に選ばれる。
    return ITEMS[item][1] + (3 if item == "C" and "A" in prefix else 0)

def decode(head=1, enforce=True):
    page, used, calls = [], set(), 0
    for row in ("comedy", "drama"):
        calls += 1  # 行を決める処理は、位置を固定した第2行でも1回と数える。
        pool = CANDIDATES[row] if enforce else list(ITEMS)
        selected = []
        for _ in range(min(head, 3)):
            eligible = [x for x in pool if not enforce or x not in used]
            winner = max(eligible, key=lambda x: (score(x, selected), x))
            selected.append(winner); used.add(winner); calls += 1
        if len(selected) < 3:
            calls += 1
            eligible = [x for x in pool if not enforce or x not in used]
            suffix = sorted(eligible, key=lambda x: (-score(x, selected), x))[:3-len(selected)]
            selected.extend(suffix); used.update(suffix)
        page.append({"row": row, "items": selected})
    violations = sum(x not in CANDIDATES[r["row"]] for r in page for x in r["items"])
    return {"page": page, "forward_calls": calls, "candidate_violations": violations}

def compute():
    cases = {"無制約": decode(3, False), "全逐次": decode(3),
             "先頭1件のみ逐次": decode(1), "行全体を一括": decode(0)}
    return {"note": "Labは固定した点数で架空の作品を並べました。「forward回数」は、モデルを模した処理を何回呼ぶかを数えた値です。Netflixで応答時間を測った結果ではありません。",
      "experiments": [{"name": "表示できる候補を限定し、行の残りをまとめて選ぶ場合を比べる", "metrics": {
         k: {"forward回数": v["forward_calls"], "候補違反": v["candidate_violations"]} for k,v in cases.items()}}],
      "cases": cases, "checks": {"candidate_boundary": "CONFIRMED", "hybrid_matches_full_in_this_case": "CONFIRMED",
      "whole_page_optimality": "NOT TESTED", "production_latency": "NOT TESTED"}}


def main():
    result = compute()
    Path(__file__).with_name("results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
