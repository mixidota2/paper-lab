"""Conservative prefix targeting, correlation false positives and beam slots."""
import json,hashlib
from pathlib import Path


def bloom(values,width=256):
    bits=0
    for v in values:
        h=hashlib.sha256(v.encode()).digest()
        for offset in [0,4,8]:bits|=1 << (int.from_bytes(h[offset:offset+4],'little')%width)
    return bits


def match(mask,user):return mask & user == user


def union(masks):
    out=0
    for m in masks:out|=m
    return out


def main():
    # Country: US=1, CA=2. Age: young=4, adult=8.
    ads={'a':1|4,'b':2|8,'c':1|8,'d':2|4}
    groups={'mixed':['a','b'],'eligible':['c'],'wrong':['d']}
    request=1|8
    masks={k:union(ads[i] for i in v) for k,v in groups.items()}
    coarse={k:match(m,request) for k,m in masks.items()}
    exact={k:[i for i in v if match(ads[i],request)] for k,v in groups.items()}
    assert coarse['mixed'] and not exact['mixed']
    for user in [1|4,1|8,2|4,2|8]:
        for k,items in groups.items():
            if any(match(ads[i],user) for i in items):assert match(masks[k],user)
    scores={'mixed':.9,'wrong':.8,'eligible':.7};beam=2
    baseline=sorted(scores,key=scores.get,reverse=True)[:beam]
    gtm=sorted((k for k in scores if coarse[k]),key=scores.get,reverse=True)[:beam]
    def final(paths):return [i for k in paths for i in exact[k]]
    assert final(baseline)==[] and final(gtm)==['c']
    # Force a tiny Bloom budget to make the false-positive mechanism visible.
    cities=['Tokyo','Osaka','Kyoto'];mask=bloom(cities,width=8)
    false=[f'city-{i}' for i in range(100) if match(mask,bloom([f'city-{i}'],8))]
    assert all(match(mask,bloom([city],8)) for city in cities)
    out={'note':'4広告の人工targeting。CPUの論理検査でありGH200速度や実pass rateは再現しない。',
      'scope':{'conservative_no_false_negative_fixture':'CONFIRMED','mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'},
      'request_mask':request,'ads':ads,'prefix_masks':masks,'coarse':coarse,'exact':exact,'beam':{'CD_only':baseline,'GTM':gtm},'bloom_8bit_false_positives':false,
      'experiments':[{'name':'beam 2の枠をrequest条件で使い直す','metrics':{'eligible_ads_after_exact':{'CD_only':len(final(baseline)),'GTM':len(final(gtm))},'mixed_prefix_false_positive':{'observed':True}}}]}
    Path(__file__).with_name('results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');return out
if __name__=='__main__':main()
