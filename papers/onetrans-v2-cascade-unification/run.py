"""Standalone deterministic teaching experiment; standard library only."""
import math

CANDIDATES=[dict(item='A',prefix=.6,conditional=.8,offset=0),dict(item='B',prefix=.3,conditional=.7,offset=1),dict(item='C',prefix=.1,conditional=.9,offset=1.5)]

def rank(beta):
    return sorted([dict(c,score=math.log(c['prefix'])+beta*c['offset']+math.log(c['conditional'])) for c in CANDIDATES],key=lambda c:c['score'],reverse=True)

def experiment():
    frames=[dict(label=f'β = {b}',beta=b,ranking=rank(b)) for b in [0,.5,1,2]]
    # Abstract operation units: context encoding 100, stage work 10+20+30.
    return dict(lab28='onetrans',frames=frames,cache_cost={'separate':3*100+10+20+30,'shared':100+10+20+30},checks={'zero_offset_baseline':rank(0)[0]['item']=='A'})

if __name__ == '__main__':
    import json
    from pathlib import Path
    result=experiment()
    result['note']='教育用の人工例。原論文の学習・性能・本番効果は再現していない。'
    result['verification']={'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'}
    Path(__file__).with_name('results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))
