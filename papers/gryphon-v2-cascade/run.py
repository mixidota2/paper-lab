"""Source-normalized MAE distillation of a tiny linear student on synthetic pools."""
import json
from pathlib import Path


def score(w, x):
    return sum(a*b for a, b in zip(w, x))


def teacher(x):
    return .8*x[0] - .6*x[1]


def fit(pools):
    w = [0., 0.]
    # Same initialization, optimizer steps and source-normalized objective.
    for step in range(2400):
        grad = [0., 0.]
        for pool in pools:
            for x in pool:
                delta = score(w, x)-teacher(x)
                sign = (delta > 0)-(delta < 0)
                for j in range(2):
                    grad[j] += sign*x[j]/len(pool)
        lr = .05/(1+step/100)
        w = [a-lr*g for a, g in zip(w, grad)]
    return w


def evaluate(w, pool):
    mae = sum(abs(score(w, x)-teacher(x)) for x in pool)/len(pool)
    pairs = [(a, b) for a in pool for b in pool if teacher(a)>teacher(b)]
    correct = sum(score(w, a)>score(w, b) for a, b in pairs)
    return {'teacher_mae': round(mae, 6), 'pair_accuracy_proxy': correct/len(pairs)}


def main():
    # Deliberately complementary feature support. Not sampled from real impressions.
    impressions = [(x, 0.) for x in (-1., -.5, .5, 1.)]
    rollouts = [(0., x) for x in (-1., -.5, .5, 1.)]
    test = [(a, b) for a in (-.9, -.3, .3, .9) for b in (-.8, -.2, .2, .8)]
    metrics = {}
    for name, pools in [('impressions only', [impressions]), ('rollouts only', [rollouts]), ('mix', [impressions, rollouts])]:
        w = fit(pools)
        metrics[name] = {'weights': w, 'rollout_teacher_mae': evaluate(w, [(0., -.7), (0., .7)])['teacher_mae'],
                         'impression_pair_accuracy_proxy': evaluate(w, [(-.7, 0.), (.7, 0.)])['pair_accuracy_proxy'],
                         **evaluate(w, test)}
    out = {'note': '合成分布の被覆を調べる線形 MAE toy。pair labels も教師から構成し、独立なユーザー品質を測らない。Production NOT TESTED。',
           'experiments': [{'name': '候補源の被覆と教師への一致', 'metrics': metrics}],
           'controls': {'steps': 2400, 'initial_weights': [0, 0], 'loss': 'sum of per-source mean absolute errors',
                        'test_points': test, 'teacher_weights': [.8, -.6], 'learned_generator': False}}
    Path(__file__).with_name('results.json').write_text(json.dumps(out, ensure_ascii=False, indent=2)+'\n')
    return out

if __name__ == '__main__':
    main()
