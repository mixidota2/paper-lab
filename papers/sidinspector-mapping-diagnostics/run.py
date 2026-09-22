"""Same-item mapping probes: addressability does not imply neighbor alignment."""
from collections import Counter,defaultdict
import json,math
from pathlib import Path


def validate(rows,universe):
    ids=[i for i,c in rows]
    if len(set(ids))!=len(ids):raise ValueError('duplicate item key')
    if set(ids)!=set(universe):raise ValueError('missing or extra item')
    if len({len(c) for _,c in rows})!=1:raise ValueError('inconsistent depth')
    if any(not isinstance(t,int) for _,c in rows for t in c):raise ValueError('non-discrete token')
    return dict(rows)


def probe(mapping,edges,popularity):
    n=len(mapping);counts=Counter(mapping.values());depth=len(next(iter(mapping.values())))
    tail=sorted(mapping,key=lambda i:(popularity[i],i))[:n//2]
    d3=sum(w for i,j,w in edges if mapping[i][:1]==mapping[j][:1])/sum(w for _,_,w in edges)
    per_level=[]
    for level in range(depth):
        c=Counter(s[level] for s in mapping.values())
        per_level.append({'used':len(c),'entropy_bits':-sum(v/n*math.log2(v/n) for v in c.values())})
    fan=defaultdict(set)
    for sid in mapping.values():
        for j,t in enumerate(sid):fan[sid[:j]].add(t)
    return {'D1':per_level,'D2_alias_item_rate':sum(counts[c]>1 for c in mapping.values())/n,'D3_L1_weighted':d3,'D4_tail_unique_ratio':len({mapping[i] for i in tail})/len(tail),'D5_active_prefixes':[len({c[:k] for c in mapping.values()}) for k in range(1,depth+1)],'D5_max_fanout':max(map(len,fan.values()))}


def main():
    items=list('abcdef');edges=[('a','b',4),('c','d',3),('e','f',2)];pop=dict(zip(items,[20,15,8,4,2,1]))
    maps={'aliased':{'a':(0,0),'b':(0,0),'c':(1,0),'d':(1,1),'e':(2,0),'f':(2,0)},
          'unique_unaligned':{'a':(0,0),'b':(1,0),'c':(2,0),'d':(0,1),'e':(1,1),'f':(2,1)},
          'unique_aligned':{'a':(0,0),'b':(0,1),'c':(1,0),'d':(1,1),'e':(2,0),'f':(2,1)}}
    profiles={name:probe(validate(list(m.items()),items),edges,pop) for name,m in maps.items()}
    assert profiles['unique_unaligned']['D2_alias_item_rate']==profiles['unique_aligned']['D2_alias_item_rate']==0
    assert profiles['unique_unaligned']['D3_L1_weighted']==0 and profiles['unique_aligned']['D3_L1_weighted']==1
    failures=[]
    for rows in [[('a',(0,0))],[('a',(0,0)),('a',(1,0))],[(i,(0,0) if i!='f' else (0,)) for i in items]]:
        try:validate(rows,items)
        except ValueError as e:failures.append(str(e))
    assert len(failures)==3
    out={'note':'同じ6 itemと固定co-occurrence edgeの診断。公式tokenizerの再学習・A/Bはしていない。',
      'scope':{'mapping_contract':'CONFIRMED','mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'},
      'maps':maps,'profiles':profiles,'rejected':failures,
      'experiments':[{'name':'同じcollision-freeでもprefixの意味は異なる','metrics':{k:{'alias_item_rate':v['D2_alias_item_rate'],'neighbor_recovery':v['D3_L1_weighted'],'tail_capacity':v['D4_tail_unique_ratio']} for k,v in profiles.items()}}]}
    from plot import render
    render(out)
    Path(__file__).with_name('results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');return out
if __name__=='__main__':main()
