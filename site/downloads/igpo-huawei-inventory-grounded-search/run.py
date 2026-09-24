"""Deterministic inventory-boundary lesson, not an LLM or IGPO reproduction."""
import json
from pathlib import Path

QUERIES = ('photo', 'vegan', 'wedding', 'gluten-free')
# Ground truth is used by evaluation only, never by retrieval.
BASE = [
    {'id': 'a', 'category': 'cake', 'tags': ['photo'], 'description': [], 'truth': ['photo']},
    {'id': 'b', 'category': 'cake', 'tags': ['vegan'], 'description': [], 'truth': ['vegan']},
    {'id': 'c', 'category': 'cake', 'tags': [], 'description': ['wedding'], 'truth': ['wedding']},
]

def portrait(items):
    """Toy probe sees the whole small catalog; production top-k need not."""
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
    # Frozen baseline assumes a nearby cake is acceptable when a category is dense.
    if not guided and query == 'gluten-free' and visible:
        return {'id': visible[0]['id'], 'decision': 'match', 'fields': fields}
    # No match is evidence-limited: it must never establish inventory absence.
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
    """Simplified finite replay gate; not Appendix B's statistical thresholds."""
    return (all(after[i] >= before[i] for i in target_indices)
            and any(after[i] > before[i] for i in target_indices)
            and all(after[i] >= before[i] for i in background_indices))


def simulate():
    renamed = [{**i, 'tags': [], 'description': i['tags'] + i['description']} for i in BASE]
    deleted = [i for i in renamed if i['id'] != 'a']
    scenarios = [('元の属性', BASE, None), ('属性を移動', renamed, None),
                 ('商品aを削除', deleted, None), ('probeが商品cを見落とす', BASE, ['a', 'b'])]
    records, frames = [], []
    for n, (label, items, ids) in enumerate(scenarios):
        b, g = evaluate(items, False, ids), evaluate(items, True, ids)
        records.append({'label': label, 'baseline': b, 'guided': g})
        frames.append({'value': n, 'note': label + '。人工4要求。規則は固定し、現在の属性を読み直す。',
                       'bars': [{'label': '固定属性：正答', 'value': b['correct']},
                                {'label': '在庫を参照：正答', 'value': g['correct']} ]})
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
        'explorer': {'label': '在庫の状態', 'unit': '', 'metric': '正答数 / 4',
                     'default': 0, 'frames': frames}}

if __name__ == '__main__':
    p = Path(__file__).with_name('results.json')
    p.write_text(json.dumps(simulate(), ensure_ascii=False, indent=2) + '\n')
    print(p)
