"""式(9)・(15)・(20)を1商品の線形な例で計算する。FBSDEは学習しない。"""
import json
from pathlib import Path


def frame(capacity):
    x, pipeline, demand, tau, gamma, nominal = 7., 4., 1., 2., .5, 4.
    hx = capacity - x
    h1 = demand - pipeline / tau + gamma * hx
    transit_cap = pipeline / tau + gamma * (6 - pipeline)
    onhand_cap = pipeline / tau - gamma * pipeline + gamma * tau * demand + gamma * tau * h1
    upper = min(transit_cap, onhand_cap)
    feasible = upper >= 0
    order = min(nominal, upper) if feasible else None
    # この線形な例では h1dot + gamma*h1 = (onhand_cap-u)/tau となる。
    residual = (onhand_cap - order) / tau if feasible else None
    return dict(label=f'{capacity:g}', capacity=capacity, x=x, pipeline=pipeline,
                h=hx, h1=h1, transit_upper=transit_cap, onhand_upper=onhand_cap,
                nominal=nominal, order=order, residual=residual,
                augmented_initial_safe=hx >= 0 and h1 >= 0, feasible=feasible)


def main():
    frames = [frame(h) for h in [6, 8, 10, 14]]
    assert frames[2]['order'] == 1.5 and frames[2]['residual'] == 0
    assert not frames[1]['augmented_initial_safe'] and frames[1]['h'] > 0
    assert not frames[0]['feasible']
    # 発注率を変えると輸送中の在庫は1回目、手元在庫は2回目の微分に変化が出る。
    du, tau = .01, 2
    derivative_check = {'d_dLdot_du': du / du, 'd_dXdot_du': 0., 'd_dXddot_du': (du/tau)/du}
    result = {'lab30_fbsde': True, 'seed': None, 'scope': '雑音がなく、入荷率を輸送中在庫に比例させた1商品の例。学習、確率的な経路で上限を守れるか、実験の性能は検証しない。',
              'frames': frames, 'derivative_check': derivative_check,
              'paper_reported': {'source': '表II・IIIの50商品・乱数の初期値8種類の結果。Labでは再現していない。', 'M': 50,
                'fill_rate': .562, 'fill_rate_sd': .031, 'onhand_violation': .815, 'onhand_M1': .050,
                'onhand_M3': .083, 'onhand_utilization': 1.02, 'emission_onhand_violation': .077},
              'verification': {'mechanism': 'PARTIAL', 'performance': 'NOT TESTED', 'scaling': 'NOT TESTED', 'production_applicability': 'NOT TESTED'}}
    Path(__file__).with_name('results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print('発注率が現れる微分回数、発注の上限、定理の初期条件と制約内の発注率がない場合を確認した。')

if __name__ == '__main__':
    main()
