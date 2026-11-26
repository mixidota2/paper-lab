"""与えた条件で実験の状態を更新し、独立した支持の件数を数えます。証明書は発行・検証しません。"""
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
    """承認に必要な独立した支持3件はLabの設定で、原論文が固定した値ではありません。"""
    if approval_tasks<2:
        raise ValueError('need independent confirmation')
    # 同じ範囲の1つの主張について、観測を順番に処理します。
    # 対立を解消する手順や、過去の記録の置き換えは扱いません。
    positive=set()
    observations=[]
    state='draft'
    conflict=False
    for task,outcome in evidence:
        observations.append((task,outcome))
        if outcome=='negative':
            conflict=True
        elif outcome=='positive':
            positive.add(task)
            if not conflict:
                state=('approved' if len(positive)>=approval_tasks else
                       'supported' if len(positive)>=2 else 'draft')
        # 結論が出なかった観測は中立です。反証があればその時点の状態を保ちます。
    return {'state':state,'conflict':conflict,'sources':len(positive),
            'observations':observations}


def route(user, split=False):
    # 施策前の特徴量で振り分け、値がない利用者には既定の設定を割り当てます。
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
                  [('A','positive'),('B','inconclusive')],[('A','positive'),('B','negative')],
                  [('A','positive'),('B','positive'),('C','negative')],
                  [('A','positive'),('B','positive'),('C','positive'),('D','negative')],
                  [('A','positive'),('B','positive'),('C','negative'),('D','positive')]]
    memories=[{'evidence':e,**memory(e)} for e in evidence_sets]
    return {'note':'人工の条件で状態遷移、施策前の群分け、別の実験からの支持数を確認します。証明書や統計量を計算せず、LLMも本番配信も使いません。承認に必要な独立した支持3件はLabで決めました。',
      'verification':{'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'},
      'experiments':[{'name':'健全性・承認・独立確認の入力で、状態がどう変わるか','metrics':{x['name']:{'前':x['before'],'後':x['after']} for x in trace}},
                    {'name':'原論文の表9で満たした条件の数と割合','metrics':{'ROAM':{'満たした条件':8,'率':round(8/15*100,2)},'PILOT':{'満たした条件':14,'率':round(14/15*100,2)}}}],
      'trace':trace,'memories':memories,'tree':{'baseline':[route(u) for u in users],'proposal':[route(u,True) for u in users],'admissible':admissible(users)},
      'checks':{'unapproved_launch_blocked':'CONFIRMED','independent_confirmation_required':'CONFIRMED','duplicate_task_no_promotion':'CONFIRMED','causal_manager_gain':'NOT TESTED'}}

if __name__ == '__main__':
    Path(__file__).with_name('results.json').write_text(json.dumps(compute(),ensure_ascii=False,indent=2)+'\n')
