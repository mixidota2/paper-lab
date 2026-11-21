"""DeepStock action coordinates and paired KPI evidence; values from results.json."""
import json
from html import escape
from paper_lab.batch28 import table as _table


def table(headers, rows):
    return _table(headers, rows).replace('aria-label="人工実験の比較"', 'aria-label="著者報告の比較"')


def widget(result):
    if not isinstance(result, dict) or result.get('lab01') != 'deepstock':
        return ''
    frames = []
    for f in result['frames']:
        target = f['target']
        svg = '<svg viewBox="0 0 600 330" role="img" aria-label="固定出力で在庫を増やしたときの発注量" style="width:100%;height:auto"><path d="M55 35V270H575" fill="none" stroke="currentColor"/>'
        for key, color, dash in [('None','#a168ba','8 4'),('Coeff','#a168ba',''),('Base','#087f8c','8 4'),('Both','#087f8c','')]:
            points=' '.join(f'{55+r["inventory"]*10},{270-r[key]*5}' for r in f['curve'])
            svg+=f'<polyline points="{points}" stroke="{color}" stroke-width="3" stroke-dasharray="{dash}" fill="none"/>'
        for inv in (0,12,24,36,48):
            svg+=f'<text x="{55+inv*10}" y="292" text-anchor="middle">{inv}</text>'
        svg+='<text x="55" y="22">発注量 q（上端48）</text><text x="390" y="320">総在庫 tot(I)</text></svg>'
        frames.append(f'<p><strong>出力を {target} に固定</strong>。紫のNoneとCoeffは総在庫を引かず、緑のBaseとBothは目標在庫から総在庫を引く。この例では同じ色の線が重なる。</p>'+svg+f'<p>Coeffで使う係数 {escape(str(f["weights"]))} × 需要特徴 [4, 8, 12, 16, 1] を足し合わせると {target}。Coeffではこれが発注量、Bothではこの値から総在庫を引き、負なら0にする。</p><p>線は、モデルの出力を固定して在庫だけを動かした結果。実際に学習したモデルが、在庫が増えるたびに発注を減らすことを示すわけではない。</p>')
    data=json.dumps(frames,ensure_ascii=False).replace('</','<\\/')
    out='<figure class="teaching" data-b21><h3>同じ出力でも、目標在庫と読むと発注量が変わる</h3><label>固定する出力 <select>'+''.join(f'<option value="{i}">{f["target"]}</option>' for i,f in enumerate(result['frames']))+'</select></label><script type="application/json" data-frames>'+data+'</script><div data-output aria-live="polite">'+frames[0]+'</div><figcaption>導入部pp.3–4の4式をrun.pyで計算した図。同じ色の線が重なるように出力を選んだ例。</figcaption></figure>'
    svg='<svg viewBox="0 0 620 390" role="img" aria-label="DDPG Bothとの差、欠品率と回転日数" style="width:100%;height:auto"><path d="M55 30V325H575" fill="none" stroke="currentColor"/><path d="M55 244H575" stroke="#888" stroke-dasharray="4"/>'
    for i,r in enumerate(result['offline']):
        x=70+r['sr_pp']*44
        y=244-r['tt_days']*25
        color='#087f8c' if r['method']=='DDPG Both' else '#a168ba'
        svg+=f'<circle cx="{x}" cy="{y}" r="5" fill="{color}"/><text x="{x+8}" y="{y-7 if i%2 else y+16}" font-size="13">{escape(r["method"])}</text>'
    svg+='<text x="55" y="20">Δ回転日数（日） ↑ 悪化</text><text x="250" y="368">Δ欠品率（ポイント） → 悪化</text><text x="35" y="248">0</text><text x="65" y="345">0</text><text x="510" y="345">10</text></svg>'
    out+='<figure class="teaching"><h3>欠品率と回転日数のどちらを重く見るかで評価は変わる</h3>'+svg+table(['Table 1の方策','Δ欠品率 (pp)','Δ回転日数 (日)'],[[r['method'],r['sr_pp'],r['tt_days']] for r in result['offline']])+'<figcaption>著者報告。DDPG Bothとの差なので、左下ほど欠品が少なく、在庫が早く回る。DS Baseは回転日数で良い一方、欠品率では悪い。指標の絶対値や誤差の幅はこの表からは分からない。</figcaption></figure>'
    out+='<figure class="teaching"><h3>7月は導入前後、4月は旧方式を続けた場合と比較</h3>'+table(['比較設計','Δ欠品率 (pp)','Δ回転日数 (日)'],[[r['name'],'判別可能な差なし' if r['sr_pp']==0 else r['sr_pp'],r['tt_days']] for r in result['deployment']])+'<p>4月の国内A+は−4.04日。7月は改善余地が大きい10%を選んだ比較なので、4月との差だけで、展開後に効果が弱まったとは言えない。</p><figcaption>§4とTable 2の著者報告。4月の欠品率は判別可能な差がなかった。元データの0は表示用で、効果が厳密に0という推定ではない。</figcaption></figure>'
    return out
