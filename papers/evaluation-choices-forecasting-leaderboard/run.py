"""予測と実績を固定し、買い手の組分けを変えてWAPEを計算します。"""
def score(actual, prediction, groups):
    error=sum(abs(sum(prediction[i]-actual[i] for i in g)) for g in groups)
    return 100*error/sum(actual)

def experiment():
    actual=[100,100,100,100]
    # Aは過大予測と過小予測が交互に並びます。Bは各社を同じ額だけ過大に予測します。
    predictions={'A':[140,60,140,60],'B':[110,110,110,110]}
    frames=[]
    for label,groups in [('4社を1組にする',[[0,1,2,3]]),('過大と過小を同じ組にする',[[0,1],[2,3]]),('過大どうしと過小どうしで分ける',[[0,2],[1,3]]),('4社を1社ずつ評価する',[[0],[1],[2],[3]])]:
        values={name:score(actual,pred,groups) for name,pred in predictions.items()}
        frames.append(dict(label=label,groups=groups,scores=values,winner=min(values,key=values.get)))
    return dict(lab28='evaluation',actual=actual,predictions=predictions,frames=frames,gap_closed_from_rounded_table6=(.946-.724)/(.946-.540)*100)

if __name__ == '__main__':
    import json
    from pathlib import Path
    result=experiment()
    result['note']='4社の人工例です。予測と実績は固定し、組の作り方だけを変えました。論文の予測手法や本番での評価は再現していません。'
    result['verification']={'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'}
    Path(__file__).with_name('results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))
