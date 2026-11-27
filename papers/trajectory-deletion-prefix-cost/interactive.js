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
 document.getElementById('deletion-output').innerHTML=`<p>消さない場合 <strong data-baseline>${fmt(b.total)}</strong> ／ 消す場合 <strong data-changed>${fmt(c.total)}</strong> ／ 費用の差 <strong data-delta>${fmt(c.total-b.total)}</strong> 費用単位</p><p>全呼び出しの入力：${b.tokens} → ${c.tokens}トークン。消す時点：${s.rewrite_call===null?'なし':s.rewrite_call+'回目の通常の呼び出し'}。この作例は、課題を解けるかどうかを計算しません。</p><p>緑は前回と先頭から一致して再利用する記号です。橙は前回にあっても通常の単価になる記号、灰は今回新しく追加した記号です。</p>`+
 '<div class="deletion-ledger tablewrap"><table><caption>履歴を消した場合の内訳（追加の読み取りも1行）</caption><thead><tr><th>回</th><th>入力した記号</th><th>n / c</th><th>再課金</th><th>出力</th><th>費用</th></tr></thead><tbody>'+c.rows.map((r,i)=>{
 const prev=i?c.rows[i-1].prompt:[];
 const strip=r.prompt.map((t,j)=>`<span class="token ${j<r.c?'cached':prev.slice(r.c).includes(t)?'rebilled':'new'}">${j===r.first_changed?'↓':''}${t}</span>`).join('');
 return `<tr><th>${i+1}</th><td><div class="tokens">${strip}</div><small>${r.first_changed===null?'共通部分に変更なし':'前回との最初の違い：'+(r.first_changed+1)+'番目'}</small></td><td>${r.n} / ${r.c}</td><td>${r.rebilled}</td><td>${r.output}</td><td>${fmt(r.cost)}</td></tr>`;
 }).join('')+'</tbody></table></div>';
}
controls.forEach(c=>c.addEventListener('change',render));
document.getElementById('deletion-reset').addEventListener('click',()=>{controls.forEach((c,i)=>c.value=String(initial[i]));render();});
render();
})();
