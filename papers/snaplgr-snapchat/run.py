"""SID-to-item materialization: same generated SID, different item recall.
Tests the retrieval metric boundary, not LLM training or TensorRT throughput.
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
    # A controlled target favours value; this assumption is intentionally declared.
    targets=[max(g,key=lambda i:values[i]) for g in mapping.values()]
    base=materialize(list(mapping),mapping,values,False); prop=materialize(list(mapping),mapping,values,True)
    metric=lambda a:sum(x==y for x,y in zip(a,targets))/len(targets)
    # Counterexample: preferences opposite to value make weighting harmful.
    opposite=[min(g,key=lambda i:values[i]) for g in mapping.values()]
    return {'note':'30個の合成SID、各2動画。valueと正解が一致する条件と逆転条件を比較。Snapのvalue重みを推定していない。','verification':{'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'},'experiments':[{'name':'同じSID hitでも動画hitは変わる','seed':41,'metrics':{'first_item':{'SID_hit':1.,'video_hit':metric(base),'opposite_target_hit':sum(a==b for a,b in zip(base,opposite))/30},'value_weighted':{'SID_hit':1.,'video_hit':metric(prop),'opposite_target_hit':sum(a==b for a,b in zip(prop,opposite))/30}}}]}

if __name__ == "__main__":
    result = compute()
    Path(__file__).with_name("results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
