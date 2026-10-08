"""Four paper-specific October 8 interactives; all empirical numbers come from results.json."""
import json

STYLE = '''<style>
.b08{--ink:#203b45;--accent:#176d79;color:var(--ink);padding:clamp(12px,3vw,28px);border:1px solid #bbcecf;border-radius:16px;background:#f3f7f5;margin-top:24px}.b08 *{box-sizing:border-box}.b08.harness08{background:#f4f2fa;--accent:#665289;border-color:#c7bfd8}.b08.traffic08{background:#fff8eb;--accent:#a46b20;border-color:#dec79e}.b08.hear08{background:#eef4fc;--accent:#3c6495;border-color:#b6c8e0}.b08 h3{margin:24px 0 12px}.b08 h4{margin:8px 0}.b08 p{line-height:1.75}.b08 label{display:block;margin:12px 0}.b08 select,.b08 button{font:inherit;padding:8px;max-width:100%;border:1px solid #839ba1;border-radius:6px;background:white;color:#203b45}.b08 button{cursor:pointer}.b08 button:focus-visible,.b08 select:focus-visible,.b08 input:focus-visible{outline:3px solid #cc651f;outline-offset:3px}.b08 input[type=range]{width:100%;max-width:360px;display:block}.b08 .cols{display:grid;grid-template-columns:1fr 1fr;gap:16px}.b08 .card{background:white;padding:14px;border-radius:9px;border-top:3px solid var(--accent)}.b08 .cards{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.b08 .big{display:block;font-size:1.6rem;font-weight:750}.b08 .plot{overflow:auto;max-width:100%;background:#fff;border-radius:8px;margin:12px 0}.b08 svg{display:block;width:100%;height:auto;min-width:500px}.b08 .wide{min-width:550px}.b08 .eq{background:#203b45;color:white;padding:15px;border-radius:8px;font-family:monospace;overflow-wrap:anywhere}.b08 .muted{font-size:.9rem;color:#45616a}.b08 .legend{display:flex;flex-wrap:wrap;gap:15px}.b08 .bar{height:14px;background:var(--accent);border-radius:3px}.b08 .band{border-left:5px solid #d38b36;padding:12px;background:#fff5e8}.b08 table{font-size:.9rem}.b08 th,.b08 td{padding:8px}.b08 .tablewrap{overflow:auto}.b08 .gates{display:grid;gap:8px;counter-reset:gate}.b08 .gates button{text-align:left;counter-increment:gate;border-left:6px solid var(--accent)}.b08 .gates button:before{content:counter(gate) '　';font-weight:bold}.b08 .gates button[aria-pressed=true]{background:#d7ece8}.b08 .junctions{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.b08 .junction{padding:15px;text-align:center;background:#e7ebed;border-radius:6px}.b08 .junction.free{background:#ffd99e}.b08 .lanes{display:grid;grid-template-columns:1fr 1fr;gap:20px;text-align:center;font-weight:bold}.b08 .message{margin:14px 0;padding:12px;border-left:4px solid var(--accent);background:white;opacity:.35}.b08 .message.on{opacity:1}.b08 .message.back{border-left:0;border-right:4px solid #bb642f;text-align:right}.b08 .request{display:inline-block;min-width:30px;margin:2px;padding:6px 4px;font-size:.85rem;border:1px solid #9cacb1;background:#f4ded0}.b08 .request.hit{background:#cee9e1}.b08 .request.selected{outline:3px solid #ca771f}.b08 .request.guard{border-bottom:4px solid #a44830}.b08 .flow{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:12px 0}.b08 .flow div{background:#fff;padding:15px;border-bottom:4px solid var(--accent)}
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
<h3>入荷は方策の応答である</h3>
<div class="flow"><div><b>容量計画 G → λ</b><p>dual coordinatorが共通コストを通知</p></div><div><b>π(X,λ) → 注文 a → 入荷 J</b><p>納期を経た入荷が容量を消費</p></div><div><b>Ĵ=ψ(X,λ) → 容量計画へ</b><p>候補λの応答を先読みして調整</p></div></div>
<p class="band">旧履歴にはπ₀の応答だけが残る。新方策π₁での教師データを、外生系列を固定したrolloutから作る。</p>
<h3>同じ需要を再生し、内生状態だけを計算し直す</h3>
<div class="cols"><label>共通入荷コスト λ<select data-cost><option value="0">0</option><option value="2">2</option><option value="4">4</option></select></label><label>表示週 <output data-week-label></output><input data-week type="range" min="1" max="23" value="8"></label></div>
<div class="plot"><svg viewBox="0 0 600 265" role="img" aria-label="固定需要とλ別の入荷・在庫の時系列" data-replay></svg></div>
<div class="legend"><span style="color:#7d8990">● 需要：全λで同じ</span><span style="color:#176d79">● 入荷</span><span style="color:#b86d34">● 期末在庫</span></div>
<div class="cards" data-stock></div><p class="eq" data-equation aria-live="polite"></p>
<p class="muted">人工24商品。納期は1〜2週。図は需要・入荷・在庫の総量、Eq.2は商品別に計算してから合算する。総量にminを適用したものではない。</p>
<h3>再現性の傾きと、転移後のMAPEを分けて読む</h3>
<div class="cols"><div class="card"><h4>Table 1：実績 / 模擬の回帰</h4><div data-fidelity></div><p class="muted">横軸：模擬、縦軸：実績。傾き1が尺度の一致。R²は別の診断。</p></div><div><label>実配備<select data-study><option>S1</option><option>S2</option></select></label><p>S1：約2万商品・1年<br>S2：約10万商品・3カ月</p><p>● 旧方策履歴　● 模擬学習<br>橙色の線：模擬→逐次補正の点推定値</p></div></div>
<div class="plot"><svg class="wide" viewBox="0 0 600 300" role="img" aria-label="予測期間別MAPEと95%信頼区間" data-transfer></svg></div>
<p class="muted">著者報告 Table 2–3。青緑：模擬、灰：旧履歴、橙：補正後。各群の95% CIであり、対応差のCIではない。補正後のCIは図では省略し、本文の値と原表を参照する。</p>
'''
SIM_JS = r'''
function replay(){const rows=d.traces[$('[data-cost]').value],t=+$('[data-week]').value,r=rows[t];$('[data-week-label]').textContent=t;let s='';const max=Math.max(...Object.values(d.traces).flat().map(r=>Math.max(r.demand,r.inbound,r.inventory))),x=i=>45+i*23,y=v=>225-v/max*190;[0,.5,1].forEach(a=>{s+=line(45,y(max*a),580,y(max*a))+txt(3,y(max*a)+4,f(max*a,0));});for(const [k,c] of [['demand','#7d8990'],['inbound','#176d79'],['inventory','#b86d34']]){s+=`<polyline points="${rows.map((v,i)=>`${x(i)},${y(v[k])}`).join(' ')}" fill="none" stroke="${c}" stroke-width="2.5"/>`;}s+=line(x(t),20,x(t),228,'#172f3b',2)+txt(45,255,'0週')+txt(550,255,'23週');$('[data-replay]').innerHTML=s;$('[data-stock]').innerHTML=[['前週末在庫',r.before],['今週入荷 J',r.inbound],['販売 s',r.sales],['今週発注 a',r.orders]].map(([k,v])=>`<div class="card">${k}<span class="big">${f(v)}</span></div>`).join('');$('[data-equation]').textContent=`Eq.1：過去の発注から納期到来分 ${f(r.inbound)} が入荷。Eq.2：${f(r.before)} + ${f(r.inbound)} − ${f(r.sales)} = 期末在庫 ${f(r.inventory)}`;}
function transfer(){let a=d.paper.studies[$('[data-study]').value],s='',x=i=>105+i*135,y=v=>255-v*6;[0,10,20,30].forEach(v=>s+=line(55,y(v),580,y(v))+txt(15,y(v)+4,v));s+=txt(15,20,'MAPE %');for(let i=0;i<4;i++){for(const [key,ci,dx,col] of [['history','history_ci',-15,'#7d8990'],['sim','sim_ci',10,'#176d79']]){let xx=x(i)+dx;s+=line(xx,y(a[key][i]-a[ci][i]),xx,y(a[key][i]+a[ci][i]),col,2)+dot(xx,y(a[key][i]),col)+txt(xx,y(a[key][i])-8,a[key][i],'middle',col);}s+=line(x(i)+10,y(a.sim[i]),x(i)+30,y(a.cal[i]),'#c27831',3)+dot(x(i)+30,y(a.cal[i]),'#c27831')+txt(x(i),282,d.paper.horizons[i],'middle');}$('[data-transfer]').innerHTML=s;}
$('[data-fidelity]').innerHTML=d.paper.fidelity.map(([name,b,r])=>`<p>${name}　傾き ${f(b,3)} ／ R² ${r}<span class="bar" style="display:block;width:${b*100}%"></span></p>`).join('');$('[data-cost]').addEventListener('change',replay);$('[data-week]').addEventListener('input',replay);$('[data-study]').addEventListener('change',transfer);replay();transfer();
'''

