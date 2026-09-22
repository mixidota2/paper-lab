"""AURA-inspired deterministic retention and evidence checks, no LLM diagnosis."""
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
    # Illustrative gate, not an official AURA numerical promotion threshold.
    deltas=[.0003,.0006,.0001];noise=.001
    decision='hold' if max(deltas)<=noise else 'review'
    assert decision=='hold'
    out={'note':'人工カテゴリと参照検証のみ。診断精度・因果的な原因推定・LLM rubric採点は未実行。',
      'scope':{'reference_rejection':'CONFIRMED','mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'},
      'categories':rows,'retained':{'percentage_only':baseline,'combined':combined},'validation_errors':checks,'decision':decision,
      'experiments':[{'name':'低頻度でも残す規則と架空参照の排除','metrics':{'retained_categories':{'baseline':len(baseline),'combined':len(combined)},'invalid_findings_rejected':{'count':3},'noise_gate':{'decision':decision}}}]}
    Path(__file__).with_name('results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');return out
if __name__=='__main__':main()
