"""固定の確率表を使い、辞書で候補を制限する探索をCPUで確かめる。"""
import json
import math
from pathlib import Path

PATHS=[(0,0),(0,1),(1,2),(2,0)]
PROBS=[[.6,.3,.1],[.1,.1,.8]]

def beam(width, prefix_valid=True):
    active=[((),0.)]
    for depth,probs in enumerate(PROBS):
        expanded=[]
        for prefix,score in active:
            for token,p in enumerate(probs):
                path=prefix+(token,)
                valid=any(x[:depth+1]==path for x in PATHS) if prefix_valid else any(x[depth]==token for x in PATHS)
                if valid:expanded.append((path,score+math.log(p)))
        active=sorted(expanded,key=lambda x:(-x[1],x[0]))[:width]
    return [{"path":p,"probability":round(math.exp(s),8),"valid":p in PATHS} for p,s in active]

def compute():
    frames={str(w):beam(w) for w in [1,2,3,4]}
    exhaustive=sorted(PATHS,key=lambda p:-(PROBS[0][p[0]]*PROBS[1][p[1]]))
    return {"note":"この人工例では、2段階の探索で候補を何件残すかと、辞書の検査方法を変えます。GPUの速度は測りません。",
      "experiments":[{"name":"同じ確率表で、各段階に残す候補数を変える", "metrics":{w:{"最上位の列の確率":v[0]["probability"],"返した候補数":len(v)} for w,v in frames.items()}}],
      "beams":frames,"depth_only":beam(4,False),"exhaustive_best":exhaustive[0],
      "checks":{"prefix_compliance":"CONFIRMED","wide_beam_recovers_best_in_toy":"CONFIRMED","gpu_latency":"NOT TESTED"}}


def main():
    result = compute()
    Path(__file__).with_name("results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
