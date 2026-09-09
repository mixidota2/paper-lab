"""CPU teaching experiment: shared linear scorer, two normalized CE targets.
This is an alpha sensitivity experiment, NOT a TT/LambdaMART comparison.
Run: uv run papers/otto-gbdt-vs-dnn-ltr/run.py
"""
import json
import math
import random
from pathlib import Path


def softmax(xs):
    es = [math.exp(x - max(xs)) for x in xs]
    return [e / sum(es) for e in es]


def dataset(seed, n):
    rng = random.Random(seed)
    data = []
    for _ in range(n):
        xs = [[rng.uniform(-1, 1), rng.uniform(-1, 1)] for _ in range(8)]
        # Different latent preferences; the order label is also a click.
        order = max(range(8), key=lambda i: xs[i][1])
        click = max(range(8), key=lambda i: xs[i][0])
        yc = [int(i in {order, click}) for i in range(8)]
        yo = [int(i == order) for i in range(8)]
        data.append((xs, yc, yo))
    return data


def fit(train, alpha):
    w = [0.0, 0.0]
    for _ in range(250):
        gradient = [0.0, 0.0]
        for xs, yc, yo in train:
            probs = softmax([sum(a*b for a, b in zip(w, x)) for x in xs])
            target = [alpha*c/sum(yc)+(1-alpha)*o/sum(yo) for c, o in zip(yc, yo)]
            for p, y, x in zip(probs, target, xs):
                for j in range(2):
                    gradient[j] += (p-y)*x[j]/len(train)
        w = [a-0.3*g for a, g in zip(w, gradient)]
    return w


def ndcg(scores, labels, k=3):
    rank = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
    dcg = sum(labels[i]/math.log2(j+2) for j, i in enumerate(rank))
    ideal = sum(v/math.log2(j+2) for j, v in enumerate(sorted(labels, reverse=True)[:k]))
    return dcg/ideal if ideal else 0.0


def experiment():
    train, test = dataset(19, 160), dataset(20, 240)
    metrics = {}
    for alpha in [0, 0.25, 0.5, 0.75, 1]:
        w = fit(train, alpha)
        values = [0.0, 0.0]
        for xs, yc, yo in test:
            scores = [sum(a*b for a, b in zip(w, x)) for x in xs]
            values[0] += ndcg(scores, yc)/len(test)
            values[1] += ndcg(scores, yo)/len(test)
        metrics[str(alpha)] = dict(zip(["NDCG_click@3", "NDCG_order@3"], map(lambda v: round(v, 6), values)))
        metrics[str(alpha)]["weights"] = [round(v, 6) for v in w]
    return {"note": "合成データ。αで共有スコアの優先順位が変わる例。OTTOの性能、因果関係、モデル間優劣は未検証。", "experiments": [{"name": "クリック損失の重みα", "seed": [19, 20], "n": {"train_queries": 160, "test_queries": 240, "items_per_query": 8}, "metrics": metrics}]}


def compute():
    result = experiment()
    result["verification"] = {
        "mechanism": "PARTIAL", "performance": "NOT TESTED",
        "scaling": "NOT TESTED", "production_applicability": "NOT TESTED",
    }
    result["explorer"] = {
        "label": "クリック損失の重みα", "unit": "", "metric": "NDCG@3（合成テスト）", "default": 0,
        "frames": [
            {"value": float(a), "note": "合成の共有線形スコア。αだけを変えた結果で、OTTOやDNNの性能ではない。",
             "bars": [{"label": k, "value": m[k]} for k in ("NDCG_click@3", "NDCG_order@3")], "lines": []}
            for a, m in result["experiments"][0]["metrics"].items()
        ],
    }
    return result


if __name__ == "__main__":
    Path(__file__).with_name("results.json").write_text(json.dumps(compute(), ensure_ascii=False, indent=2)+"\n")
