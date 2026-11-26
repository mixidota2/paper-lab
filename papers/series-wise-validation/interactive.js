(function(){'use strict';const get=k=>document.getElementById('scv-'+k),M=SeriesCV,table=JSON.parse(get('table-data').textContent),keys=['scheme','stage','series','origin','q','method','weather'];let saved=null;
const fmt=v=>v===null?'未定義':Number(v.toPrecision(8)).toString();
const labels={fit:'学習に使う正解値',inner:'内側検証',outer:'外側検証',test:'最終評価',unused:'選択対象外'};
const colors={fit:'#b9dacb',inner:'#f7d085',outer:'#c3b1e1',test:'#efb4b0',unused:'#e6e9ed'};
function parseQ(text){
 if(text==='auto')return null;
 const q=Number(text);
 if(text.trim()===''||!Number.isFinite(q)||q<0||q>100)throw Error('Qにはautoか、0〜100の有限数を入力してください。');
 // A nonzero decimal coefficient must not silently underflow to explicit Q=0.
 if(q===0&&/[1-9]/.test(text.trim().split(/[eE]/)[0]))throw Error('入力したQが小さすぎて0と区別できません。大きい値を入力してください。');
 return q;
}
function render(){
get('json').value='';get('json').disabled=true;get('export-status').textContent='';
try{const scheme=get('scheme').value,stage=get('stage').value,s=get('series').value,o=Number(get('origin').value);if(!['inner','outer','final'].includes(stage)||!Number.isInteger(o)||o<92||o>96||get('origin').value.trim()===''||s.length!==1||!'ABCDEFGHIJ'.includes(s))throw Error('系列と予測起点を確認してください。起点は92〜96の整数です。');const q=parseQ(get('q').value);const toy=M.evaluate(undefined,scheme,q),sensitivity=M.sensitivity(table,get('method').value,get('weather').checked),r=toy.records.find(r=>r.series===s&&r.origin===o);const co=stage==='inner'?84:stage==='outer'?88:o,eligible=stage==='final'||(stage==='inner'?'ABCDE':scheme==='series'?'FG':'ABCDE').includes(s);
let cells='';for(let i=0;i<10;i++)for(let t=1;t<=100;t++){const id='ABCDEFGHIJ'[i],role=M.role(id,t,stage,scheme),context=eligible&&id===s&&t>co-8&&t<=co;cells+=`<rect x="${40+(t-1)*8}" y="${28+i*24}" width="8" height="20" fill="${colors[role]}" ${context?'stroke="#174e9a" stroke-width="2"':''}><title>${id} t${t}：${labels[role]}${context?'／予測に入力する観測値':''}</title></rect>`;}
const names=[...'ABCDEFGHIJ'].map((s,i)=>`<text x="10" y="${43+i*24}">${s}</text>`).join(''),ticks=[1,8,80,84,88,92,96,100].map(t=>`<text x="${40+(t-1)*8}" y="18" font-size="9">${t}</text>`).join('');
get('split').innerHTML=`<svg viewBox="0 0 850 275" role="img" aria-label="系列A〜Jの時点1〜100について、データの用途と予測に使う観測値を表示。下に文字で説明します。">${names}${ticks}${cells}</svg>`;
get('out').textContent=`合成例：${scheme}方式。学習に使う最後の起点は内側80、外側84、最終学習88です。\n選んだ候補は${toy.selection.chosen.family}、傾きの係数は${toy.selection.chosen.scale}です。最終評価は選択に使いません。\n${toy.selection.candidates.map(c=>c.family+' scale='+c.scale+'：内側MAE='+fmt(c.inner_mae)+'／外側MAE='+fmt(c.outer_mae)).join('\n')}\n外側の検証に使う系列：${toy.selection.outer_validation_ids}。最終学習はA〜Gの時点92までです。H〜Jは過去の観測を予測の入力にだけ使います。\n予測に使う過去の観測：${eligible?s+' t'+(co-7)+'..'+co:'なし（この段階の評価対象外）'}。段階の切り替えは図の表示だけを変えます。\n系列${s}の起点${o}から各時点（${r.target_times.join(',')}）を予測した値：${r.prediction.map(fmt).join(', ')}\nQ=${fmt(toy.Q)}、1系列20件を数えるMAE=${fmt(toy.MAE)}、MASE=${fmt(toy.MASE)}\n1系列8時点を同じ重みで数えるMAE=${fmt(toy.equal_target_time_MAE)}\n時点93〜100で誤差を数える回数=${Object.values(toy.weights).join(',')}。予測の起点を動かしてもモデルの重みは変えません。`;
get('table-out').textContent=`論文の表3の丸め済みの値：${sensitivity.method}、${sensitivity.dataset_count}データセット\n表示中の行の平均=${fmt(sensitivity.displayed_row_mean)}／原著掲載の全11平均=${fmt(sensitivity.published_full_mean)}\nTime-CVよりMASEが小さい=${sensitivity.wins_vs_time}、同値=${sensitivity.ties_vs_time}\n改善合計=${fmt(sensitivity.delta_sum)}、差の合計÷Time-CVの合計=${fmt(sensitivity.mean_difference_ratio)}\n差の合計に占めるWeatherの割合=${fmt(sensitivity.weather_contribution)}。Weatherを除くべきだという判断や、信頼区間を示すものではありません。`;
get('table-rows').innerHTML=Object.entries(table.rows).filter(([k])=>get('weather').checked||k!=='Weather').map(([k,v])=>`<tr><th>${k}</th><td>${v[table.methods.indexOf(get('method').value)]}</td><td>${v[6]}</td></tr>`).join('');saved={toy,table3_sensitivity:sensitivity,display:{stage,series:s,origin:o},note:'Synthetic experiment and rounded published table analysis are distinct; not original replication.'};get('error').textContent='';get('download').disabled=false;
}catch(e){saved=null;get('error').textContent=e.message;get('out').textContent='入力不正：結果を保留';get('split').innerHTML='';get('table-out').textContent='';get('table-rows').innerHTML='';get('download').disabled=true;}}
for(const k of keys)get(k).addEventListener(k==='weather'?'change':'input',render);
get('reset').addEventListener('click',()=>{for(const [k,v] of Object.entries({scheme:'series',stage:'final',series:'H',origin:'92',q:'auto',method:'Holdout'}))get(k).value=v;get('weather').checked=true;render();});
get('download').addEventListener('click',()=>{
 if(!saved)return;
 // ダウンロードの可否にかかわらず、同じJSONをコピーできるよう先に表示する。
 const text=JSON.stringify(saved,null,2);get('json').value=text;get('json').disabled=false;
 let url;
 try{
  url=URL.createObjectURL(new Blob([text],{type:'application/json'}));
  const a=document.createElement('a');a.href=url;a.download='series-cv-synthetic.json';a.click();
  get('export-status').textContent='保存用JSONを用意しました。ファイルがダウンロードされない場合は、下の欄からコピーして保存してください。';
 }catch(e){
  get('export-status').textContent='ファイルのダウンロードを開始できませんでした。下のJSON欄からコピーして保存してください。';
 }finally{
  // このダウンロードで作ったURLだけを片付け、後の保存や初期化には触れない。
  if(url)setTimeout(()=>{try{URL.revokeObjectURL(url);}catch(e){}},1000);
 }
});
render();if(saved)for(const k of [...keys,'reset','download'])get(k).disabled=false;
})();
