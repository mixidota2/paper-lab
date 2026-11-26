"""同じ予測を使い、補充量の候補を変えると平均費用がどう変わるかを計算します。"""
import json, random
from pathlib import Path


def loss(action,demand): return abs(action-demand)


def experiment(actions):
    rng=random.Random(20261008)
    demand=[rng.choice([4,8,12]) for _ in range(600)]
    forecast={'historical':[8]*600,'improved':[d+rng.choice([-1,0,1]) for d in demand],'oracle':demand}
    rows={}
    for name,pred in forecast.items():
        chosen=[min(actions,key=lambda a:loss(a,p)) for p in pred]
        rows[name]={'mae':sum(abs(d-p) for d,p in zip(demand,pred))/600,'decision_loss':sum(loss(a,d) for a,d in zip(chosen,demand))/600,'actions_used':sorted(set(chosen))}
    base=rows['historical']['decision_loss']
    for row in rows.values(): row['value_percent']=100*(base-row['decision_loss'])/base
    return rows


PAPER = {'source': 'Table 2–3 / Fig.4, v1', 'coverage': [90.72, 75.66], 'effective_actions': [1, 1, 1, 1, 1, 1, 1, 8, 8], 'effects': [['予測あり：待ち行列', -6.09, -12.94, 1.15], ['将来の流入あり：待ち行列', -3.39, -7.24, 3.08], ['将来の流入あり：上流への滞留', 3.78, -1.25, 12.26]]}


def main():
    cases={'one':experiment([8]),'several':experiment([4,8,12]),'irrelevant':experiment([0,1,2])}
    assert cases['one']['improved']['mae']<cases['one']['historical']['mae']
    assert cases['one']['oracle']['value_percent']==0
    assert cases['several']['oracle']['value_percent']>0
    assert cases['irrelevant']['oracle']['value_percent']==0
    result={'lab_kind':'traffic08','note':'1期間の人工例です。補充の不足と余りを同じ重みで数えます。交通の信号制御や、実店舗で生じる費用は再現していません。','cases':cases,'experiments':[{'name':name,'metrics':rows} for name,rows in cases.items()]}
    result['paper'] = PAPER
    (Path(__file__).parent/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(cases)

if __name__=='__main__': main()
