"""人工の入荷と需要で計算する。SabreAgentの学習、言語モデル、ベンチマークデータは使わない。"""
import json
from functools import lru_cache
from pathlib import Path


def project(stock, arrivals, demand):
    rows = []
    lost = 0
    for a, d in zip(arrivals, demand):
        sales = min(stock + a, d)
        lost += d - sales
        stock += a - sales
        rows.append(dict(arrival=a, demand=d, sales=sales, ending=stock, lost=d-sales))
    return stock, lost, rows


def capped(ip, rate, theta, cap):
    return min(max(theta * rate - ip, 0), cap * rate)


def dp_check():
    # 各期の需要は独立で同じ分布に従う。仕入れ費用・発注固定費・残存価値は0で、注文は即時に届く。
    support = [(0, .2), (2, .5), (4, .3)]
    @lru_cache(None)
    def value(t, stock):
        if t == 3:
            return 0.
        return max(sum(prob * (4 * min(y, d) - max(y-d, 0) + value(t+1, max(y-d, 0)))
                       for d, prob in support) for y in range(stock, 9))
    @lru_cache(None)
    def myopic(t, stock):
        if t == 3:
            return 0.
        y = max(stock, 4)  # 需要分布の0.8分位点
        return sum(prob * (4*min(y,d)-max(y-d,0)+myopic(t+1,max(y-d,0))) for d,prob in support)
    error = max(abs(value(t,s)-myopic(t,s)) for t in range(3) for s in range(7))
    assert error < 1e-10
    return dict(dp_value=value(0,0), myopic_value=myopic(0,0), max_error=error,
                states=21, action_upper_bound=8)


def experiment():
    frames = []
    for initial in [0, 2, 8]:
        arrivals, demand, target = [0, 4], [5, 2], 3
        stock, lost, rows = project(initial, arrivals, demand)
        textbook = sum(demand) + target - (initial + sum(arrivals))
        projected = target - stock
        assert textbook - projected == lost
        frames.append(dict(label=f'{initial}個', initial=initial, rows=rows,
                           textbook=textbook, projected=projected, lost=lost,
                           textbook_order=max(0,textbook), projected_order=max(0,projected)))
    curve = [dict(ip=ip, base=max(12-ip,0), capped=capped(ip,4,3,1)) for ip in range(17)]
    return dict(lab29='sabre', frames=frames, cap_curve=curve, stationary_dp=dp_check(),
                verification=dict(mechanism='PARTIAL',performance='NOT TESTED',scaling='NOT TESTED',production_applicability='NOT TESTED'),
                checks={'pathwise_shortfall_identity':'CONFIRMED','stationary_myopic_finite_case':'CONFIRMED'},
                note='Labの人工例。式(3)のκを使う発注、統計予測に季節性を組み合わせる処理、確率的な納期での発注パラメータ探索は行わない。')

if __name__ == '__main__':
    Path(__file__).with_name('results.json').write_text(json.dumps(experiment(),ensure_ascii=False,indent=2)+'\n')
