/* Pure model assertions. Does not launch a browser or claim DOM validation. */
const assert=require('node:assert/strict'),fs=require('node:fs');
const reason=require('../papers/reasoncast-agentic-demand-forecasting/model.js');
const retail=require('../papers/retailbench-long-horizon-store-agents/model.js');
const clone=x=>structuredClone(x);
const close=(a,b)=>assert.ok(Math.abs(a-b)<=1e-9+1e-10*Math.abs(b),`${a} != ${b}`);
function compare(a,b){
 if(typeof b==='number'){close(a,b);return;}
 if(b===null||typeof b!=='object'){assert.equal(a,b);return;}
 assert.deepEqual(Object.keys(a).sort(),Object.keys(b).sort());for(const k of Object.keys(b))compare(a[k],b[k]);
}
const rows=reason.evaluate(clone(reason.defaults)).rows;
close(rows[0].wmape,50);close(rows[1].wmape,0);close(rows[2].wmape,29.28932188134524);
let x=clone(reason.defaults);x.actual.fill(10);x.gate=1;close(reason.evaluate(x).rows[2].wmape,100);
x.actual.fill(0);assert.equal(reason.evaluate(x).rows[2].wmape,null);
x=clone(reason.defaults);x.additive.fill(-15);x.gate=1;assert.deepEqual(reason.evaluate(x).rows[2].prediction,Array(7).fill(-10));
x.route='Skip';x.base[0]=-0;assert.ok(Object.is(reason.evaluate(x).rows[2].prediction[0],-0));
for(const bad of [{gate:2},{actual:[1]},{actual:Array(7).fill(-1)},{level:Array(7).fill(Infinity)}])assert.throws(()=>reason.evaluate({...clone(reason.defaults),...bad}));
x={...retail.defaults,mode:'funded',cash:40,demand:10,price:10,rent:35,days:2,return_a:.15,return_b:0};
let result=retail.evaluate(x);assert.deepEqual(result.suppliers.map(s=>s.trace.map(t=>t.cash)),[[50,60],[45,55]]);
x.rent=80;x.days=4;result=retail.evaluate(x);assert.deepEqual(result.suppliers[0].trace.map(t=>t.cash),[5,-70.5,-70.5,-70.5]);
assert.equal(result.suppliers[0].trace[2].rent,0);
for(const rate of [.2,.25,.3])close(retail.evaluate({...retail.defaults,return_b:rate}).suppliers[1].final_cash,rate===.2?3000:rate===.25?0:-3000);
assert.equal(retail.evaluate({...retail.defaults,price:0,demand:0}).return_b_tie,null);
assert.equal(retail.evaluate({...retail.defaults,price:0,demand:0}).suppliers[0].trace[0].return_ratio,null);
for(const bad of [{mode:'funded',cost_a:0},{mode:'funded',demand:.5},{return_b:1.1},{days:NaN}])assert.throws(()=>retail.evaluate({...retail.defaults,...bad}));
for(const model of [reason,retail]){
 const input=clone(model.defaults);if(model===reason)input.gate=.37123;else input.return_b=.13791;
 const packed=JSON.parse(JSON.stringify(model.pack(input)));packed.output='forged output';
 assert.deepEqual(model.unpack(packed),input);compare(model.evaluate(model.unpack(packed)),model.evaluate(input));
 assert.throws(()=>model.unpack({...packed,schema:99}));
}
assert.equal(reason.evaluate({...reason.defaults,base:Array(7).fill(1e200),actual:Array(7).fill(1e-200)}).rows[0].status,'unavailable');
assert.throws(()=>retail.evaluate({...retail.defaults,price:1e-320,demand:0}));
assert.equal(retail.evaluate({...retail.defaults,mode:'funded',cash:1,demand:1,cost_a:5e-324,cost_b:5e-324,days:1}).suppliers[0].trace[0].sold,1);
const cases=JSON.parse(fs.readFileSync(0,'utf8'));
for(const c of cases){const model=c.slug.startsWith('reasoncast')?reason:retail;compare(model.evaluate(c.inputs),c.expected);}
console.log(`PASS: independent JS boundaries, export/import data contract, ${cases.length} Python/JS parity cases; browser NOT TESTED`);
for(const [cash,sold] of [[.3,3],[.29999999999999993,2],[.30000000000000004,3],[.299,2]]){
 const row=retail.evaluate({...retail.defaults,mode:'funded',cash,cost_a:.1,cost_b:.1,demand:3,price:0,rent:0,days:1,return_a:0,return_b:0}).suppliers[0].trace[0];
 assert.equal(row.sold,sold);assert.ok(row.purchase<=cash);assert.ok(row.cash>=0);
 if(cash===.3){assert.equal(row.purchase,.3);assert.equal(row.cash,0);}
}
let overflow=reason.evaluate({...reason.defaults,route:'Skip',level:Array(7).fill(1000)});
assert.equal(overflow.rows[1].status,'unavailable');assert.equal(overflow.rows[1].prediction,null);
assert.deepEqual(overflow.rows[2].prediction,Array(7).fill(10));assert.equal(overflow.rows[2].wmape,50);
assert.ok(reason.evaluate({...reason.defaults,base:Array(7).fill(-10),additive:Array(7).fill(20),level:Array(7).fill(0),gate:1}).negative_prediction);
for(const raw of ['1,2,3,4,5,6,','1,,2,3,4,5,6,7',',1,2,3,4,5,6,7','1、2、3、4、5、6、 ',' '])assert.throws(()=>reason.parseArray(raw));
for(const raw of ['1,2,3,4,5,6,7',' 1 2 3 4 5 6 7 ','1、2、3、4、5、6、7','1, 2, 3, 4, 5, 6, 7'])assert.deepEqual(reason.parseArray(raw),[1,2,3,4,5,6,7]);
for(const model of [reason,retail]){
 const packet=model.pack(model.defaults);assert.equal(packet.schema,2);assert.equal(packet.model.version,'2.0.0');
 assert.ok(packet.model.source.url.startsWith('https://arxiv.org/html/'));assert.ok(packet.model.conventions);
 assert.throws(()=>model.unpack({...packet,model:{...packet.model,version:'unknown'}}));
}
console.log('PASS: exact decimal boundaries, overflow isolation, negative baseline, missing-token parser and model metadata');
