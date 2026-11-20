"""Forecast accuracy versus cost: paper Table 1 and a separate toy experiment."""
from paper_lab.retailbench30 import panel
from paper_lab.batch28 import table


def widget(result):
    if not isinstance(result, dict) or not result.get('lab01_forecast'):
        return ''
    rows = result['reported']
    frames = []
    for metric, idx, maximum in [('平均絶対誤差（MAE、個/日）', 1, .6), ('総費用（論文内の費用単位）', 2, 900000)]:
        bars = ''
        for i, r in enumerate(sorted(rows, key=lambda r:r[idx])):
            y = 35 + i*39
            color = '#247c73' if r[0] == 'Croston' else '#42679c'
            bars += f'<text x="2" y="{y+16}" font-size="14">{r[0]}</text><rect x="130" y="{y}" width="{r[idx]/maximum*295:.1f}" height="23" fill="{color}"/><text x="{140+r[idx]/maximum*295:.1f}" y="{y+16}" font-size="14">{r[idx]:,.2f}</text>'
        frames.append(f'<svg viewBox="0 0 570 320" role="img" aria-label="{metric}が小さい順"><title>{metric}は小さいほど良い</title>{bars}</svg>'+table(['モデル','平均絶対誤差（個/日）','総費用（論文内の費用単位）'],[[r[0],r[1],f'{r[2]:,}'] for r in sorted(rows,key=lambda r:r[idx])]))
    frames = [f.replace('aria-label="人工実験の比較"', 'aria-label="著者報告の比較"') for f in frames]
    out = panel('原論文の結果：予測誤差と費用でモデルを並べ替える','並べ替える指標',['MAE','総費用'],frames,'著者の報告値（v2 Table 1 / Figure 5）。MAEは条件ごとの値の平均、費用は全条件の合計で、軸は別です。表示は丸められており、同じ値のモデル同士に順位は付けません。')
    frames = []
    for f in result['frames']:
        rows = f['rows']
        frames.append(table(['説明用モデル','平均絶対誤差（個/日）','保管費（教材の費用単位）','欠品個数','総費用（教材の費用単位）','充足率'],[[r['model'],f"{r['mae']:.3f}",r['holding'],r['lost'],r['cost'],f"{r['fill_rate']*100:.0f}%"] for r in rows]).replace('<table>', '<table style="min-width:560px">')+f'<p>総費用 = 保管費 + {f["penalty"]} × 欠品個数。予測と需要は同じまま、欠品1個の費用だけを変えます。</p>')
    out += panel('Labの実験：欠品1個の費用でどちらが安いかを比べる','欠品1個当たりの費用（教材の費用単位）',[str(f['penalty']) for f in result['frames']],frames,'run.pyで行った別の人工実験です。Zeroは毎日0個と予測する比較対象で、XGBoostの代わりではありません。原論文の費用計算や7モデルは再現していません。')
    return out
