"""特徴の分布が異なる二種類の人工候補で、教師の点数を学べるか試す。

Sonaの採点部の代わりに線形モデルを使う。教師は決めておいた式で採点し、
学習するモデルは教師との点数差の絶対値を小さくする。
"""
import json, random
from pathlib import Path

def data(seed,n,rollout):
    rng=random.Random(seed)
    return [(1.,rng.uniform(-1,1),rng.uniform(.5,1.5) if rollout else 0.) for _ in range(n)]
def teacher(x):return .3+1.2*x[1]-1.8*x[2]
def predict(w,x):return sum(a*b for a,b in zip(w,x))
def train(sources,steps=1400):
    w=[0.,0.,0.]
    for _ in range(steps):
        grad=[0.]*3
        for source in sources:
            for x in source:
                e=predict(w,x)-teacher(x); sign=(e>0)-(e<0)
                for j in range(3):grad[j]+=sign*x[j]/len(source)
        w=[a-.012*g for a,g in zip(w,grad)]
    return w

def compute():
    imp=data(11,160,False); rollout=data(12,32,True); test=data(13,120,True)
    out={}
    for name,sources in [('impressions_only',[imp]),('rollouts_only',[rollout]),('both_source_means',[imp,rollout])]:
        w=train(sources); correct=0; total=0
        for i in range(len(test)):
            for j in range(i):
                correct+=(predict(w,test[i])-predict(w,test[j]))*(teacher(test[i])-teacher(test[j]))>0;total+=1
        out[name]={'heldout_MAE':round(sum(abs(predict(w,x)-teacher(x)) for x in test)/len(test),6),'pair_accuracy':round(correct/total,6),'weights':w}
    n,r,l=8192,2048,7
    return {'note':'二種類の人工候補の特徴の分布が違うとき、学習に使う候補の違いだけを比べる。教師が利用者の好みを当てるか、Transformerで再現できるか、本番で効果があるかは試していない。','verification':{'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'},'experiments':[{'name':'学習に使わなかった同じ生成候補で、教師との点数の差と順位の一致を測る','seed':13,'metrics':out}], 'attention_pair_counts':{'seven_full_layers':l*n*n,'compression_proxy':l*r*r+n*n+2*(n-r)*r,'note':'注意機構で履歴の位置どうしを照らし合わせる項の数を式から求めた。浮動小数点演算数（FLOPs）や実際にかかった時間ではない。'}}

if __name__ == "__main__":
    result = compute()
    Path(__file__).with_name("results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
