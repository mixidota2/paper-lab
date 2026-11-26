"""人工の商品カタログを検索する。言語モデルや原論文の実装は使わない。"""
import json
from pathlib import Path

QUERIES = ('photo', 'vegan', 'wedding', 'gluten-free')
# 正解の商品は評価でだけ使い、検索では参照しない。
BASE = [
    {'id': 'a', 'category': 'cake', 'tags': ['photo'], 'description': [], 'truth': ['photo']},
    {'id': 'b', 'category': 'cake', 'tags': ['vegan'], 'description': [], 'truth': ['vegan']},
    {'id': 'c', 'category': 'cake', 'tags': [], 'description': ['wedding'], 'truth': ['wedding']},
]

def portrait(items):
    """予備検索から見える商品だけを集計する。最後の条件では商品cが見えない。"""
    fields = ('tags', 'description')
    return {'category': 'cake', 'count': len(items),
            'fill_rates': {f: sum(bool(i[f]) for i in items) / max(1, len(items)) for f in fields}}


def search(query, items, guided=False, probe_ids=None):
    visible = items if probe_ids is None else [i for i in items if i['id'] in probe_ids]
    p = portrait(visible)
    fields = [f for f, rate in p['fill_rates'].items() if rate > 0] if guided else ['tags']
    candidates = [i for i in visible if any(query in i[f] for f in fields)]
    if candidates:
        return {'id': candidates[0]['id'], 'decision': 'match', 'fields': fields}
    # 比較用の規則は、グルテンフリーの指定があっても最初のケーキを返す。
    if not guided and query == 'gluten-free' and visible:
        return {'id': visible[0]['id'], 'decision': 'match', 'fields': fields}
    # 商品を返さないのは、見えた範囲で一致の根拠がないため。カタログ全体の不在ではない。
    return {'id': None, 'decision': 'no_support_observed', 'fields': fields}


def evaluate(items, guided, probe_ids=None):
    fn = fm = supported = absent = correct = 0
    decisions = []
    for q in QUERIES:
        targets = {i['id'] for i in items if q in i['truth']}
        out = search(q, items, guided, probe_ids)
        if targets:
            supported += 1
            fn += out['id'] is None
            correct += out['id'] in targets
        else:
            absent += 1
            fm += out['id'] is not None
            correct += out['id'] is None
        decisions.append({'query': q, 'targets_for_evaluation': sorted(targets), **out})
    return {'fni_pct': 100 * fn / supported if supported else None,
            'fm_pct': 100 * fm / absent if absent else None,
            'correct': correct, 'supported': supported, 'absent': absent, 'decisions': decisions}


def replay_gate(before, after, target_indices, background_indices):
    """同じ要求で変更の前後を比べる。原論文の付録Bにある統計的なしきい値は使わない。"""
    return (all(after[i] >= before[i] for i in target_indices)
            and any(after[i] > before[i] for i in target_indices)
            and all(after[i] >= before[i] for i in background_indices))


def simulate():
    renamed = [{**i, 'tags': [], 'description': i['tags'] + i['description']} for i in BASE]
    deleted = [i for i in renamed if i['id'] != 'a']
    scenarios = [('元の属性欄を使う', BASE, None), ('タグの情報を説明欄に移す', renamed, None),
                 ('属性を移した後に商品aを削除', deleted, None), ('予備検索で商品cを見落とす', BASE, ['a', 'b'])]
    records, frames = [], []
    for n, (label, items, ids) in enumerate(scenarios):
        b, g = evaluate(items, False, ids), evaluate(items, True, ids)
        records.append({'label': label, 'baseline': b, 'guided': g})
        frames.append({'value': n, 'note': label + '。4件の人工の検索要求を使います。どの条件でも判断規則は同じです。',
                       'bars': [{'label': 'タグだけを検索', 'value': b['correct']},
                                {'label': '値が入った属性欄を検索', 'value': g['correct']} ]})
    rejected = not replay_gate([0, 1], [1, 0], [0], [1])
    assert rejected
    assert records[-1]['guided']['fni_pct'] > 0
    assert all(r['guided']['fm_pct'] == 0 for r in records)
    return {'kind': 'synthetic deterministic mechanism check', 'verification': {
        'mechanism': 'PARTIAL', 'performance': 'NOT TESTED', 'scaling': 'NOT TESTED',
        'production_applicability': 'NOT TESTED'},
        'checks': {'background_regression_rejected': rejected,
                   'probe_miss_remains': True, 'guidelines_frozen_across_snapshots': True},
        'scenarios': records,
        'explorer': {'label': 'カタログと検索範囲の条件', 'unit': '', 'metric': '4件中の正答数',
                     'default': 0, 'frames': frames}}

if __name__ == '__main__':
    p = Path(__file__).with_name('results.json')
    p.write_text(json.dumps(simulate(), ensure_ascii=False, indent=2) + '\n')
    print(p)
