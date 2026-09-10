"""Deterministic DAG recovery and a commit certificate toy, not a concurrent runtime."""
import json
from pathlib import Path

# Topological order interleaves independent branches. Edges are actual value dependencies.
NODES = {'A': ([], ['budget']), 'B': ([], ['city']), 'C': (['A'], []),
         'D': (['B'], []), 'E': ([], ['style']), 'F': (['C', 'D', 'E'], [])}
LIFECYCLE = {'A': 'complete', 'B': 'complete', 'C': 'running', 'D': 'running', 'E': 'complete', 'F': 'pending'}


def intersects(a, b):
    return a == b or a.startswith(b+'.') or b.startswith(a+'.')


def affected(delta):
    bad = set()
    for node, (parents, reads) in NODES.items():
        if any(intersects(r, d) for r in reads for d in delta) or bad.intersection(parents):
            bad.add(node)
    return bad


def execute(state, cached=None, redo=None):
    result = dict(cached or {})
    for node, (parents, reads) in NODES.items():
        if redo is None or node in redo:
            result[node] = (node, tuple(result[p] for p in parents), tuple(state[r] for r in reads))
    return result


def commit_valid(reads, intervening_deltas, parents_current=True, complete=True, effect_safe=True):
    return complete and parents_current and effect_safe and not any(
        intersects(r, d) for delta in intervening_deltas for d in delta for r in reads)


def experiment(delta, provenance):
    old = {'budget': 100, 'city': 'Tokyo', 'style': 'brief'}
    new = {k: (str(v)+' revised' if k in delta else v) for k, v in old.items()}
    cache, oracle = execute(old), execute(new)
    bad = affected(delta)
    order = list(NODES)
    first = min((order.index(n) for n in bad), default=len(order))
    sets = {'restart': set(order), 'suffix': set(order[first:]),
            'selective': bad if provenance == 'complete' else set(order)}
    policies = {}
    for policy, redo in sets.items():
        actual = execute(new, cache, redo)
        policies[policy] = {'recomputed': [n for n in order if n in redo], 'calls': len(redo), 'oracle_equal': actual == oracle}
    actions = {n: ('cancel' if LIFECYCLE[n]=='running' else 'avoid' if LIFECYCLE[n]=='pending' else 'recompute')
               if n in sets['selective'] else ('continue' if LIFECYCLE[n]=='running' else 'reuse') for n in order}
    return {'delta': delta, 'provenance': provenance, 'policies': policies, 'lifecycle_plan': actions}


def main():
    cases = [experiment(['budget'], 'complete'), experiment(['budget', 'city', 'style'], 'complete'), experiment(['budget'], 'unknown')]
    checks = {'late_read_rejected': not commit_valid(['budget'], [['budget']]),
              'valid_sibling_accepted': commit_valid(['city'], [['budget']]),
              'obsolete_parent_rejected': not commit_valid([], [], parents_current=False),
              'unknown_rejected': not commit_valid([], [], complete=False),
              'unsafe_effect_rejected': not commit_valid([], [], effect_safe=False)}
    out = {'note': '合成 DAG の決定的再実行。call はノード再計算数。並行実行・LLM token・本番効果は測っていない。',
           'experiments': [{'name': 'budget の局所変更', 'metrics': {k: {'calls': v['calls'], 'oracle_equal': v['oracle_equal']} for k, v in cases[0]['policies'].items()}}],
           'cases': cases, 'commit_checks': checks}
    assert all(checks.values())
    assert all(v['oracle_equal'] for c in cases for v in c['policies'].values())
    Path(__file__).with_name('results.json').write_text(json.dumps(out, ensure_ascii=False, indent=2)+'\n')
    return out

if __name__ == '__main__':
    main()
