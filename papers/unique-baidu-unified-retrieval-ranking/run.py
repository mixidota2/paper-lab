"""Two local calculations, not a trained UNIQUE/RQ-VAE comparison."""
import json,math
from pathlib import Path
def assign(z,codes,frequency,tau):
    if len(codes)!=len(frequency) or any(p<=0 for p in frequency):raise ValueError('positive frequencies required in this toy')
    d=[sum((x-y)**2 for x,y in zip(z,c)) for c in codes]
    adjusted=[v*(p*len(codes))**tau for v,p in zip(d,frequency)]
    return dict(code=min(range(len(codes)),key=lambda i:adjusted[i]),raw_distances=d,adjusted_distances=adjusted)
def attention(q,keys):
    logits=[sum(x*y for x,y in zip(q,k))/math.sqrt(len(q)) for k in keys]
    w=[math.exp(v-max(logits)) for v in logits];total=sum(w)
    return [sum(a*k[j] for a,k in zip(w,keys))/total for j in range(len(q))]
def main():
    z=[.8,.6];codes=[[1,0],[0,1],[-1,0],[0,-1]];freq=[.7,.1,.1,.1]
    prefix=[[1,0],[0,1]];target=[1,0];extra=[5,0]
    r=dict(note='人工vector・固定頻度。モデル学習、RQ-VAE比較、HR/AUCの追試ではない。',verification=dict(mechanism='PARTIAL',performance='NOT TESTED',scaling='NOT TESTED',production_applicability='NOT TESTED'),assignments=[dict(tau=t,**assign(z,codes,freq,t)) for t in [0,1]],attention=dict(split=attention(target,prefix),split_after_extra_target=attention(target,prefix),mixed=attention(target,prefix+[target]),mixed_after_extra_target=attention(target,prefix+[target,extra])))
    Path(__file__).with_name('results.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
