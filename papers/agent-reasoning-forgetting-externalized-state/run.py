"""保存した制約が読めるかを試す作例。モデルやトークン数は計測しない。"""
import json
from pathlib import Path


def replay(prune, externalize, readable=True):
    # すべての条件で、4つの制約を同じ順序で使う。
    reasoning = {f'constraint-{i}': i * 7 + 3 for i in range(4)}
    disk = dict(reasoning) if externalize else {}
    if prune:
        reasoning.clear()
    trace, rederived, reads, cost = [], 0, 0, 0
    for key in ['constraint-0', 'constraint-2', 'constraint-1', 'constraint-0', 'constraint-3', 'constraint-2']:
        if key in reasoning:
            action, effort = 'reasoning', 1
        elif readable and key in disk:
            action, effort = 'read-file', 2
            reads += 1
            reasoning[key] = disk[key]
        else:
            action, effort = 'rederive', 10
            rederived += 1
            reasoning[key] = int(key[-1]) * 7 + 3
        cost += effort
        trace.append({'key': key, 'action': action, 'value': reasoning[key], 'effort': effort})
    return {'rederivations': rederived, 'file_reads': reads, 'effort_units': cost, 'trace': trace}


def main():
    cases = {
        'keep': replay(False, False),
        'prune_internal': replay(True, False),
        'prune_external': replay(True, True),
        'prune_unreadable': replay(True, True, False),
    }
    assert cases['keep']['rederivations'] == cases['prune_external']['rederivations'] == 0
    assert cases['prune_internal']['rederivations'] == cases['prune_unreadable']['rederivations'] == 4
    assert len({tuple(t['value'] for t in c['trace']) for c in cases.values()}) == 1
    result = {
        'lab_kind': 'forgetting05',
        'note': '同じ6回の要求で、残した制約を読めるかを比べる。労力は作例の単位で、論文のトークン数や行動の変化は再現していない。',
        'experiments': [{'name': '同じ4つの制約を6回の要求で使う', 'n': 6, 'metrics': {k: {x: c[x] for x in ['rederivations', 'file_reads', 'effort_units']} for k,c in cases.items()}}],
        'cases': cases,
        'paper': {
            'source': 'https://arxiv.org/pdf/2609.29875v1',
            'risk': [{'group': '必要な情報が推論にだけ残る', 'n': 52, 'percent': 67.31}, {'group': '必要な情報を別の記録から読める', 'n': 213, 'percent': 36.15}],
            'random': [{'delete': x, 'input_reduction': y} for x,y in [(5,53.68),(10,60.53),(20,44.01),(40,51.21)]],
            'full260': {'base': 0.698654, 'iclr': 0.717775, 'input_change_percent': -25.48},
            'ablation80': {'base': 0.6267, 'iclr': 0.7376, 'delete_all': 0.7178},
        },
        'checks': {'same_final_values': True, 'unreadable_state_is_insufficient': True},
        'verification': {'mechanism': 'PARTIAL', 'performance': 'NOT TESTED', 'scaling': 'NOT TESTED', 'production_applicability': 'NOT TESTED'},
    }
    Path(__file__).with_name('results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(result['experiments'], ensure_ascii=False))


if __name__ == '__main__':
    main()
