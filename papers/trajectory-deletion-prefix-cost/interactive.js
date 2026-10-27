(()=>{
'use strict';
const data=JSON.parse(document.getElementById('deletion-data').textContent).synthetic;
const ids=['discount','position','timing','retrieval'];
const controls=ids.map(id=>document.getElementById('deletion-'+id));
const initial=[.9,1,4,0];
const fmt=x=>x.toFixed(2);
function render(){
 const args=controls.map(x=>Number(x.value));
 const s=data.find(s=>ids.every((id,i)=>s.args[id]===args[i]));
 if(!s) throw new Error('Missing teaching case');
 const b=s.baseline,c=s.changed;
 document.getElementById('deletion-output').innerHTML=`<p>削除なし <strong data-baseline>${fmt(b.total)}</strong> ／ 削除あり <strong data-changed>${fmt(c.total)}</strong> ／ 差 <strong data-delta>${fmt(c.total-b.total)}</strong> 費用単位</p><p>延べ入力：${b.tokens} → ${c.tokens}トークン。削除実施：${s.rewrite_call===null?'なし':s.rewrite_call+'回目の通常呼出し'}。成功率は計算しません。</p><p>緑＝再利用／橙＝残っているのに再課金／灰＝新規。枠内の1記号が1トークンです。</p>`+
 '<div class="deletion-ledger"><table><caption>削除側の呼出しごとの台帳（追加読取りも1行）</caption><thead><tr><th>呼出し</th><th>入力列と再利用境界</th><th>n / c</th><th>再課金</th><th>出力</th><th>費用</th></tr></thead><tbody>'+c.rows.map((r,i)=>{
 const prev=i?c.rows[i-1].prompt:[];
 const strip=r.prompt.map((t,j)=>`<span class="token ${j<r.c?'cached':prev.slice(r.c).includes(t)?'rebilled':'new'}">${j===r.first_changed?'↓':''}${t}</span>`).join('');
 return `<tr><th>${i+1}</th><td><div class="tokens">${strip}</div><small>${r.first_changed===null?'共通部分の途中に変更なし':'最初の相違：'+(r.first_changed+1)+'番目'}</small></td><td>${r.n} / ${r.c}</td><td>${r.rebilled}</td><td>${r.output}</td><td>${fmt(r.cost)}</td></tr>`;
 }).join('')+'</tbody></table></div>';
}
controls.forEach(c=>c.addEventListener('change',render));
document.getElementById('deletion-reset').addEventListener('click',()=>{controls.forEach((c,i)=>c.value=String(initial[i]));render();});
render();
})();
