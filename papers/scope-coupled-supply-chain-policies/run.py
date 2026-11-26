"""1拠点に配送する人工例を計算する。Pythonの標準ライブラリだけを使う。"""
import math

def utility(item, cycle, dispatch):
    # 供給元と配送先は1つずつで、車両の容量は10。費用は人工例の1日あたりの値を求めるために設定した。
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
        # 比較方式は需要が多いAを先に選び、その中で評価値が最大となる補充間隔を探す。
        base=max((p for p in plans if p['item']=='A'),key=lambda p:p['utility'])
        best=max(plans,key=lambda p:p['utility'])
        frames.append(dict(label=f'{cost}',dispatch=cost,plans=plans,baseline=base,proposed=best))
    return dict(lab28='scope',frames=frames)

if __name__ == '__main__':
    import json
    from pathlib import Path
    result=experiment()
    result['note']='品揃えと補充間隔を比べる人工例。道路経路は計算せず、著者の学習や性能評価、現場での効果は再現していない。'
    result['verification']={'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'}
    Path(__file__).with_name('results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))
