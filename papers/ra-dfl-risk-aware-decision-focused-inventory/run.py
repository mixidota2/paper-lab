"""2チャネルの整数配分と、移送がない場合の欠品補正を計算する。

RA-DFLの学習、需要の補完、連続配分の勾配計算は行わない。
"""
import json
from pathlib import Path


def cost(q, d, rho=.4, h=1, b=6, tau=1):
    surplus = sum(max(a-z, 0) for a, z in zip(q, d))
    shortage = sum(max(z-a, 0) for a, z in zip(q, d))
    # この例では h と b はチャネルによらず一定で、tau < h+b なので、移せる量はすべて移すと安い。
    moved = min(surplus, rho*shortage)
    return h*surplus + b*shortage - (h+b-tau)*moved


def cvar(values, alpha=.8):
    # 各費用が同じ確率で出る場合に使う。境界の費用が同じ場合にも式は成り立つ。
    return min(eta + sum(max(v-eta, 0) for v in values)/len(values)/(1-alpha)
               for eta in values)


def evaluate(q, scenarios):
    values = [cost(q, d) for d in scenarios]
    return dict(mean=sum(values)/len(values), tail=cvar(values))


def main():
    scenarios = [(2, 3)]*6 + [(8, 2)]*2 + [(2, 10)]*2
    cases = []
    for weight in [0, .25, .5, .75, 1]:
        candidates = []
        for a in range(11):
            for b in range(11-a):
                metrics = evaluate((a, b), scenarios)
                objective = (1-weight)*metrics['mean'] + weight*metrics['tail']
                candidates.append(dict(q=[a, b], objective=objective, **metrics))
        best = min(candidates, key=lambda c: (c['objective'], c['mean'], c['q']))
        cases.append(dict(weight=weight, best=best, candidates=candidates))
    checks = 0
    curves = []
    # 移送なし（rho=0）に限り、選んだ全組の y<=D に対して補正後の損失が真の費用以下か調べる。
    for d in range(13):
        for y in range(d+1):
            for q in range(16):
                masked = 6*max(y-q, 0)
                true = max(q-d, 0)+6*max(d-q, 0)
                assert masked <= true
                checks += 1
    for q in range(16):
        curves.append(dict(q=q, naive=max(q-4, 0)+6*max(4-q, 0),
                           masked=6*max(4-q, 0), true=max(q-10, 0)+6*max(10-q, 0)))
    assert abs(cvar([1, 2, 3, 4, 5], .8)-5) < 1e-9
    result = dict(lab02='radfl', note='人工の2チャネルで、容量内の整数配分をすべて比較した。RA-DFLの学習や平均費用の悪化は再現していない。欠品補正は移送なしに限る。',
                  cases=cases, censoring=curves,
                  paper_evidence={'m5': {'LightGBM-QR PTO': [4.903, 13.70], 'PTO + CVaR': [5.380, 14.36],
                    'DFL-EV': [4.690, 14.11], 'RA-DFL': [4.721, 13.67]},
                    'censoring': {'M5': {'proxy_rate': 12.3, 'full': 4.721, 'without_mask': 4.776, 'p': .003},
                                  'Stallion': {'proxy_rate_table1': 1.3, 'proxy_rate_section58': 1.4, 'p': .25}}},
                  experiments=[dict(name='整数配分と欠品補正の人工例', metrics={
                      '容量': 10, '各リスク重みの候補数': 66, '補正後の損失が真の費用以下か調べた件数': checks,
                      '平均費用だけで選んだ配分': cases[0]['best']['q'], '高い方20%の平均費用だけで選んだ配分': cases[-1]['best']['q']})])
    Path(__file__).with_name('results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')


if __name__ == '__main__':
    main()
