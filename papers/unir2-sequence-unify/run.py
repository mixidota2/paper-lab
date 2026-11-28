"""CPUで参照範囲と勾配を試す人工例。Transformerや本番システムは再現しない。実行にはuvを使う。"""
import json
import math
from pathlib import Path


def visibility():
    keys = ['history-1', 'history-2', 'profile', 'BOS', 'q1', 'q2', 'q3', 'item-1', 'item-2']
    rows = []
    for pos in range(3, 7):
        rows.append({'query': keys[pos], 'allowed': [j <= pos for j in range(len(keys))]})
    for pos in (7, 8):
        rows.append({'query': keys[pos], 'allowed': [j >= 2 for j in range(len(keys))]})
    # 読めない位置の値を変えても、候補生成が読む位置の集計は変わらないことを確かめる。
    values = list(range(len(keys)))
    for pos, row in enumerate(rows[:4], 3):
        original = sum(v for v, ok in zip(values, row['allowed']) if ok)
        changed = [v if j <= pos else 10000 for j, v in enumerate(values)]
        assert original == sum(v for v, ok in zip(changed, row['allowed']) if ok)
    assert not any(rows[-1]['allowed'][:2]) and all(rows[-1]['allowed'][2:])
    return {'keys': keys, 'rows': rows}


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def ce(logit, target):
    return math.log1p(math.exp(logit)) - target * logit


def seesaw(isolate, steps=200, rate=0.1):
    # 候補生成だけで学習した状態から始める。次の記号を当てる確率の目標は0.8。
    base, adapter = math.log(4), 0.0
    trace = []
    for step in range(steps + 1):
        if step % 20 == 0:
            trace.append({'step': step, 'base': base, 'adapter': adapter,
                          'ntp_ce': ce(base, 0.8), 'ranking_bce': ce(base + adapter, 0.2)})
        if step == steps:
            break
        generation_grad = sigmoid(base) - 0.8
        ranking_grad = sigmoid(base + adapter) - 0.2
        # どちらも順位付け用の調整値は1個。順位付けの誤差を共有の重みに伝えるかだけを変える。
        base -= rate * (generation_grad + (0 if isolate else ranking_grad))
        adapter -= rate * ranking_grad
    return trace


def stable_trace(rows):
    # 公開データの末尾が実行環境で変わらないよう、記録だけ小数点以下10桁にそろえる。
    # 勾配の計算と比較には、丸める前の値を使う。
    return [{key: value if key == 'step' else round(value, 10)
             for key, value in row.items()} for row in rows]


def main():
    coupled, isolated = seesaw(False), seesaw(True)
    assert coupled[-1]['ntp_ce'] > coupled[0]['ntp_ce']
    assert coupled[-1]['ranking_bce'] < coupled[0]['ranking_bce']
    assert isolated[-1]['ntp_ce'] == isolated[0]['ntp_ce']
    assert isolated[-1]['ranking_bce'] < isolated[0]['ranking_bce']
    result = {'note': '人工例では、順位付け専用の調整値を1個置く。実際のLoRAは実装せず、論文の精度や本番での利用も試していない（NOT TESTED）。',
              'parameters': {'ntp_target': 0.8, 'rank_target': 0.2, 'steps': 200, 'learning_rate': 0.1},
              'mask': visibility(), 'traces': {'coupled': stable_trace(coupled), 'isolated': stable_trace(isolated)},
              'experiments': [{'name': '調整値の数をそろえ、順位付けの勾配を共有の重みに伝えるかだけを変える',
                              'metrics': {name: {k: round(row[k], 6) for k in ('ntp_ce', 'ranking_bce')}
                                          for name, row in [('initial', coupled[0]), ('coupled', coupled[-1]), ('isolated', isolated[-1])]}}]}
    Path(__file__).with_name('results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
