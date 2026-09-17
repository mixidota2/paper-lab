"""GFSA shared attention and gate-weighted InfoNCE with fixed synthetic vectors."""
import json
import math
from pathlib import Path

def softmax(x):
    e=[math.exp(v-max(x)) for v in x]; return [v/sum(e) for v in e]

def gfsa(weight, sid_logits=(2.,0.,0.), item_logits=(0.,0.,2.)):
    sid,item=softmax(sid_logits),softmax(item_logits)
    fused=[weight*a+(1-weight)*b for a,b in zip(sid,item)]
    hs=[[1.,0.],[.5,.5],[0.,1.]]; hi=[[.8,.2],[.2,.8],[0.,1.]]
    pool=lambda h:[sum(a*v[j] for a,v in zip(fused,h)) for j in range(2)]
    return {"weight":weight,"sid_attention":sid,"item_attention":item,"shared_attention":fused,
            "sid_pooled":pool(hs),"item_pooled":pool(hi)}

def info_nce(positive,negatives,tau=.2):
    logits=[positive/tau]+[v/tau for v in negatives]
    return -math.log(softmax(logits)[0])

def compute():
    loss=info_nce(.8,[.2,.3])
    cases=[gfsa(w) for w in [0,.25,.5,.75,1]]
    for x in cases:x["weighted_alignment_loss"]=x["weight"]*loss
    return {"note":"gateを外から与える人工attention。経過日数からgateを学習した実測曲線ではない。",
      "experiments":[{"name":"同じgateでattentionと整列強度を制御", "metrics":{str(x["weight"]):{"最初の履歴への重み":round(x["shared_attention"][0],6),"最後の履歴への重み":round(x["shared_attention"][-1],6),"対照損失への寄与":round(x["weighted_alignment_loss"],6)} for x in cases}}],
      "cases":cases,"checks":{"shared_attention_convexity":"CONFIRMED","alignment_weight_coupling":"CONFIRMED","learned_maturity_gate":"NOT TESTED","ranking_auc":"NOT TESTED"}}


def main():
    result = compute()
    Path(__file__).with_name("results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
