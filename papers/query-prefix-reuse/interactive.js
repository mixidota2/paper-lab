/* Actual event handlers; synthetic tests are not browser rendering tests. */
(()=>{
'use strict';
const get=id=>document.getElementById('rg-'+id);
const controls=['prepared','depth','query','history','budget','preset','p','metric'];
let saved=null;
function number(id){const s=get(id).value;if(s.trim()==='')throw Error('空の数値入力');return Number(s);}
function render(){
 get('json').value='';get('json').disabled=true;get('export-status').textContent='';
 try {
  const prepared=get('prepared').value;
  if(!['yes','no'].includes(prepared))throw Error('準備状態が不正');
  const r=ReuseGR.toy(prepared==='yes',number('depth'),get('query').value,get('history').value,number('budget'));
  const mix=ReuseGR.projection(number('p')/100),metric=get('metric').value;
  if(!['hr','recall'].includes(metric))throw Error('指標が不正');
  const k=get('preset').value;
  if(k!=='custom'&&!/^[0-5]$/.test(k))throw Error('プリセットが不正');
  const preset=k==='custom'?null:ReuseGR.presets[Number(k)];
  const route=r.route==='cold-e2e'?'Cold：別の0.5B E2E → 応答':r.route==='prepared-root'?'Prepared d=0：空のroot → LeafFill → L4採点 → admission → 応答':'Prepared：query prefix → 現在の履歴でsuffix → L4採点 → admission → 応答';
  const tree=Array.from({length:4},(_,j)=>'<li>L'+(j+1)+'：'+[...new Set(r.reachable.map(s=>s.slice(0,j+1)))].join(' / ')+'</li>').join('');
  const ranking=r.ranking.length?r.ranking.map(v=>v.sid+' (score '+v.score+')').join(' → '):'採用なし（合成budget=0）';
  const rows=ReuseGR.table1.map(v=>'<tr><th>'+v.method+'</th><td>'+v[metric].toFixed(2)+'%</td><td>'+v.ms.toFixed(2)+' ms</td></tr>').join('');
  get('route').textContent=route+'。7B待機なし。非同期準備：'+(r.async_prepare?'positive-depth missをキューへ送る想定':'なし');
  get('tree').innerHTML=tree;
  get('rank').textContent='合成目標SID '+r.target+'／到達可能 '+r.target_reachable+'／返却 '+r.target_returned+'\n'+ranking;
  get('budget-result').textContent='L4採点済み '+r.l4_scored+'葉 → '+r.branches.length+'枝のうち '+r.admitted.length+'枝を採用 → '+r.ranking.length+'葉を順位付け。'+(prepared==='no'?'Coldではadmissionを使わずbudgetを無視。':'採用数を変えてもL4採点済みの葉数は減りません。');
  get('mix').textContent='P='+ (mix.p*100).toFixed(2)+'%：'+mix.p+' × 71.45 + '+(1-mix.p).toFixed(4)+' × 117.00 = '+mix.mean_ms.toFixed(2)+' ms（平均の投影）\nHR@100投影 '+mix.hr_percent.toFixed(2)+'%／Recall@100投影 '+mix.recall_percent.toFixed(2)+'%';
  get('preset-note').textContent=preset?'Table 5 '+preset.name+'：Q='+preset.q.toFixed(2)+'%（query数）、P='+preset.p.toFixed(2)+'%（logged rows）。掲載HR '+preset.hr.toFixed(2)+'% ['+preset.quality+']、掲載mean '+preset.ms.toFixed(2)+' ms。Static Qの82.38%はpartition実測であり、同じPの投影83.40%と別です。':'任意P：Qは未指定です。PからQを推定しません。品質は固定query-macro端点の補間仮定です。';
  get('table-body').innerHTML=rows;
  get('metric-label').textContent=metric==='hr'?'HR@100：正解SIDを1つ以上得たqueryの割合':'SID Recall@100：各queryの正解SID回収割合のquery平均';
  saved={synthetic:true,model_version:ReuseGR.version,toy:r,projection:mix,preset,metric};
  get('error').textContent='';get('download').disabled=false;
 } catch(e){saved=null;get('error').textContent='入力エラー：'+e.message+'。表示結果は直前の有効条件です。保存できません。';get('download').disabled=true;}
}
function reset(){for(const [k,v] of Object.entries({prepared:'yes',depth:'1',query:'wide',history:'left',budget:'4',preset:'0',p:'100',metric:'hr'}))get(k).value=v;render();}
for(const id of controls)for(const event of ['input','change'])get(id).addEventListener(event,()=>{
 if(id==='preset'&&/^[0-5]$/.test(get(id).value))get('p').value=String(ReuseGR.presets[Number(get(id).value)].p);
 if(id==='p')get('preset').value='custom';render();
});
get('reset').addEventListener('click',reset);
get('download').addEventListener('click',()=>{
 if(!saved)return;
 // Keep the exact file contents available even if browser download APIs fail.
 const text=JSON.stringify(saved,null,2)+'\n';get('json').value=text;get('json').disabled=false;
 let url;
 try {
  const b=new Blob([text],{type:'application/json'});url=URL.createObjectURL(b);
  const a=document.createElement('a');a.href=url;a.download='query-prefix-reuse-synthetic.json';a.click();
  get('export-status').textContent='保存用JSONを用意しました。ファイルがダウンロードされない場合は、下の欄からコピーして保存してください。';
 } catch(e) {
  get('export-status').textContent='ファイルのダウンロードを開始できませんでした。下のJSON欄からコピーして保存してください。';
 } finally {
  // Do not revoke before the browser has had a chance to consume the URL.
  if(url)setTimeout(()=>{try{URL.revokeObjectURL(url);}catch(e){}},1000);
 }
});
render();
if(saved)for(const id of [...controls,'reset','download'])get(id).disabled=false;
})();
