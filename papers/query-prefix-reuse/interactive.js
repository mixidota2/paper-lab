/* 画面の操作とJSON保存を結ぶ処理。模擬テストは実ブラウザの表示検査ではない。 */
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
  const route=r.route==='cold-e2e'?'準備なし：別の0.5Bモデルが四層すべてを生成します':r.route==='prepared-root'?'準備済みで深さ0：根から番号を補い、第4層の採点後に枝を選びます':'準備済み：保存した先頭から今の履歴で残りを補い、第4層の採点後に枝を選びます';
  const tree=Array.from({length:4},(_,j)=>'<li>L'+(j+1)+'：'+[...new Set(r.reachable.map(s=>s.slice(0,j+1)))].join(' / ')+'</li>').join('');
  const ranking=r.ranking.length?r.ranking.map(v=>v.sid+'（点 '+v.score+'）').join(' → '):'枝の上限が0なので、順位表は空です';
  const rows=ReuseGR.table1.map(v=>'<tr><th>'+v.method+'</th><td>'+v[metric].toFixed(2)+'%</td><td>'+v.ms.toFixed(2)+' ms</td></tr>').join('');
  get('route').textContent=route+'。今回の検索は7Bモデルを待ちません。'+(r.async_prepare?'深さが正なので、次の検索に向けて事前準備を依頼します。':'次回用の準備は依頼しません。');
  get('tree').innerHTML=tree;
  get('rank').textContent='目標のSID：'+r.target+'。'+(r.target_reachable?'候補に入る。':'候補に入らない。')+(r.target_returned?'順位表に残る。':'順位表には残らない。')+'\n'+ranking;
  get('budget-result').textContent='第4層の'+r.l4_scored+'件を採点し、'+r.branches.length+'本の枝から'+r.admitted.length+'本を残しました。順位表には'+r.ranking.length+'件が入ります。'+(prepared==='no'?'準備なしの経路では枝の上限を使いません。':'枝の上限を変えても、先に採点した件数は減りません。');
  get('mix').textContent='P='+ (mix.p*100).toFixed(2)+'%：'+mix.p+' × 71.45 + '+(1-mix.p).toFixed(4)+' × 117.00 = '+mix.mean_ms.toFixed(2)+' ms（混合した平均の推計）\nHR@100の推計： '+mix.hr_percent.toFixed(2)+'%／Recall@100の推計： '+mix.recall_percent.toFixed(2)+'%';
  get('preset-note').textContent=preset?'表5の'+preset.name+'：Q='+preset.q.toFixed(2)+'%（検索語の種類）、P='+preset.p.toFixed(2)+'%（ログ行）。論文のHR '+preset.hr.toFixed(2)+'% ['+preset.quality+']、平均時間 '+preset.ms.toFixed(2)+' ms。Static Qの実測82.38%と、同じPでの推計83.40%は別です。':'Pを変更しました。検索語の種類の割合QはPから求めません。品質は検索語ごとの平均を端点に使う推計です。';
  get('table-body').innerHTML=rows;
  get('metric-label').textContent=metric==='hr'?'HR@100：正解SIDが一つ以上入った検索語の割合':'SID Recall@100：検索語ごとに正解SIDを何割拾えたかを平均';
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
 // ダウンロードできない場合も、同じJSONをコピーできるように表示する。
 const text=JSON.stringify(saved,null,2)+'\n';get('json').value=text;get('json').disabled=false;
 let url;
 try {
  const b=new Blob([text],{type:'application/json'});url=URL.createObjectURL(b);
  const a=document.createElement('a');a.href=url;a.download='query-prefix-reuse-synthetic.json';a.click();
  get('export-status').textContent='保存用JSONを用意しました。ファイルがダウンロードされない場合は、下の欄からコピーして保存してください。';
 } catch(e) {
  get('export-status').textContent='ファイルのダウンロードを開始できませんでした。下のJSON欄からコピーして保存してください。';
 } finally {
  // ブラウザがURLを使えるよう、破棄まで時間を置く。
  if(url)setTimeout(()=>{try{URL.revokeObjectURL(url);}catch(e){}},1000);
 }
});
render();
if(saved)for(const id of [...controls,'reset','download'])get(id).disabled=false;
})();
