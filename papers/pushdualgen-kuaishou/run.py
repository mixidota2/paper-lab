"""SID-first causal factorization and optional-copy operation trace.
Finite empirical model, no Qwen weights. Counts are fixture observations.
"""
from collections import Counter
from pathlib import Path
import json
OBS=[('music','s0','歌の続きを聴く')]*7+[('music','s1','料理を見る')]*3+[('food','s1','料理を見る')]*8+[('food','s0','歌を聴く')]*2

def decode(history,copy=True):
    counts=Counter(s for h,s,c in OBS if h==history)
    sid=counts.most_common(1)[0][0]
    text=Counter(c for h,s,c in OBS if h==history and s==sid).most_common(1)[0][0] if copy else ''
    return {'sid':sid,'copy':text,'steps':1+(len(text) if copy else 0)}

def rank(beta):
    user=[1.,0.]; semantic=[0.,1.]; videos={'familiar':[.9,.1],'discovery':[.4,.9],'mixed':[.6,.6]}
    query=[a+beta*b for a,b in zip(user,semantic)]
    return sorted(videos,key=lambda i:-sum(a*b for a,b in zip(query,videos[i])))

def compute():
    rows={h:{'copy_on':decode(h),'copy_off':decode(h,False)} for h in ['music','food']}
    assert all(x['copy_on']['sid']==x['copy_off']['sid'] for x in rows.values())
    return {'note':'合成頻度モデル。copyはSIDの後なので省略しても先のSIDは同一。説明の忠実性やQwen品質は未検証。','verification':{'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'},'experiments':[{'name':'copy省略と表現融合','metrics':{'baseline_user_only':{'ranking':rank(0)},'user_plus_SID':{'ranking':rank(1)}}}],'decode_trace':rows}

if __name__ == "__main__":
    result = compute()
    Path(__file__).with_name("results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
