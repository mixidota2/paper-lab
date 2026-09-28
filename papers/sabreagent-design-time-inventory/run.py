"""Finite artificial paths; no fitted SabreAgent, LLM, or benchmark data."""
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
    # Independent stationary demand. Zero purchase/setup/salvage; instant supply.
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
        y = max(stock, 4)  # 0.8 quantile
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
        frames.append(dict(label=f'初期在庫 {initial}', initial=initial, rows=rows,
                           textbook=textbook, projected=projected, lost=lost,
                           textbook_order=max(0,textbook), projected_order=max(0,projected)))
    curve = [dict(ip=ip, base=max(12-ip,0), capped=capped(ip,4,3,1)) for ip in range(17)]
    return dict(lab29='sabre', frames=frames, cap_curve=curve, stationary_dp=dp_check(),
                verification=dict(mechanism='PARTIAL',performance='NOT TESTED',scaling='NOT TESTED',production_applicability='NOT TESTED'),
                checks={'pathwise_shortfall_identity':'CONFIRMED','stationary_myopic_finite_case':'CONFIRMED'},
                note='人工例。式(3)のκ付き探索、季節学習、確率的納期のrolloutは未実装。')

if __name__ == '__main__':
    Path(__file__).with_name('results.json').write_text(json.dumps(experiment(),ensure_ascii=False,indent=2)+'\n')
