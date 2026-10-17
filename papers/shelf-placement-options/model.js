(function(root){'use strict';
const tol=1e-10;
// UI dimensions are multiples of 0.1. Arithmetic uses integer tenths;
// exported decimals therefore match Python's exact Fraction(str(value)).
function grid(x){if(!Number.isFinite(x)||x<0||Math.abs(x*10-Math.round(x*10))>1e-9)throw new RangeError('寸法は非負の0.1刻み');return Math.round(x*10);}
function finish(input,candidates){const good=candidates.filter(x=>x.feasible);const value=Math.max(...good.map(x=>x.profit));const ties=good.filter(x=>Math.abs(x.profit-value)<=tol);return {input,candidates,best:ties[0]||null,ties,complete:true};}
function toyA(nu=0,beta=.5){const n=grid(nu);const candidates=[];for(const mode of ['hang','shelf'])for(let b=1;b<=4;b++){const hUnits=mode==='hang'?b*(30+n):20*b,h=hUnits/10;const feasible=hUnits<=80;candidates.push({mode,faces:b,profit:(mode==='hang'?12:8)*b**beta,feasible,reasons:feasible?[]:['A:外枠超過'],layout:{width:2,height:8,nu,thickness:0,boards:[],expected_ids:['A'],rects:[{id:'A',x:0,y:0,w:2,h,mode,faces:b,max_faces:4}]}});}return finish({nu,beta},candidates);}
function toyB(fixed_y=null,nu=1,thickness=1){const n=grid(nu),t=grid(thickness),fixed=fixed_y===null?null:grid(fixed_y);const rows=[];for(let a=1;a<=3;a++)for(let b=1;b<=3;b++)for(const lower of ['A','B']){const hs={A:2*a,B:b},upper=lower==='A'?'B':'A',yUnits=fixed===null?10*hs[lower]+n+t:fixed,y=yUnits/10,reasons=[];if(10*hs[lower]+n>yUnits-t)reasons.push('棚板下余白不足');if(yUnits+10*hs[upper]>90)reasons.push('外枠超過');if(yUnits-t<0||yUnits>90)reasons.push('棚板境界');rows.push({faces:[a,b],lower,profit:10*Math.sqrt(a)+8*Math.sqrt(b),feasible:!reasons.length,reasons,layout:{width:4,height:9,nu,thickness,boards:[y],expected_ids:['A','B'],rects:['A','B'].map(id=>({id,x:0,y:id===lower?0:y,w:4,h:hs[id],mode:'shelf',faces:id==='A'?a:b,max_faces:3}))}});}return finish({fixed_y,nu,thickness},rows);}
const api={toyA,toyB};if(typeof module!=='undefined')module.exports=api;else root.PlacementModel=api;
})(globalThis);
