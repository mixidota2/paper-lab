"""VARG Eqs. 3–6, 11–18: finite address/reward probes; no neural training."""
import json
import math
from pathlib import Path
from collections import Counter


def eb(buys, clicks, prior=.1, strength=5):
    return (buys + strength * prior) / (clicks + strength)


def assign(values, old=None):
    ordered = sorted(values, key=lambda k: (-values[k], k))
    if old is None:
        return {item: rank for rank, item in enumerate(ordered)}
    capacity = max(old.values()) + 1
    return {item: old[item] if item in old else min(rank, capacity - 1)
            for rank, item in enumerate(ordered)}


def alias_rate(mapping):
    sizes = Counter(mapping.values())
    return sum(sizes[c] > 1 for c in mapping.values()) / len(mapping)


def reward(state, behavior=None, advantage=0, relevance=3):
    if state == 'malformed': return -2.0
    if state == 'unoccupied': return -1.0
    adv = .2 * math.tanh(max(0, advantage) / 1.5) if math.isfinite(advantage) else 0
    if behavior in {'buy', 'click', 'exposure'}:
        return {'buy': 3., 'click': 1., 'exposure': .1}[behavior] + adv
    return adv + {3: .08, 2: .03, 1: -.1}.get(relevance, 0)


def ordinal(target, capacity, radius=3, temperature=1):
    weights = {r: math.exp(-abs(r-target)/temperature)
               for r in range(capacity) if abs(r-target) <= radius}
    total = sum(weights.values())
    return {str(r): v/total for r, v in weights.items()}


def main():
    old_values = {'A': .8, 'B': .5, 'C': .2}
    old = assign(old_values)
    values = {**old_values, 'D': .6}
    full, frozen = assign(values), assign(values, old)
    stable = {mode: sum(m[i] == old[i] for i in old)/len(old)
              for mode, m in [('reorder', full), ('frozen', frozen)]}
    probes = [{'state': s, 'behavior': b, 'reward': reward(s, b, 2, 3)}
              for s,b in [('malformed','buy'),('unoccupied','buy'),('occupied','buy'),
                           ('occupied','click'),('occupied',None)]]
    assert stable['frozen'] == 1 and stable['reorder'] < 1
    assert alias_rate(old) == 0 and alias_rate(frozen) == .5
    assert probes[0]['reward'] < 0 and probes[1]['reward'] < 0
    assert reward('occupied','buy',0,3) == reward('occupied','buy',0,1)
    assert reward('occupied',None,0,1) < 0
    assert abs(sum(ordinal(0,4).values())-1) < 1e-12
    result = {'note':'人工4商品・1 prefix。学習済みモデルのHRやGMVを再現していない。',
      'scope':{'address_invariants':'CONFIRMED','mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'},
      'experiments':[{'name':'新商品DをAとBの間へ追加','metrics':{'old_address_retention':stable,'alias_item_rate':{'initial':0,'full_reorder':alias_rate(full),'frozen':alias_rate(frozen)}}}],
      'maps':{'initial':old,'full_reorder':full,'frozen':frozen},'reward_probes':probes,
      'ordinal_edge':ordinal(0,4),'eb_sparse_example':{'raw_1_of_1':1.,'smoothed_1_of_1':eb(1,1)},
      'branch_weights':{str(n):.1+.9*math.log(n)/math.log(8) for n in [1,2,4,8]}}
    Path(__file__).with_name('results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result

if __name__ == '__main__': main()
