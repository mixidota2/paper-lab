"""人工のIDの木で、探索前と生成後に順位を使う違いを調べる。

デコーダーの確率と順位付けの遷移表を固定した。評価用の正解は順位付けに使わない。
TIGER、LIGERやAmazonの実験は再現しない。
"""
from collections import Counter
import json
import math
from pathlib import Path

SIDS = {"a": "000", "b": "001", "c": "010", "d": "011",
        "e": "100", "f": "101", "g": "110", "h": "111"}
# デコーダーと商品順位が別の先頭部分を選ぶ場合を作る。確率はすべて正。
PROBS = dict(zip(SIDS, (0.24, 0.20, 0.16, 0.12, 0.10, 0.08, 0.06, 0.04)))
TRAIN = {"x": ["e"] * 12 + ["f"] * 8 + ["a"] * 2,
         "y": ["a"] * 12 + ["b"] * 8 + ["c"] * 2,
         "z": ["h"] * 12 + ["g"] * 8 + ["b"] * 2}
# 外部順位で正解が上位に来ない評価例も含める。
TEST = [("x", "e"), ("x", "f"), ("x", "a"), ("y", "a"),
        ("y", "b"), ("y", "d"), ("z", "h"), ("z", "g"), ("z", "c")]


def ranker(history, budget=3, reverse=False):
    counts = Counter(TRAIN[history])
    ranked = sorted(SIDS, key=lambda i: (-counts[i], i))
    if reverse:
        ranked.reverse()
    return ranked[:budget]


def decode(history, beam_width=2, support=True, ordering=True, budget=3,
           kappa=60, reverse=False):
    """順位を融合しても、デコーダーの累積確率は変えない。

    前のビームから伸ばせる候補をまとめて順位付けし、どの段で何が残ったかを返す。
    """
    q = ranker(history, budget, reverse)
    qranks = {item: rank for rank, item in enumerate(q, 1)}
    beam = [""]
    trace = []
    mass = lambda p: sum(PROBS[i] for i, sid in SIDS.items() if sid.startswith(p))
    for depth in (1, 2, 3):
        extensions = sorted({sid[:depth] for sid in SIDS.values()
                             if sid[:depth - 1] in beam})
        dec_order = sorted(extensions, key=lambda p: (-mass(p), p))
        dranks = {p: rank for rank, p in enumerate(dec_order, 1)}
        scores = {}
        for p in extensions:
            ranks = [r for i, r in qranks.items() if SIDS[i].startswith(p)]
            scores[p] = 1 / (kappa + dranks[p])
            if support and ranks:
                scores[p] += 1 / (kappa + min(ranks))
        beam = sorted(extensions, key=lambda p: (-scores[p], dranks[p], p))[:beam_width]
        survivors = [i for i, sid in SIDS.items() if sid[:depth] in beam]
        trace.append({"depth": depth, "prefixes": beam[:], "items": survivors,
                      "extensions": [{"prefix": p, "mass": round(mass(p), 6),
                                      "fusion": round(scores[p], 8)} for p in extensions]})
    generated = sorted(trace[-1]["items"], key=lambda i: (-PROBS[i], i))
    iranks = {i: r for r, i in enumerate(generated, 1)}
    if ordering:
        def final_score(i):
            return 1 / (kappa + iranks[i]) + (1 / (kappa + qranks[i]) if i in qranks else 0)
        generated.sort(key=lambda i: (-final_score(i), iranks[i], i))
    return {"ranked_items": generated, "provider": q, "trace": trace}


def evaluate(width, support, ordering, reverse=False):
    remaining = [0, 0, 0]
    ndcg = 0
    for history, target in TEST:
        output = decode(history, width, support, ordering, reverse=reverse)
        for n, step in enumerate(output["trace"]):
            remaining[n] += target in step["items"]
        if target in output["ranked_items"][:2]:
            rank = output["ranked_items"].index(target) + 1
            ndcg += 1 / math.log2(rank + 1)
    return {"remaining_target_rate": [round(n / len(TEST), 6) for n in remaining],
            "toy_ndcg_at_2": round(ndcg / len(TEST), 6)}


def compute():
    modes = [("通常beam", False, False, False), ("並べ替えだけ", False, True, False),
             ("prefix支援だけ", True, False, False), ("ISD型の両段階", True, True, False),
             ("逆順位の支援", True, True, True)]
    experiments = []
    for width in (1, 2, 4, 8):
        experiments.append({"name": f"beam幅 {width}", "dataset": "8商品、評価とは別の学習遷移表、9件の評価例", "n": len(TEST),
                            "metrics": {name: evaluate(width, s, o, r) for name, s, o, r in modes}})
    return {"note": "Labは固定した人工のSIDと確率を使った。残存率は評価9件すべてを分母にし、別の順位で正解が上位に入った場合だけを数える論文とは異なる。",
            "verification": {"mechanism": "PARTIAL", "performance": "NOT TESTED", "scaling": "NOT TESTED", "production_applicability": "NOT TESTED"},
            "experiments": experiments,
            "example": {"history": "x", "evaluation_target": "e", "baseline": decode("x", 1, False, False), "supported": decode("x", 1)},
            "assumptions": {"sids": SIDS, "decoder_leaf_probabilities": PROBS, "training_transitions": TRAIN,
                            "test_pairs": [list(pair) for pair in TEST], "support_budget": 3, "kappa": 60, "cutoff": 2}}


if __name__ == "__main__":
    result = compute()
    Path(__file__).with_name("results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result["experiments"], ensure_ascii=False, indent=2))
