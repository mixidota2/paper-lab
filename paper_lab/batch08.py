"""Four paper-specific October 8 interactives; all empirical numbers come from results.json."""
import json

STYLE = '''<style>
.b08{--ink:#203b45;--accent:#176d79;color:var(--ink);padding:clamp(12px,3vw,28px);border:1px solid #bbcecf;border-radius:16px;background:#f3f7f5;margin-top:24px}.b08 *{box-sizing:border-box}.b08.harness08{background:#f4f2fa;--accent:#665289;border-color:#c7bfd8}.b08.traffic08{background:#fff8eb;--accent:#a46b20;border-color:#dec79e}.b08.hear08{background:#eef4fc;--accent:#3c6495;border-color:#b6c8e0}.b08 h3{margin:24px 0 12px}.b08 h4{margin:8px 0}.b08 p{line-height:1.75}.b08 label{display:block;margin:12px 0}.b08 select,.b08 button{font:inherit;padding:8px;max-width:100%;border:1px solid #839ba1;border-radius:6px;background:white;color:#203b45}.b08 button{cursor:pointer}.b08 button:focus-visible,.b08 select:focus-visible,.b08 input:focus-visible{outline:3px solid #cc651f;outline-offset:3px}.b08 input[type=range]{width:100%;max-width:360px;display:block}.b08 .cols{display:grid;grid-template-columns:1fr 1fr;gap:16px}.b08 .cols>*{min-width:0}.b08 .card{background:white;padding:14px;border-radius:9px;border-top:3px solid var(--accent)}.b08 .cards{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.b08 .big{display:block;font-size:1.6rem;font-weight:750}.b08 .plot{overflow:auto;max-width:100%;background:#fff;border-radius:8px;margin:12px 0}.b08 svg{display:block;width:100%;height:auto;min-width:500px}.b08 .wide{min-width:550px}.b08 .eq{background:#203b45;color:white;padding:15px;border-radius:8px;font-family:monospace;overflow-wrap:anywhere}.b08 .muted{font-size:.9rem;color:#45616a}.b08 .legend{display:flex;flex-wrap:wrap;gap:15px}.b08 .bar{height:14px;background:var(--accent);border-radius:3px}.b08 .band{border-left:5px solid #d38b36;padding:12px;background:#fff5e8}.b08 table{font-size:.9rem}.b08 th,.b08 td{padding:8px}.b08 .tablewrap{overflow:auto}.b08 .gates{display:grid;gap:8px;counter-reset:gate}.b08 .gates button{text-align:left;counter-increment:gate;border-left:6px solid var(--accent)}.b08 .gates button:before{content:counter(gate) '　';font-weight:bold}.b08 .gates button[aria-pressed=true]{background:#d7ece8}.b08 .junctions{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.b08 .junction{padding:15px;text-align:center;background:#e7ebed;border-radius:6px}.b08 .junction.free{background:#ffd99e}.b08 .lanes{display:grid;grid-template-columns:1fr 1fr;gap:20px;text-align:center;font-weight:bold}.b08 .message{margin:14px 0;padding:12px;border-left:4px solid var(--accent);background:white;opacity:.35}.b08 .message.on{opacity:1}.b08 .message.back{border-left:0;border-right:4px solid #bb642f;text-align:right}.b08 .request{display:inline-block;min-width:30px;margin:2px;padding:6px 4px;font-size:.85rem;border:1px solid #9cacb1;background:#f4ded0}.b08 .request.hit{background:#cee9e1}.b08 .request.selected{outline:3px solid #ca771f}.b08 .request.guard{border-bottom:4px solid #a44830}.b08 .flow{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:12px 0}.b08 .flow div{background:#fff;padding:15px;border-bottom:4px solid var(--accent)}
@media(max-width:650px){.b08 .cols,.b08 .flow{grid-template-columns:1fr}.b08 .cards{grid-template-columns:repeat(2,1fr)}.b08{padding:12px}.b08 .big{font-size:1.3rem}.b08 .junction{padding:10px}.b08 .message{font-size:.9rem}}
</style>'''

