"""Standalone deterministic teaching experiment; standard library only."""
import math

def collect(proposal, decision, replacement=None):
    if decision not in ('PASS','REPLACE'): raise ValueError(decision)
    if decision=='REPLACE' and replacement is None: raise ValueError('replacement required')
    # Private reviewer messages and rejected proposals do not enter training targets.
    accepted=proposal if decision=='PASS' else replacement
    return dict(executed=accepted,student_visible=[accepted],training_targets=[accepted])

def nll(probability):
    if not 0<probability<=1: raise ValueError('probability')
    return -math.log(probability)

def experiment():
    frames=[]
    for label,proposal,decision,replacement in [
        ('PASS：確認済みの読取','read cell A1','PASS',None),
        ('REPLACE：上書き前に退避','overwrite workbook','REPLACE','backup workbook then edit cell A1'),
        ('REPLACE：結果を確認','finish','REPLACE','reload workbook and check cell A1')]:
        trace=collect(proposal,decision,replacement)
        frames.append(dict(label=label,proposal=proposal,decision=decision,**trace))
    return dict(lab28='harness',frames=frames,nll_illustration={'p_0.2':nll(.2),'p_0.8':nll(.8)},checks={'rejected_excluded':'overwrite workbook' not in frames[1]['training_targets']})

if __name__ == '__main__':
    import json
    from pathlib import Path
    result=experiment()
    result['note']='教育用の人工例。原論文の学習・性能・本番効果は再現していない。'
    result['verification']={'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'}
    Path(__file__).with_name('results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))