HARNESS = r'''
<h3>差を測る物差し：何も替えない再実行</h3><div class="cards" data-flips></div>
<p class="muted">Fig.2のhard45中央値。成否の反転率であり、成功率の差ではない。</p>
<h3>±5ポイントの帯と、対応差の95%区間</h3><div class="plot"><svg class="wide" role="img" aria-label="pool447のharness間の成功率差と信頼区間" data-forest></svg></div>
<p class="muted">Table 1。単位pp、右が先に書いたharnessの優位。緑の帯は±5。等価性のTOSTには90%区間を使う。95%区間を帯へ収める判定ではない。</p>
<h3>この課題数で、どれほどの差が見えるか</h3>
<div class="cols"><label>対応する課題数 n<select data-n><option>45</option><option>100</option><option>200</option><option selected>447</option><option>800</option></select></label><label>不一致率 q<select data-q><option value="0.07">7%</option><option value="0.14">14%（丸め）</option><option value="0.14008941877794337">14.0089%（hard45実測）</option><option value="0.14392803598200898" selected>14.3928%（pool447実測）</option><option value="0.27">27%</option></select></label></div>
<div class="cards" data-power aria-live="polite"></div><p class="eq">M ~ Binomial(n,q) → B|M ~ Binomial(M,(1+Δ/q)/2) → exact McNemar p≤.05</p><p class="muted">Pythonの厳密計算。差Δはq以下。45件・14%では80%検出力に到達する差が存在しない。447件は丸めた14%なら5.09pp、実測14.3928%なら5.16ppとなり論文の約5.2ppと一致する。</p>
<h3>tokenの請求を、初期入力・履歴増加・step数へ分ける</h3>
<div class="cols"><label>共通step数 <output data-steps-label></output><input data-steps type="range" min="10" max="200" value="80"></label><label>cache hit / miss単価比 <output data-price-label></output><input data-price type="range" min="0.001" max="0.5" step="0.001" value="0.287"></label></div>
<label><input data-papersteps type="checkbox" checked> GLMの代表step数（CC 88 / mini 80 / OC 55）を使う</label>
<label><input data-compact type="checkbox"> 60 stepごとに履歴だけをゼロへ戻す説明用の圧縮</label>
<div class="plot"><svg viewBox="0 0 600 290" role="img" aria-label="3種類のharnessのstep別入力token数" data-billplot></svg></div>
<div class="tablewrap"><table><thead><tr><th>構成</th><th>定型 / 増加</th><th>入力M token</th><th>miss単価換算M</th></tr></thead><tbody data-bill></tbody></table></div>
<p class="muted">Appendix GのP,gと課題文554 token。入力hit率を共通97%と置く近似。出力、実際の圧縮・終了分布を含まない。表の換算量はCNYではない。step数を変えた仮想比較で、論文の順位不変を保証しない。</p>
'''
HARNESS_JS = r'''
$('[data-flips]').innerHTML=['同じharnessの再実行','harness交換','モデル交換'].map((n,i)=>`<div class="card">${n}<span class="big">${d.paper.flip[i]}%</span><div class="bar" style="width:${d.paper.flip[i]*3}%"></div></div>`).join('');forest($('[data-forest]'),d.paper.pairs,-8,15,true);
function power(){let v=d.power_grid.find(x=>x.n===+$('[data-n]').value && x.q===+$('[data-q]').value);$('[data-power]').innerHTML=[['50%検出力の最小差',v.mde50==null?'到達不可':f(v.mde50,2)+' pp'],['80%検出力の最小差',v.mde80==null?'到達不可':f(v.mde80,2)+' pp'],['検出力の上限',f(v.ceiling*100,1)+'%']].map(([k,v])=>`<div class="card">${k}<span class="big">${v}</span></div>`).join('');}
function bill(){const n=+$('[data-steps]').value,ratio=+$('[data-price]').value,actual=$('[data-papersteps]').checked,compact=$('[data-compact]').checked;$('[data-steps-label]').textContent=n;$('[data-price-label]').textContent=f(ratio,3);$('[data-steps]').disabled=actual;const colors=['#176d79','#b56332','#6c61a0'];let all=Object.entries(d.bill_params).map(([name,[p,g,N]],j)=>{N=actual?N:n;const values=Array.from({length:N},(_,k)=>p+554+g*(compact?k%60:k));return {name,p,g,N,values,total:values.reduce((a,b)=>a+b,0),c:colors[j]};});const maxN=Math.max(...all.map(a=>a.N)),max=Math.max(...all.flatMap(a=>a.values)),x=k=>55+k/maxN*500,y=v=>230-v/max*190;let s=txt(10,20,'入力 token / call');[0,.5,1].forEach(a=>s+=line(55,y(max*a),565,y(max*a))+txt(5,y(max*a)+4,f(max*a/1000,0)+'k'));all.forEach(a=>{s+=`<polyline points="${a.values.map((v,k)=>`${x(k)},${y(v)}`).join(' ')}" stroke="${a.c}" stroke-width="3" fill="none"/>`;});s+=txt(55,260,'0 step')+txt(510,260,maxN+' step');$('[data-billplot]').innerHTML=s;$('[data-bill]').innerHTML=all.map(a=>`<tr><th style="color:${a.c}">${a.name}</th><td>${a.p} / ${a.g}</td><td>${f(a.total/1e6,3)}</td><td>${f(a.total*(.03+.97*ratio)/1e6,3)}</td></tr>`).join('');}
for(const sel of ['[data-n]','[data-q]'])$(sel).addEventListener('change',power);for(const sel of ['[data-steps]','[data-price]','[data-papersteps]','[data-compact]'])$(sel).addEventListener('input',bill);power();bill();
'''

