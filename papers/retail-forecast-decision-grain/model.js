(function(root){'use strict';
function vectors(...xs){if(!xs.every(Array.isArray)||!xs[0].length||xs.some(x=>x.length!==xs[0].length))throw Error('空でない同じ長さの配列が必要です。');}
function valid(xs){if(xs.some(x=>!Number.isFinite(x)||x<0||x>10000))throw Error('値は0〜10000の有限数で入力してください。');}
// Reject non-finite results and complete underflow before JSON can hide them.
// This is a bounded floating-point teaching API, not arbitrary precision.
function finite(x){if(!Number.isFinite(x))throw RangeError('計算結果が数値の表現範囲を超えました。入力の尺度を見直してください。');return x;}
function product(a,b){const x=finite(a*b);if(x===0&&a!==0&&b!==0)throw RangeError('計算途中の値が小さすぎます。入力の尺度を見直してください。');return x;}
function ratio(a,b){const x=finite(a/b);if(x===0&&a!==0)throw RangeError('計算結果が小さすぎます。入力の尺度を見直してください。');return x;}
function total(xs){return xs.reduce((s,x)=>finite(s+x),0);}
function metrics(a,f,p,w,group){vectors(a,f,p,w,group);for(const g of group)if(!((typeof g==='number'&&Number.isFinite(g))||(typeof g==='string'&&g.length>0)))throw Error('groupは有限数または空でない文字列で指定してください。');valid([...a,...f,...p,...w]);const nodes=[...new Set(group)].map(g=>{const ix=group.map((v,i)=>v===g?i:-1).filter(i=>i>=0);if(ix.some(i=>p[i]!==p[ix[0]]))throw Error('集約する商品の単価は同一にしてください。');return [total(ix.map(i=>a[i])),total(ix.map(i=>f[i])),p[ix[0]],total(ix.map(i=>w[i]))];});const den=total(nodes.map(([y,f,p])=>product(p,y))),wd=total(w);return {old:wd?ratio(total(nodes.map(([y,f,p,w])=>ratio(product(w,Math.abs(y-f)),Math.max(y,1e-9)))),wd):null,corrected:den?ratio(total(nodes.map(([y,f,p])=>product(p,Math.abs(y-f)))),den):null};}
function windows(a,f){vectors(a,f);valid([...a,...f]);const den=total(a);return {mean:a.every(y=>y>0)?ratio(total(a.map((y,i)=>ratio(Math.abs(y-f[i]),y))),a.length):null,pooled:den?ratio(total(a.map((y,i)=>Math.abs(y-f[i]))),den):null};}
function loss(q,y,r){valid([q,y]);if(![.5,.8,.95].includes(r))throw Error('不足費用の比率を選んでください。');return Math.max(q-y,0)+r/(1-r)*Math.max(y-q,0);}
const api={metrics,windows,loss};if(typeof module!=='undefined')module.exports=api;else root.GrainModel=api;
})(globalThis);
