"""架空の提案から採用した手順だけを残す。Pythonの標準ライブラリだけで動く。"""
import math

def collect(proposal, decision, replacement=None):
    if decision not in ('PASS','REPLACE'): raise ValueError(decision)
    if decision=='REPLACE' and replacement is None: raise ValueError('replacement required')
    # 点検役だけのやりとりや、見送った元の案は学習対象に入れない。
    accepted=proposal if decision=='PASS' else replacement
    return dict(executed=accepted,student_visible=[accepted],training_targets=[accepted])

def nll(probability):
    if not 0<probability<=1: raise ValueError('probability')
    return -math.log(probability)

def experiment():
    frames=[]
    for label,proposal,decision,replacement in [
        ('PASS：セルを読む案をそのまま使う','read cell A1','PASS',None),
        ('REPLACE：上書きより先にバックアップする','overwrite workbook','REPLACE','backup workbook then edit cell A1'),
        ('REPLACE：終える前にセルを読み直す','finish','REPLACE','reload workbook and check cell A1')]:
        trace=collect(proposal,decision,replacement)
        frames.append(dict(label=label,proposal=proposal,decision=decision,**trace))
    return dict(lab28='harness',frames=frames,nll_illustration={'p_0.2':nll(.2),'p_0.8':nll(.8)},checks={'rejected_excluded':'overwrite workbook' not in frames[1]['training_targets']})

if __name__ == '__main__':
    import json
    from pathlib import Path
    result=experiment()
    result['note']='Labは架空の提案から採用案を選びます。元のモデルを学習させたり、性能や本番での効果を測ったりはしていません。'
    result['verification']={'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'}
    Path(__file__).with_name('results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))
