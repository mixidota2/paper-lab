'use strict';
(function(root) {
 const modes=['increment','selection','substitution'];
 const sum=xs=>xs.reduce((a,b)=>a+b,0);
 const dot=(a,b)=>sum(a.map((v,i)=>v*b[i]));
 const ctrl=r=>Array.from({length:7},(_,d)=>Number(d===r[0])).concat(r[1],r[2]);
 // 人工例の各行には、曜日、小売の予測値、朝の在庫数、値引き価格で売れた数、
 // 総販売数、店がシールを貼ったかどうか、値引きで増えた販売数をこの順に入れる。
 function rows(mode){
   if(!modes.includes(mode)) throw new RangeError('unknown mode');
   const data=[];
   for(let day=0;day<7;day++)for(const f of [4,8])for(const s of [20,30]){
     const b=3+day+f+s/10;
     for(const u of [-1,0,1])data.push([day,f,s,0,b+u,false,0]);
     // 店がシールを貼っても、値引き品が1個も売れない行を作る。
     data.push([day,f,s,0,b,true,0]);
     for(const d of [1,3]){
       // 最初の二例で実際に売れた数は同じ。値引きしなかった場合に売れた数だけが違う。
       const observed=b+(mode==='substitution'?0:d), unexposed=b+(mode==='selection'?d:0);
       data.push([day,f,s,d,observed,true,observed-unexposed]);
     }
   }
   return data;
 }
 function ols(xs,ys){
   const cols=xs[0].map((_,i)=>xs.map(row=>row[i]));
   const m=cols.map(a=>cols.map(b=>dot(a,b)).concat(dot(a,ys)));
   for(let i=0;i<m.length;i++){
     const j=m.findIndex((row,k)=>k>=i&&Math.abs(row[i])>1e-9);
     if(j<0)throw new Error('rank deficient');
     [m[i],m[j]]=[m[j],m[i]];
     const p=m[i][i];m[i]=m[i].map(v=>v/p);
     for(let k=0;k<m.length;k++)if(k!==i){const c=m[k][i];m[k]=m[k].map((v,l)=>v-c*m[i][l]);}
   }
   return m.map(r=>r.at(-1));
 }
 function evaluate(mode){
   // 回帰は値引き品が売れたかどうかで行を分ける。シールの有無では分けない。
   const data=rows(mode), a=data.filter(r=>r[3]===0), b=data.filter(r=>r[3]>0);
   const beta=ols(a.map(ctrl),a.map(r=>r[4])), x=b.map(r=>ctrl(r).concat(r[3]));
   const u=b.map(r=>r[4]-dot(ctrl(r),beta));
   const round=x=>Math.round(1e9*x)/1e9;
   return {base_rows:a.length,positive_ds_rows:b.length,sticker_only_rows:a.filter(r=>r[5]).length,slope:round(ols(x,u).at(-1)),total_slope:round(ols(x,b.map(r=>r[4])).at(-1)),regular_slope:round(ols(x,b.map(r=>r[4]-r[3])).at(-1)),mean_residual:round(sum(u)/u.length),true_increment:round(sum(b.map(r=>r[6]))/b.length)};
 }
 const api={modes,evaluate};
 if(typeof module!=='undefined')module.exports=api;else root.MarkdownToy=api;
})(globalThis);
