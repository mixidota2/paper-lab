"""Intent graph anchoring and RCPO coefficient; no encoder/LLM training."""
import math,json
from pathlib import Path


def beta_factor(delta):
    return min(1.8,max(.2,1+math.log((2-delta)/(2+delta))))


def propagate(x,w,steps=3,anchor=.2):
    n=len(x);degree=[sum(r) for r in w]
    normalized=[[w[i][j]/math.sqrt(degree[i]*degree[j]) if degree[i]*degree[j] else 0 for j in range(n)] for i in range(n)]
    h=[r[:] for r in x]
    for _ in range(steps):
        h=[[(1-anchor)*sum(normalized[i][j]*h[j][k] for j in range(n))+anchor*x[i][k] for k in range(len(x[0]))] for i in range(n)]
    return h


def main():
    # Lipstick and necklace share gift intent, despite different product content.
    x=[[1.,0.],[0.,1.],[-1.,0.]]
    w=[[0,4,0],[4,0,0],[0,0,0]]
    h=propagate(x,w)
    dist=lambda a,b:math.sqrt(sum((i-j)**2 for i,j in zip(a,b)))
    candidates=[{'id':'lipstick','relevance':.9,'business':.6},{'id':'necklace','relevance':.85,'business':.8},{'id':'repair','relevance':.1,'business':1.}]
    business=max(candidates,key=lambda r:r['business'])['id']
    # Illustrative hard gate, not the full SRA/BPR pair construction.
    gated=max((r for r in candidates if r['relevance']>=.8),key=lambda r:r['business'])['id']
    assert business=='repair' and gated=='necklace'
    assert dist(h[0],h[1])<dist(x[0],x[1])
    margins=[-1,-.5,0,.5,1];factors=[beta_factor(d) for d in margins]
    assert all(a>=b for a,b in zip(factors,factors[1:]))
    assert propagate(x,w,anchor=1)==x
    out={'note':'人工3商品。Eq. 3と9の算術、関連性gateの意義を確認。ICEGRの学習・A/B再現ではない。',
      'scope':{'calibration_monotonicity':'CONFIRMED','mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'},
      'embeddings':{'content':x,'after_graph':h},'calibration':[{'margin':d,'factor':v} for d,v in zip(margins,factors)],
      'experiments':[{'name':'意図で結ぶ2商品の距離と関連性制約','metrics':{'gift_pair_distance':{'before':dist(x[0],x[1]),'after':dist(h[0],h[1])},'chosen':{'business_only':business,'relevance_gate':gated}}}]}
    from plot import render
    render(out)
    Path(__file__).with_name('results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');return out
if __name__=='__main__':main()
