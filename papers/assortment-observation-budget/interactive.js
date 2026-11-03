/* Original finite teaching UI. Saved expectations, executable observation rules. */
(function(){
'use strict';
const defaults=()=>({a:'0',m:'2',preference:'0',scale:'1',observation:'0'});
const num=x=>{const p=String(x).split('/').map(Number);return p[0]/(p[1]||1);};
function index(x,n){if(!/^(0|[1-9][0-9]*)$/.test(String(x))||Number(x)>=n)throw Error('選択肢を確認してください。');return Number(x);}
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
 if(!/^[2-9]$/.test(String(state.m)))throw Error('総観測数mは2〜9の整数にしてください。');
 if(!['1/2','1','2'].includes(state.scale))throw Error('収益倍率を確認してください。');
 const m=Number(state.m),a=data.a[ai],c=data.cases.find(c=>c.m===m&&c.preference===v&&c.scale===state.scale);
 if(!c)throw Error('対応する計算結果がありません。');
 const rows=a.cuts.map(r=>`<tr><td>${r.k}</td><td>${r.exclusion}</td><td>${r.inclusion}</td><td>${r.regret}</td></tr>`).join('');
 const comparison=c.policies.map(p=>`<tr><th scope="row">${p.name}</th>${p.distribution.map(x=>`<td>${x}</td>`).join('')}<td>${p.expected}</td><td>${p.regret}</td></tr>`).join('');
 const bars=c.policies.map(p=>`<p>${p.name}：${p.regret}<span class="aob-bar" style="width:${100*num(p.regret)/(3*num(c.scale))}%" aria-hidden="true"></span></p>`).join('');
 const d=decision(m,mode),scale=num(c.scale);
 return {rows,comparison,bars,
 aSummary:`r=(${a.r.join(', ')})：最適cut ${a.optimal.join(', ')}、採用 k=${a.chosen}。g₀=${a.g0}、半額上界=${a.bound}。`,
 summary:`選好v=(${c.v.join(', ')})、収益倍率=${c.scale}、同じ選好の最適期待収益=${c.oracle}。Cの総観測 ${m}／判断に使用 ${c.effective}／判断に不使用 ${c.unused}。有効経路 ${c.paths}。`,
 observation:`例示経路（平均ではありません）：B 購入 ${d.x}/${m} → [${d.b}]。C 観測ID (${d.first.join(',')}) と (${d.second.join(',')})、平均収益 ${d.means.map(x=>x*scale).join(' / ')} → [${d.c}]。閾値=${scale}。奇数の余りは[1]に提示しますが判断には使いません。`};
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
