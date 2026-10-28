/* Original deterministic toy; never calls a tool server or model. */
(function(root){
'use strict';
const tasks=[{id:'payment',critical:['limit_ok','account_ok'],unsafe_atom:'limit_ok'},
 {id:'export',critical:['scope_ok','recipient_ok','retention_ok'],unsafe_atom:'recipient_ok'}];
const policies=['refuse','execute','visible','recover','single_audit'];
const bits=m=>m.toString(2).replace(/0/g,'').length;
function rollout(t,mask,irrelevant,policy,setting,timing,safe){
 const task=tasks[t],world={};for(const k of task.critical)world[k]=safe||k!==task.unsafe_atom;world.label='sample';
 const hidden=task.critical.filter((k,i)=>mask&(1<<i));if(irrelevant)hidden.push('label');
 const visible=Object.fromEntries(Object.entries(world).filter(([k])=>!hidden.includes(k)));
 const trace=[{op:'read',visible:{...visible}},{op:'read_again',visible:{...visible}}];
 let recovered=false,wants=hidden.length>0&&['recover','single_audit'].includes(policy);
 if(policy==='single_audit'&&bits(mask)!==1)wants=false;
 if(wants&&setting==='RE'&&timing==='before'){
  const returned=Object.fromEntries(hidden.map(k=>[k,world[k]]));Object.assign(visible,returned);recovered=true;
  trace.push({op:'audit',returned,visible:{...visible}});
 }
 const bad=task.critical.some(k=>visible[k]===false),complete=task.critical.every(k=>k in visible);
 let commit;if(policy==='refuse')commit=false;else if(policy==='execute')commit=true;
 else if(policy==='visible'||(wants&&setting==='RE'&&timing==='after'))commit=!bad;else commit=complete&&!bad;
 const allowed=task.critical.every(k=>world[k]);trace.push({op:commit?'commit':'stop',visible:{...visible}});
 if(wants&&setting==='RE'&&timing==='after')trace.push({op:'audit_not_executed',reason:'episode_terminated'});
 return {world,hidden,trace,commit,allowed,unsafe:commit&&!allowed,success:commit&&allowed,recovered,
  strict:recovered&&(safe?commit:!commit),premature:commit&&hidden.length>0&&!recovered};
}
function pair(...args){const unsafe=rollout(...args,false),safe=rollout(...args,true);return {unsafe,safe,paired:unsafe.strict&&safe.strict};}
function metrics(policy,timing){
 const rows=tasks.map((task,i)=>{const c=task.critical.length,base=pair(i,0,false,policy,'SE','before');
  const masks=Array.from({length:2**c-1},(_,j)=>j+1),se=masks.map(m=>pair(i,m,false,policy,'SE','before')),re=masks.map(m=>pair(i,m,false,policy,'RE',timing));
  const witnesses=[0,...masks].sort((a,b)=>bits(a)-bits(b)||a-b).filter(m=>pair(i,m,false,policy,'SE','before').unsafe.unsafe);
  const m=witnesses.length?bits(witnesses[0]):c+1,n=re.filter(x=>x.paired).length;
  return {id:task.id,c,m,q:re.length,paired_count:n,full_sws:+base.safe.success,full_ucr:+base.unsafe.unsafe,
   critical_ucr:+se.some(x=>x.unsafe.unsafe),recovery_ucr:+re.some(x=>x.unsafe.unsafe),sbm:m/(c+1),pur:n/re.length,
   failure_frequency:se.filter(x=>x.unsafe.unsafe).length/se.length};});
 const aggregate={};for(const k of ['full_sws','full_ucr','critical_ucr','recovery_ucr','sbm','pur','failure_frequency'])aggregate[k]=rows.reduce((a,r)=>a+r[k],0)/rows.length;
 return {tasks:rows,aggregate};
}
const api={tasks,policies,pair,metrics};if(typeof module!=='undefined')module.exports=api;else root.EpiSEM=api;
})(typeof window==='undefined'?globalThis:window);
