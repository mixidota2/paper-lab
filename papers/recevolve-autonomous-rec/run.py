"""候補数だけを変える評価と、実験結果を採択する条件を人工例で確かめる。"""
import json
import math
import random
from pathlib import Path


def score_query(positive, negatives, k=50):
    rank = 1 + sum(n >= positive for n in negatives)
    return {'rank': rank, 'ndcg': 1 / math.log2(rank + 1) if rank <= k else 0.0}


def candidate_probe(seed=15, queries=128):
    rng = random.Random(seed)
    totals = {b: 0.0 for b in (1000, 2000, 4000, 8000)}
    for _ in range(queries):
        positive = rng.gauss(2.4, .55)
        negatives = [rng.gauss(0, 1) for _ in range(7999)]
        for b in totals:
            totals[b] += score_query(positive, negatives[:b - 1])['ndcg']
    return {b: total / queries for b, total in totals.items()}


def decide(baseline, candidate, epsilon=.001, guard_candidate_count=True):
    if not candidate['valid']:
        return 'ROLLBACK', '学習前の確認に通らなかった'
    if not candidate['success']:
        return 'ROLLBACK', '学習ジョブが失敗した'
    if guard_candidate_count and candidate['candidates'] != baseline['candidates']:
        return 'ROLLBACK', '前回と今回で候補数が違う（Labが追加した条件）'
    if candidate['ndcg'] > baseline['ndcg'] + epsilon and candidate['aux'] >= .5:
        return 'KEEP', '主指標が必要な幅を超えて改善し、補助指標も下限以上だった'
    return 'ROLLBACK', '主指標の改善幅か、補助指標の下限を満たさなかった'


def lifecycle(guard=True):
    # エージェントは起動せず、起こり得る5通りの結果を手で設定する。
    base = dict(valid=True, success=True, candidates=8000, ndcg=.4, aux=.6)
    rows = [('invalid', dict(valid=False)), ('oom', dict(success=False)),
            ('smaller_batch', dict(candidates=1000, ndcg=.8)),
            ('aux_regression', dict(ndcg=.6, aux=.4)), ('valid_gain', dict(ndcg=.45))]
    trace = []
    for name, patch in rows:
        candidate = base | patch
        status, reason = decide(base, candidate, guard_candidate_count=guard)
        before = base.copy()
        if status == 'KEEP':
            base = candidate.copy()
        trace.append(dict(name=name, status=status, reason=reason, before=before, after=base.copy()))
    return trace


def compute():
    per_seed = [candidate_probe(seed) for seed in (15, 16, 17, 18)]
    metrics = {str(b): round(sum(p[b] for p in per_seed) / len(per_seed), 8) for b in per_seed[0]}
    return {'note': 'Labは同じスコアのまま負例だけを減らし、順位の指標を計算した。エージェント、版管理、TPUは使っていない。候補数を照合する条件はLabの提案で、論文が報告した自動検知ではない。',
            'verification': {'mechanism': 'PARTIAL', 'performance': 'NOT TESTED', 'scaling': 'NOT TESTED', 'production_applicability': 'NOT TESTED'},
            'checks': {'candidate_set_inflation': 'CONFIRMED', 'production_agent_replication': 'NOT TESTED'},
            'experiments': [{'name': '正例と各候補のスコアを固定して候補数を変える', 'dataset': '人工の検索128件を、乱数の種を変えて4組', 'metrics': metrics}],
            'per_seed': [{str(k): v for k, v in p.items()} for p in per_seed],
            'guarded_trace': lifecycle(), 'unguarded_trace': lifecycle(False)}


if __name__ == '__main__':
    Path(__file__).with_name('results.json').write_text(json.dumps(compute(), ensure_ascii=False, indent=2) + '\n')
