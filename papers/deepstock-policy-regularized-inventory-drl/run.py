"""4つの発注式を検算する。強化学習やTmallの非公開データは使わない。"""
import json
from pathlib import Path


def action(mode, inventory, output, features):
    if mode == 'None':
        return output[0]
    target = output[0] if mode == 'Base' else sum(a*b for a,b in zip(output, features))
    return max(target-inventory, 0) if mode in ('Base', 'Both') else target


def main():
    frames = []
    for target in (12, 24, 36):
        features = [4, 8, 12, 16, 1]
        weights = [0.1, 0.2, 0.3, 0.4, target-12]
        frames.append({'target':target, 'features':features, 'weights':weights,
          'curve':[{'inventory':i, **{m:round(action(m,i,[target] if m in ('None','Base') else weights,features),8)
             for m in ('None','Base','Coeff','Both')}} for i in range(0,49,2)]})
    # 値が1の定数特徴を使い、指定した非負の発注量 q を返す出力を求める。
    cases = []
    for inv in range(0,51,5):
        for q in (0, 1, 7, 23, 50):
            outputs = {'None':[q], 'Base':[q+inv], 'Coeff':[0,0,0,0,q], 'Both':[0,0,0,0,q+inv]}
            errors = [abs(action(m,inv,out,[4,8,12,16,1])-q) for m,out in outputs.items()]
            cases.append(max(errors))
    assert max(cases) == 0
    assert all(r['Base']==r['Both'] for f in frames for r in f['curve'])
    # Table 1の値はDDPG Bothとの差で、各方式の絶対値ではない。
    names=['DDPG None','DDPG Base','DDPG Coeff','DDPG Both','DS None','DS Base','DS Coeff','DS Both']
    sr=[10.10,6.03,4.41,0,2.10,2.18,1.74,1.91]
    tt=[6.13,6.46,-0.41,0,-1.25,-2.81,3.80,0.23]
    result={'lab01':'deepstock','note':'Labは発注量を求める4つの式だけを検証した。Table 1・2と導入時の数値は論文の著者報告に基づく。4月の欠品率は差を判別できず、0ではなく null として記録した。',
       'checks':{'status':'CONFIRMED','arbitrary_action_cases':len(cases),'max_inverse_error':max(cases),'base_both_equal':True},
       'frames':frames, 'offline':[{'method':n,'sr_pp':s,'tt_days':t} for n,s,t in zip(names,sr,tt)],
       'deployment':[{'name':'2024年7月：選んだ海外商品10%の差の差分析','sr_pp':None,
                      'sr_reported_percent':-0.83,'sr_status':'reported_as_percent','tt_days':-9.53},
          {'name':'2025年4月：海外商品で旧方式の試算と比較','sr_pp':None,
           'sr_reported_percent':None,'sr_status':'no_distinguishable_difference','tt_days':-1},
          {'name':'2025年4月：国内商品で旧方式の試算と比較','sr_pp':None,
           'sr_reported_percent':None,'sr_status':'no_distinguishable_difference','tt_days':-2}],
       'turnover_by_class':{'classes':['A+','A','B','C','D','Z'],'international':[-1.36,-0.82,-1.02,-1.27,None,None],'domestic':[-4.04,-3.81,-2.93,-2.23,-2.13,-0.64]},
       'verification':{'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'}}
    Path(__file__).with_name('results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result['checks']))

if __name__ == '__main__':
    main()