COMMON = r'''
const $=s=>root.querySelector(s), f=(x,n=1)=>Number(x).toFixed(n);
const line=(x1,y1,x2,y2,color='#bac7ca',w=1)=>`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="${w}"/>`;
const txt=(x,y,t,anchor='start',color='#203b45')=>`<text x="${x}" y="${y}" text-anchor="${anchor}" font-size="14" fill="${color}">${t}</text>`;
const dot=(x,y,c)=>`<circle cx="${x}" cy="${y}" r="5" fill="${c}"/>`;
function forest(el,rows,min,max,band=false){const x=v=>175+(v-min)/(max-min)*360,H=rows.length*46+60;el.setAttribute('viewBox',`0 0 575 ${H}`);let s='';if(band)s+=`<rect x="${x(-5)}" y="6" width="${x(5)-x(-5)}" height="${H-36}" fill="#e2efe8"/>`;s+=line(x(0),5,x(0),H-35,'#667f86');for(let v=Math.ceil(min/5)*5;v<=max;v+=5){s+=txt(x(v),H-10,v,'middle');}rows.forEach((r,i)=>{let y=25+i*46;s+=txt(8,y+4,r[0])+line(x(r[2]),y,x(r[3]),y,'#176d79',3)+line(x(r[2]),y-5,x(r[2]),y+5,'#176d79',2)+line(x(r[3]),y-5,x(r[3]),y+5,'#176d79',2)+dot(x(r[1]),y,'#bc6536')+txt(x(r[1]),y+20,`${r[1]} [${r[2]}, ${r[3]}]`,'middle');});el.innerHTML=s;}
'''

