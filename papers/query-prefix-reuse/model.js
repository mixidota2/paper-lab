/* Self-authored scalar API, matching run.py. No trained model or measured timing. */
const ReuseGR=(()=>{
'use strict';
const version='query-prefix-reuse-toy-1';
const table1=[{method:'0.5B E2E',hr:81.99,recall:45.53,ms:117},{method:'7B E2E',hr:85.71,recall:50.96,ms:168.88},{method:'ReuseGR prepared',hr:85.82,recall:46.05,ms:71.45}];
const presets=[['Prepared',100,100,85.82,71.45,'endpoint'],['Cold',0,0,81.99,117,'endpoint'],['Static Q',20.97,36.87,82.38,100.21,'measured partition'],['Static mix',20.97,36.87,83.40,100.21,'projection'],['Backfill',42.15,58.40,84.23,90.40,'projection'],['Rolling 1M',68.50,84.20,85.21,78.65,'projection']].map(([name,q,p,hr,ms,quality])=>({name,q,p,hr,ms,quality}));
function integer(x,lo,hi){if(!Number.isInteger(x)||x<lo||x>hi)throw Error('integer outside domain');return x;}
function projection(p){if(typeof p!=='number'||!Number.isFinite(p)||p<0||p>1)throw Error('finite numeric P in [0, 1] required');return {p,mean_ms:p*71.45+(1-p)*117,hr_percent:p*85.82+(1-p)*81.99,recall_percent:p*46.05+(1-p)*45.53,kind:'fixed-endpoint projection; not measured mixed traffic'};}
function toy(prepared=true,depth=1,query='wide',history='left',budget=4){
 if(typeof prepared!=='boolean')throw Error('prepared must be boolean');integer(depth,0,3);integer(budget,0,8);
 if(!['wide','narrow'].includes(query)||!['left','right'].includes(history))throw Error('unknown query or history');
 const sets={wide:[[''],['0','1'],['00','10'],['000','100']],narrow:[[''],['0'],['00'],['000']]};
 const active_depth=prepared?depth:0,prefixes=sets[query][active_depth],target=history==='left'?'0001':'1111';
 const reachable=Array.from({length:16},(_,i)=>i.toString(2).padStart(4,'0')).filter(s=>prefixes.some(c=>s.startsWith(c)));
 const score=s=>Array.from(s).reduce((n,ch,j)=>n+(j<active_depth?Number(ch==='0'):(j+1)*Number(ch===target[j])),0);
 const order=(a,b)=>a<b?-1:a>b?1:0;
 const ranked=[...reachable].sort((a,b)=>score(b)-score(a)||order(a,b));
 const branchScore=b=>Math.max(...reachable.filter(s=>s.startsWith(b)).map(score));
 const branches=[...new Set(reachable.map(s=>s.slice(0,3)))].sort((a,b)=>branchScore(b)-branchScore(a)||order(a,b));
 const admitted=prepared?branches.slice(0,budget):branches,final=ranked.filter(s=>admitted.includes(s.slice(0,3)));
 return {synthetic:true,model_version:version,input:{prepared,depth,query,history,budget},route:prepared?(depth===0?'prepared-root':'prepared-prefix'):'cold-e2e',waits_for_planner:false,async_prepare:!prepared&&depth>0,active_depth,prefixes,target,reachable,target_reachable:reachable.includes(target),layer_nodes:[1,2,3,4].map(j=>new Set(reachable.map(s=>s.slice(0,j))).size),l4_scored:reachable.length,branches,admitted,ranking:final.map(s=>({sid:s,score:score(s)})),target_returned:final.includes(target)};
}
return {toy,projection,table1,presets,version};
})();
if(typeof module!=='undefined')module.exports=ReuseGR;