TRAFFIC = r'''
<h3>予測を制御へ入れる前の5つの関門</h3>
<div class="cols"><div class="gates" data-gates></div><div class="card" data-gate-detail aria-live="polite"></div></div>
<h3>9交差点でも、選べるのは2地点</h3><div class="cols"><div class="junctions" data-junctions></div><div class="card"><span class="big">1⁷ × 8² = 64</span><p>同じ非空movement集合を重複除去した実効行動。最終版は64組合せを全探索する。</p><p class="muted">模式的な並び。実際の地理や交差点IDの対応を示す地図ではない。</p></div></div>
<h3>周辺の90%被覆は、高需要での90%を意味しない</h3><div class="cols" data-coverage></div>
<h3>凍結テスト7日：正が改善、ゼロをまたぐ区間</h3><div class="plot"><svg class="wide" role="img" aria-label="予測とoracleのqueueおよびspillback改善率と95%CI" data-effects></svg></div>
<p class="muted">Fig.4。独立単位は7日。50,000 bootstrap反復は50,000日分の証拠ではない。</p>
<h3>同じ予測改善を、異なる行動集合へ渡す</h3>
<label>補充の選択肢<select data-actions><option value="one">{8}：1つだけ</option><option value="several">{4,8,12}：需要に応じて替えられる</option><option value="irrelevant">{0,1,2}：複数あるが需要より小さい</option></select></label>
<div class="tablewrap"><table><thead><tr><th>予測</th><th>MAE</th><th>決定費用</th><th>費用削減</th><th>選んだ量</th></tr></thead><tbody data-toy></tbody></table></div><p class="eq" data-oracle aria-live="polite"></p>
<p class="muted">人工600需要、|a−D|の1期間費用。小売への解釈を試すtoyで、交通制御性能の再現ではない。</p>
'''
TRAFFIC_JS = r'''
const gates=[['予測品質','MAE −4.03% / −3.92%','historical meanに対するExtraTreesとhierarchical rolling-shareの改善。区間はLightGBM+CQR。'],['時刻の整合','分mの判断にはm−1起点','未完了の分mの総量をlag-0へ使わない。既に観測した流入を引き、現在slotへ二重に入れない。'],['行動の識別','2/9交差点だけが複数行動','流入口総量だけでは右左折の需要を区別できない。空間分解と実効行動の両方を監査する。'],['oracleの構造的価値','検証日：NO_GO','人工例は内部費用−61.5%。修正後の検証2日ではoracleのqueue改善−1.38%。人工の成功を実需要の合格と混同しない。'],['凍結後の閉ループ価値','安定したqueue便益を未観測','負の結果を定量化するため一度だけ最終7日を評価。全区間がゼロをまたぐ。新しい制御器は新しい分割で評価する。']];let gate=0;
function showGate(){root.querySelectorAll('[data-gates] button').forEach((b,i)=>b.setAttribute('aria-pressed',i===gate));let g=gates[gate];$('[data-gate-detail]').innerHTML=`<h4>${g[0]}</h4><span class="big">${g[1]}</span><p>${g[2]}</p>`;}$('[data-gates]').innerHTML=gates.map((g,i)=>`<button type="button" data-gate="${i}" aria-pressed="false">${g[0]}</button>`).join('');root.querySelectorAll('[data-gate]').forEach(b=>b.addEventListener('click',()=>{gate=+b.dataset.gate;showGate();}));showGate();$('[data-junctions]').innerHTML=d.paper.effective_actions.map(a=>`<div class="junction ${a>1?'free':''}"><b>${a}</b><br>実効行動</div>`).join('');$('[data-coverage]').innerHTML=d.paper.coverage.map((v,i)=>`<div class="card">${i?'事後的な高需要群':'全体'}<span class="big">${v}%</span><div class="bar" style="width:${v}%"></div></div>`).join('');forest($('[data-effects]'),d.paper.effects,-15,15);
function toy(){let c=d.cases[$('[data-actions]').value];$('[data-toy]').innerHTML=Object.entries(c).map(([k,v])=>`<tr><th>${{historical:'historical',improved:'改善した予測',oracle:'oracle'}[k]}</th><td>${f(v.mae,3)}</td><td>${f(v.decision_loss,3)}</td><td>${f(v.value_percent)}%</td><td>${v.actions_used.join(', ')}</td></tr>`).join('');$('[data-oracle]').textContent=c.oracle.value_percent>0?'oracle関門：正の価値あり。このtoyでは改善予測も同じ行動を選べる。':'oracle関門：価値ゼロ。予測だけを改善しても、この行動集合の費用は下がらない。';}$('[data-actions]').addEventListener('change',toy);toy();
'''