SIM = r'''
<h3>同じ発注ルールでも、共通の費用を変えると入荷量は変わる</h3>
<p>Gは容量目標で、倉庫が受け入れられる数量を表します。各商品の発注ルールπは、在庫などの状態Xと、全商品に共通の費用λをもとに注文数を決めます。予測器ψは、その費用の候補を使うと全商品で何個届くかを予測します。</p>
<div class="flow"><div><b>容量計画 G → λ</b><p>調整モデルは、受け入れ枠の目標を全商品に共通の費用に置き換えます。</p></div><div><b>π(X,λ) → 注文 a → 入荷 J</b><p>シミュレーターは、納期を迎えた注文を入荷として数えます。</p></div><div><b>Ĵ=ψ(X,λ) → 容量計画へ</b><p>担当者は予測した入荷量を、受け入れ枠と見比べられます。</p></div></div>
<p class="band">旧ルールπ₀の実績だけでは、新ルールπ₁で発注するとどれだけ届くかは分かりません。著者らは過去の需要と納期を使ってπ₁を動かし、そのときの総入荷量を学習データにしました。</p>
<h3>費用だけを変え、発注・入荷・在庫の違いを見る</h3>
<p>この図では、Labが架空の商品で計算した発注・入荷・在庫を表示します。費用と週を選んでください。どの費用でも、需要と納期には同じ値を使います。下の予測誤差の図は、論文の著者らが実際の導入事例で測った値です。</p>
<div class="cols"><label>比較する共通費用 λ<select data-cost><option value="0">0</option><option value="2">2</option><option value="4">4</option></select></label><label>内訳を表示する週 <output data-week-label></output><input data-week type="range" min="1" max="23" value="8"></label></div>
<div class="plot"><svg viewBox="0 0 600 265" role="img" aria-label="選んだ費用で計算した需要・入荷・期末在庫" data-replay></svg></div>
<div class="legend"><span style="color:#7d8990">● 需要（費用を変えても同じ）</span><span style="color:#176d79">● 入荷</span><span style="color:#b86d34">● 期末在庫</span></div>
<div class="cards" data-stock></div><p class="eq" data-equation aria-live="polite"></p>
<p class="muted">Labは24個の架空の商品を使い、納期を1〜2週に設定しました。商品ごとに需要と手元の在庫を比べ、少ないほうを販売数にします。その後、各商品の販売数と在庫数をそれぞれ合計します。</p>
<h3>シミュレーターのずれと、そこで学習した予測器の誤差を分けて読む</h3>
<div class="cols"><div class="card"><h4>表1：各商品の各週で、模擬値と実績を比べる</h4><div data-fidelity></div><p class="muted">著者らは横軸に模擬値、縦軸に実績を置いて回帰しました。傾きが1なら、回帰線上の模擬値と実績は同じです。棒は論文の95%信頼区間の中点だけを表します。R²は、回帰がどの程度当てはまるかを表す別の値です。</p></div><div><label>表示する導入事例<select data-study><option>S1</option><option>S2</option></select></label><p>S1：約2万商品・1年<br>S2：約10万商品・3カ月</p><p>灰：旧ルールの実績で学習　青緑：新ルールの模擬データで学習<br>橙：青緑の予測を導入後の実績で補正</p></div></div>
<div class="plot"><svg class="wide" viewBox="0 0 600 300" role="img" aria-label="予測期間別MAPEと95%信頼区間" data-transfer></svg></div>
<p class="muted">著者らは、各週に出した総入荷量の予測について、絶対誤差を実績で割りました。その割合を、同じ予測期間の値どうしで平均した指標がMAPEです。本文では、実績がゼロの週をどう扱ったかは明示していません。Labの人工例では、入荷実績と1の大きいほうで割ります。<a href="https://arxiv.org/html/2610.03662v1">原典§4・Tables 2–3</a>。灰と青緑の縦線は、各モデルのMAPEに対する95%信頼区間です。モデル間の差に対する区間ではありません。橙は補正後のMAPEの点推定値です。補正後の区間は原論文の表3で確認できます。</p>
'''
SIM_JS = r'''
function replay(){const rows=d.traces[$('[data-cost]').value],t=+$('[data-week]').value,r=rows[t];$('[data-week-label]').textContent=t;let s='';const max=Math.max(...Object.values(d.traces).flat().map(r=>Math.max(r.demand,r.inbound,r.inventory))),x=i=>45+i*23,y=v=>225-v/max*190;[0,.5,1].forEach(a=>{s+=line(45,y(max*a),580,y(max*a))+txt(3,y(max*a)+4,f(max*a,0));});for(const [k,c] of [['demand','#7d8990'],['inbound','#176d79'],['inventory','#b86d34']]){s+=`<polyline points="${rows.map((v,i)=>`${x(i)},${y(v[k])}`).join(' ')}" fill="none" stroke="${c}" stroke-width="2.5"/>`;}s+=line(x(t),20,x(t),228,'#172f3b',2)+txt(45,255,'0週')+txt(550,255,'23週');$('[data-replay]').innerHTML=s;$('[data-stock]').innerHTML=[['前週末在庫',r.before],['今週入荷 J',r.inbound],['販売 s',r.sales],['今週発注 a',r.orders]].map(([k,v])=>`<div class="card">${k}<span class="big">${f(v)}</span></div>`).join('');$('[data-equation]').textContent=`式1：今週は、以前に注文した分のうち ${f(r.inbound)} が届きました。式2：前週末の在庫 ${f(r.before)} に今回の入荷 ${f(r.inbound)} を足し、今週売れた ${f(r.sales)} を引くと、期末には ${f(r.inventory)} 残ります。`;}
function transfer(){let a=d.paper.studies[$('[data-study]').value],s='',x=i=>105+i*135,y=v=>255-v*6;[0,10,20,30].forEach(v=>s+=line(55,y(v),580,y(v))+txt(15,y(v)+4,v));s+=txt(15,20,'MAPE %');for(let i=0;i<4;i++){for(const [key,ci,dx,col] of [['history','history_ci',-15,'#7d8990'],['sim','sim_ci',10,'#176d79']]){let xx=x(i)+dx;s+=line(xx,y(a[key][i]-a[ci][i]),xx,y(a[key][i]+a[ci][i]),col,2)+dot(xx,y(a[key][i]),col)+txt(xx,y(a[key][i])-8,a[key][i],'middle',col);}s+=line(x(i)+10,y(a.sim[i]),x(i)+30,y(a.cal[i]),'#c27831',3)+dot(x(i)+30,y(a.cal[i]),'#c27831')+txt(x(i),282,d.paper.horizons[i],'middle');}$('[data-transfer]').innerHTML=s;}
$('[data-fidelity]').innerHTML=d.paper.fidelity.map(([name,b,r])=>`<p>${name}　傾きの95%信頼区間の中点 ${f(b,3)} ／ R² ${r}<span class="bar" style="display:block;width:${b*100}%"></span></p>`).join('');$('[data-cost]').addEventListener('change',replay);$('[data-week]').addEventListener('input',replay);$('[data-study]').addEventListener('change',transfer);replay();transfer();
'''

