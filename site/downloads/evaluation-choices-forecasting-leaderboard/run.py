"""Standalone deterministic teaching experiment; standard library only."""
def score(actual, prediction, groups):
    error=sum(abs(sum(prediction[i]-actual[i] for i in g)) for g in groups)
    return 100*error/sum(actual)

def experiment():
    actual=[100,100,100,100]
    # A has offsetting errors; B has smaller errors of the same sign.
    predictions={'A':[140,60,140,60],'B':[110,110,110,110]}
    frames=[]
    for label,groups in [('全体を1系列',[[0,1,2,3]]),('相殺する2組',[[0,1],[2,3]]),('同方向の2組',[[0,2],[1,3]]),('4系列を個別評価',[[0],[1],[2],[3]])]:
        values={name:score(actual,pred,groups) for name,pred in predictions.items()}
        frames.append(dict(label=label,groups=groups,scores=values,winner=min(values,key=values.get)))
    return dict(lab28='evaluation',actual=actual,predictions=predictions,frames=frames,gap_closed_from_rounded_table6=(.946-.724)/(.946-.540)*100)

if __name__ == '__main__':
    import json
    from pathlib import Path
    result=experiment()
    result['note']='教育用の人工例。原論文の学習・性能・本番効果は再現していない。'
    result['verification']={'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'}
    Path(__file__).with_name('results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))
