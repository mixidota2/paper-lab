"""Render the DeepStock toy order curves and the paper's reported comparisons."""
import json
from html import escape
from paper_lab.batch28 import table as _table


def table(headers, rows):
    return _table(headers, rows).replace('aria-label="人工実験の比較"', 'aria-label="論文が報告した比較"')


def widget(result):
    if not isinstance(result, dict) or result.get('lab01') != 'deepstock':
        return ''
    frames = []
    for f in result['frames']:
        target = f['target']
        svg = '<svg viewBox="0 0 600 330" role="img" aria-label="総在庫を変えたときに4方式の式が返す発注量" style="width:100%;height:auto"><path d="M55 35V270H575" fill="none" stroke="currentColor"/>'
        for key, color, dash in [('None','#a168ba','8 4'),('Coeff','#a168ba',''),('Base','#087f8c','8 4'),('Both','#087f8c','')]:
            points=' '.join(f'{55+r["inventory"]*10},{270-r[key]*5}' for r in f['curve'])
            svg+=f'<polyline points="{points}" stroke="{color}" stroke-width="3" stroke-dasharray="{dash}" fill="none"/>'
        for inv in (0,12,24,36,48):
            svg+=f'<text x="{55+inv*10}" y="292" text-anchor="middle">{inv}</text>'
        svg+='<text x="55" y="22">発注量 q（個）</text><text x="390" y="320">総在庫 tot(I)（個）</text></svg>'
        frames.append(
            f'<p>Noneの発注量とBaseの目標在庫は<strong>{target}個</strong>です。紫のNoneとCoeffは総在庫を引きません。'
            '青緑のBaseとBothは、目標在庫から総在庫を引き、不足分だけを発注します。各色の2本は、この図では重なります。</p>'
            + svg +
            f'<p>図では係数 {escape(str(f["weights"]))} を需要特徴 [4, 8, 12, 16, 1] に順に掛け、足すと{target}になります。'
            'Coeffは合計を発注量に、Bothは目標在庫に使います。グラフはこの出力と係数を固定したときの計算で、学習後も在庫が増えるたびに発注が減るとは限りません。</p>'
        )
    data=json.dumps(frames,ensure_ascii=False).replace('</','<\\/')
    out='<figure class="teaching" data-b21><h3>総在庫と4方式の発注量</h3><label>Noneの発注量とBaseの目標在庫（個） <select>'+''.join(f'<option value="{i}">{f["target"]}</option>' for i,f in enumerate(result['frames']))+'</select></label><script type="application/json" data-frames>'+data+'</script><div data-output aria-live="polite">'+frames[0]+'</div><figcaption>原論文の導入部pp.3–4にある4式をrun.pyで計算しました。同じ色の線が重なるように出力と係数を選んでいます。</figcaption></figure>'
    svg='<svg viewBox="0 0 620 390" role="img" aria-label="DDPG Bothを基準にした欠品率と在庫回転日数の差" style="width:100%;height:auto"><path d="M55 30V325H575" fill="none" stroke="currentColor"/><path d="M55 244H575" stroke="#888" stroke-dasharray="4"/>'
    for i,r in enumerate(result['offline']):
        x=70+r['sr_pp']*44
        y=244-r['tt_days']*25
        color='#087f8c' if r['method']=='DDPG Both' else '#a168ba'
        svg+=f'<circle cx="{x}" cy="{y}" r="5" fill="{color}"/><text x="{x+8}" y="{y-7 if i%2 else y+16}" font-size="13">{escape(r["method"])}</text>'
    svg+='<text x="55" y="20">在庫回転日数の差（日）</text><text x="355" y="368">欠品率の差（ポイント）</text><text x="35" y="248">0</text><text x="65" y="345">0</text><text x="510" y="345">10</text></svg>'
    out+='<figure class="teaching"><h3>欠品率と在庫回転日数のオフライン比較</h3>'+svg+table(['Table 1の方式','欠品率の差（ポイント）','在庫回転日数の差（日）'],[[r['method'],r['sr_pp'],r['tt_days']] for r in result['offline']])+'<figcaption>それぞれの値は著者が報告したDDPG Bothとの差です。左ほど欠品率が低く、下ほど回転日数が短くなります。DS BaseはDDPG Bothより回転日数は短く、欠品率は高い方式です。この表からは指標の絶対値や誤差の幅は分かりません。</figcaption></figure>'
    deployment_rows = []
    for row in result['deployment']:
        sr = {
            'reported_as_percent': lambda: f'{row["sr_reported_percent"]:.2f}%',
            'no_distinguishable_difference': lambda: '判別可能な差なし',
        }[row['sr_status']]()
        deployment_rows.append([row['name'], sr, row['tt_days']])
    out+='<figure class="teaching"><h3>2024年7月と2025年4月の導入時の比較</h3>'+table(['比較の対象と方法','欠品率の差（論文の表記）','在庫回転日数の差（日）'],deployment_rows)+'<p>4月の国内A+は−4.04日でした。7月は改善の余地が大きい海外商品の10%を選んでおり、4月と対象も比較方法も異なります。二つの値の差だけでは、対象を広げて効果が小さくなったとは言えません。</p><figcaption>原論文の§4とTable 2に基づきます。4月の欠品率は差を判別できなかったため、数値では表示しません。測定した差が0だったという意味ではありません。</figcaption></figure>'
    return out
