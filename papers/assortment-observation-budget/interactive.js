/* Original finite teaching UI. Saved expectations, executable observation rules. */
(function(){
'use strict';
const defaults=()=>({a:'0',m:'2',preference:'0',scale:'1',observation:'0'});
const num=x=>{const p=String(x).split('/').map(Number);return p[0]/(p[1]||1);};
function index(x,n){if(!/^(0|[1-9][0-9]*)$/.test(String(x))||Number(x)>=n)throw Error('一覧にある選択肢を選んでください。');return Number(x);}
function observations(m,mode){
 const t=Math.floor(m/2);let first=Array(t).fill(0),second=Array(t).fill(0),x=0;
 if(mode===1){first.fill(1);x=m;}
 if(mode===2){second.fill(2);x=Math.floor(m/2);}
 if(mode===3){first.fill(1);second.fill(1);x=Math.ceil(2*m/3);}
 return {first,second,x};
}
function decision(m,mode){
 const o=observations(m,mode),t=o.first.length;
 const avg=ids=>ids.reduce((s,i)=>s+(i?4-i:0),0)/t;
 const means=[avg(o.first),avg(o.second)];const winner=means[0]>=means[1]?0:1;
 return {...o,means,b:3*o.x>=2*m?1:2,c:means[winner]>=1?winner+1:3};
}
function view(data,state){
 const ai=index(state.a,data.a.length),v=index(state.preference,4),mode=index(state.observation,4);
 if(!/^[2-9]$/.test(String(state.m)))throw Error('顧客を観測する総回数mには、2〜9の整数を入力してください。');
 if(!['1/2','1','2'].includes(state.scale))throw Error('収益の倍率は1/2、1、2のいずれかを選んでください。');
 const m=Number(state.m),a=data.a[ai],c=data.cases.find(c=>c.m===m&&c.preference===v&&c.scale===state.scale);
 if(!c)throw Error('この設定での計算結果が見つかりません。');
 const rows=a.cuts.map(r=>`<tr><td>${r.k}</td><td>${r.exclusion}</td><td>${r.inclusion}</td><td>${r.regret}</td></tr>`).join('');
 const comparison=c.policies.map(p=>`<tr><th scope="row">${p.name}</th>${p.distribution.map(x=>`<td>${x}</td>`).join('')}<td>${p.expected}</td><td>${p.regret}</td></tr>`).join('');
 const bars=c.policies.map(p=>`<p>${p.name}：${p.regret}<span class="aob-bar" style="width:${100*num(p.regret)/(3*num(c.scale))}%" aria-hidden="true"></span></p>`).join('');
 const d=decision(m,mode),scale=num(c.scale);
 return {rows,comparison,bars,
 aSummary:`収益r=(${a.r.join(', ')})。最大損失が最も小さい区切りは${a.optimal.join(', ')}です。Aはk=${a.chosen}を選びます。g₀=${a.g0}、最高収益の半分=${a.bound}。`,
 summary:`評価用の選好v=(${c.v.join(', ')})、収益の倍率=${c.scale}。この選好を知っていれば、最適期待収益は${c.oracle}です。Cは全${m}回のうち${c.effective}回の結果を使い、${c.unused}回分は使いません。判断に使う経路数は${c.paths}通りです。`,
 observation:`ここでは観測の一例を示します。Bでは${m}人のうち${d.x}人が買い、Bは[${d.b}]を選びます。Cの第1群と第2群の購入結果は(${d.first.join(',')})と(${d.second.join(',')})です。各群の平均収益は${d.means.map(x=>x*scale).join('と')}、判定に使う閾値は${scale}です。Cは[${d.c}]を選びます。総観測数が奇数のときは最後の1回も[1]を提示しますが、その結果は判断に使いません。`};
}
function mount(doc){
 const get=k=>doc.getElementById('aob-'+k),data=JSON.parse(get('data').textContent),keys=Object.keys(defaults());
 function render(){try{const state=Object.fromEntries(keys.map(k=>[k,get(k).value]));const v=view(data,state);
 for(const k of ['rows','comparison','bars'])get(k).innerHTML=v[k];
 for(const k of ['aSummary','summary','observation'])get(k+'-output').textContent=v[k];get('error').textContent='';
 }catch(e){get('error').textContent=e.message;}}
 for(const k of keys)get(k).addEventListener('change',render);
 get('reset').addEventListener('click',()=>{for(const [k,v]of Object.entries(defaults()))get(k).value=v;render();});render();
}
if(typeof module!=='undefined')module.exports={defaults,view,decision,mount};
if(typeof document!=='undefined')mount(document);
})();
