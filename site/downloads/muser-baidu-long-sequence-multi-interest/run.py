"""Pooling arithmetic and information-loss counterexample, not MuSeR training."""
import json
from pathlib import Path
def pool(xs,k):return [sum(xs[i:i+k]) for i in range(0,len(xs),k)]
def compress(xs,recent=800,middle=1200):
    if recent<0 or middle<0 or recent+middle>len(xs):raise ValueError('invalid boundaries')
    early=len(xs)-recent-middle
    return pool(xs[:early],64)+pool(xs[early:early+middle],16)+xs[early+middle:]
def orthogonal_penalty(heads):
    return sum(sum(x*y for x,y in zip(a,b))**2 for i,a in enumerate(heads) for j,b in enumerate(heads) if i!=j)/len(heads)**2
def main():
    xs=list(range(10000));small=compress(xs)
    r=dict(note='人工数列のsum pooling。attention pair数はproxyでありlatencyではない。',verification=dict(mechanism='PARTIAL',performance='NOT TESTED',scaling='NOT TESTED',production_applicability='NOT TESTED'),tokens=dict(original=len(xs),compressed=len(small),pair_count_ratio=(len(small)/len(xs))**2,sum_preserved=sum(xs)==sum(small)),order_loss=dict(a=pool([1,0],2),b=pool([0,1],2)),orthogonal_penalty=dict(distinct=orthogonal_penalty([[1,0],[0,1]]),duplicate=orthogonal_penalty([[1,0],[1,0]])))
    Path(__file__).with_name('results.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