HARNESS = r'''
<h3>差を測る物差し：何も替えない再実行</h3><div class="cards" data-flips></div>
<p class="muted">Fig.2のhard45中央値。成否の反転率であり、成功率の差ではない。</p>
<h3>±5ポイントの帯と、対応差の95%区間</h3><div class="plot"><svg class="wide" role="img" aria-label="pool447のharness間の成功率差と信頼区間" data-forest></svg></div>
<p>図のCCはClaude Code、miniはmini-SWE-agent、OCはOpenCodeです。harnessはモデルに渡す指示やツール、履歴、実行の継続・終了を管理する仕組みです。</p>
<p class="muted">Table 1。単位pp（パーセントポイント）、右が先に書いたharnessの優位。緑の帯は±5。差が事前に定めた範囲内かを調べる等価性検定（TOST）には90%区間を使う。95%区間を帯へ収める判定ではない。</p>
<h3>この課題数で、どれほどの差が見えるか</h3>
<p>nは両構成を比較できる課題のペア数、qは同じ課題の成否が構成間で異なる割合です。検出力は、仮定した成功率差Δを検定で見つけられる確率です。到達不可は、そのnとqでは目標の検出力に届かないことを表します。</p>
<div class="cols"><label>対応する課題数 n<select data-n><option>45</option><option>100</option><option>200</option><option selected>447</option><option>800</option></select></label><label>不一致率 q<select data-q><option value="0.07">7%</option><option value="0.14">14%（丸め）</option><option value="0.14008941877794337">14.0089%（45課題の集合hard45での実測）</option><option value="0.14392803598200898" selected>14.3928%（447課題の集合pool447での実測）</option><option value="0.27">27%</option></select></label></div>
<div class="cards" data-power aria-live="polite"></div><p class="eq">M ~ Binomial(n,q) → B|M ~ Binomial(M,(1+Δ/q)/2) → exact McNemar p≤.05</p><p class="muted">Pythonの厳密計算。差Δはq以下。45件・14%では80%検出力に到達する差が存在しない。447件は丸めた14%なら5.09pp、実測14.3928%なら5.16ppとなり論文の約5.2ppと一致する。</p>
<h3>入力トークンの費用を、初期入力・履歴の増加・実行ステップ数に分けて考える</h3>
<div class="cols"><label>共通の実行ステップ数 <output data-steps-label></output><input data-steps type="range" min="10" max="200" value="80"></label><label>再利用時÷非再利用時の入力単価 <output data-price-label></output><input data-price type="range" min="0.001" max="0.5" step="0.001" value="0.287"></label></div>
<label><input data-papersteps type="checkbox" checked> GLMの代表的な実行ステップ数（CC 88 / mini 80 / OC 55）を使う</label>
<label><input data-compact type="checkbox"> 60ステップごとに履歴だけをゼロへ戻す説明用の圧縮</label>
<div class="plot"><svg viewBox="0 0 600 290" role="img" aria-label="3種類のharnessの実行ステップごとの入力トークン数" data-billplot></svg></div>
<div class="tablewrap"><table><thead><tr><th>構成</th><th>固定入力量 / 1ステップの追加量</th><th>入力トークン数（百万）</th><th>非再利用時の単価への換算量（百万トークン）</th></tr></thead><tbody data-bill></tbody></table></div>
<p class="muted">Appendix GのP,gと課題文554トークン。入力のキャッシュ再利用率を共通97%と置く近似。出力、実際の圧縮・終了分布を含まない。Mは百万、図のkは千を表す。表はトークン数の換算量であり、金額ではない。実行ステップ数を変えた仮想比較で、論文の順位不変を保証しない。</p>
'''
HARNESS_JS = r'''
$('[data-flips]').innerHTML=['同じharnessの再実行','harness交換','モデル交換'].map((n,i)=>`<div class="card">${n}<span class="big">${d.paper.flip[i]}%</span><div class="bar" style="width:${d.paper.flip[i]*3}%"></div></div>`).join('');forest($('[data-forest]'),d.paper.pairs,-8,15,true);
function power(){let v=d.power_grid.find(x=>x.n===+$('[data-n]').value && x.q===+$('[data-q]').value);$('[data-power]').innerHTML=[['50%検出力の最小差',v.mde50==null?'到達不可':f(v.mde50,2)+' pp'],['80%検出力の最小差',v.mde80==null?'到達不可':f(v.mde80,2)+' pp'],['検出力の上限',f(v.ceiling*100,1)+'%']].map(([k,v])=>`<div class="card">${k}<span class="big">${v}</span></div>`).join('');}
function bill(){const n=+$('[data-steps]').value,ratio=+$('[data-price]').value,actual=$('[data-papersteps]').checked,compact=$('[data-compact]').checked;$('[data-steps-label]').textContent=n;$('[data-price-label]').textContent=f(ratio,3);$('[data-steps]').disabled=actual;const colors=['#176d79','#b56332','#6c61a0'];let all=Object.entries(d.bill_params).map(([name,[p,g,N]],j)=>{N=actual?N:n;const values=Array.from({length:N},(_,k)=>p+554+g*(compact?k%60:k));return {name,p,g,N,values,total:values.reduce((a,b)=>a+b,0),c:colors[j]};});const maxN=Math.max(...all.map(a=>a.N)),max=Math.max(...all.flatMap(a=>a.values)),x=k=>55+k/maxN*500,y=v=>230-v/max*190;let s=txt(10,20,'1回の呼出し当たりの入力トークン数');[0,.5,1].forEach(a=>s+=line(55,y(max*a),565,y(max*a))+txt(5,y(max*a)+4,f(max*a/1000,0)+'k'));all.forEach(a=>{s+=`<polyline points="${a.values.map((v,k)=>`${x(k)},${y(v)}`).join(' ')}" stroke="${a.c}" stroke-width="3" fill="none"/>`;});s+=txt(55,260,'0ステップ')+txt(510,260,maxN+'ステップ');$('[data-billplot]').innerHTML=s;$('[data-bill]').innerHTML=all.map(a=>`<tr><th style="color:${a.c}">${a.name}</th><td>${a.p} / ${a.g}</td><td>${f(a.total/1e6,3)}</td><td>${f(a.total*(.03+.97*ratio)/1e6,3)}</td></tr>`).join('');}
for(const sel of ['[data-n]','[data-q]'])$(sel).addEventListener('change',power);for(const sel of ['[data-steps]','[data-price]','[data-papersteps]','[data-compact]'])$(sel).addEventListener('input',bill);power();bill();
'''

