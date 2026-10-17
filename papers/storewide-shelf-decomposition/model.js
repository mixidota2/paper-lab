/* Synthetic finite-capacity model. Browser and Node share this implementation. */
(function(root){
'use strict';
const items=[
{id:'A1',category:'A',brand:'A赤',q:12,p:4,w:1,d:4},
{id:'A2',category:'A',brand:'A赤',q:8,p:6,w:1,d:2},
{id:'A3',category:'A',brand:'A青',q:4,p:3,w:1,d:6},
{id:'B1',category:'B',brand:'B赤',q:10,p:5,w:1,d:3},
{id:'B2',category:'B',brand:'B青',q:6,p:4,w:1,d:6},
{id:'B3',category:'B',brand:'B青',q:3,p:8,w:1,d:2}];
const defaults={capacity:5,s:.4,beta:.25,r:4,c:2,e:.5,brands:1};
const sum=a=>a.reduce((x,y)=>x+y,0), EPS=1e-9;
function evaluate(xs,faces,p){
 const chosen=xs.map((x,i)=>({...x,f:faces[i]})).filter(x=>x.f);
 const T=sum(xs.map(x=>x.q)), B=sum(chosen.map(x=>x.q));
 if(!B || B+EPS<p.e*T || new Set(chosen.map(x=>x.brand)).size<p.brands) return null;
 const rows=chosen.map(x=>{const direct=x.q*x.f**p.beta,transfer=p.s*x.q*(T-B)/B,demand=direct+transfer;
 return {id:x.id,faces:x.f,direct,transfer,demand,gross:demand*x.p,replenishment:p.r*demand/(x.f*x.d),fixed:p.c};});
 return {faces:[...faces],used:sum(chosen.map(x=>x.w*x.f)),profit:sum(rows.map(x=>x.gross-x.replenishment-x.fixed)),unmet_base:T-B,lost:(1-p.s)*(T-B),rows};
}
function vectors(n){return n ? vectors(n-1).flatMap(a=>[0,1,2].map(f=>[...a,f])):[[]];}
function values(xs,p,caps){
 const states=vectors(xs.length).map(f=>evaluate(xs,f,p)).filter(Boolean);
 return caps.map(capacity=>{let best=null,alternatives=[]; for(const state of states){if(state.used>capacity)continue;if(!best||state.profit>best.profit+EPS){best=state;alternatives=[state];}else if(Math.abs(state.profit-best.profit)<=EPS)alternatives.push(state);}return {capacity,best,alternatives};});
}
function choose(tables,p){
 let profit=-Infinity,options=[];
 for(const a of tables[0])for(const b of tables[1]){
  if(!a.best||!b.best||a.capacity+b.capacity>p.capacity)continue;
  for(const aa of a.alternatives)for(const bb of b.alternatives){
   const value=aa.profit+bb.profit,row={profit:value,allocation:[a.capacity,b.capacity],categories:[aa,bb]};
   if(value>profit+EPS){profit=value;options=[row];}else if(Math.abs(value-profit)<=EPS)options.push(row);
  }
 }
 const faceKey=x=>x.categories.flatMap(c=>c.faces).join('');
 options.sort((a,b)=>faceKey(a).localeCompare(faceKey(b))||sum(a.allocation)-sum(b.allocation)||a.allocation[0]-b.allocation[0]);
 if(!options.length)return null;
 const unique=[...new Set(options.map(faceKey))].sort().map(x=>x.split('').map(Number));
 return {...options[0],optimal_face_vectors:unique,optimal_face_count:unique.length};
}
function solve(p=defaults,caps=[1,2,3,4]){
 const tables=[values(items.slice(0,3),p,caps),values(items.slice(3),p,caps)];
 const best=choose(tables,p);
 // Choose among capacity pairs satisfying the category constraints first.
 let pairs=[]; for(const a of caps) for(const b of caps) if(a+b<=p.capacity && tables[0].find(x=>x.capacity===a).best && tables[1].find(x=>x.capacity===b).best) pairs.push([a,b]);
 const target=[108/206*p.capacity,98/206*p.capacity];
 const error=a=>sum(a.map((v,i)=>(v-target[i])**2));
 pairs.sort((a,b)=>error(a)-error(b)||sum(b)-sum(a)||a[0]-b[0]||a[1]-b[1]);
 let proportional=null;
 if(pairs.length){const allocation=pairs[0], categories=tables.map((t,i)=>t.find(x=>x.capacity===allocation[i]).best);
 proportional={allocation,feasible:categories.every(Boolean),categories,profit:categories.every(Boolean)?sum(categories.map(x=>x.profit)):null};}
 const ignoreTables=[values(items.slice(0,3),{...p,s:0},caps),values(items.slice(3),{...p,s:0},caps)];
 const unaware=choose(ignoreTables,p);
 const ignored=unaware?{...unaware,categories:unaware.categories.map((x,i)=>evaluate(items.slice(i*3,i*3+3),x.faces,p))}:null;
 if(ignored) ignored.profit=sum(ignored.categories.map(x=>x.profit));
 return {model_version:'shelf-decomposition-2',tables,best,proportional,ignored};
}
const api={items,defaults,evaluate,solve}; if(typeof module!=='undefined')module.exports=api;else root.ShelfModel=api;
})(typeof globalThis!=='undefined'?globalThis:this);
