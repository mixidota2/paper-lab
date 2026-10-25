"""Fail-closed automatic gate, independent of reachability and visual review."""
from collections import Counter
import argparse
import json
from pathlib import Path


def automatic_errors(report, plan):
    errors=[]
    expected=plan.get('required_cases',[])
    if not expected or len(expected)!=len(set(expected)):errors.append('Invalid or missing mandatory case plan')
    for key in ('source_hashes','page_hashes'):
        if report.get('preflight',{}).get(key)!=plan.get(key) or not plan.get(key):errors.append('Missing or stale '+key)
    cases=report.get('cases',[])
    if Counter(c.get('name') for c in cases)!=Counter(expected):errors.append('Mandatory cases missing, duplicated, or unexpected')
    if any(c.get('status')!='PASS' for c in cases):errors.append('Mandatory case not PASS')
    if report.get('execution_completed') is not True or report.get('browser')!='EXECUTED':errors.append('Execution not complete')
    if report.get('interruption') or report.get('events'):errors.append('Mandatory errors or interruption recorded')
    actions=report.get('action_checks',[])
    if any(not a.get('status','').startswith('CONFIRMED:') for a in actions):errors.append('Required semantic assertion not confirmed')
    groups={(a.get('slug'),a.get('width')) for a in actions if a.get('status','').startswith('CONFIRMED:')}
    if not {tuple(g) for g in plan.get('semantic_groups',[])} <= groups:errors.append('Required semantic group missing')
    return errors


def validation(report,plan):
    errors=automatic_errors(report,plan)
    return {'automatic_status':'FAIL' if errors else 'PASS','errors':errors,
        'mandatory_expected':len(plan.get('required_cases',[])),
        'mandatory_recorded':len(report.get('cases',[])),
        'external_reachability':report.get('external_status','NOT TESTED'),
        'manual_screenshot_review':report.get('manual_screenshot_review','NOT TESTED'),
        'publication_decision':'PENDING'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--site',type=Path,required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    try:
        from review_103 import preflight
        # Reconstruct expectations from the checked-out source and full build, not the report's self-description.
        result=validation(json.loads(a.report.read_text()),preflight(a.site.resolve()))
    except Exception as e:
        result={'automatic_status':'FAIL','errors':[f'{type(e).__name__}: {e}'],'publication_decision':'PENDING'}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False))
    if result['automatic_status']!='PASS':raise SystemExit(1)

if __name__=='__main__':main()
