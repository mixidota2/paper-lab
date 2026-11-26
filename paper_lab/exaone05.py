"""EXAONEの分類比率、補正の構成、欠品で見えない需要を図にします。"""
from html import escape
import math


def initial_stock():
    """在庫目標40個、販促ありの初期条件で30期間の曲線を描きます。"""
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
    return svg, f'潜在需要は{sum(latent)}個です。在庫が足りず、{lost}個を売り逃しました。'


def widget(result):
    if not isinstance(result, dict) or not result.get('lab05_exaone'):
        return ''
    heat=''
    for row in result['reported_datasets']:
        best=min(row[1:])
        cells=''.join(f'<td style="background:hsl({155 if v==best else 36} 42% {88 if v==best else 96}%)">{v:.3f}</td>' for v in row[1:])
        heat+=f'<tr><th>{escape(row[0])}</th>{cells}</tr>'
    toy=''.join(f'<tr><td>{r["seed"]}</td><td>{r["global_method"]}</td><td>{r["mase_global"]:.4f}</td><td>{r["mase_routed"]:.4f}</td></tr>' for r in result['seed_results'])
    html = r'''<section class="exa-lab" aria-label="需要の分類比率と、在庫が販売数に与える影響">
<style>.exa-lab{--ex:#246b67}.exa-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:1rem}.exa-lab svg{width:100%;height:auto}.exa-lab label{display:block;margin:.7rem 0}.exa-lab input[type=range]{width:100%;min-height:28px}.exa-lab .ex-card{padding:1rem;border:1px solid #bfd4d0;border-radius:12px;background:#f6faf8;color:#183a36}.ex-weights{display:grid;grid-template-columns:1fr 1fr;gap:.4rem}.ex-weights div{padding:.55rem;background:#e5efea;border-radius:6px}.exa-lab table{width:100%;font-size:.88rem}.exa-lab .ex-scroll{overflow:auto}.exa-lab .ex-formula{overflow:auto;padding:.8rem;background:#e5efea;font-family:monospace}.exa-lab output{font-variant-numeric:tabular-nums}@media(max-width:640px){.exa-grid{grid-template-columns:1fr}.exa-lab th,.exa-lab td{padding:.45rem}}</style>
<h3>需要型の分類比率と学習用の比率</h3>
<p>図は式5・6の分類比率πと、式10で変換した学習用の教師比率π̃を表示します。学習済みの配分器が予測時に出すqは表示しません。需要が出る間隔が短く、数量のばらつきが小さい側がSmoothです。間隔だけが長い側をIntermittent、ばらつきだけが大きい側をErratic、両方が大きい側をLumpyと呼びます。</p>
<p data-ex-status role="status">初期条件はADI=1.32、CV²=0.49、補充後の在庫目標40個、販促ありです。操作の準備が終わるまでは初期値を表示します。</p><noscript><p>JavaScriptが無効のため、初期条件の結果のみを表示しています。</p></noscript>
<div class="exa-grid"><div class="ex-card">
<label>ADI（ゼロでない観測値が出る平均間隔） <output data-adi>1.32</output><input data-a disabled type="range" min="1" max="12" step=".01" value="1.32"></label>
<label>CV²（ゼロでない数量のばらつき） <output data-cv>0.49</output><input data-c disabled type="range" min=".01" max="4" step=".01" value=".49"></label>
<svg viewBox="0 0 440 300" role="img" aria-label="ADIとCV²を対数軸にした需要分類の図"><rect x="58" y="20" width="332" height="222" fill="#eaf3ee"/><path d="M95 20V242M58 98H390" stroke="#618d80" stroke-dasharray="4"/><text x="66" y="46" font-size="12">Erratic</text><text x="220" y="46" font-size="16">Lumpy</text><text x="61" y="221" font-size="11">Smooth</text><text x="185" y="221" font-size="16">Intermittent</text><path d="M58 20V242H390" fill="none" stroke="#294a43"/><text x="170" y="285" font-size="14">ADI（対数軸）→</text><text x="5" y="15" font-size="14">CV² ↑</text><text x="52" y="261" font-size="12">1</text><text x="88" y="261" font-size="12">1.32</text><text x="373" y="261" font-size="12">12</text><text x="14" y="103" font-size="12">0.49</text><text x="17" y="241" font-size="12">0.01</text><circle data-point cx="__EX_CX__" cy="__EX_CY__" r="7" fill="#bd613b" stroke="white" stroke-width="2"/></svg>
</div><div class="ex-card"><h4>分類比率πから教師比率π̃へ（T=0.5）</h4><div class="ex-weights" data-weights aria-live="polite">__EX_WEIGHTS__</div><p>ADIとCV²がともに境界にあると、4成分は25%ずつです。温度を下げても、もとの比率が同じ成分どうしに差はつきません。</p><div class="ex-formula">π̃c = πc² / Σ πc²<br>a = σ(log(ADI/1.32)/0.35)<br>c = σ(log(CV²/0.49)/0.60)</div></div></div>
<h3>固定した変換に加える5本の補正</h3>
<svg viewBox="0 0 660 280" role="img" aria-label="固定した変換に、共有の補正1本と需要型別の補正4本を足す構成"><title>原論文の図9と式11</title><g fill="none" stroke="#77958a" stroke-width="2"><path d="M45 130H100V40H490V130H600M100 130V95H490V130M100 130V170H490V130M100 130V225H490V130"/></g><g fill="#e4efe9" stroke="#7e9f8f"><rect x="160" y="18" width="260" height="42" rx="8"/><rect x="160" y="75" width="260" height="42" rx="8"/><rect x="130" y="143" width="325" height="44" rx="8"/><rect x="130" y="207" width="325" height="42" rx="8"/></g><g fill="#173c34" font-size="16" text-anchor="middle"><text x="24" y="136">x</text><text x="290" y="45">元の変換 W₀（固定）</text><text x="290" y="102">共有 B₀A₀：rank 16 / g₀=0.5</text><text x="293" y="162">Smooth・Intermittent：各rank 4</text><text x="293" y="181">重み 0.5q₁・0.5q₂</text><text x="293" y="224">Erratic・Lumpy：各rank 4</text><text x="293" y="242">重み 0.5q₃・0.5q₄</text><text x="510" y="136">＋</text><text x="625" y="136">y</text></g></svg>
<p>モデルは元の変換W₀を固定し、共有の補正1本と需要型別の補正4本を足します。図中のrankは補正のランクです。</p><p>式11：y = W₀x + Σ gₑ(8/rₑ)BₑAₑx。補正を加える投影ごとに、2層の配分器が入力系列の8つの値からqを求めます。教師比率は学習時に4本の配分を教えるためにだけ使い、共有の補正の重みは0.5に固定します。この構成を144か所に使います（表10）。</p>
<h3>在庫によって変わる販売数と売り逃し</h3>
<div class="ex-card"><label>補充後の在庫目標S（個） <output data-stock-label>40</output><input data-stock disabled type="range" min="10" max="100" step="5" value="40"></label><label><input data-promo disabled type="checkbox" checked> 販促による需要の増加と反動を入れる</label><svg data-series viewBox="0 0 640 235" role="img" aria-label="30期間の潜在需要と、在庫の範囲で売れた数量">__EX_SERIES__</svg><p data-lost aria-live="polite">__EX_LOST__</p></div>
<p>青は在庫に関係なく買いたかった数量、橙は実際に売れた数量です。教材の在庫は8個を下回ると3期間後にS個まで戻ります。販促ありでは、需要が事前に増え、ピークの後に反動で落ちます。図は表5の考え方を説明する人工例です。公式の生成器や、販売数から潜在需要を復元するモデルは実装していません。</p>
<h3>データセット別の予測誤差</h3><p>表9のうち4モデルの著者報告を転記しました。緑は、各行に表示した4モデルの中で最小のMASEです。MASEは、予測期間の平均絶対誤差を、同じ系列の学習期間に1季節前の値をそのまま使った場合の平均絶対誤差で割ります。小さいほど予測誤差が少ないことを示します。<a href="https://arxiv.org/html/2609.30880v1">原典§5.1式(13)</a>では、季節の長さを一律に1期とはしていません。Labは分母がゼロの場合の処理を確認していません。値が1を超えても、同じ予測期間の季節ナイーブ法と直接比べた結果ではありません。緑は表8の全モデルや表9の全7モデルの順位を示しません。</p>
<div class="ex-scroll"><table><thead><tr><th>データセット</th><th>実データと人工データ</th><th>人工データのみ</th><th>TiRex-1.1</th><th>Chronos-2</th></tr></thead><tbody>''' + heat + '''</tbody></table></div>
<h3>人工需要で比べた共通手法と混合方式</h3><div class="ex-scroll"><table><thead><tr><th>乱数の初期値</th><th>検証で選んだ共通手法</th><th>共通手法のMASE</th><th>混合方式のMASE</th></tr></thead><tbody>''' + toy + r'''</tbody></table></div><p>手法の選択に使っていない同じ系列で比較しました。乱数の初期値5つのうち4つでは、混合方式の誤差が大きくなりました。分類式どおりに比率が変わっても、この混合方式で誤差が安定して下がることは確認できませんでした。</p>
<script>(()=>{const root=document.currentScript.closest('.exa-lab');const a=root.querySelector('[data-a]'),c=root.querySelector('[data-c]');function update(){let av=+a.value,cv=+c.value;let aa=1/(1+Math.exp(-Math.log(av/1.32)/.35)),cc=1/(1+Math.exp(-Math.log(cv/.49)/.6));let p=[(1-aa)*(1-cc),aa*(1-cc),(1-aa)*cc,aa*cc],den=p.reduce((s,v)=>s+v*v,0);root.querySelector('[data-adi]').value=av.toFixed(2);root.querySelector('[data-cv]').value=cv.toFixed(2);root.querySelector('[data-point]').setAttribute('cx',58+332*Math.log(av)/Math.log(12));root.querySelector('[data-point]').setAttribute('cy',242-222*Math.log(cv/.01)/Math.log(400));root.querySelector('[data-weights]').innerHTML=p.map((v,i)=>'<div><b>'+['Smooth','Intermittent','Erratic','Lumpy'][i]+'</b><br>'+(100*v).toFixed(1)+'% → '+(100*v*v/den).toFixed(1)+'%</div>').join('');}function stock(){let S=+root.querySelector('[data-stock]').value,inv=S,due=-1,lost=0,latent=[],observed=[],promo=root.querySelector('[data-promo]').checked;for(let t=0;t<30;t++){if(t===due){inv=S;due=-1;}let d=Math.round((7+3*Math.sin(t*1.3))*(promo?(t>=9&&t<12?1.4:t>=12&&t<16?2.4:t>=16&&t<20?.65:1):1));let y=Math.min(inv,d);inv-=y;lost+=d-y;latent.push(d);observed.push(y);if(inv<8&&due<0)due=t+3;}const path=xs=>xs.map((v,i)=>(i?'L':'M')+(42+i*19)+','+(195-v*6)).join('');root.querySelector('[data-stock-label]').value=S;root.querySelector('[data-series]').innerHTML='<path d="M42 15V195H610" fill="none" stroke="#64766e"/><text x="5" y="22" font-size="13">数量</text><text x="270" y="227" font-size="13">期間（0〜29）</text><text x="14" y="195" font-size="12">0</text><text x="8" y="75" font-size="12">20</text><path d="'+path(latent)+'" fill="none" stroke="#316d99" stroke-width="3"/><path d="'+path(observed)+'" fill="none" stroke="#c27035" stroke-width="3" stroke-dasharray="5 3"/>';root.querySelector('[data-lost]').textContent='潜在需要は'+latent.reduce((s,v)=>s+v,0)+'個です。在庫が足りず、'+lost+'個を売り逃しました。';}const controls=[a,c,root.querySelector('[data-stock]'),root.querySelector('[data-promo]')];let ready=false;
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
