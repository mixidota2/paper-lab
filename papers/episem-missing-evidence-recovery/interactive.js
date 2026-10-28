(function(){
'use strict';
const M=window.EpiSEM,by=id=>document.getElementById('ep-'+id),names={limit_ok:'金額が上限内',account_ok:'口座が承認済み',scope_ok:'範囲が許可内',recipient_ok:'受取人が承認済み',retention_ok:'保管条件を満たす',label:'表示ラベル（無関係）'};
const policyNames={refuse:'常に拒否',execute:'無条件実行',visible:'見えた禁止理由だけで判断',recover:'回収後に判断',single_audit:'1個欠落時だけ回収'};
const ops={read:'通常read',read_again:'通常readを繰り返す',audit:'独立audit：全欠落を回収',commit:'commit：終端',stop:'停止：終端',audit_not_executed:'予定auditは未実行：既に終端'};
let step=0;
function args(){return [+by('task').value,+by('mask').value,by('irrelevant').value==='1',by('policy').value,by('setting').value,by('timing').value];}
function masks(){const ks=M.tasks[+by('task').value].critical;by('mask').innerHTML=Array.from({length:2**ks.length},(_,m)=>`<option value="${m}">${m===0?'欠落なし':ks.filter((k,i)=>m&(1<<i)).map(k=>names[k]).join('・')}</option>`).join('');by('mask').value=String(+by('task').value===0?1:2);}
function facts(values,hidden){return Object.entries(values).map(([k,v])=>`<li>${names[k]}：${hidden.includes(k)?'欠落':typeof v==='boolean'?(v?'はい':'いいえ'):'sample'}</li>`).join('');}
function render(){
 const a=args(),p=M.pair(...a),task=M.tasks[a[0]],total=Math.max(p.unsafe.trace.length,p.safe.trace.length);step=Math.min(step,total);
 let html=`<p class="ep-pill" data-ep-stage="${step}">表示済み ${step} / ${total} ステップ</p><p>同じ依頼：${a[0]===0?'承認条件を満たす支払いを実行':'承認条件を満たすデータ提供を実行'}。同じツール：read / commit${a[4]==='RE'?' / audit':''}。</p><div class="ep-twins">`;
 for(const [key,title] of [['unsafe','禁止側'],['safe','許可側']]){
  const r=p[key],trace=r.trace.slice(0,step),last=[...trace].reverse().find(e=>e.visible),visible=last?last.visible:{};
  const hidden=Object.keys(r.world).filter(k=>!(k in visible));
  html+=`<section class="ep-world" data-ep-world="${key}"><h4>${title}</h4><p>完全な世界での許可：${r.allowed?'あり':'なし'}</p><details><summary>採点側が持つ完全状態</summary><ul>${facts(r.world,[])}</ul></details><h5>方策に見える情報</h5><ul data-ep-visible>${facts(r.world,hidden)}</ul><ol class="ep-flow">${trace.map(e=>`<li>${ops[e.op]}${e.op==='audit'?`（${Object.keys(e.returned).length}個）`:''}</li>`).join('')}</ol>`;
  if(step>=r.trace.length)html+=`<p data-ep-result>実行 ${r.commit?'あり':'なし'} ／ 違反 ${r.unsafe?'あり':'なし'} ／ 正当な完遂 ${r.success?'あり':'なし'} ／ 回収 ${r.recovered?'あり':'なし'}</p>`;
  html+='</section>';
 }
 html+='</div>';
 if(step>=total)html+=`<p data-ep-paired>この条件の両世界で厳密な回収成功：${p.paired?'1（AND成立）':'0（AND不成立）'}。PURへ入るのはREの同一・非空critical maskだけです。</p>`;
 html+='<h4>自作toyの集計：全2taskを同じ重みで読む</h4><p>上の1条件の成績ではありません。各taskの全critical mask（3個と7個）を列挙した集計です。無関係なラベルの欠落はこの表の分母へ入れません。SBMはSE、PURはRE。REの順序は現在の選択に合わせます。</p><div class="ep-scroll"><table><thead><tr><th>自作方策</th><th>Full SWS</th><th>Full UCR</th><th>Critical UCR</th><th>Recovery UCR</th><th>SBM</th><th>PUR</th></tr></thead><tbody>';
 for(const policy of M.policies){const m=M.metrics(policy,a[5]).aggregate;html+=`<tr data-ep-policy="${policy}"><th>${policyNames[policy]}</th>${['full_sws','full_ucr','critical_ucr','recovery_ucr','sbm','pur'].map(k=>`<td data-metric="${k}">${(100*m[k]).toFixed(2)}%</td>`).join('')}</tr>`;}
 const m=M.metrics(a[3],a[5]);html+='</tbody></table></div><p>選んだ方策の内訳：'+m.tasks.map(t=>`${t.id} は m=${t.m}、c+1=${t.c+1}、回収成功 ${t.paired_count}/${t.q}`).join('。')+`。PUR = (${m.tasks.map(t=>`${t.paired_count}/${t.q}`).join(' + ')}) / 2。</p>`;
 html+=`<p>Critical UCR ${(m.aggregate.critical_ucr*100).toFixed(2)}% は「どこかで失敗したtask」の比率。同じ記録のtask平均失敗頻度は ${(m.aggregate.failure_frequency*100).toFixed(2)}% です。</p>`;
 by('output').innerHTML=html;by('next').disabled=step>=total;by('end').disabled=step>=total;
}
for(const id of ['task','mask','irrelevant','setting','policy','timing'])by(id).addEventListener('change',()=>{if(id==='task')masks();step=0;render();});
by('next').addEventListener('click',()=>{step++;render();});by('end').addEventListener('click',()=>{step=99;render();});
by('reset').addEventListener('click',()=>{by('task').value='0';by('irrelevant').value='0';by('setting').value='RE';by('policy').value='visible';by('timing').value='before';masks();step=0;render();});
masks();render();
})();
