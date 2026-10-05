"""Sparse-event teaching: probability mass, threshold ties, dataset dot plots."""
import json
from paper_lab.batch28 import table
from paper_lab.retailbench30 import panel


def widget(result):
    if not isinstance(result,dict) or not result.get('lab05_sparse'):
        return ''
    frames=[]
    for f in result['distribution_frames']:
        bars=''
        for k,m in enumerate(f['masses']):
            x=40+k*25; h=m*210
            bars+=f'<rect x="{x}" y="{235-h:.2f}" width="18" height="{h:.2f}" fill="{"#ce6d39" if k==0 else "#257d85"}"/><text x="{x+9}" y="255" text-anchor="middle" font-size="12">{k}</text>'
        frames.append(f'<svg viewBox="0 0 590 280" role="img" aria-label="発生確率{f["p"]:.0%}での数量分布" style="width:100%;height:auto"><title>0の確率質量と正の数量</title><text x="40" y="20">P(Y = y)（縦軸 0〜1）</text><line x1="35" y1="235" x2="570" y2="235" stroke="#657780"/>{bars}</svg>'+table(['発生確率 p','中央値','平均','9分位点平均'],[[f'{f["p"]:.0%}',f['median'],f'{f["mean"]:.2f}',f'{f["quantile_average"]:.2f}']]))
    payload=json.dumps(frames,ensure_ascii=False).replace('</','<\\/')
    out=f'''<figure class="teaching" id="sparse-mass"><h3>49%の発生確率も、中央値は0になる</h3><p>人工分布 Y = B × (1 + NB)、B ~ Bernoulli(p)。正の数量の平均は5個。横軸は数量、棒の高さは確率。</p><label for="sparse-p">発生確率 p <input id="sparse-p" type="range" min="1" max="99" value="30" step="1" style="max-width:100%"></label><output id="sparse-p-value">30%</output><div data-mass aria-live="polite">{frames[29]}</div><script type="application/json" id="sparse-mass-data">{payload}</script><figcaption>§1の中央値の説明を人工分布で図解。9分位点平均は0.1〜0.9の平均で、裾を含む予測平均とは異なる。図は20個までを表示。</figcaption></figure><script>(()=>{{const root=document.getElementById('sparse-mass');const f=JSON.parse(document.getElementById('sparse-mass-data').textContent);root.querySelector('input').addEventListener('input',e=>{{root.querySelector('[data-mass]').innerHTML=f[Number(e.target.value)-1];root.querySelector('output').textContent=e.target.value+'%';}});}})();</script>'''
    out+='''<figure class="teaching"><h3>同点をまとめて評価し、窓ごとに偶然分を引く</h3><p>AP = Σ aᵦ Aᵦ / (k Cᵦ)<br>AP₀ = (k−1)/(n−1) + (n−k)/[n(n−1)] × Σ sᵦ/Cᵦ<br>AP skill = (AP−AP₀)/(1−AP₀)</p><p>高いスコアから同点群bを作る。sᵦは群の人数、aᵦは群の発生数、CᵦとAᵦはそこまでの累積数。nは窓の長さ、kは全発生数。同点群を途中で分けない。</p><p>例：発生ラベル [1, 0, 0, 1] に全て0点を付けると、AP = AP₀ = 2/4、skill = 0。AP₀を常に発生率で置き換えると、同点がない場合の有限標本補正を誤る。</p><figcaption>原典 Appendix B.1。0は偶然並べ替えの期待値、1は完全順位。負の値も残す。全て0または全て1の窓は対象外。</figcaption></figure>'''
    dotframes=[]
    for r in result['reported']:
        rows=[('参照',r['reference']),('Chronos-2 点予測',r['chronos2_point']),('Chronos-2 線形probe',r['chronos2_probe']),('Raw LightGBM',r['raw_lightgbm'])]
        dots=''
        for i,(name,value) in enumerate(rows):
            y=40+i*46; x=195+value/.25*300
            dots+=f'<text x="5" y="{y+5}" font-size="14">{name}</text><line x1="195" y1="{y}" x2="495" y2="{y}" stroke="#d1dce1"/><circle cx="{x}" cy="{y}" r="6" fill="{["#879095","#ce6d39","#257d85","#7854a0"][i]}"/><text x="{x+10}" y="{y+5}" font-size="13">{value:.4f}</text>'
        dotframes.append(f'<svg viewBox="0 0 590 250" role="img" aria-label="{r["dataset"]}のAP skill" style="width:100%;height:auto"><title>{r["dataset"]}・著者報告</title>{dots}<text x="195" y="240">0</text><text x="420" y="240">AP skill → 0.25</text></svg>'+table(['評価経路','AP skill'],rows))
    out+=panel('同じChronos-2でも、点予測と発生headは別の評価になる','データセット',[r['dataset'] for r in result['reported']],dotframes,'著者報告 Tables 14–18を転記。軸は全データセット共通。点の差だけで有意性を判断しない。Chronos-2は代表例で、最高値を選んだ図ではない。')
    sim=[]
    for f in result['scenarios']:
        sim.append(table(['人工実験の方法','平均AP skill','3 seedの最小〜最大'],[[r['method'],f'{r["ap_skill"]:.4f}',f'{r["seed_min"]:.4f}〜{r["seed_max"]:.4f}'] for r in f['rows']]))
    out+=panel('平均が発生順位になるのは、正の数量が同じとき','正の数量の条件',['平均5個で固定','発生しやすいほど数量が小さい'],sim,'run.pyの人工実験。中央値・平均・分位点は真の分布を知る比較対象。headは独立した訓練データから学ぶ。TSFM表現のprobeではない。')
    return out
