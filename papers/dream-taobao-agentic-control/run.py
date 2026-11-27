"""DREAMが設定の一部を変更し、無効な提案なら既定値へ戻すしくみを人工例で試す。"""
import json
import math
from pathlib import Path

DEFAULT = {'ctr':1., 'ipv':1., 'cvr':1., 'gmv':1., 'scatter':3}
BASE_WEIGHT = {'ctr':.1, 'ipv':.2, 'cvr':.1, 'gmv':.1}


def compile_strategy(bundle, now=100):
    """Labが決めた形式と期限を確認し、許可されない項目や値があれば既定値を返す。"""
    default = dict(DEFAULT)
    if not isinstance(bundle, dict):
        return default, 'fallback: missing'
    if set(bundle) - {'version','expires','boost','category'}:
        return default, 'fallback: allowlist'
    if type(bundle.get('version')) is not int or bundle['version'] != 1:
        return default, 'fallback: version'
    expires = bundle.get('expires')
    if isinstance(expires,bool) or not isinstance(expires,(int,float)) or not math.isfinite(expires) or expires <= now:
        return default, 'fallback: expired'
    boosts = bundle.get('boost',{})
    if not isinstance(boosts,dict) or set(boosts)-set(BASE_WEIGHT):
        return default, 'fallback: objective schema'
    category = bundle.get('category',0)
    values = list(boosts.values())+[category]
    if any(type(x) is not int or x not in [-2,-1,0,1,2] for x in values):
        return default, 'fallback: level range'
    for key,level in boosts.items():
        # 校正した予測値を1と仮定し、各目的の項に掛ける値を計算する。
        default[key] = 1+BASE_WEIGHT[key]*level
    default['scatter'] = max(1,DEFAULT['scatter']+category)
    return default, 'override'


def invoke(score, threshold, remaining):
    if not 0<=score<=1 or not 0<=threshold<=1 or remaining<0:
        raise ValueError('invalid trigger inputs')
    return score>=threshold and remaining>0


def replay_reward(baseline, proposal):
    if not baseline or not proposal:
        raise ValueError('repeated calls required')
    return int(sum(proposal)/len(proposal)>sum(baseline)/len(baseline))


def compute():
    valid={'version':1,'expires':120,'boost':{'ipv':2},'category':-2}
    bundles=[None,valid,{**valid,'expires':99},{**valid,'boost':{'ipv':3}},
             {**valid,'shell':'write-global'}, {**valid,'boost':{'ipv':True}}]
    names=['未設定','有効','期限切れ','範囲外','未許可field','bool値']
    cases=[{'name':name,'bundle':bundle,'parameters':compile_strategy(bundle)[0],'status':compile_strategy(bundle)[1]} for name,bundle in zip(names,bundles)]
    scores=[.1,.8,.4,.9,.7]
    left=2; decisions=[]
    for s in scores:
        accepted=invoke(s,.7,left)
        left-=int(accepted)
        decisions.append({'score':s,'invoke':accepted,'remaining':left})
    # 著者が報告した増加率を使う。表の引き算は、別に測った追加の因果効果ではない。
    lifts={'IPV':[2.06,2.71],'GMV':[.88,1.31],'PV':[1.03,1.04]}
    return {'note':'Labは同じ既定値に異なる方針案を渡した。期限、重み、呼び出し枠2件は人工の値で、LLMの推論や本番のA/Bテストは実行していない。',
      'verification':{'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'},
      'experiments':[{'name':'方針案が許可された設定だけを変えるか','metrics':{x['name']:{'status':x['status'],**x['parameters']} for x in cases}},
                     {'name':'表7の共通基準に対する増加率を比べる','metrics':{k:{'rerank':v[0],'rerank+rank':v[1],'差（percentage points）':round(v[1]-v[0],4),'比の変化（%）':round(((1+v[1]/100)/(1+v[0]/100)-1)*100,4)} for k,v in lifts.items()}}],
      'cases':cases,'trigger_trace':decisions,'reward_tie':replay_reward([1,1],[1,1]),
      'checks':{'invalid_defaults':'CONFIRMED','local_override':'CONFIRMED','budget_gate':'CONFIRMED','business_lift':'NOT TESTED'}}

if __name__ == '__main__':
    Path(__file__).with_name('results.json').write_text(json.dumps(compute(),ensure_ascii=False,indent=2)+'\n')
