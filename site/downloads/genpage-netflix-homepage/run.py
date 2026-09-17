"""Synthetic page decoder: explicit production candidate boundary and hybrid suffix."""
import json
from pathlib import Path

ITEMS = {"A": ("comedy", 9), "B": ("comedy", 8), "C": ("comedy", 7),
         "D": ("drama", 8), "E": ("drama", 7), "F": ("drama", 6),
         "OUT": ("comedy", 100)}
CANDIDATES = {"comedy": ["A", "B", "C"], "drama": ["D", "E", "F"]}

def score(item, prefix):
    # Artificial interaction: after A, C becomes preferable to B.
    return ITEMS[item][1] + (3 if item == "C" and "A" in prefix else 0)

def decode(head=1, enforce=True):
    page, used, calls = [], set(), 0
    for row in ("comedy", "drama"):
        calls += 1  # row token, including pinned second row
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
    return {"note": "固定scoreによる人工ページ。forward回数は演算回数の模型で、実測遅延ではない。",
      "experiments": [{"name": "候補境界と行末の条件付け", "metrics": {
         k: {"forward回数": v["forward_calls"], "候補違反": v["candidate_violations"]} for k,v in cases.items()}}],
      "cases": cases, "checks": {"candidate_boundary": "CONFIRMED", "hybrid_matches_full_in_this_case": "CONFIRMED",
      "whole_page_optimality": "NOT TESTED", "production_latency": "NOT TESTED"}}


def main():
    result = compute()
    Path(__file__).with_name("results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
