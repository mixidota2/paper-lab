"""標準ライブラリで、候補の得点と履歴の計算回数を人工例から求める。"""
import math

CANDIDATES=[dict(item='A',prefix=.6,conditional=.8,offset=0),dict(item='B',prefix=.3,conditional=.7,offset=1),dict(item='C',prefix=.1,conditional=.9,offset=1.5)]

def rank(beta):
    return sorted([dict(c,score=math.log(c['prefix'])+beta*c['offset']+math.log(c['conditional'])) for c in CANDIDATES],key=lambda c:c['score'],reverse=True)

def experiment():
    frames=[dict(label=f'β = {b}',beta=b,ranking=rank(b)) for b in [0,.5,1,2]]
    # 履歴の計算を100、3段階の計算を10、20、30と仮定する。
    return dict(lab28='onetrans',frames=frames,cache_cost={'separate':3*100+10+20+30,'shared':100+10+20+30},checks={'zero_offset_baseline':rank(0)[0]['item']=='A'})

if __name__ == '__main__':
    import json
    from pathlib import Path
    result=experiment()
    result['note']='教材用の候補と計算量を使いました。論文の学習や配信の速度、実際の利用者への効果は測っていません。'
    result['verification']={'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'}
    Path(__file__).with_name('results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))
