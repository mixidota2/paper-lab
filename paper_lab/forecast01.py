"""Forecast accuracy versus cost: paper Table 1 and a separate toy experiment."""
from paper_lab.retailbench30 import panel
from paper_lab.batch28 import table


def widget(result):
    if not isinstance(result, dict) or not result.get('lab01_forecast'):
        return ''
    rows = result['reported']
    frames = []
    for metric, idx, maximum in [('MAE（個/日）', 1, .6), ('総費用（論文内の費用単位）', 2, 900000)]:
        bars = ''
        for i, r in enumerate(sorted(rows, key=lambda r:r[idx])):
            y = 35 + i*39
            color = '#247c73' if r[0] == 'Croston' else '#42679c'
            bars += f'<text x="2" y="{y+16}" font-size="14">{r[0]}</text><rect x="130" y="{y}" width="{r[idx]/maximum*295:.1f}" height="23" fill="{color}"/><text x="{140+r[idx]/maximum*295:.1f}" y="{y+16}" font-size="14">{r[idx]:,.2f}</text>'
        frames.append(f'<svg viewBox="0 0 570 320" role="img" aria-label="{metric}の昇順"><title>{metric}は小さいほど良い</title>{bars}</svg>'+table(['モデル','MAE','総費用'],[[r[0],r[1],f'{r[2]:,}'] for r in sorted(rows,key=lambda r:r[idx])]))
    frames = [f.replace('aria-label="人工実験の比較"', 'aria-label="著者報告の比較"') for f in frames]
    out = panel('指標を変えると、モデルの順番が変わる','並べ替える指標',['MAE','総費用'],frames,'著者報告：v2 Table 1 / Figure 5。丸め値を転記。MAEはシナリオ平均、費用は全シナリオ合計。異なる集計量を同じ軸に混ぜない。同値から細かな順位は決めない。')
    frames = []
    for f in result['frames']:
        rows = f['rows']
        frames.append(table(['説明用モデル','MAE','保管費','欠品個数','総費用','充足率'],[[r['model'],f"{r['mae']:.3f}",r['holding'],r['lost'],r['cost'],f"{r['fill_rate']*100:.0f}%"] for r in rows]).replace('<table>', '<table style="min-width:560px">')+f'<p>総費用 = 保管費 + {f["penalty"]} × 欠品個数。予測と需要は固定し、欠品単価だけを変える。</p>')
    out += panel('同じ予測でも、欠品単価で費用の優劣が変わる','欠品単価',[str(f['penalty']) for f in result['frames']],frames,'run.pyの独立した人工実験。ZeroはXGBoostの代理ではない。原論文の費用シミュレータや7モデルの再現ではない。')
    return out
