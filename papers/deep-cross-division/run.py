"""Small, deterministic quotient example; not the authors' training pipeline."""
import json
import math
from pathlib import Path

EPSILON = 0.01
TABLE5 = {
    "fullscreen": [6238, 6307, 6077, 6289],
    "like": [7325, 7377, 7200, 7391],
    "share": [5805, 5926, 5632, 5934],
    "view_time": [5589, 5681, 5152, 5629],
}


def score(n, d, eligible=True):
    sign = (d > 0) - (d < 0)
    rho = sign / max(abs(d), EPSILON) if eligible else 0.0
    return dict(product=n * d, reciprocal=rho, term=n * rho,
                raw_ratio=n / d if d else None)


def fit(examples, feature):
    xs = [example[feature] for example in examples]
    ys = [example["raw_ratio"] for example in examples]
    return sum(x*y for x, y in zip(xs, ys)) / sum(x*x for x in xs)


def examples(denominators):
    return [dict(n=n, d=d, **score(n, d)) for n in (2, 5) for d in denominators]


def rmse(rows, feature, coefficient):
    return math.sqrt(sum((coefficient*r[feature]-r["raw_ratio"])**2 for r in rows) / len(rows))


def build():
    train = examples([1, 2, 4])
    heldout = examples([0.125, 0.25, 0.5])
    fits = {}
    for name in ("product", "term"):
        coeff = fit(train, name)
        fits[name] = dict(weight=coeff, train_rmse=rmse(train, name, coeff),
                          heldout_rmse=rmse(heldout, name, coeff))
    return dict(experiment="local_single_term_least_squares", source="https://arxiv.org/html/2611.27514v1",
                epsilon=EPSILON, toy=dict(train=train, heldout=heldout, fits=fits),
                table5=dict(unit="XAUC × 10000", columns=["dcn_full", "dcdn_full", "dcn_reduced", "dcdn_reduced"],
                            rows=TABLE5))


if __name__ == "__main__":
    Path(__file__).with_name("results.json").write_text(
        json.dumps(build(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
