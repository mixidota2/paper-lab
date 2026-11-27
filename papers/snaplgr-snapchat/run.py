"""同じSIDに対応する動画を、名前順と点の高い順で選ぶ人工例。
LLMを学習したり、TensorRTの処理量を測ったりはしない。
"""
import json, random
from pathlib import Path

def materialize(codes,mapping,values,weighted):
    out=[]
    for code in codes:
        group=mapping.get(code,[])
        if group:out.append(max(group,key=lambda i:values[i]) if weighted else sorted(group)[0])
    return out

def compute():
    rng=random.Random(41); mapping={str(k):[f'{k}-a',f'{k}-b'] for k in range(30)}
    values={i:rng.random() for group in mapping.values() for i in group}
    # 最初は点の高い動画を正解にする。
    targets=[max(g,key=lambda i:values[i]) for g in mapping.values()]
    base=materialize(list(mapping),mapping,values,False); prop=materialize(list(mapping),mapping,values,True)
    metric=lambda a:sum(x==y for x,y in zip(a,targets))/len(targets)
    # 別の条件では点の低い動画を正解にする。
    opposite=[min(g,key=lambda i:values[i]) for g in mapping.values()]
    return {'note':'Labは30個の人工のSIDに2本ずつ動画を付けた。正解が点の高い方にある条件と低い方にある条件を比べた。本番の点の重みは推定していない。','verification':{'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'},'experiments':[{'name':'同じSIDが当たっても、選ぶ動画は変わる','seed':41,'metrics':{'first_item':{'SID_hit':1.,'video_hit':metric(base),'opposite_target_hit':sum(a==b for a,b in zip(base,opposite))/30},'value_weighted':{'SID_hit':1.,'video_hit':metric(prop),'opposite_target_hit':sum(a==b for a,b in zip(prop,opposite))/30}}}]}

if __name__ == "__main__":
    result = compute()
    Path(__file__).with_name("results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
