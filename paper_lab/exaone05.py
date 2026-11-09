"""EXAONE-specific classification plane, adapter anatomy, and censoring view."""
from html import escape
import math


def initial_stock():
    """The existing 30-period illustrative stock curve at S=40, promotion on."""
    inventory, due, lost = 40, -1, 0
    latent, observed = [], []
    for t in range(30):
        if t == due:
            inventory, due = 40, -1
        factor = 1.4 if 9 <= t < 12 else 2.4 if 12 <= t < 16 else .65 if 16 <= t < 20 else 1
        demand = math.floor((7 + 3 * math.sin(t * 1.3)) * factor + .5)
        sales = min(inventory, demand)
        inventory -= sales
        lost += demand - sales
        latent.append(demand)
        observed.append(sales)
        if inventory < 8 and due < 0:
            due = t + 3
    def path(values):
        return ''.join(('L' if i else 'M') + f'{42 + i * 19},{195 - value * 6}' for i, value in enumerate(values))
    svg = ('<path d="M42 15V195H610" fill="none" stroke="#64766e"/>'
           '<text x="5" y="22" font-size="13">数量</text><text x="270" y="227" font-size="13">期間（0〜29）</text>'
           '<text x="14" y="195" font-size="12">0</text><text x="8" y="75" font-size="12">20</text>'
           f'<path d="{path(latent)}" fill="none" stroke="#316d99" stroke-width="3"/>'
           f'<path d="{path(observed)}" fill="none" stroke="#c27035" stroke-width="3" stroke-dasharray="5 3"/>')
    return svg, f'潜在需要 {sum(latent)} 個のうち、観測されなかった需要は {lost} 個。'


