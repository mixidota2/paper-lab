"""人工例で商品候補の絞り込みと、報酬を比べる量を計算する。モデルは学習しない。"""
import json
import math
import random
from pathlib import Path


def advantages(rewards):
    mean=sum(rewards)/len(rewards)
    std=math.sqrt(sum((r-mean)**2 for r in rewards)/len(rewards))
    return [(r-mean)/(std+1e-8) for r in rewards]


def split_cluster(count, maximum=50, cap=100):
    groups=min(math.ceil(count/maximum),cap)
    return [count//groups + (i<count%groups) for i in range(groups)] if count else []


def gradient_probe(k, seed=16, trials=2000):
    rng=random.Random(seed)
    dead=0
    gradients=[]
    # 5個の人工SIDを使う。最後の2個にはクリックや表示に対応する高い報酬を付ける。
    probs=[.7,.2,.08,.015,.005]
    reward=[.1,.1,.1,.5,1.]
    for _ in range(trials):
        sampled=rng.choices(range(5),weights=probs,k=8)
        group=sampled+[rng.choice([3,4]) for _ in range(k)]
        adv=advantages([reward[i] for i in group])
        dead+=max(adv)-min(adv)<1e-9
        # 新旧の出力確率比が1の時点で、mean(A log pi(o))の勾配を求める。
        # モデルが出した例と、後から加えた教師例の両方を使う。
        grad=[sum(a*((j==o)-probs[j]) for o,a in zip(group,adv))/len(group) for j in range(5)]
        gradients.append(sum(grad[3:]))
    return {'expert_k':k,'zero_advantage_fraction':dead/trials,
            'mean_positive_sid_logit_gradient':round(sum(gradients)/trials,6)}


def compute():
    frames=[]
    # 商品番号を後段の点として使う。候補の群を増やすと、商品23が上位20件から外れ得る。
    clusters=[list(range(i*10,(i+1)*10)) for i in range(6)]
    for width in (1,2,3,4,6):
        expanded=sum(clusters[:width],[])
        selected=sorted(expanded,reverse=True)[:20]
        frames.append({'beam':width,'unique_items':width,'cluster_items':len(expanded),
                       'after_cap':len(selected),'target_retained':23 in selected,'selected':selected})
    probes=[gradient_probe(k) for k in (0,2,4)]
    return {'note':'人工のSIDから商品を取り出し、上位20件に絞った。教師例を加えた場合に各報酬が群の平均とどれだけ違うかも計算した。本番の検索精度や学習の収束は測っていない。',
            'experiments':[{'name':'モデルが出した8個の候補に教師例を加える','dataset':'人工のSID 5個','seed':16,'n':2000,
                           'metrics':{f'K={p["expert_k"]}':{k:v for k,v in p.items() if k!='expert_k'} for p in probes}}],
            'frames':frames,'group_examples':{str(k):advantages([.1]*8+[1.]*k) for k in (0,2,4)},
            'cluster_split':{str(n):split_cluster(n) for n in (120,5001)}}


if __name__ == '__main__':
    Path(__file__).with_name('results.json').write_text(json.dumps(compute(),ensure_ascii=False,indent=2)+'\n')
