"""Original deterministic teaching program. No agent, API, or author artifact."""
from copy import deepcopy
import json
from pathlib import Path

SCENARIOS = {"inherited":"境界の実装漏れを引き継ぐ", "regression":"第3段階で境界を壊す", "oracle":"自己テストの期待値も誤る", "correct":"要求どおりに実装", "legacy":"既存の合計処理を壊す"}

def initial():
    return dict(filter=False, cap=False, render=False, inclusive=True, signed=True)

def execute(state, op, values, threshold=0, limit=1):
    # Actual behavior under test; no access to any acceptance expectation.
    if op == 'total':
        return sum(values) if state['signed'] else sum(abs(v) for v in values)
    if not state['filter']:
        return 'UNAVAILABLE'
    chosen = [v for v in values if v >= threshold] if state['inclusive'] else [v for v in values if v > threshold]
    if op == 'filter':
        return chosen
    if not state['cap']:
        return 'UNAVAILABLE'
    chosen = chosen[:limit]
    if op == 'cap':
        return chosen
    if not state['render']:
        return 'UNAVAILABLE'
    return ','.join(str(v) for v in chosen)

# Literal independent specification examples, never derived from defect flags.
F2P = [
    [('境界を含める', 'filter', [1,2,3], 2, 1, [2,3]), ('空集合', 'filter', [], 2, 1, [])],
    [('境界から1件', 'cap', [1,2,3], 2, 1, [2]), ('上限0件', 'cap', [1,2,3], 2, 0, [])],
    [('表示の追加', 'render', [1,3,4], 2, 1, '3'), ('空表示', 'render', [], 2, 1, '')],
]
BASE = [('符号付き合計', 'total', [-2,3], 0, 1, 1), ('空の合計', 'total', [], 0, 1, 0)]
P2P = [[('既存の合計', 'total', [1,2], 0, 1, 3)],
       [('既存の絞込み', 'filter', [1,3], 2, 1, [3])],
       [('既存の件数制限', 'cap', [1,3,4], 2, 2, [3,4])]]
CHAIN = sum(F2P, []) + [('境界を表示', 'render', [1,2,3], 2, 1, '2')]
SELF = [[('境界を試さない', 'filter', [1,3], 2, 1, [3])],
        [('1件に制限', 'cap', [1,3,4], 2, 1, [3])],
        [('文字列を表示', 'render', [1,3,4], 2, 1, '3')]]
WRONG_SELF = [('境界を除くと誤解', 'filter', [1,2,3], 2, 1, [3])]

def check(state, tests):
    checks=[]
    for name,op,values,threshold,limit,expected in tests:
        actual=execute(state,op,values,threshold,limit)
        checks.append(dict(name=name, op=op, values=values, threshold=threshold, limit=limit,
                           expected=expected, actual=actual, passed=actual==expected))
    return dict(passed=all(c['passed'] for c in checks), checks=checks)

def edit(state, stage, scenario, repair):
    # Modify the same workspace. Gates are not inputs and never roll back edits.
    state[['filter','cap','render'][stage]]=True
    if stage==0 and scenario in ('inherited','oracle'):state['inclusive']=False
    if stage==2 and scenario=='regression':state['inclusive']=False
    if stage==2 and scenario=='legacy':state['signed']=False
    if stage==2 and repair:state.update(inclusive=True,signed=True)

def simulate(scenario='inherited', repair=False):
    if scenario not in SCENARIOS:raise ValueError('Unknown scenario')
    state=initial();stages=[]
    for stage in range(3):
        before=deepcopy(state);edit(state,stage,scenario,repair)
        f2p=check(state,F2P[stage]);p2p=check(state,P2P[stage])
        tests=WRONG_SELF if scenario=='oracle' and stage==0 else SELF[stage]
        stages.append(dict(stage=stage,before=before,after=deepcopy(state),self_test=check(state,tests),
                           f2p=f2p,p2p=p2p,gate=f2p['passed'] and p2p['passed']))
    f2p=check(state,CHAIN);p2p=check(state,BASE)
    return dict(scenario=scenario,repair=repair,stages=stages,
                chain=dict(f2p=f2p,p2p=p2p,gate=f2p['passed'] and p2p['passed']))

def ratio(n,d):
    return dict(numerator=n,denominator=d,value=n/d if d else None)

def metrics(cases):
    n=len(cases);later=[s for c in cases for s in c['stages'][1:] if all(p['gate'] for p in c['stages'][:s['stage']])]
    last=[c for c in cases if c['stages'][-1]['gate']]
    failed=[c for c in cases if not all(s['gate'] for s in c['stages'])]
    return dict(first=ratio(sum(c['stages'][0]['gate'] for c in cases),n),
                chain=ratio(sum(c['chain']['gate'] for c in cases),n),
                continuation=ratio(sum(s['gate'] for s in later),len(later)),
                last_pass_chain_fail=ratio(sum(not c['chain']['gate'] for c in last),len(last)),
                recovery=ratio(sum(c['chain']['gate'] for c in failed),len(failed)))

def results():
    cases=[simulate(s,r) for s in SCENARIOS for r in (False,True)]
    return dict(kind='featurearc-teaching-v1',synthetic=cases,
                metrics={str(r).lower():metrics([c for c in cases if c['repair']==r]) for r in (False,True)},
                reported=dict(tasks=73,stages=263,repositories=53,configured_agents=10,
                              first_percent=62.7,chain_percent=28.5,last_pass_chain_fail=ratio(69,273),
                              inheritance_failed_later_percent=72.9,missed_prior_failure_percent=94.9),
                note='Synthetic cases are hand-designed illustrations, not a performance estimate or author replication.')

if __name__=='__main__':
    path=Path(__file__).resolve().parent
    data=results()
    (path/'results.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
    from render import document
    (path/'experiment.md').write_text(document(data))
