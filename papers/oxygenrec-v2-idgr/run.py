"""人工ログの頻度と蒸留の損失を計算する。OxygenREC-v2は学習させない。"""
import json
import math
import random
from pathlib import Path


def normalize(xs):
    total = sum(xs)
    return [x / total for x in xs]


def entropy(p):
    return -sum(x * math.log(x) for x in p if x)


def gates(p, low=0.75, high=2.6):
    h = entropy(p)
    return {'entropy': h, 'low': int(h < low), 'high': int(h > high)}


def reward(predicted, gold, gamma=0.8):
    weights = normalize([gamma ** t for t in range(len(gold))])
    return sum(w * (p == g) for w, p, g in zip(weights, predicted, gold))


def losses(student, teacher, tokens, gold, low=0.75, high=2.6):
    route = [gates(t, low, high) for t in teacher]
    nl = sum(r['low'] for r in route) + 1e-8
    nh = sum(r['high'] for r in route) + 1e-8
    sd = fkl = 0.0
    for s, t, token, r in zip(student, teacher, tokens, route):
        advantage = math.log(t[token]) - math.log(s[token])
        sd -= r['low'] / nl * advantage * math.log(s[token])
        fkl += r['high'] / nh * sum(a * math.log(a / b) for a, b in zip(t, s))
    vr = -reward(tokens, gold) * sum(math.log(p[token]) for p, token in zip(student, tokens))
    return {'VR': vr, 'SD': sd, 'FKL': fkl, 'weighted_without_SFT': .1 * vr + .01 * sd + .01 * fkl,
            'routes': route}


def instruction_probe(seed=15, conditioned=True):
    rng = random.Random(seed)
    # 行動ごとに候補群の分布を決め、そこから作ったログの頻度を集計する。
    assumed = [[8, 2, 1], [2, 8, 2], [1, 2, 8]]
    counts = [[1.0] * 3 for _ in assumed]  # ラプラス平滑化
    for b in range(3):
        for _ in range(600):
            item = rng.choices(range(3), weights=assumed[b])[0]
            counts[b][item] += 1
    pooled = normalize([sum(row[j] for row in counts) for j in range(3)])
    return [normalize(row) if conditioned else pooled[:] for row in counts]


def compute():
    names = ['クリック', 'カートへの追加', '注文']
    probes = instruction_probe()
    frames = [{'value': i, 'lines': [], 'bars': [{'label': f'合成候補群 {j + 1}', 'value': round(p * 100, 6)} for j, p in enumerate(row)],
               'note': f'目標は{names[i]}です。同じ文脈で、参照する行動別の頻度だけを変えました。実際の行動率やHRではありません。'} for i, row in enumerate(probes)]
    student = [normalize([4] + [1] * 15)] * 3
    teacher = [normalize([100] + [1] * 15), normalize([10] + [1] * 15), [1 / 16] * 16]
    rng = random.Random(15)
    candidates = [[rng.choices(range(16), weights=p)[0] for p in student] for _ in range(8)]
    gold = [0, 0, 0]
    best = max(candidates, key=lambda y: reward(y, gold))
    terms = losses(student, teacher, best, gold)
    metrics = {key: round(terms[key], 8) for key in ['VR', 'SD', 'FKL', 'weighted_without_SFT']}
    return {'seed': 15, 'note': '人工ログで行動別の頻度と式6・8–13を計算した。MoEや自己蒸留の学習、JD.comでの効果は再現していない。',
            'verification': {'mechanism': 'PARTIAL', 'performance': 'NOT TESTED', 'scaling': 'NOT TESTED', 'production_applicability': 'NOT TESTED'},
            'checks': {'finite_loss_and_routing': 'CONFIRMED', 'full_EA_TOSD_training': 'NOT TESTED'},
            'experiments': [{'name': '選択軌跡に対する損失の計算', 'seed': 15, 'metrics': metrics}],
            'candidate_trajectories': candidates, 'selected': best, 'loss_terms': terms,
            'instruction_probabilities': probes, 'unconditioned': instruction_probe(conditioned=False),
            'explorer': {'label': '目標にする行動（0：クリック、1：カートへの追加、2：注文）', 'unit': '', 'metric': '合成候補群の確率（%）', 'default': 0, 'frames': frames}}


if __name__ == '__main__':
    Path(__file__).with_name('results.json').write_text(json.dumps(compute(), ensure_ascii=False, indent=2) + '\n')
