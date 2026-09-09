"""Known-propensity catalog bandit: IPS/SNIPS at nested prefix depths."""
import json
import math
import random
import statistics
from pathlib import Path


def policies():
    p0, pe, q = [], [], []
    for c in range(4):
        for j in range(16):
            p0.append([0.55, 0.25, 0.15, 0.05][c] * (0.97 if j == 0 else 0.03/15))
            pe.append([0.1, 0.2, 0.3, 0.4][c] * (0.6 if j == 15 else 0.4/15))
            q.append(0.12+0.19*c+0.12*j/15)
    return p0, pe, q


def cluster_masses(p, depth):
    width = 64//(4**depth)
    return [sum(p[i:i+width]) for i in range(0, 64, width)]


def decoder_prefix(p, cluster, depth):
    # Recover conditional probabilities from a normalized toy leaf policy.
    # Reading a real SID decoder would supply these conditionals directly.
    product, parent, parent_mass = 1.0, 0, 1.0
    for level in range(1, depth+1):
        digit = (cluster//(4**(depth-level))) % 4
        parent = parent*4+digit
        mass = cluster_masses(p, level)[parent]
        product *= mass/parent_mass
        parent_mass = mass
    return product


def experiment():
    p0, pe, q = policies()
    truth = sum(p*r for p, r in zip(pe, q))
    logs = []
    for seed in range(250):
        rng = random.Random(seed)
        actions = rng.choices(range(64), weights=p0, k=600)
        logs.append([(a, int(rng.random() < q[a])) for a in actions])
    metrics, max_mass_error = {}, 0.0
    for depth in range(4):
        m0, me = cluster_masses(p0, depth), cluster_masses(pe, depth)
        width = 64//(4**depth)
        ips, snips, ess, coverage = [], [], [], []
        expected = sum(p0[a]*me[a//width]/m0[a//width]*q[a] for a in range(64))
        for log in logs:
            ws = [me[a//width]/m0[a//width] for a, _ in log]
            weighted = sum(w*r for w, (_, r) in zip(ws, log))
            ips.append(weighted/len(log))
            snips.append(weighted/sum(ws))
            ess.append(sum(ws)**2/sum(w*w for w in ws))
            coverage.append(len({a//width for a, _ in log})/(4**depth))
        metrics[f"depth_{depth}"] = {"clusters": 4**depth, "IPS_RMSE": round(math.sqrt(statistics.mean((v-truth)**2 for v in ips)), 6), "SNIPS_RMSE": round(math.sqrt(statistics.mean((v-truth)**2 for v in snips)), 6), "IPS_variance": round(statistics.pvariance(ips), 6), "exact_IPS_bias": round(expected-truth, 6), "mean_ESS": round(statistics.mean(ess), 3), "observed_cluster_fraction": round(statistics.mean(coverage), 6)}
        for c, mass in enumerate(me):
            max_mass_error = max(max_mass_error, abs(decoder_prefix(pe, c, depth)-mass))
    return {"note": "64商品・既知確率の合成実験。深さ0は全商品を一群にまとめる対照、深さ3は商品IPS。実データのSID学習・深さ選択・本番性能は未検証。", "oracle_value": truth, "decoder_mass_max_error": max_mass_error, "experiments": [{"name": "粒度ごとの誤差と有効標本数", "seed": "0..249", "n": {"items": 64, "logs_per_seed": 600, "seeds": 250}, "metrics": metrics}]}


def compute():
    result = experiment()
    result["verification"] = {
        "mechanism": "PARTIAL", "performance": "NOT TESTED",
        "scaling": "NOT TESTED", "production_applicability": "NOT TESTED",
    }
    result["explorer"] = {
        "label": "接頭辞の深さ", "unit": "", "metric": "RMSE（小さいほどよい）", "default": 0,
        "frames": [
            {"value": i, "note": f"群数 {m['clusters']}、平均ESS {m['mean_ESS']}、raw IPSの厳密バイアス {m['exact_IPS_bias']}。深さ3は商品粒度。",
             "bars": [{"label": "IPS RMSE", "value": m["IPS_RMSE"]}, {"label": "SNIPS RMSE", "value": m["SNIPS_RMSE"]}], "lines": []}
            for i, m in enumerate(result["experiments"][0]["metrics"].values())
        ],
    }
    return result


if __name__ == "__main__":
    Path(__file__).with_name("results.json").write_text(json.dumps(compute(), ensure_ascii=False, indent=2)+"\n")
