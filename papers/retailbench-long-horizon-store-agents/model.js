/* Two explicit local accounting modes; not the official RetailBench simulator. */
(() => {
'use strict';
const finite=x=>typeof x==='number' && Number.isFinite(x);
const defaults={price:10,demand:200,rent:600,cash:3000,days:30,cost_a:4,cost_b:5,return_a:.3,return_b:.05,mode:'accounting'};
// Exact rational arithmetic over each input Number's canonical decimal string.
// Monetary transitions never use an affordability epsilon or cent rounding.
function gcd(a,b){a=a<0n?-a:a;while(b){[a,b]=[b,a%b];}return a;}
function rational(n,d=1n){const g=gcd(n,d);return {n:n/g,d:d/g};}
function decimal(value){
  const [mantissa,exp='0']=String(value).split('e');
  const scale=(mantissa.split('.')[1]||'').length-Number(exp);
  const n=BigInt(mantissa.replace('.',''));
  return scale>=0?rational(n,10n**BigInt(scale)):rational(n*10n**BigInt(-scale));
}
const add=(a,b)=>rational(a.n*b.d+b.n*a.d,a.d*b.d);
const neg=a=>({n:-a.n,d:a.d});
const sub=(a,b)=>add(a,neg(b));
const mul=(a,b)=>rational(a.n*b.n,a.d*b.d);
function number(a){
  let d=a.d,two=0,five=0;
  while(d%2n===0n){d/=2n;two++;}while(d%5n===0n){d/=5n;five++;}
  if(d!==1n)throw Error('内部の十進金額形式が不正です。');
  const scale=Math.max(two,five);
  return Number(String(a.n*2n**BigInt(scale-two)*5n**BigInt(scale-five))+'e-'+scale);
}
function evaluate(x) {
  for(const k of ['price','demand','rent','cash','days','cost_a','cost_b','return_a','return_b']) if(!finite(x[k])) throw Error(k+'は有限の数値が必要です。');
  if(!['accounting','funded'].includes(x.mode)) throw Error('会計モードが不正です。');
  if(!Number.isInteger(x.days)||x.days<1||x.days>365) throw Error('日数は1〜365の整数です。');
  if(['price','demand','rent','cash','cost_a','cost_b'].some(k=>x[k]<0)) throw Error('価格・需要・家賃・初期現金・原価は0以上です。');
  if(['return_a','return_b'].some(k=>x[k]<0||x[k]>1)) throw Error('返品率は0〜1です。');
  if(x.mode==='funded' && (!Number.isSafeInteger(x.demand)||Math.min(x.cost_a,x.cost_b)<=0)) throw Error('手元資金モードの需要は0〜9007199254740991の整数、原価は正の値にしてください。');
  const zero=decimal(0),price=decimal(x.price),demand=decimal(x.demand),dailyRent=decimal(x.rent);
  const suppliers=['a','b'].map(label=>{
    const c=decimal(x['cost_'+label]),rate=decimal(x['return_'+label]);
    let cash=decimal(x.cash),stopped=null;const trace=[];
    for(let day=1;day<=x.days;day++){
      const opening=cash,active=stopped===null;
      let sold=active?demand:zero;
      if(active&&x.mode==='funded'){
        const budget=cash.n>0n?cash:zero;
        const affordable=(budget.n*c.d)/(budget.d*c.n);
        sold=rational(affordable<BigInt(x.demand)?affordable:BigInt(x.demand));
      }
      const purchase=mul(sold,c),gross=mul(sold,price),refund=mul(gross,rate),rent=active?dailyRent:zero;
      cash=sub(sub(add(sub(opening,purchase),gross),refund),rent);
      const values={opening,purchased:sold,purchase,gross,refund,rent,sold,
        lost:active?sub(demand,sold):zero,expected_returns:mul(sold,rate),cash};
      const row=Object.fromEntries(Object.entries(values).map(([k,v])=>[k,number(v)]));
      if(!Object.values(row).every(finite))throw Error('金額が有限値を超えました。');
      trace.push({day,active,...row,return_ratio:sold.n!==0n?x['return_'+label]:null});
      if(x.mode==='funded'&&stopped===null&&cash.n<0n)stopped=day;
    }
    return {supplier:label.toUpperCase(),margin:number(sub(mul(price,sub(decimal(1),rate)),c)),final_cash:number(cash),stopped,trace};
  });
  const return_b_tie=x.price===0?null:x.return_a-(x.cost_b-x.cost_a)/x.price;
  const margin_difference=x.price*(x.return_a-x.return_b)-(x.cost_b-x.cost_a);
  if((return_b_tie!==null&&!finite(return_b_tie))||!finite(margin_difference)) throw Error('境界計算が有限値を超えました。');
  return {suppliers,return_b_tie,margin_difference};
}
const api={kind:'retailbench',defaults,evaluate};
const spec={"id": "retailbench-local-accounting", "version": "2.0.0", "source": {"url": "https://arxiv.org/html/2603.16453v3", "version": "arXiv:2603.16453v3"}, "conventions": {"money": "Input JSON numbers interpreted by canonical decimal value; exact rational monetary transitions internally; no affordability epsilon or cent rounding. Display/export numbers are rounded to binary64; inputs are recomputed on import.", "accounting": "Unlimited borrowing; daily q*(p*(1-r)-c)-rent; no stop at negative cash.", "funded": "Safe integer demand 0..9007199254740991, positive cost; floor(exact cash/cost) capped by demand; prepay, same-day delivery/sale/refund, then rent; negative closing cash stops next-day transactions and rent.", "returns": "Same-day full refunds, returned stock discarded, zero lead time and carryover; fractional returned units are expectations. Zero sales return ratio undefined.", "boundary": "p*(r_A-r_B)=c_B-c_A describes accounting unit-margin tie only; price zero threshold undefined; local cash is not paper net worth or survival."}};
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
