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
// Portable UI scenarios contain inputs and recomputable self-authored results.
const defaults=Object.freeze({y2:0,a2:1,group:'separate',window:100,q:8,y:10,r:.8});
const scenarioKind='retail-grain-scenario',modelVersion='retail-grain-1';
function scenarioInputs(x){
  if(!x||typeof x!=='object'||Array.isArray(x)||Object.keys(x).length!==Object.keys(defaults).length||
    Object.keys(defaults).some(k=>!Object.prototype.hasOwnProperty.call(x,k)))
    throw Error('保存条件には7つの入力項目が必要です。');
  valid([x.y2,x.a2,x.window,x.q,x.y]);
  if(!['separate','together'].includes(x.group))throw Error('集計単位を選んでください。');
  if(![.5,.8,.95].includes(x.r))throw Error('不足費用の比率を選んでください。');
  return Object.fromEntries(Object.keys(defaults).map(k=>[k,x[k]]));
}
function scenario(x){
  const inputs=scenarioInputs(x),groups=inputs.group==='together'?[0,0]:[0,1];
  return {metrics:{A:metrics([100,inputs.y2],[90,inputs.a2],[1,1],[1,1],groups),
                   B:metrics([100,inputs.y2],[80,0],[1,1],[1,1],groups)},
          windows:{A:windows([1,inputs.window],[0,inputs.window]),
                   B:windows([1,inputs.window],[1,Math.max(0,inputs.window-10)])},
          order:{loss:loss(inputs.q,inputs.y,inputs.r),shortage_cost:inputs.r/(1-inputs.r)}};
}
function pack(x){
  const inputs=scenarioInputs(x);
  return {schema:1,kind:scenarioKind,model_version:modelVersion,synthetic:true,inputs,
          note:'Self-authored arithmetic examples, not author model training, inference or original experimental results.',
          output:scenario(inputs)};
}
function unpack(d){
  if(!d||d.schema!==1||d.kind!==scenarioKind||d.model_version!==modelVersion||d.synthetic!==true)
    throw Error('この教材の保存形式1・retail-grain-1の合成例JSONを使ってください。');
  const inputs=scenarioInputs(d.inputs);
  scenario(inputs); // Recompute before changing the UI; saved output is never trusted.
  return inputs;
}
// Deltas describe arithmetic changes, not comparable model performance.
const comparisonKind='retail-grain-comparison';
function compare(baseline,current){
  const b=pack(baseline),c=pack(current);
  function difference(x,y){
    if(x===null||y===null)return null;
    if(typeof x==='object')return Object.fromEntries(Object.keys(x).map(k=>[k,difference(x[k],y[k])]));
    return finite(y-x);
  }
  return {baseline:b,current:c,changed_inputs:Object.keys(defaults).filter(k=>b.inputs[k]!==c.inputs[k]),
          delta:difference(b.output,c.output)};
}
function packComparison(baseline,current){
  const result=compare(baseline,current);
  return {schema:1,kind:comparisonKind,model_version:modelVersion,synthetic:true,
          baseline:result.baseline,current:result.current,changed_inputs:result.changed_inputs,delta:result.delta,
          note:'Current minus baseline. Changes to evaluation conditions are not evidence of performance improvement. The three examples use separate scales.'};
}
function unpackComparison(d){
  if(!d||d.schema!==1||d.kind!==comparisonKind||d.model_version!==modelVersion||d.synthetic!==true)
    throw Error('この教材の比較保存形式1・retail-grain-1の合成例JSONを使ってください。');
  const baseline=unpack(d.baseline),current=unpack(d.current);
  compare(baseline,current); // Validate both before a caller changes any state.
  return {baseline,current};
}
const api={metrics,windows,loss,defaults,scenario,pack,unpack,compare,packComparison,unpackComparison};if(typeof module!=='undefined')module.exports=api;else root.GrainModel=api;
})(globalThis);
