"""Destination service conservation check, not the official 13-node simulator."""
import json
from pathlib import Path
from statistics import variance


def simulate(capacity):
    # Same exogenous demand in all scenarios; single delayed transport edge.
    demand = [8 + (t % 7 in (4, 5)) * 6 for t in range(84)]
    stock, backlog, transit = 15, 0, 0
    rows = []
    cumulative_arrival = cumulative_service = 0
    for t, d in enumerate(demand):
        arrival = transit
        old_service = min(backlog, arrival)
        backlog -= old_service
        stock += arrival - old_service
        new_service = min(stock, d)
        stock -= new_service
        backlog += d - new_service
        cumulative_arrival += arrival
        cumulative_service += old_service + new_service
        # Explicit teaching surrogate for replenishment: destination (s,S).
        transit = min(capacity, max(0, 30 - stock + backlog)) if stock < 12 else 0
        assert stock == 15 + cumulative_arrival - cumulative_service
        assert backlog == sum(demand[:t+1]) - cumulative_service
        rows.append(dict(day=t+1,demand=d,backlog=backlog,stock=stock,
                         fill=new_service/d,utilization=transit/capacity))
    return dict(label=f'輸送容量 {capacity} / 日',capacity=capacity,rows=rows,
                ending_backlog=backlog,conservation_max_error=0,
                current_demand_fill=sum(r['fill']*r['demand'] for r in rows)/sum(demand))


def main():
    frames = [simulate(c) for c in (8,12,20)]
    assert len({tuple(r['demand'] for r in f['rows']) for f in frames}) == 1
    assert frames[0]['ending_backlog'] > frames[-1]['ending_backlog']
    result = dict(lab30='isomorph',note='人工的な1辺の実験。13拠点の再現、予測モデルの比較、補充方策の性能検証ではない。',
        frames=frames,experiments=[dict(name='同一需要・容量だけを変更',n=84,
        metrics={f['label']:{'期末滞留':f['ending_backlog'],'当日需要充足率':round(f['current_demand_fill'],4),'保存則の最大誤差':0} for f in frames})])
    Path(__file__).with_name('results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')

if __name__ == '__main__': main()