TRAFFIC = r'''
<h3>予測から信号制御までの5つの確認</h3>
<p>著者は予測誤差を測り、判断に使う時刻、信号の候補、将来を知らせた場合の効果を確認しました。ボタンごとに、点検した条件と結果が表示されます。</p>
<div class="cols"><div class="gates" data-gates></div><div class="card" data-gate-detail aria-live="polite"></div></div>
<h3>9交差点で車を通せる方向の組み合わせ</h3><div class="cols"><div class="junctions" data-junctions></div><div class="card"><span class="big">1⁷ × 8² = 64</span><p>著者は、通せる方向が同じ候補をまとめ、通せる方向がない候補を除きました。2地点だけに8つずつ候補が残り、組み合わせは最大64通りです。制御器はその時点で切り替え可能な組み合わせをすべて比べます。</p><p class="muted">図の並びは、交差点の所在地や番号を示していません。</p></div></div>
<h3>名目90%の予測区間に実績が入った割合</h3><div class="cols" data-coverage></div>
<h3>最終7日間の改善率と95%信頼区間</h3><div class="plot"><svg class="wide" role="img" aria-label="待ち行列と上流への滞留の改善率、95%信頼区間。すべての区間が0を含む" data-effects></svg></div>
<p>将来を使わない同じ制御器と比べた改善率です。負の値は悪化を示します。上流への滞留とは、下流でできた列が上流へはみ出すことです。将来の流入を知らせた条件は比較用で、実際に使える予測器ではありません。</p>
<p class="muted">原論文の図4です。著者は同じ日の結果を対にし、7日を50,000回引き直して区間を計算しました。いずれの区間も0をまたぎます。</p>
<h3>補充量の候補ごとの予測誤差と費用</h3>
<p>人工需要600件で、いつも8と予測する基準、需要に最大1のずれを加えた予測、正確な需要を知らせる条件を比べます。予測値に最も近い候補を選び、実際の需要との差の絶対値を平均します。費用の削減率は、基準予測から減った費用を、同じ候補で基準予測を使ったときの費用で割ります。</p>
<label>選べる補充量<select data-actions><option value="one">{8}：8だけを選べる</option><option value="several">{4,8,12}：需要と同じ量を選べる</option><option value="irrelevant">{0,1,2}：どの候補も需要より少ない</option></select></label>
<div class="tablewrap"><table><thead><tr><th>予測</th><th>MAE</th><th>平均費用</th><th>費用の削減率</th><th>選んだ補充量</th></tr></thead><tbody data-toy></tbody></table></div><p class="eq" data-oracle aria-live="polite"></p>
<p class="muted">1期間だけの比較で、余りと不足を同じ重みで数えます。交通や実店舗の結果ではありません。</p>
'''
TRAFFIC_JS = r'''
const gates=[['予測誤差','流入口のMAEは4.03%、方向別は3.92%減少','流入口の平均絶対誤差は、ExtraTreesを使うと過去平均より下がりました。進行方向別では、流入口の予測を方向の比率で分けます。予測区間はLightGBMの分位点を別の日のデータで調整しました。'],['判断に使える時刻','分mの予測には分m−1までの情報を使う','分mの途中に信号を選ぶときは、その分の実績総量を使いません。予測総量から、すでに観測した台数を引き、残りが負なら0にしてまだ観測していない時間へ割り振ります。'],['信号の選択肢','9交差点のうち2地点（2/9）で候補が複数','流入口の総量が同じでも、右折車と左折車の数は違うことがあります。著者は進行方向別の予測を使い、その方向を通す信号を選べるか確認しました。'],['将来の流入を知らせる試験','検証2日では採用条件を満たさず（NO_GO）','人工交差点では、通す方向が変わり、内部計算の費用が61.5%下がりました。交通記録をもとにした検証2日では、将来を知らせても待ち行列の改善率は−1.38%でした。'],['設定を固定した最終評価','待ち行列の安定した削減は確認できず','著者は差の大きさを調べるため、設定を変えずに7日間を1回だけ評価しました。図の信頼区間はすべて0を含みます。結果を見てから採用の指標を変更していません。']];let gate=0;
function showGate(){root.querySelectorAll('[data-gates] button').forEach((b,i)=>b.setAttribute('aria-pressed',i===gate));let g=gates[gate];$('[data-gate-detail]').innerHTML=`<h4>${g[0]}</h4><span class="big">${g[1]}</span><p>${g[2]}</p>`;}$('[data-gates]').innerHTML=gates.map((g,i)=>`<button type="button" data-gate="${i}" aria-pressed="false">${g[0]}</button>`).join('');root.querySelectorAll('[data-gate]').forEach(b=>b.addEventListener('click',()=>{gate=+b.dataset.gate;showGate();}));showGate();$('[data-junctions]').innerHTML=d.paper.effective_actions.map(a=>`<div class="junction ${a>1?'free':''}"><b>${a}</b><br>信号の候補</div>`).join('');$('[data-coverage]').innerHTML=d.paper.coverage.map((v,i)=>`<div class="card">${i?'実績で選んだ高需要群':'全体'}<span class="big">${v}%</span><div class="bar" style="width:${v}%"></div></div>`).join('');forest($('[data-effects]'),d.paper.effects,-15,15);
function toy(){let c=d.cases[$('[data-actions]').value];$('[data-toy]').innerHTML=Object.entries(c).map(([k,v])=>`<tr><th>${{historical:'基準予測（常に8）',improved:'需要を最大1ずらした予測',oracle:'正確な需要を知らせる条件'}[k]}</th><td>${f(v.mae,3)}</td><td>${f(v.decision_loss,3)}</td><td>${f(v.value_percent)}%</td><td>${v.actions_used.join(', ')}</td></tr>`).join('');$('[data-oracle]').textContent=c.oracle.value_percent>0?'この候補では、正確な需要を知らせると平均費用が下がりました。ずらした予測でも、実際の需要と同じ量を選べます。':'この候補では、予測を替えても同じ補充量を選びます。正確な需要を知らせても平均費用は変わりませんでした。';}$('[data-actions]').addEventListener('change',toy);toy();
'''

