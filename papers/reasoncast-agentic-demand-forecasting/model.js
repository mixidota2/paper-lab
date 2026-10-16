/* Output-space teaching proxy, not ReasonCast Eq. 8. No model or network calls. */
(() => {
'use strict';
const finite = x => typeof x === 'number' && Number.isFinite(x);
const defaults = {base:Array(7).fill(10),actual:Array(7).fill(20),additive:Array(7).fill(0),level:Array(7).fill(Math.log(2)),gate:.5,route:'Correct'};
function evaluate(x) {
  for (const k of ['base','actual','additive','level']) if (!Array.isArray(x[k]) || x[k].length !== 7 || !x[k].every(finite)) throw Error(k+'は有限な7日分の値が必要です。');
  if (x.actual.some(y=>y<0)) throw Error('実績は0以上にしてください。');
  if (!finite(x.gate) || x.gate<0 || x.gate>1 || !['Skip','Correct'].includes(x.route)) throw Error('強さは0〜1、経路はSkipまたは補正です。');
  const denominator=x.actual.reduce((a,b)=>a+b,0);
  if(!finite(denominator))throw Error('実績分母が有限値を超えました。');
  const correct = g => x.base.map((b,i)=>(b+g*x.additive[i])*Math.exp(g*x.level[i]));
  const rows=[['baseline',()=>x.base.slice()],['always',()=>correct(1)],
    ['selected',()=>x.route==='Skip'?x.base.slice():correct(x.gate)]].map(([name,predict])=>{
    let prediction=null;
    try{
      prediction=predict();
      if(!prediction.every(finite)){prediction=null;throw Error('prediction overflow');}
      const errors=prediction.map((p,i)=>Math.abs(x.actual[i]-p)),error_sum=errors.reduce((a,b)=>a+b,0);
      const wmape=denominator===0?null:100*(error_sum/denominator);
      if(!finite(error_sum)||(wmape!==null&&!finite(wmape)))throw Error('metric overflow');
      return {name,status:'ok',prediction,errors,error_sum,denominator,mae:error_sum/7,wmape,issue:null};
    }catch(e){return {name,status:'unavailable',prediction,errors:null,error_sum:null,denominator,mae:null,wmape:null,issue:'finite_range_exceeded'};}
  });
  rows.forEach(row=>row.delta_pp=rows[0].wmape===null||row.wmape===null?null:row.wmape-rows[0].wmape);
  return {rows,route:x.route,negative_prediction:rows.some(r=>(r.prediction||[]).some(v=>v<0))};
}
function parseArray(raw){
  const text=raw.trim();
  if(!text)throw Error('配列を入力してください。');
  const groups=text.split(/[,、]/);
  if(groups.some(part=>!part.trim()))throw Error('区切りの前後に空欄があります。欠測を0には変換しません。');
  const tokens=groups.flatMap(part=>part.trim().split(/\s+/));
  const values=tokens.map(Number);
  if(!values.every(finite))throw Error('配列は有限な数値で入力してください。');
  return values;
}

const api={kind:'reasoncast',defaults,evaluate,parseArray};
const spec={"id": "reasoncast-output-proxy", "version": "2.0.0", "source": {"url": "https://arxiv.org/html/2608.15291v1", "version": "arXiv:2608.15291v1"}, "conventions": {"prediction": "Seven-day output-space proxy (b+g*a)*exp(g*l), not paper Eq.8; Skip copies base without correction.", "metrics": "WMAPE percent=100*sum(abs(y-p))/sum(y); zero denominator is null; MAE in original units; delta is selected minus baseline in percentage points.", "failure": "Finite inputs required. Each comparison row may be unavailable on numeric overflow; other rows remain. Negative predictions are preserved and warned, including baseline."}};
api.spec=spec;
api.pack=x=>({schema:2,kind:spec.id,model:structuredClone(spec),inputs:structuredClone(x),implementation:structuredClone(typeof window!=='undefined'&&window.ReferenceImplementation?window.ReferenceImplementation:{status:'unavailable',runtime:'javascript'}),output:evaluate(x)});
api.unpack=d=>{
  if(d.schema!==2||d.kind!==spec.id||d.model?.id!==spec.id||d.model?.version!==spec.version||!d.inputs)
    throw Error('このLabのschema 2・教材仕様2.0.0のJSONを使ってください。');
  evaluate(d.inputs);return structuredClone(d.inputs);
};
if(typeof module!=='undefined') module.exports=api;
if(typeof window!=='undefined') window.ReferenceModel=api;
})();
