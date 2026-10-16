/* Two explicit local accounting modes; not the official RetailBench simulator. */
(() => {
'use strict';
const finite=x=>typeof x==='number' && Number.isFinite(x);
const defaults={price:10,demand:200,rent:600,cash:3000,days:30,cost_a:4,cost_b:5,return_a:.3,return_b:.05,mode:'accounting'};
function evaluate(x) {
  for(const k of ['price','demand','rent','cash','days','cost_a','cost_b','return_a','return_b']) if(!finite(x[k])) throw Error(k+'は有限の数値が必要です。');
  if(!['accounting','funded'].includes(x.mode)) throw Error('会計モードが不正です。');
  if(!Number.isInteger(x.days)||x.days<1||x.days>365) throw Error('日数は1〜365の整数です。');
  if(['price','demand','rent','cash','cost_a','cost_b'].some(k=>x[k]<0)) throw Error('価格・需要・家賃・初期現金・原価は0以上です。');
  if(['return_a','return_b'].some(k=>x[k]<0||x[k]>1)) throw Error('返品率は0〜1です。');
  if(x.mode==='funded' && (!Number.isInteger(x.demand)||Math.min(x.cost_a,x.cost_b)<=0)) throw Error('手元資金モードは整数需要・正の原価が必要です。');
  const suppliers=['a','b'].map(label=>{
    const c=x['cost_'+label],rate=x['return_'+label];let cash=x.cash,stopped=null;const trace=[];
    for(let day=1;day<=x.days;day++){
      const opening=cash,active=stopped===null;
      const sold=active?(x.mode==='funded'?Math.min(x.demand,Math.floor(Math.max(cash,0)/c)):x.demand):0;
      const purchase=sold*c,gross=sold*x.price,refund=sold*x.price*rate,rent=active?x.rent:0;
      cash=opening-purchase+gross-refund-rent;
      if(!finite(cash)) throw Error('現金計算が有限値を超えました。');
      trace.push({day,active,opening,purchased:sold,purchase,gross,refund,rent,sold,lost:active?x.demand-sold:0,expected_returns:sold*rate,return_ratio:sold?rate:null,cash});
      if(x.mode==='funded' && stopped===null && cash<0) stopped=day;
    }
    return {supplier:label.toUpperCase(),margin:x.price*(1-rate)-c,final_cash:cash,stopped,trace};
  });
  return {suppliers,return_b_tie:x.price===0?null:x.return_a-(x.cost_b-x.cost_a)/x.price,
    margin_difference:x.price*(x.return_a-x.return_b)-(x.cost_b-x.cost_a)};
}
const api={kind:'retailbench',defaults,evaluate};
api.pack=x=>({schema:1,kind:api.kind,inputs:x,output:evaluate(x)});
api.unpack=d=>{if(d.schema!==1 || d.kind!==api.kind || !d.inputs) throw Error('このLabのschema 1 JSONを使ってください。');evaluate(d.inputs);return structuredClone(d.inputs);};
if(typeof module!=='undefined') module.exports=api;
if(typeof window!=='undefined') window.ReferenceModel=api;
})();
