// Original teaching calculator, not an author implementation.
function evaluate(a,h,admit=true,bypass=false,condition=false){
 if(!Array.isArray(a)||!a.length||!a.every(x=>x===0||x===1)||!Array.isArray(h)||!h.length||!h.every(x=>Number.isInteger(x)&&x>=0&&x<=3))throw Error('判定値を確認してください');
 if(!admit)return {admitted:false,score:null,link:false};
 const success=a.every(x=>x===1),binary=h.map(x=>x===1?1:x===2?Number(success):0),raw=binary.some(x=>x===0);
 return {admitted:true,agent:a.reduce((s,x)=>s+x,0)/a.length,harness:binary.reduce((s,x)=>s+x,0)/h.length,score:50*a.reduce((s,x)=>s+x,0)/a.length+50*binary.reduce((s,x)=>s+x,0)/h.length,success,clean:success&&!raw,raw,adjusted:raw&&!bypass,link:raw&&!success&&condition,validated:false};
}
if(typeof module!=='undefined')module.exports={evaluate};
