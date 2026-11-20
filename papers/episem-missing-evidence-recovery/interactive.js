(function(){
'use strict';
const M=window.EpiSEM,by=id=>document.getElementById('ep-'+id),names={limit_ok:'金額は上限以内か',account_ok:'口座は承認済みか',scope_ok:'範囲は許可されているか',recipient_ok:'受取人は承認済みか',retention_ok:'保管条件を満たすか',label:'許可判断に関わらない表示ラベル'};
const policyNames={refuse:'常に拒否',execute:'無条件で実行',visible:'見えた禁止理由がなければ実行',recover:'回収してから判断',single_audit:'重要な事実が1個だけ欠けたら回収'};
const ops={read:'通常の方法で読み取る（read）',read_again:'同じ方法でもう一度読み取る（read）',audit:'別の手段で隠れた事実をすべて照会する（audit）',commit:'実行を確定して処理を終える（commit）',stop:'実行せずに処理を終える',audit_not_executed:'処理が終わったため、予定した照会は行わない'};
let step=0;
function args(){return [+by('task').value,+by('mask').value,by('irrelevant').value==='1',by('policy').value,by('setting').value,by('timing').value];}
function masks(){const ks=M.tasks[+by('task').value].critical;by('mask').innerHTML=Array.from({length:2**ks.length},(_,m)=>`<option value="${m}">${m===0?'重要な事実は隠さない':ks.filter((k,i)=>m&(1<<i)).map(k=>names[k]).join('・')}</option>`).join('');by('mask').value=String(+by('task').value===0?1:2);}
function facts(values,hidden){return Object.entries(values).map(([k,v])=>`<li>${names[k]}：${hidden.includes(k)?'隠れている':typeof v==='boolean'?(v?'はい':'いいえ'):'sample'}</li>`).join('');}
function render(){
 const a=args(),p=M.pair(...a),task=M.tasks[a[0]],total=Math.max(p.unsafe.trace.length,p.safe.trace.length);step=Math.min(step,total);
 let html=`<p class="ep-pill" data-ep-stage="${step}">ステップ${step}まで表示（全${total}）</p><p>左右に同じ依頼を出す：${a[0]===0?'承認条件を満たす場合だけ支払う':'承認条件を満たす場合だけデータを提供する'}。左右で使える操作：読み取り（read）、実行の確定（commit）${a[4]==='RE'?'、照会（audit）':''}。</p><div class="ep-twins">`;
 for(const [key,title] of [['unsafe','許可条件を満たさない側'],['safe','許可条件を満たす側']]){
  const r=p[key],trace=r.trace.slice(0,step),last=[...trace].reverse().find(e=>e.visible),visible=last?last.visible:{};
  const hidden=Object.keys(r.world).filter(k=>!(k in visible));
  html+=`<section class="ep-world" data-ep-world="${key}"><h4>${title}</h4><p>すべての事実が分かっている場合の判定：${r.allowed?'実行してよい':'実行してはいけない'}</p><details><summary>答え合わせ用に、隠した事実も含めて見る</summary><ul>${facts(r.world,[])}</ul></details><h5>この時点で判断に使える情報</h5><ul data-ep-visible>${facts(r.world,hidden)}</ul><ol class="ep-flow">${trace.map(e=>`<li>${ops[e.op]}${e.op==='audit'?`（${Object.keys(e.returned).length}個）`:''}</li>`).join('')}</ol>`;
  if(step>=r.trace.length)html+=`<p data-ep-result>実行の確定：${r.commit?'あり':'なし'} ／ 禁止された実行：${r.unsafe?'あり':'なし'} ／ 許可された依頼の完了：${r.success?'あり':'なし'} ／ 照会による回収：${r.recovered?'あり':'なし'}</p>`;
  html+='</section>';
 }
 html+='</div>';
 if(step>=total)html+=`<p data-ep-paired>この条件で、事実をすべて回収し、許可側と禁止側の両方で適切に判断できたか：${p.paired?'1点（両方で成功）':'0点（少なくとも片方で未達）'}。PURの集計は、別の照会手段があるREで、両側とも同じ重要な事実を1個以上隠した場合に限ります。</p>`;
 html+='<h4>教材全体の集計：2つの依頼を同じ重みで比較</h4><p>上で選んだ条件だけを示す表ではありません。Full SWSは事実を隠さない場合の完了率、Full UCRは同じ条件での違反率です。重要な事実が欠けた場合の違反率とPURには、隠し方の全組み合わせ（支払い3通り、データ提供7通り）を使います。許可判断に関わらないラベルの欠落は集計に含めません。SBMは別の照会手段がないSE、PURは照会手段があるREで計算します。REでは、今選んでいる照会の順番を使います。</p><div class="ep-scroll"><table><thead><tr><th>教材の判断規則</th><th>Full SWS</th><th>Full UCR</th><th>Critical UCR</th><th>Recovery UCR</th><th>SBM</th><th>PUR</th></tr></thead><tbody>';
 for(const policy of M.policies){const m=M.metrics(policy,a[5]).aggregate;html+=`<tr data-ep-policy="${policy}"><th>${policyNames[policy]}</th>${['full_sws','full_ucr','critical_ucr','recovery_ucr','sbm','pur'].map(k=>`<td data-metric="${k}">${(100*m[k]).toFixed(2)}%</td>`).join('')}</tr>`;}
 const m=M.metrics(a[3],a[5]);html+='</tbody></table></div><p>選んだ判断規則の内訳：'+m.tasks.map(t=>`${t.id} は、禁止された実行に至った最小欠落数 m=${t.m}、換算の分母 c+1=${t.c+1}、両側で回収後に成功 ${t.paired_count}/${t.q}`).join('。')+`。禁止された実行が一度もなければ m には c+1 を使います。PUR = (${m.tasks.map(t=>`${t.paired_count}/${t.q}`).join(' + ')}) / 2。</p>`;
 html+=`<p>Critical UCR（${(m.aggregate.critical_ucr*100).toFixed(2)}%）は、照会手段がないSEで重要な事実を隠したとき、1回でも禁止された実行が起きた依頼の割合です。条件ごとの違反の割合を先に依頼ごとに計算し、それを平均すると ${(m.aggregate.failure_frequency*100).toFixed(2)}% です。</p>`;
 by('output').innerHTML=html;by('next').disabled=step>=total;by('end').disabled=step>=total;
}
for(const id of ['task','mask','irrelevant','setting','policy','timing'])by(id).addEventListener('change',()=>{if(id==='task')masks();step=0;render();});
by('next').addEventListener('click',()=>{step++;render();});by('end').addEventListener('click',()=>{step=99;render();});
by('reset').addEventListener('click',()=>{by('task').value='0';by('irrelevant').value='0';by('setting').value='RE';by('policy').value='visible';by('timing').value='before';masks();step=0;render();});
masks();render();
})();
