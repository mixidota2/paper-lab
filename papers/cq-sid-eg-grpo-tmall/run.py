"""Cluster expansion and sparse reward group probe. Not Qwen training or GRPO reproduction."""
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
    # Five tabular SIDs: the rarely sampled clicked/exposed SIDs have positive reward.
    probs=[.7,.2,.08,.015,.005]
    reward=[.1,.1,.1,.5,1.]
    for _ in range(trials):
        sampled=rng.choices(range(5),weights=probs,k=8)
        group=sampled+[rng.choice([3,4]) for _ in range(k)]
        adv=advantages([reward[i] for i in group])
        dead+=max(adv)-min(adv)<1e-9
        # Gradient of mean A log pi(o) at old policy (ratio=1); includes injected samples.
        grad=[sum(a*((j==o)-probs[j]) for o,a in zip(group,adv))/len(group) for j in range(5)]
        gradients.append(sum(grad[3:]))
    return {'expert_k':k,'zero_advantage_fraction':dead/trials,
            'mean_positive_sid_logit_gradient':round(sum(gradients)/trials,6)}


def compute():
    frames=[]
    # Item target=23. Cluster order is intentionally coarse; efficiency truncation can discard it.
    clusters=[list(range(i*10,(i+1)*10)) for i in range(6)]
    for width in (1,2,3,4,6):
        expanded=sum(clusters[:width],[])
        selected=sorted(expanded,reverse=True)[:20]
        frames.append({'beam':width,'unique_items':width,'cluster_items':len(expanded),
                       'after_cap':len(selected),'target_retained':23 in selected,'selected':selected})
    probes=[gradient_probe(k) for k in (0,2,4)]
    return {'note':'人工SID群で展開件数と正規化advantageを計算。学習崩壊や実際の検索精度は再現していない。',
            'experiments':[{'name':'疎報酬の8サンプルにexpertを注入','dataset':'five synthetic SID outcomes','seed':16,'n':2000,
                           'metrics':{f'K={p["expert_k"]}':{k:v for k,v in p.items() if k!='expert_k'} for p in probes}}],
            'frames':frames,'group_examples':{str(k):advantages([.1]*8+[1.]*k) for k in (0,2,4)},
            'cluster_split':{str(n):split_cluster(n) for n in (120,5001)}}


if __name__ == '__main__':
    Path(__file__).with_name('results.json').write_text(json.dumps(compute(),ensure_ascii=False,indent=2)+'\n')
