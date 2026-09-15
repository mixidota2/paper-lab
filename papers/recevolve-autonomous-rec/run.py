"""Fixed-score candidate-set audit and an in-memory KEEP/rollback fixture."""
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
        return 'ROLLBACK', '事前検証に失敗'
    if not candidate['success']:
        return 'ROLLBACK', '訓練ジョブに失敗'
    if guard_candidate_count and candidate['candidates'] != baseline['candidates']:
        return 'ROLLBACK', '比較候補数が変化（Labで追加した監査）'
    if candidate['ndcg'] > baseline['ndcg'] + epsilon and candidate['aux'] >= .5:
        return 'KEEP', '主指標と補助指標の条件を満たす'
    return 'ROLLBACK', '改善幅または補助指標が不足'


def lifecycle(guard=True):
    # Deliberate fixtures, not discoveries attributed to an agent.
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
    return {'note': '同じモデルscoreで候補だけを減らす合成実験。実エージェント、VCS、TPUは使用しない。候補数監査はLabの提案で、論文の自動検知実績ではない。',
            'verification': {'mechanism': 'PARTIAL', 'performance': 'NOT TESTED', 'scaling': 'NOT TESTED', 'production_applicability': 'NOT TESTED'},
            'checks': {'candidate_set_inflation': 'CONFIRMED', 'production_agent_replication': 'NOT TESTED'},
            'experiments': [{'name': '固定scoreで候補数だけを変更', 'dataset': '合成：4 seeds × 128 queries', 'metrics': metrics}],
            'per_seed': [{str(k): v for k, v in p.items()} for p in per_seed],
            'guarded_trace': lifecycle(), 'unguarded_trace': lifecycle(False)}


if __name__ == '__main__':
    Path(__file__).with_name('results.json').write_text(json.dumps(compute(), ensure_ascii=False, indent=2) + '\n')
