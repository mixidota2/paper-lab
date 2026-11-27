"""架空のゲーム状態で助言を選ぶ規則を試す。言語モデルや本番の評価は使わない。"""
import json
import random
from pathlib import Path

CANDIDATES = [
    {"id": "A", "requires": {"A", "skill-X"}, "weight": 5, "leak": .9},
    {"id": "B", "requires": {"B"}, "weight": 2, "leak": .8},
    {"id": "C", "requires": {"C"}, "weight": 1, "leak": .7},
]


def freeze_tools(intent, sub_intent, snapshot):
    """登録例は2組。試合状態がないか、意図が未登録ならツールを先に確定しない。"""
    table = {("recommend", "counter-pick"): ["lineup_search", "counter_rank", "dex_lookup"],
             ("teaching", "skill-explain"): ["skill_dex", "prereq_check"]}
    if snapshot is None:
        return {"path": "fallback", "tools": []}
    selected = table.get((intent, sub_intent))
    return {"path": "early" if selected else "fallback", "tools": selected or []}


def ground(required, inventory):
    missing = sorted(set(required) - set(inventory))
    return {"missing": missing, "eligible": ["constraint-account"] if missing else ["praise"],
            "required": ["constraint-account"] if missing else []}


def schedule(candidates, history, turn, rng, cooldown=1):
    """待機中の候補を除き、抽選で残った候補から重みに応じ一つ選ぶ。"""
    allowed = [c for c in candidates if turn - history.get(c["id"], -100) > cooldown]
    survivors = [c for c in allowed if rng.random() < c["leak"]]
    if not survivors:
        return None
    return rng.choices(survivors, weights=[c["weight"] for c in survivors], k=1)[0]["id"]


def replay(inventory, seed=25, n=12, grounding=True, scheduling=True):
    rng, history, selected = random.Random(seed), {}, []
    valid = [c for c in CANDIDATES if not ground(c["requires"], inventory)["missing"]] if grounding else CANDIDATES
    for turn in range(n):
        chosen = schedule(valid, history, turn, rng) if scheduling else (valid[0]["id"] if valid else None)
        selected.append(chosen)
        if chosen is not None:
            history[chosen] = turn
    invalid = sum(x is not None and not next(c for c in CANDIDATES if c['id'] == x)['requires'] <= set(inventory) for x in selected)
    repeats = sum(a is not None and a == b for a, b in zip(selected, selected[1:]))
    return {"selected": selected, "invalid": invalid, "consecutive_repeats": repeats,
            "abstentions": selected.count(None)}


def evaluate():
    inventory = {"A", "B", "C"}  # Aに必要な技は、いまの試合状態では使えない。
    variants = {"static_priority": replay(inventory, grounding=False, scheduling=False),
                "grounding_only": replay(inventory, scheduling=False),
                "grounding_and_history": replay(inventory)}
    assert variants['grounding_and_history'] == replay(inventory)
    assert variants['static_priority']['invalid'] == 12
    assert variants['grounding_only']['consecutive_repeats'] == 11
    assert variants['grounding_and_history']['invalid'] == variants['grounding_and_history']['consecutive_repeats'] == 0
    assert replay(set())['abstentions'] == 12
    return {"note": "Labは架空の12ターンで助言を選ぶ規則を比べた。原論文の言語モデル、評価データ、応答速度は再現していない。",
            "seed": 25, "verification": {"mechanism": "PARTIAL", "performance": "NOT TESTED", "scaling": "NOT TESTED", "production_applicability": "NOT TESTED"},
            "variants": variants,
            "w1": {"live": freeze_tools('recommend', 'counter-pick', inventory),
                   "missing_state": freeze_tools('recommend', 'counter-pick', None),
                   "unknown_intent": freeze_tools('other', 'unknown', inventory)},
            "w2": {"locked_skill": ground({'A', 'skill-X'}, inventory), "owned_B": ground({'B'}, inventory)},
            "edge_cases": {"empty_inventory": replay(set()), "single_candidate": replay({'B'}),
                           "stale_snapshot": replay(inventory | {'skill-X'})},
            "experiments": [{"name": "同じ所持品で助言の選び方を変える", "n": 12, "seed": 25,
                              "metrics": {k: {"無効な提案数": v['invalid'], "連続反復数": v['consecutive_repeats'], "提案見送り数": v['abstentions']} for k, v in variants.items()}}]}


if __name__ == '__main__':
    result = evaluate()
    Path(__file__).with_name('results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
