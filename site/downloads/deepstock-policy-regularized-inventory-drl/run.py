"""Deterministic action-remapping checks; no DRL training or private Tmall data."""
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
    # Construct outputs to represent arbitrary nonnegative q. Bias feature = 1.
    cases = []
    for inv in range(0,51,5):
        for q in (0, 1, 7, 23, 50):
            outputs = {'None':[q], 'Base':[q+inv], 'Coeff':[0,0,0,0,q], 'Both':[0,0,0,0,q+inv]}
            errors = [abs(action(m,inv,out,[4,8,12,16,1])-q) for m,out in outputs.items()]
            cases.append(max(errors))
    assert max(cases) == 0
    assert all(r['Base']==r['Both'] for f in frames for r in f['curve'])
    # Table 1 reports differences relative to DDPG Both, not absolute levels.
    names=['DDPG None','DDPG Base','DDPG Coeff','DDPG Both','DS None','DS Base','DS Coeff','DS Both']
    sr=[10.10,6.03,4.41,0,2.10,2.18,1.74,1.91]
    tt=[6.13,6.46,-0.41,0,-1.25,-2.81,3.80,0.23]
    result={'lab01':'deepstock','note':'式の再写像のみを検証。Table 1・2と実運用の数値は著者報告の転記で、再現実験ではない。',
       'checks':{'status':'CONFIRMED','arbitrary_action_cases':len(cases),'max_inverse_error':max(cases),'base_both_equal':True},
       'frames':frames, 'offline':[{'method':n,'sr_pp':s,'tt_days':t} for n,s,t in zip(names,sr,tt)],
       'deployment':[{'name':'2024年7月 DiD・選抜10%国際SKU','sr_pp':-0.83,'tt_days':-9.53},
          {'name':'2025年4月 反実仮想・国際SKU','sr_pp':0,'tt_days':-1},
          {'name':'2025年4月 反実仮想・国内SKU','sr_pp':0,'tt_days':-2}],
       'turnover_by_class':{'classes':['A+','A','B','C','D','Z'],'international':[-1.36,-0.82,-1.02,-1.27,None,None],'domestic':[-4.04,-3.81,-2.93,-2.23,-2.13,-0.64]},
       'verification':{'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'}}
    Path(__file__).with_name('results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result['checks']))

if __name__ == '__main__':
    main()