HEAR = r'''
<h3>通信の意味を1往復ずつ追う</h3><div class="lanes"><div>Harness<br>役割・依存・再利用予定</div><div>Engine<br>KV・queue・資源圧力</div></div>
<div data-messages></div><button type="button" data-next>次の通信へ</button> <button type="button" data-reset>先頭へ</button><p class="eq" data-force aria-live="polite"></p>
<p class="muted">Fig.2 / Table 1–2を説明する模式例。規格で必須の通信順やwire formatではない。</p>
<h3>平均を縮めても、冷たい要求の待ちは伸びる</h3>
<div class="legend"><span>緑：cache hit</span><span>桃：miss・旧KVを追い出す</span><span>下線：待機保護</span></div>
<div data-timelines></div><div class="card" data-event aria-live="polite"></div>
<div class="plot"><svg viewBox="0 0 600 220" role="img" aria-label="toyの平均と最大TTFT比較" data-latency></svg></div>
<p class="muted">到着：B/Cは0、Aは0,2,…,30。1スロット、KVは1文脈。hit prefill=1、miss=6、decode=1人工秒。待機8秒で保護。Guardは締切保証ではない。</p>
<h3>著者報告：SCBenchとMooncakeを混ぜない</h3>
<label>表示する評価<select data-benchmark><option value="scbench">SCBench：待機と再利用の交換条件</option><option value="mooncake">Mooncake：100%負荷での逆転</option></select></label>
<div class="tablewrap"><table><thead data-paper-head></thead><tbody data-paper-rows></tbody></table></div>
<p class="band" data-paper-note></p>
'''
HEAR_JS = r'''
const messages=[['Execution Description and Intent','Aの文脈v3を次のtool完了後に再利用する見込み →',false,'意図 ≠ 制御：予定を伝えただけではKV保持を命じていない。'],['State and Capabilities','← Aのprefixは今GPU上。prepare操作に対応',true,'観測 ≠ 保証：現在の所在は、次の要求時の予約ではない。'],['Execution Requirements and Control','BのKV準備を要求。待機8秒後は追い越し禁止 →',false,'希望 ≠ 要件：cache優先という希望より、待機保護の要件が優先する。'],['Execution Outcomes','← prepare B: accepted',true,'受理 ≠ 完了：準備はまだ進行中。Bが使えると決めつけない。'],['Execution Outcomes','← prepare B: completed、文脈versionを確認',true,'完了を確認してから利用する。rejected / unsupported / failedは別の結果として扱う。']];let step=0;
function msg(){$('[data-messages]').innerHTML=messages.map((m,i)=>`<div class="message ${m[2]?'back':''} ${i<=step?'on':''}"><b>${m[0]}</b><br>${m[1]}</div>`).join('');$('[data-force]').textContent=messages[step][3];$('[data-next]').disabled=step===messages.length-1;}$('[data-next]').addEventListener('click',()=>{step=Math.min(step+1,messages.length-1);msg();});$('[data-reset]').addEventListener('click',()=>{step=0;msg();});msg();
const names={fcfs:'FCFS',cache:'Cache-Aware',cache_guard:'Cache-Aware + Guard'};$('[data-timelines]').innerHTML=Object.entries(d.cases).map(([k,v])=>`<h4>${names[k]} ／ 完了 ${v.batch}人工秒</h4><div>${v.trace.map((t,i)=>`<button type="button" class="request ${t.hit?'hit':''} ${t.guarded?'guard':''}" data-policy="${k}" data-event-index="${i}" aria-label="${names[k]}の${t.id}、開始${t.start}秒">${t.id}<br>${t.start}–${t.end}</button>`).join('')}</div>`).join('');
function event(k,i){root.querySelectorAll('.request').forEach(b=>b.classList.toggle('selected',b.dataset.policy===k && +b.dataset.eventIndex===i));let t=d.cases[k].trace[i];$('[data-event]').innerHTML=`<b>${names[k]} / ${t.id}</b><p>開始 ${t.start} → 最初のtoken ${t.first} → 完了 ${t.end}。TTFT ${t.ttft}、待機 ${t.wait}人工秒。</p><p>実行前KV：${t.cache_before}。${t.hit?'再利用できた。':t.evicted+'を追い出して再prefill。'} ${t.guarded?'待機保護を適用。':'待機保護なし。'}</p>`;}root.querySelectorAll('[data-event-index]').forEach(b=>b.addEventListener('click',()=>event(b.dataset.policy,+b.dataset.eventIndex)));event('fcfs',0);
let s=txt(5,18,'TTFT（人工秒）'),x=v=>210+v*7;Object.entries(d.cases).forEach(([k,c],i)=>{let y=48+i*58;s+=txt(5,y+8,names[k])+`<rect x="210" y="${y-9}" width="${c.mean_ttft*7}" height="12" fill="#176d79"/><rect x="210" y="${y+7}" width="${c.max_ttft*7}" height="12" fill="#b96335"/>`+txt(x(c.mean_ttft)+5,y+1,f(c.mean_ttft))+txt(x(c.max_ttft)+5,y+19,c.max_ttft);});s+=txt(210,218,'緑：平均　橙：最大');$('[data-latency]').innerHTML=s;
function paper(){let sc=$('[data-benchmark]').value==='scbench';let cols=sc?['構成','P50','P95','最大','batch秒','reuse %']:['構成','P50秒','turns/min'];$('[data-paper-head]').innerHTML='<tr>'+cols.map(c=>`<th>${c}</th>`).join('')+'</tr>';$('[data-paper-rows]').innerHTML=(sc?d.paper.scbench:d.paper.mooncake_100).map(r=>'<tr>'+r.map((x,i)=>i?`<td>${x}</td>`:`<th>${x}</th>`).join('')+'</tr>').join('');$('[data-paper-note]').textContent=sc?'Table 3：87.6%と63.1→4.6秒はSCBench。guardなしの最大TTFTは79.0→93.9秒と悪化。':'Table 4：100%負荷ではSession+Cache+GuardのthroughputがFCFSを下回る。再利用の意図だけで混雑を解決できない。';}$('[data-benchmark]').addEventListener('change',paper);paper();
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
