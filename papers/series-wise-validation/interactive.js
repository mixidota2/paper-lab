(function(){'use strict';const get=k=>document.getElementById('scv-'+k),M=SeriesCV,table=JSON.parse(get('table-data').textContent),keys=['scheme','stage','series','origin','q','method','weather'];let saved=null;
const fmt=v=>v===null?'未定義':Number(v.toPrecision(8)).toString();
const labels={fit:'学習ラベル',inner:'内側検証',outer:'外側検証',test:'最終test',unused:'選択対象外'};
const colors={fit:'#b9dacb',inner:'#f7d085',outer:'#c3b1e1',test:'#efb4b0',unused:'#e6e9ed'};
function parseQ(text){
 if(text==='auto')return null;
 const q=Number(text);
 if(text.trim()===''||!Number.isFinite(q)||q<0||q>100)throw Error('Qはautoまたは0〜100の有限数です。');
 // A nonzero decimal coefficient must not silently underflow to explicit Q=0.
 if(q===0&&/[1-9]/.test(text.trim().split(/[eE]/)[0]))throw Error('Qが小さすぎて0になります。値を大きくして入力してください。');
 return q;
}
function render(){try{const scheme=get('scheme').value,stage=get('stage').value,s=get('series').value,o=Number(get('origin').value);if(!['inner','outer','final'].includes(stage)||!Number.isInteger(o)||o<92||o>96||get('origin').value.trim()===''||s.length!==1||!'ABCDEFGHIJ'.includes(s))throw Error('系列とorigin（92〜96の整数）を確認してください。');const q=parseQ(get('q').value);const toy=M.evaluate(undefined,scheme,q),sensitivity=M.sensitivity(table,get('method').value,get('weather').checked),r=toy.records.find(r=>r.series===s&&r.origin===o);const co=stage==='inner'?84:stage==='outer'?88:o,eligible=stage==='final'||(stage==='inner'?'ABCDE':scheme==='series'?'FG':'ABCDE').includes(s);
let cells='';for(let i=0;i<10;i++)for(let t=1;t<=100;t++){const id='ABCDEFGHIJ'[i],role=M.role(id,t,stage,scheme),context=eligible&&id===s&&t>co-8&&t<=co;cells+=`<rect x="${40+(t-1)*8}" y="${28+i*24}" width="8" height="20" fill="${colors[role]}" ${context?'stroke="#174e9a" stroke-width="2"':''}><title>${id} t${t}：${labels[role]}${context?'／予測入力context（学習用途とは別）':''}</title></rect>`;}
const names=[...'ABCDEFGHIJ'].map((s,i)=>`<text x="10" y="${43+i*24}">${s}</text>`).join(''),ticks=[1,8,80,84,88,92,96,100].map(t=>`<text x="${40+(t-1)*8}" y="18" font-size="9">${t}</text>`).join('');
get('split').innerHTML=`<svg viewBox="0 0 850 275" role="img" aria-label="系列A〜J、時点1〜100の分割とcontext。下の文字説明も参照">${names}${ticks}${cells}</svg>`;
get('out').textContent=`自作例：${scheme}方式、内側最終origin80／外側84／最終88\n選択=${toy.selection.chosen.family}, scale=${toy.selection.chosen.scale}（最終testは選択に不使用）\n${toy.selection.candidates.map(c=>c.family+' scale='+c.scale+'：内側MAE='+fmt(c.inner_mae)+'／外側MAE='+fmt(c.outer_mae)).join('\n')}\n外側検証系列=${toy.selection.outer_validation_ids}。最終fitはA〜Gのt≤92。H〜Jはcontext専用。\n表示context=${eligible?s+' t'+(co-7)+'..'+co:'なし（この段階の評価対象外）'}。stage切替は図だけを変えます。\n保存済みrolling予測 ${s}, origin${o} → t${r.target_times.join(',')}：${r.prediction.map(fmt).join(', ')}\nQ=${fmt(toy.Q)}、20誤差/系列のMAE=${fmt(toy.MAE)}、MASE=${fmt(toy.MASE)}\n8時点を等重みにしたMAE=${fmt(toy.equal_target_time_MAE)}\n時点93..100の重み=${Object.values(toy.weights).join(',')}。重みは再学習しません。`;
get('table-out').textContent=`公表Table3の丸め済み値：${sensitivity.method}、${sensitivity.dataset_count} dataset\n表示行からの平均=${fmt(sensitivity.displayed_row_mean)}／原著掲載の全11平均=${fmt(sensitivity.published_full_mean)}\nTime-CVより小さい=${sensitivity.wins_vs_time}、同値=${sensitivity.ties_vs_time}\n改善合計=${fmt(sensitivity.delta_sum)}、合計差/Time合計=${fmt(sensitivity.mean_difference_ratio)}\nWeather寄与=${fmt(sensitivity.weather_contribution)}。除外の正当化や信頼区間ではありません。`;
get('table-rows').innerHTML=Object.entries(table.rows).filter(([k])=>get('weather').checked||k!=='Weather').map(([k,v])=>`<tr><th>${k}</th><td>${v[table.methods.indexOf(get('method').value)]}</td><td>${v[6]}</td></tr>`).join('');saved={toy,table3_sensitivity:sensitivity,display:{stage,series:s,origin:o},note:'Synthetic experiment and rounded published table analysis are distinct; not original replication.'};get('error').textContent='';get('download').disabled=false;
}catch(e){saved=null;get('error').textContent=e.message;get('out').textContent='入力不正：結果を保留';get('split').innerHTML='';get('table-out').textContent='';get('table-rows').innerHTML='';get('download').disabled=true;}}
for(const k of keys)get(k).addEventListener(k==='weather'?'change':'input',render);
get('reset').addEventListener('click',()=>{for(const [k,v] of Object.entries({scheme:'series',stage:'final',series:'H',origin:'92',q:'auto',method:'Holdout'}))get(k).value=v;get('weather').checked=true;render();});
get('download').addEventListener('click',()=>{if(!saved)return;const url=URL.createObjectURL(new Blob([JSON.stringify(saved,null,2)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download='series-cv-synthetic.json';a.click();URL.revokeObjectURL(url);});
render();if(saved)for(const k of [...keys,'reset','download'])get(k).disabled=false;
})();
