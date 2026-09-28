"""Standalone deterministic teaching experiment; standard library only."""
import math

def utility(item, cycle, dispatch):
    # One depot, one destination, capacity 10. Costs are invented teaching units/day.
    demand,value,weight={'A':(8,5,1.5),'B':(7,5,0.5)}[item]
    load=demand*weight*cycle
    vehicles=math.ceil(load/10)
    route=vehicles*dispatch/cycle
    holding=0.2*demand*(cycle-1)/2
    uncovered=2*(15-demand)
    u=demand*value-uncovered-route-holding
    return dict(item=item,cycle=cycle,load=load,vehicles=vehicles,route_cost=route,holding=holding,utility=round(u,6))

def experiment():
    frames=[]
    for cost in [0,2,10,30]:
        plans=[utility(a,t,cost) for a in ['A','B'] for t in [1,2,3,4]]
        # Decomposed baseline selects largest demand, then optimizes its cycle.
        base=max((p for p in plans if p['item']=='A'),key=lambda p:p['utility'])
        best=max(plans,key=lambda p:p['utility'])
        frames.append(dict(label=f'配車費用 {cost}/台',dispatch=cost,plans=plans,baseline=base,proposed=best))
    return dict(lab28='scope',frames=frames)

if __name__ == '__main__':
    import json
    from pathlib import Path
    result=experiment()
    result['note']='教育用の人工例。原論文の学習・性能・本番効果は再現していない。'
    result['verification']={'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'}
    Path(__file__).with_name('results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))
