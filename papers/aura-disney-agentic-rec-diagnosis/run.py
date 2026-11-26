"""人工の分類を選び、診断の参照先を確かめる合成例。LLMには問い合わせない。"""
import json
from pathlib import Path


def select(rows,mode):
    total=sum(r['count'] for r in rows)
    top={r['name'] for r in sorted(rows,key=lambda r:-r['count'])[:2]}
    return [r['name'] for r in rows if r['count']/total>=.05 or
            (mode=='combined' and (r['name'] in top or r['count']>=100 or r['safety']))]


def validate(finding,session_ids,paths):
    errors=[]
    if not set(finding['sessions'])<=session_ids:errors.append('unknown_session')
    if finding['path'] not in paths:errors.append('unknown_path')
    if not finding['sessions']:errors.append('missing_evidence')
    return errors


def main():
    rows=[{'name':n,'count':c,'safety':s} for n,c,s in
          [('genre',4700,False),('popularity',4000,False),('format',110,False),('age',10,True),('other',1180,False)]]
    baseline=select(rows,'percentage');combined=select(rows,'combined')
    good={'sessions':['s1'],'path':'ranker.py'}
    mutations=[good,{**good,'sessions':['invented']},{**good,'path':'phantom.py'},{**good,'sessions':[]}]
    checks=[validate(x,{'s1','s2'},{'ranker.py'}) for x in mutations]
    assert checks[0]==[] and all(checks[1:])
    assert 'age' not in baseline and 'age' in combined
    # 正の差を使うLabの保留例。AURAの正式な採用基準ではない。
    deltas=[.0003,.0006,.0001];noise=.001
    decision='hold' if max(deltas)<=noise else 'review'
    assert decision=='hold'
    out={'note':'Labは人工の分類を選び、参照先を入力と照合しました。診断の精度、原因の推定、LLMによる採点は試していません。',
      'scope':{'reference_rejection':'CONFIRMED','mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'},
      'categories':rows,'retained':{'percentage_only':baseline,'combined':combined},'validation_errors':checks,'decision':decision,
      'experiments':[{'name':'件数が少ない分類を残し、入力にない参照を退ける','metrics':{'retained_categories':{'baseline':len(baseline),'combined':len(combined)},'invalid_findings_rejected':{'count':3},'noise_gate':{'decision':decision}}}]}
    Path(__file__).with_name('results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');return out
if __name__=='__main__':main()
