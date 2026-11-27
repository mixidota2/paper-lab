"""Render the comparison from this one article without changing the shared charts."""
import json

from paper_lab.batch08 import COMMON, STYLE

HARNESS = r'''
<h3>第1版：成否が入れ替わった課題の割合</h3><div class="cards" data-flips></div>
<p class="muted">第1版の図2に載った45課題の中央値です。この図ではモデル交換は22%ですが、本文の第2版は追加試行を含めて25.6%と報告しています。</p>
<h3>第1版：同じ課題で測った成功率の差と95%区間</h3><div class="plot"><svg class="wide" role="img" aria-label="第1版の447課題で比べたハーネスごとの成功率差" data-forest></svg></div>
<p>CCはClaude Code、miniはmini-SWE-agent、OCはOpenCodeです。たとえばCC−miniで右へ行くほど、Claude Codeの成功率が高いことを示します。</p>
<p class="muted">第1版の表1の差と95%区間です。単位はポイントです。緑の帯は±5ですが、著者が同等の範囲を調べるときは別に90%区間を使いました。第2版は、±5へ狭めたのは447課題の実行後だったと明記しています。</p>
<h3>この課題数で、どれほどの差を見つけられるか</h3>
<p>nは両方で結果がある課題の件数、qは成否の違う課題の割合です。検出力は仮定した成功率差Δがあるときに検定がその差を見つけられる確率です。「到達不可」は、選んだnとqでは目標の確率に届かないという意味です。</p>
<div class="cols"><label>両方を比較できる課題数 n<select data-n><option>45</option><option>100</option><option>200</option><option selected>447</option><option>800</option></select></label><label>不一致率 q<select data-q><option value="0.07">7%</option><option value="0.14">14%（丸め）</option><option value="0.14008941877794337">14.0089%（第1版の45課題の計算に使用）</option><option value="0.14392803598200898" selected>14.3928%（第1版の447課題の計算に使用）</option><option value="0.27">27%</option></select></label></div>
<div class="cards" data-power aria-live="polite"></div><p class="eq">M ~ Binomial(n,q) → B|M ~ Binomial(M,(1+Δ/q)/2) → exact McNemar p≤.05</p><p class="muted">不一致率が14%の45課題では、どんな成功率差でも検出力は80%に届きません。447課題なら、14%で約5.09ポイント、14.3928%で約5.16ポイントの差が80%の確率で見つかる計算です。</p>
<h3>入力トークンは、定型文・履歴・呼び出し回数で変わる</h3>
<div class="cols"><label>同じ回数で比べるときの呼び出し回数 <output data-steps-label></output><input data-steps type="range" min="10" max="200" value="80"></label><label>キャッシュを使えるときの入力単価 ÷ 使用できないときの単価 <output data-price-label></output><input data-price type="range" min="0.001" max="0.5" step="0.001" value="0.287"></label></div>
<label><input data-papersteps type="checkbox" checked> 第1版のGLMの代表値（CC 88回、mini 80回、OC 55回）を使う</label>
<label><input data-compact type="checkbox"> 説明用に、60回ごとに履歴を空にする</label>
<div class="plot"><svg viewBox="0 0 600 290" role="img" aria-label="ハーネスごとの1回当たりの入力トークン数" data-billplot></svg></div>
<div class="tablewrap"><table><thead><tr><th>構成</th><th>定型入力 / 呼び出すたびに増える量</th><th>入力トークン数（百万）</th><th>キャッシュなしの単価に直した量（百万トークン）</th></tr></thead><tbody data-bill></tbody></table></div>
<p class="muted">定型入力と履歴の増え方は第1版の付録Gを使い、課題文は554トークン、キャッシュを使う割合は97%と置きます。出力、実際の履歴圧縮、停止するタイミングは含めません。表は金額ではなく、キャッシュなしの単価に直したトークン数です。図のkは千を表します。</p>
'''
HARNESS_JS = r'''
$('[data-flips]').innerHTML=['同じ設定で再実行','ハーネスだけ交換','モデルを交換'].map((n,i)=>`<div class="card">${n}<span class="big">${d.paper.flip[i]}%</span><div class="bar" style="width:${d.paper.flip[i]*3}%"></div></div>`).join('');forest($('[data-forest]'),d.paper.pairs,-8,15,true);
function power(){let v=d.power_grid.find(x=>x.n===+$('[data-n]').value && x.q===+$('[data-q]').value);$('[data-power]').innerHTML=[['50%検出力の最小差',v.mde50==null?'到達不可':f(v.mde50,2)+' pp'],['80%検出力の最小差',v.mde80==null?'到達不可':f(v.mde80,2)+' pp'],['検出力の上限',f(v.ceiling*100,1)+'%']].map(([k,v])=>`<div class="card">${k}<span class="big">${v}</span></div>`).join('');}
function bill(){const n=+$('[data-steps]').value,ratio=+$('[data-price]').value,actual=$('[data-papersteps]').checked,compact=$('[data-compact]').checked;$('[data-steps-label]').textContent=n;$('[data-price-label]').textContent=f(ratio,3);$('[data-steps]').disabled=actual;const colors=['#176d79','#b56332','#6c61a0'];let all=Object.entries(d.bill_params).map(([name,[p,g,N]],j)=>{N=actual?N:n;const values=Array.from({length:N},(_,k)=>p+554+g*(compact?k%60:k));return {name,p,g,N,values,total:values.reduce((a,b)=>a+b,0),c:colors[j]};});const maxN=Math.max(...all.map(a=>a.N)),max=Math.max(...all.flatMap(a=>a.values)),x=k=>55+k/maxN*500,y=v=>230-v/max*190;let s=txt(10,20,'1回の呼び出しで送るトークン数');[0,.5,1].forEach(a=>s+=line(55,y(max*a),565,y(max*a))+txt(5,y(max*a)+4,f(max*a/1000,0)+'k'));all.forEach(a=>{s+=`<polyline points="${a.values.map((v,k)=>`${x(k)},${y(v)}`).join(' ')}" stroke="${a.c}" stroke-width="3" fill="none"/>`;});s+=txt(55,260,'0回')+txt(510,260,maxN+'回');$('[data-billplot]').innerHTML=s;$('[data-bill]').innerHTML=all.map(a=>`<tr><th style="color:${a.c}">${a.name}</th><td>${a.p} / ${a.g}</td><td>${f(a.total/1e6,3)}</td><td>${f(a.total*(.03+.97*ratio)/1e6,3)}</td></tr>`).join('');}
for(const sel of ['[data-n]','[data-q]'])$(sel).addEventListener('change',power);for(const sel of ['[data-steps]','[data-price]','[data-papersteps]','[data-compact]'])$(sel).addEventListener('input',bill);power();bill();
'''

def widget(results):
    if not isinstance(results, dict) or results.get('lab_kind') != 'harness08':
        return ''
    data = json.dumps(results, ensure_ascii=False).replace('<', '\u003c')
    help_text = '<p class="muted">条件を変えると、表示する比較が変わります。画面に収まらない図や表は横へスクロールできます。</p>'
    return ('<section class="b08 harness08" aria-label="論文の比較と、条件を変えて試せる計算">' + STYLE + help_text
            + HARNESS + '<script type="application/json" data-batch08>' + data + '</script>'
            + '<script>(()=>{const root=document.currentScript.parentElement,d=JSON.parse(root.querySelector("[data-batch08]").textContent);'
            + COMMON + HARNESS_JS + '})();</script></section>')
