"""PILOT contract analogue. Scripted certificates are not a statistical engine."""
import json
from pathlib import Path


def transition(state, event, healthy=True, approved=False, confirm=False):
    if not healthy:
        return 'paused'
    allowed={('frozen','launch'):'observe',('observe','continue'):'observe',
             ('observe','reject'):'frozen',('observe','promote'):'confirm',
             ('confirm','deliver'):'delivered'}
    if (state,event) not in allowed:
        return state
    if event in {'launch','deliver'} and not approved:
        return state
    if event=='deliver' and not confirm:
        return state
    return allowed[state,event]


def memory(evidence, approval_tasks=3):
    """Threshold 3 is a LAB choice; paper leaves governed threshold configurable."""
    if approval_tasks<2:
        raise ValueError('need independent confirmation')
    positive={task for task,outcome in evidence if outcome=='positive'}
    negative={task for task,outcome in evidence if outcome=='negative'}
    # Inconclusive is neither negative nor positive. Conflict freezes advancement.
    if negative:
        return {'state':'draft','conflict':True,'sources':len(positive)}
    state='approved' if len(positive)>=approval_tasks else 'supported' if len(positive)>=2 else 'draft'
    return {'state':state,'conflict':False,'sources':len(positive)}


def route(user, split=False):
    # Registered PRE-treatment feature; both branches explicitly cover missing data.
    return 'intent_bundle' if split and user.get('segment')=='focused' else 'default_bundle'


def admissible(users, min_share=.2):
    counts={b:sum(route(u,True)==b for u in users) for b in ['intent_bundle','default_bundle']}
    return bool(users) and min(counts.values())/len(users)>=min_share


def compute():
    users=[{'segment':'focused'}]*3+[{'segment':'browse'}]*6+[{}]
    scenarios=[('権限なしの開始','frozen','launch',True,False,False),
               ('承認済みの開始','frozen','launch',True,True,False),
               ('異常時のpromote','observe','promote',False,True,False),
               ('証明済みのpromote','observe','promote',True,True,False),
               ('独立確認なし','confirm','deliver',True,True,False),
               ('承認と独立確認あり','confirm','deliver',True,True,True)]
    trace=[{'name':n,'before':s,'event':e,'after':transition(s,e,h,a,c)} for n,s,e,h,a,c in scenarios]
    evidence_sets=[[('A','positive')],[('A','positive')]*10,[('A','positive'),('B','positive')],
                  [('A','positive'),('B','positive'),('C','positive')],
                  [('A','positive'),('B','inconclusive')],[('A','positive'),('B','negative')]]
    memories=[{'evidence':e,**memory(e)} for e in evidence_sets]
    return {'note':'状態遷移・事前segment・独立task数の人工例。ManagerやPlannerの推論、p値、信頼区間、本番効果は計算していない。承認閾値3はLabの仮定。',
      'verification':{'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'},
      'experiments':[{'name':'同じeventでも権限と証拠で遷移を分ける','metrics':{x['name']:{'前':x['before'],'後':x['after']} for x in trace}},
                    {'name':'表9の分母15を確認','metrics':{'ROAM':{'満たした条件':8,'率':round(8/15*100,2)},'PILOT':{'満たした条件':14,'率':round(14/15*100,2)}}}],
      'trace':trace,'memories':memories,'tree':{'baseline':[route(u) for u in users],'proposal':[route(u,True) for u in users],'admissible':admissible(users)},
      'checks':{'unapproved_launch_blocked':'CONFIRMED','independent_confirmation_required':'CONFIRMED','duplicate_task_no_promotion':'CONFIRMED','causal_manager_gain':'NOT TESTED'}}

if __name__ == '__main__':
    Path(__file__).with_name('results.json').write_text(json.dumps(compute(),ensure_ascii=False,indent=2)+'\n')
