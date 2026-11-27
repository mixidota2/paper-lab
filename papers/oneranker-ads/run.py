"""出力を分ける場合と、固定候補の確率分布を近づける場合を人工データで計算する。"""
import json
import math
from pathlib import Path


def softmax(z):
    e = [math.exp(x-max(z)) for x in z]
    return [x/sum(e) for x in e]


def topk(z, k=2):
    return sorted(range(len(z)), key=lambda i: (-z[i], i))[:k]


def align(steps=200, rate=.2, teacher=None):
    # 候補集合と教師を固定し、交差エントロピーの勾配p−qで更新する。新しい候補は探さない。
    z = [2., 1., 0., -1.]
    q = softmax(teacher or [-1., 0., 1., 2.])
    frames = []
    for step in range(steps+1):
        p = softmax(z)
        if step in (0, 10, 50, steps):
            frames.append({'step': step, 'kl_teacher_generator': sum(a*math.log(a/b) for a,b in zip(q,p)),
                           'top2_disagreement': 1-len(set(topk(p)) & set(topk(q)))/2,
                           'generator': p, 'teacher': q})
        z = [a-rate*(b-c) for a,b,c in zip(z,p,q)]
    return frames


def conflict():
    # 同じ入力xで、興味の正解はx、価値の正解は−xとする。
    # 共有出力の最適な重みは0。出力を分けると1と−1を使える。
    xs = [-2., -1., 1., 2.]
    def loss(w, sign):
        return sum((w*x-sign*x)**2 for x in xs)/len(xs)
    return {'shared': {'interest_mse': loss(0,1), 'value_mse': loss(0,-1)},
            'task_conditioned': {'interest_mse': loss(1,1), 'value_mse': loss(-1,-1)}}


def experiment():
    return {'kind': 'synthetic mechanism illustration', 'seed': 'deterministic',
            'metrics': conflict(), 'alignment': align(),
            'counterexample': '教師が誤っていても生成側は模倣する。候補に含まれない広告は戻せない。',
            'not_tested': ['因果マスク付きの注意機構', '拾える興味の広さ', '本番のeCPM', '応答時間', '取引総額']}

if __name__ == '__main__':
    result = experiment()
    Path(__file__).with_name('results.json').write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n')
    print(json.dumps(result, indent=2, ensure_ascii=False))