HEAR = r'''
<h3>操作を頼んでから結果が返るまで</h3><div class="lanes"><div>手順を管理する側（ハーネス）<br>役割、依存関係、再利用の予定</div><div>推論を実行する側（エンジン）<br>キャッシュ、待ち行列、混雑状況</div></div>
<div data-messages></div><button type="button" data-next>次のメッセージ</button> <button type="button" data-reset>最初に戻す</button><p class="eq" data-force aria-live="polite"></p>
<p class="muted">原論文の図2と表1–2を基にした説明です。この通信順やデータ形式は規格で決まっていません。prepareはキャッシュを使う準備を指します。</p>
<h3>三つの処理順で要求の待ち時間を比べる</h3>
<p>FCFSは到着順、Cache-Awareはキャッシュを再利用できる要求を先に処理します。Guardは長く待った要求を次の処理で保護します。TTFTは要求が届いてから最初のトークンが出るまでの時間です。</p>
<div class="legend"><span>緑：保存済みの計算を再利用</span><span>桃：以前のキャッシュを削除して再計算</span><span>下線：待機保護を適用</span></div>
<div data-timelines></div><div class="card" data-event aria-live="polite"></div>
<div class="plot"><svg viewBox="0 0 600 220" role="img" aria-label="合成例でのTTFTの平均と最大値" data-latency></svg></div>
<p class="muted">BとCは時刻0、Aは時刻0から30まで2秒ごとに届きます。一度に一つの要求を処理し、保存できる文脈は一つです。入力の処理は再利用できれば1秒、できなければ6秒、出力は1秒と仮定します。待機保護の8秒は次の要求を選ぶ基準で、締切ではありません。</p>
<h3>著者が報告したSCBenchとMooncakeの結果</h3>
<label>表示するベンチマーク<select data-benchmark><option value="scbench">SCBench：キャッシュと待ち時間</option><option value="mooncake">Mooncake：負荷100%の処理数</option></select></label>
<div class="tablewrap"><table><thead data-paper-head></thead><tbody data-paper-rows></tbody></table></div>
<p class="band" data-paper-note></p>
'''
HEAR_JS = r'''
const messages=[['実行内容と予定（Execution Description and Intent）','次のツールが終わったら、文脈Aの第3版を再利用する見込み →',false,'再利用の予定を知らせただけで、保存しておくよう求めたわけではありません。'],['状態と対応機能（State and Capabilities）','← 文脈Aの先頭部分は今GPUにあり、準備操作に対応しています。',true,'今キャッシュがあることと、次の要求まで予約することは異なります。'],['実行要件と制御（Execution Requirements and Control）','文脈Bのキャッシュの準備を要求。8秒待ったら次の処理で追い越さない →',false,'キャッシュ優先は希望ですが、長く待った要求を先に処理するのは要件です。'],['実行結果（Execution Outcomes）','← 文脈Bの準備の要求を受理（accepted）',true,'要求を受理しても、準備が終わったとは限りません。完了を確認してからBを使います。'],['実行結果（Execution Outcomes）','← 文脈Bの準備が完了（completed）。文脈の版を確認',true,'準備の完了を確認しました。拒否（rejected）、操作に未対応（unsupported）、実行の失敗（failed）はそれぞれ別の結果です。']];let step=0;
function msg(){$('[data-messages]').innerHTML=messages.map((m,i)=>`<div class="message ${m[2]?'back':''} ${i<=step?'on':''}"><b>${m[0]}</b><br>${m[1]}</div>`).join('');$('[data-force]').textContent=messages[step][3];$('[data-next]').disabled=step===messages.length-1;}$('[data-next]').addEventListener('click',()=>{step=Math.min(step+1,messages.length-1);msg();});$('[data-reset]').addEventListener('click',()=>{step=0;msg();});msg();
const names={fcfs:'FCFS',cache:'Cache-Aware',cache_guard:'Cache-Aware + Guard'};$('[data-timelines]').innerHTML=Object.entries(d.cases).map(([k,v])=>`<h4>${names[k]} ／ 全要求が終わるまで ${v.batch}人工秒</h4><div>${v.trace.map((t,i)=>`<button type="button" class="request ${t.hit?'hit':''} ${t.guarded?'guard':''}" data-policy="${k}" data-event-index="${i}" aria-label="${names[k]}の${t.id}、時刻${t.start}に開始">${t.id}<br>${t.start}–${t.end}</button>`).join('')}</div>`).join('');
function event(k,i){root.querySelectorAll('.request').forEach(b=>b.classList.toggle('selected',b.dataset.policy===k && +b.dataset.eventIndex===i));let t=d.cases[k].trace[i];$('[data-event]').innerHTML=`<b>${names[k]} / ${t.id}</b><p>時刻${t.start}に開始、${t.first}に最初のトークン、${t.end}に完了。TTFTは${t.ttft}秒、開始までの待ちは${t.wait}秒です（仮定した秒数）。</p><p>処理を始める前にキャッシュにあった文脈：${t.cache_before}。${t.hit?'そのまま再利用しました。':t.evicted+'を削除して入力を計算しました。'} ${t.guarded?'待機保護を適用しました。':'待機保護は適用していません。'}</p>`;}root.querySelectorAll('[data-event-index]').forEach(b=>b.addEventListener('click',()=>event(b.dataset.policy,+b.dataset.eventIndex)));event('fcfs',0);
let s=txt(5,18,'TTFT（人工秒）'),x=v=>210+v*7;Object.entries(d.cases).forEach(([k,c],i)=>{let y=48+i*58;s+=txt(5,y+8,names[k])+`<rect x="210" y="${y-9}" width="${c.mean_ttft*7}" height="12" fill="#176d79"/><rect x="210" y="${y+7}" width="${c.max_ttft*7}" height="12" fill="#b96335"/>`+txt(x(c.mean_ttft)+5,y+1,f(c.mean_ttft))+txt(x(c.max_ttft)+5,y+19,c.max_ttft);});s+=txt(210,218,'緑：平均値　橙：最大値');$('[data-latency]').innerHTML=s;
function paper(){let sc=$('[data-benchmark]').value==='scbench';let cols=sc?['構成','TTFT中央値（秒）','TTFTの95パーセンタイル（秒）','最大TTFT（秒）','全要求の処理時間（秒）','KV再利用率（%）']:['構成','TTFT中央値（秒）','1分当たりの処理ターン数'];$('[data-paper-head]').innerHTML='<tr>'+cols.map(c=>`<th>${c}</th>`).join('')+'</tr>';$('[data-paper-rows]').innerHTML=(sc?d.paper.scbench:d.paper.mooncake_100).map(r=>'<tr>'+r.map((x,i)=>i?`<td>${x}</td>`:`<th>${x}</th>`).join('')+'</tr>').join('');$('[data-paper-note]').textContent=sc?'表3のSCBenchでは、キャッシュだけを優先すると再利用率は87.6%、TTFTの中央値は63.1秒から4.6秒になりました。最大値は79.0秒から93.9秒に延びました。':'表4のMooncakeでは、負荷100%で三つの方法を合わせると、1分あたり108.9ターンでした。到着順の122.7ターンより少なくなりました。';}$('[data-benchmark]').addEventListener('change',paper);paper();
'''


def widget(results):
    if not isinstance(results, dict):
        return ''
    spec = {'sim08': (SIM, SIM_JS), 'harness08': (HARNESS, HARNESS_JS),
            'traffic08': (TRAFFIC, TRAFFIC_JS), 'hear08': (HEAR, HEAR_JS)}.get(results.get('lab_kind'))
    if not spec:
        return ''
    body, js = spec
    data = json.dumps(results, ensure_ascii=False).replace('<', '\\u003c')
    return ('<section class="b08 ' + results['lab_kind'] + '" aria-label="論文別の対話図">' + STYLE + '<p class="muted">操作して比較する。幅の広い図と表は横へスクロールできます。</p>' + body
            + '<script type="application/json" data-batch08>' + data + '</script>'
            + '<script>(()=>{const root=document.currentScript.parentElement,d=JSON.parse(root.querySelector("[data-batch08]").textContent);'
            + COMMON + js + '})();</script></section>')
