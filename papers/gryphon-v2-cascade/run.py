"""線形モデルで、候補源ごとに平均した教師との誤差を比べる。"""
import json
from pathlib import Path


def score(w, x):
    return sum(a*b for a, b in zip(w, x))


def teacher(x):
    return .8*x[0] - .6*x[1]


def fit(pools):
    w = [0., 0.]
    # 各条件は同じ初期値と更新回数で比べ、候補源ごとに誤差を平均する。
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
    # 候補源ごとに別の特徴だけを観測できるようにした。本番の表示ログは使わない。
    impressions = [(x, 0.) for x in (-1., -.5, .5, 1.)]
    rollouts = [(0., x) for x in (-1., -.5, .5, 1.)]
    test = [(a, b) for a in (-.9, -.3, .3, .9) for b in (-.8, -.2, .2, .8)]
    metrics = {}
    for name, pools in [('impressions only', [impressions]), ('rollouts only', [rollouts]), ('mix', [impressions, rollouts])]:
        w = fit(pools)
        metrics[name] = {'weights': w, 'rollout_teacher_mae': evaluate(w, [(0., -.7), (0., .7)])['teacher_mae'],
                         'impression_pair_accuracy_proxy': evaluate(w, [(-.7, 0.), (.7, 0.)])['pair_accuracy_proxy'],
                         **evaluate(w, test)}
    out = {'note': 'Labは線形モデルで、候補源によって観測できる特徴が変わる場合を調べた。前後の正解も教師から作るため、実際の利用者への推薦品質は測っていない。',
           'experiments': [{'name': '候補をどこから集めると、教師の点数と順序に近づくか', 'metrics': metrics}],
           'controls': {'steps': 2400, 'initial_weights': [0, 0], 'loss': '候補源ごとに平均した絶対誤差を足す',
                        'test_points': test, 'teacher_weights': [.8, -.6], 'learned_generator': False}}
    Path(__file__).with_name('results.json').write_text(json.dumps(out, ensure_ascii=False, indent=2)+'\n')
    return out

if __name__ == '__main__':
    main()