def widget(result):
    if not isinstance(result, dict) or not result.get('lab05_exaone'):
        return ''
    heat=''
    for row in result['reported_datasets']:
        best=min(row[1:])
        cells=''.join(f'<td style="background:hsl({155 if v==best else 36} 42% {88 if v==best else 96}%)">{v:.3f}</td>' for v in row[1:])
        heat+=f'<tr><th>{escape(row[0])}</th>{cells}</tr>'
    toy=''.join(f'<tr><td>{r["seed"]}</td><td>{r["global_method"]}</td><td>{r["mase_global"]:.4f}</td><td>{r["mase_routed"]:.4f}</td></tr>' for r in result['seed_results'])
    html = r'''<section class="exa-lab" aria-label="需要分類の操作実験">
<style>.exa-lab{--ex:#246b67}.exa-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:1rem}.exa-lab svg{width:100%;height:auto}.exa-lab label{display:block;margin:.7rem 0}.exa-lab input[type=range]{width:100%;min-height:28px}.exa-lab .ex-card{padding:1rem;border:1px solid #bfd4d0;border-radius:12px;background:#f6faf8;color:#183a36}.ex-weights{display:grid;grid-template-columns:1fr 1fr;gap:.4rem}.ex-weights div{padding:.55rem;background:#e5efea;border-radius:6px}.exa-lab table{width:100%;font-size:.88rem}.exa-lab .ex-scroll{overflow:auto}.exa-lab .ex-formula{overflow:auto;padding:.8rem;background:#e5efea;font-family:monospace}.exa-lab output{font-variant-numeric:tabular-nums}@media(max-width:640px){.exa-grid{grid-template-columns:1fr}.exa-lab th,.exa-lab td{padding:.45rem}}</style>
<h3>需要の地図：境界を越えても、配分は急変しない</h3>
<p>式5–6の分類比率πと式10の教師分布π̃を表示する。学習済みの振り分け器（router）のqを表示するものではない。Smoothは発生間隔が短く数量変動が小さい側、Intermittentは間隔が長く変動が小さい側、Erraticは間隔が短く変動が大きい側、Lumpyは間隔が長く変動が大きい側を表す。</p>
<p data-ex-status role="status">初期条件はADI=1.32、CV²=0.49、補充上限S=40、販促ありです。JavaScriptの準備が完了するまで条件は変更できません。</p><noscript><p>JavaScriptが無効なため、初期条件の結果のみを表示しています。</p></noscript>
<div class="exa-grid"><div class="ex-card">
<label>ADI（非ゼロ需要の平均間隔） <output data-adi>1.32</output><input data-a disabled type="range" min="1" max="12" step=".01" value="1.32"></label>
<label>CV²（非ゼロ数量の相対分散） <output data-cv>0.49</output><input data-c disabled type="range" min=".01" max="4" step=".01" value=".49"></label>
<svg viewBox="0 0 440 300" role="img" aria-label="対数軸のADIとCV二乗の分類平面"><rect x="58" y="20" width="332" height="222" fill="#eaf3ee"/><path d="M95 20V242M58 98H390" stroke="#618d80" stroke-dasharray="4"/><text x="66" y="46" font-size="12">Erratic</text><text x="220" y="46" font-size="16">Lumpy</text><text x="61" y="221" font-size="11">Smooth</text><text x="185" y="221" font-size="16">Intermittent</text><path d="M58 20V242H390" fill="none" stroke="#294a43"/><text x="170" y="285" font-size="14">ADI（対数軸）→</text><text x="5" y="15" font-size="14">CV² ↑</text><text x="52" y="261" font-size="12">1</text><text x="88" y="261" font-size="12">1.32</text><text x="373" y="261" font-size="12">12</text><text x="14" y="103" font-size="12">0.49</text><text x="17" y="241" font-size="12">0.01</text><circle data-point cx="__EX_CX__" cy="__EX_CY__" r="7" fill="#bd613b" stroke="white" stroke-width="2"/></svg>
</div><div class="ex-card"><h4>π → π̃（T=0.5）</h4><div class="ex-weights" data-weights aria-live="polite">__EX_WEIGHTS__</div><p>両軸が境界なら4成分は25%ずつ。温度を下げても完全な同率は崩れない。</p><div class="ex-formula">π̃c = πc² / Σ πc²<br>a = σ(log(ADI/1.32)/0.35)<br>c = σ(log(CV²/0.49)/0.60)</div></div></div>
<h3>補正を入れる場所：更新しない元の変換に5本の補正を足す</h3>
<svg viewBox="0 0 660 280" role="img" aria-label="更新しない元の変換に、共有の補正1本と需要型別の補正4本を足す"><title>Figure 9と式11の再構成</title><g fill="none" stroke="#77958a" stroke-width="2"><path d="M45 130H100V40H490V130H600M100 130V95H490V130M100 130V170H490V130M100 130V225H490V130"/></g><g fill="#e4efe9" stroke="#7e9f8f"><rect x="160" y="18" width="260" height="42" rx="8"/><rect x="160" y="75" width="260" height="42" rx="8"/><rect x="130" y="143" width="325" height="44" rx="8"/><rect x="130" y="207" width="325" height="42" rx="8"/></g><g fill="#173c34" font-size="16" text-anchor="middle"><text x="24" y="136">x</text><text x="290" y="45">凍結 W₀（更新しない）</text><text x="290" y="102">共有 B₀A₀：rank 16 / g₀=0.5</text><text x="293" y="162">Smooth・Intermittent：各rank 4</text><text x="293" y="181">重み 0.5q₁・0.5q₂</text><text x="293" y="224">Erratic・Lumpy：各rank 4</text><text x="293" y="242">重み 0.5q₃・0.5q₄</text><text x="510" y="136">＋</text><text x="625" y="136">y</text></g></svg>
<p>元の変換W₀は更新せず、共有する補正1本と需要型別の補正4本を足す。図中のrankは補正行列のランクを表す。</p><p>式11：y = W₀x + Σ gₑ(8/rₑ)BₑAₑx。8統計量 → 各層の2層MLP → q。教師分布は学習時だけ使い、共有する補正1本と需要型別の補正4本を使う。共有する補正は教師損失に含めない。144投影に適用する（Table 10）。</p>
<h3>潜在需要と売上を分ける：在庫が尽きると何を観測するか</h3>
<div class="ex-card"><label>補充上限S <output data-stock-label>40</output><input data-stock disabled type="range" min="10" max="100" step="5" value="40"></label><label><input data-promo disabled type="checkbox" checked> 販促の盛り上がりと反動を入れる</label><svg data-series viewBox="0 0 640 235" role="img" aria-label="30期間の潜在需要と在庫で制限された売上">__EX_SERIES__</svg><p data-lost aria-live="polite">__EX_LOST__</p></div>
<p>青：潜在需要、橙：観測売上。s=8を下回ると3期間後にSまで補充する説明用(s,S)モデル。販促は事前増・ピーク・反動の3段階。Table 5の考え方を示す人工曲線で、公式生成器や欠品復元モデルの再現ではない。</p>
<h3>著者報告：22データセットを同じ色で平均化しない</h3><p>Table 9の4列を転記。各行の掲載4モデル中の最小値を緑で示す。MASEは、予測期間の平均絶対誤差を、同じ系列の学習期間で「1季節前の値をそのまま予測する方法」の平均絶対誤差で割った指標。小さいほどよい。<a href="https://arxiv.org/html/2609.30880v1">原典§5.1式(13)</a>の定義で、季節の長さを一律に1とは置かない。分母が0の場合の処理は未確認。1を超えても、同じ将来期間で季節予測が優れていたとは限らない。全比較モデル中の最良を表す色ではない。</p>
<div class="ex-scroll"><table><thead><tr><th>データセット</th><th>EXAONE</th><th>Synthetic</th><th>TiRex</th><th>Chronos-2</th></tr></thead><tbody>''' + heat + '''</tbody></table></div>
<h3>人工実験：混ぜるだけでは安定して改善しなかった</h3><div class="ex-scroll"><table><thead><tr><th>seed</th><th>検証で選んだ共通法</th><th>共通MASE</th><th>混合MASE</th></tr></thead><tbody>''' + toy + r'''</tbody></table></div><p>同じ未使用系列で比較。5seed中4seedで混合が悪化。分類の式は確認できたが、混合による安定した改善は今回の人工実験では見られなかった（NOT OBSERVED）。</p>
<script>(()=>{const root=document.currentScript.closest('.exa-lab');const a=root.querySelector('[data-a]'),c=root.querySelector('[data-c]');function update(){let av=+a.value,cv=+c.value;let aa=1/(1+Math.exp(-Math.log(av/1.32)/.35)),cc=1/(1+Math.exp(-Math.log(cv/.49)/.6));let p=[(1-aa)*(1-cc),aa*(1-cc),(1-aa)*cc,aa*cc],den=p.reduce((s,v)=>s+v*v,0);root.querySelector('[data-adi]').value=av.toFixed(2);root.querySelector('[data-cv]').value=cv.toFixed(2);root.querySelector('[data-point]').setAttribute('cx',58+332*Math.log(av)/Math.log(12));root.querySelector('[data-point]').setAttribute('cy',242-222*Math.log(cv/.01)/Math.log(400));root.querySelector('[data-weights]').innerHTML=p.map((v,i)=>'<div><b>'+['Smooth','Intermittent','Erratic','Lumpy'][i]+'</b><br>'+(100*v).toFixed(1)+'% → '+(100*v*v/den).toFixed(1)+'%</div>').join('');}function stock(){let S=+root.querySelector('[data-stock]').value,inv=S,due=-1,lost=0,latent=[],observed=[],promo=root.querySelector('[data-promo]').checked;for(let t=0;t<30;t++){if(t===due){inv=S;due=-1;}let d=Math.round((7+3*Math.sin(t*1.3))*(promo?(t>=9&&t<12?1.4:t>=12&&t<16?2.4:t>=16&&t<20?.65:1):1));let y=Math.min(inv,d);inv-=y;lost+=d-y;latent.push(d);observed.push(y);if(inv<8&&due<0)due=t+3;}const path=xs=>xs.map((v,i)=>(i?'L':'M')+(42+i*19)+','+(195-v*6)).join('');root.querySelector('[data-stock-label]').value=S;root.querySelector('[data-series]').innerHTML='<path d="M42 15V195H610" fill="none" stroke="#64766e"/><text x="5" y="22" font-size="13">数量</text><text x="270" y="227" font-size="13">期間（0〜29）</text><text x="14" y="195" font-size="12">0</text><text x="8" y="75" font-size="12">20</text><path d="'+path(latent)+'" fill="none" stroke="#316d99" stroke-width="3"/><path d="'+path(observed)+'" fill="none" stroke="#c27035" stroke-width="3" stroke-dasharray="5 3"/>';root.querySelector('[data-lost]').textContent='潜在需要 '+latent.reduce((s,v)=>s+v,0)+' 個のうち、観測されなかった需要は '+lost+' 個。';}const controls=[a,c,root.querySelector('[data-stock]'),root.querySelector('[data-promo]')];let ready=false;
a.value='1.32';c.value='.49';controls[2].value='40';controls[3].checked=true;
try{
a.addEventListener('input',()=>{if(ready)update();});c.addEventListener('input',()=>{if(ready)update();});
controls[2].addEventListener('input',()=>{if(ready)stock();});controls[3].addEventListener('change',()=>{if(ready)stock();});
update();stock();
for(const control of controls)control.disabled=false;
root.querySelector('[data-ex-status]').hidden=true;ready=true;
}catch(error){for(const control of controls)control.disabled=true;}
})();</script></section>'''

    series, lost = initial_stock()
    weights = ''.join(f'<div><b>{name}</b><br>25.0% → 25.0%</div>'
                      for name in ('Smooth', 'Intermittent', 'Erratic', 'Lumpy'))
    return (html.replace('__EX_WEIGHTS__', weights).replace('__EX_SERIES__', series)
            .replace('__EX_LOST__', lost)
            .replace('__EX_CX__', str(58 + 332 * math.log(1.32) / math.log(12)))
            .replace('__EX_CY__', str(242 - 222 * math.log(.49 / .01) / math.log(400))))
