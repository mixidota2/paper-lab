/* Output-space teaching proxy, not ReasonCast Eq. 8. No model or network calls. */
(() => {
'use strict';
const finite = x => typeof x === 'number' && Number.isFinite(x);
const defaults = {base:Array(7).fill(10),actual:Array(7).fill(20),additive:Array(7).fill(0),level:Array(7).fill(Math.log(2)),gate:.5,route:'Correct'};
function evaluate(x) {
  for (const k of ['base','actual','additive','level']) if (!Array.isArray(x[k]) || x[k].length !== 7 || !x[k].every(finite)) throw Error(k+'は有限な7日分の値が必要です。');
  if (x.actual.some(y=>y<0)) throw Error('実績は0以上にしてください。');
  if (!finite(x.gate) || x.gate<0 || x.gate>1 || !['Skip','Correct'].includes(x.route)) throw Error('強さは0〜1、経路はSkipまたは補正です。');
  const correct = g => x.base.map((b,i)=>(b+g*x.additive[i])*Math.exp(g*x.level[i]));
  const always=correct(1), selected=x.route==='Skip'?x.base.slice():correct(x.gate);
  if (![...always,...selected].every(finite)) throw Error('補正が有限値を超えました。');
  const denominator=x.actual.reduce((a,b)=>a+b,0);
  const rows=[['baseline',x.base.slice()],['always',always],['selected',selected]].map(([name,prediction])=>{
    const errors=prediction.map((p,i)=>Math.abs(x.actual[i]-p)), error_sum=errors.reduce((a,b)=>a+b,0);
    if (!finite(error_sum) || !finite(denominator)) throw Error('誤差計算が有限値を超えました。');
    return {name,prediction,errors,error_sum,denominator,mae:error_sum/7,wmape:denominator===0?null:100*(error_sum/denominator)};
  });
  rows.forEach(row=>{
    row.delta_pp=rows[0].wmape===null?null:row.wmape-rows[0].wmape;
    if([row.wmape,row.delta_pp].some(v=>v!==null&&!finite(v))) throw Error('指標が有限値を超えました。');
  });
  return {rows,route:x.route,negative_prediction:[...always,...selected].some(v=>v<0)};
}
const api={kind:'reasoncast',defaults,evaluate};
api.pack=x=>({schema:1,kind:api.kind,inputs:x,output:evaluate(x)});
api.unpack=d=>{if(d.schema!==1 || d.kind!==api.kind || !d.inputs) throw Error('このLabのschema 1 JSONを使ってください。');evaluate(d.inputs);return structuredClone(d.inputs);};
if(typeof module!=='undefined') module.exports=api;
if(typeof window!=='undefined') window.ReferenceModel=api;
})();
