'use strict';
const M=ShelfModel, p={...M.defaults}, $=id=>document.getElementById(id), fmt=x=>x.toFixed(3);
const specs=[['capacity','店全体で使える棚幅',2,8,1],['s','代替率 s',0,1,.1],['beta','フェイス数による需要の伸び方 β',0,1,.05],['r','補充費係数 r',0,12,1],['c','1商品を採用する費用 c',0,10,1],['e','採用商品に残す基礎需要の割合 e',0,1,.05],['brands','カテゴリ内の最低ブランド数',1,2,1]];
const explanations={capacity:'2カテゴリへの割当幅の合計を、この幅以下にします。',s:'未採用品の基礎需要のうち、採用品へ移る割合です。',beta:'β=0では面数を増やしても商品自身の需要は増えません。',r:'需要を棚在庫で割った値に掛ける費用です。最適な商品構成も変わる場合があります。',c:'採用した商品ごとに、期間あたり一度差し引きます。',e:'流入や面数による増加を含めず、採用品の基礎需要だけで判定します。',brands:'各カテゴリのブランド数の下限です。上限は2ブランドです。'};
let result, selected=[3,2];
function band(solution,label){if(!solution)return `<h3>${label}</h3><p>条件を満たす案がありません。</p>`;return `<h3>${label}</h3><div class="shelf">`+solution.categories.map((c,i)=>`<div class="slot" style="width:${100*solution.allocation[i]/p.capacity}%"><div class="used" style="width:${100*c.used/solution.allocation[i]}%">${'AB'[i]}</div></div>`).join('')+`</div><p>${solution.categories.map((c,i)=>`${'AB'[i]}：割当${solution.allocation[i]}、使用${c.used}、空き${solution.allocation[i]-c.used}`).join(' ／ ')}。未割当${p.capacity-solution.allocation.reduce((a,b)=>a+b,0)}。</p>`;}
function breakdown(b){const maxD=Math.max(1,...b.rows.map(x=>x.direct+x.transfer)),maxC=Math.max(1,...b.rows.flatMap(x=>[x.gross,x.replenishment,x.fixed]));return '<h4>需要の内訳（個／期間）</h4><p>緑＝商品自身、茶＝未採用品からの流入</p>'+b.rows.map(x=>`<p>${x.id}：${fmt(x.direct)} ＋ ${fmt(x.transfer)}<br><span class="bar" style="width:${70*x.direct/maxD}%"></span><span class="bar transfer" style="width:${70*x.transfer/maxD}%"></span></p>`).join('')+'<h4>金額の内訳（教材用金額／期間）</h4>'+b.rows.map(x=>`<p>${x.id}</p>`+[['粗利合計','gross'],['補充費','replenishment'],['商品採用費','fixed']].map(([label,k])=>`<p>${label} ${fmt(x[k])}<br><span class="bar ${k==='gross'?'':'cost'}" style="width:${70*x[k]/maxC}%"></span></p>`).join('')).join('');}
for(const [key,label,min,max,step] of specs){const el=document.createElement('label');el.innerHTML=`${label} <output id="out-${key}"></output><small>${explanations[key]}</small><input id="control-${key}" type="range" min="${min}" max="${max}" step="${step}" value="${p[key]}" aria-label="${label}">`;$('controls').append(el);el.querySelector('input').addEventListener('input',e=>{p[key]=Number(e.target.value);render();});}
$('inputs').innerHTML=M.items.map(x=>`<tr>${[x.id,x.brand,x.q,x.p,x.w,x.d].map(v=>`<td>${v}</td>`).join('')}</tr>`).join('');
function details(){
 $('selection').innerHTML=selected.map((cap,i)=>{const row=result.tables[i].find(x=>x.capacity===cap),b=row.best;
 if(!b)return `<h3>${'AB'[i]}：割当幅${cap}は実行不能</h3>`;
 return `<h3>${'AB'[i]}：割当幅${cap}、実使用幅${b.used}、利益${fmt(b.profit)}</h3><p>非採用商品の基礎需要U=${fmt(b.unmet_base)}、購入断念=(1−s)U=${fmt(b.lost)}</p><div class="scroll"><table><thead><tr>${['商品ID','フェイス数（面）','商品自身の需要（個／期間）','未採用商品からの流入','粗利合計','補充費','商品採用費'].map(v=>`<th>${v}</th>`).join('')}</tr></thead><tbody>${b.rows.map(x=>`<tr>${[x.id,x.faces,...['direct','transfer','gross','replenishment','fixed'].map(k=>fmt(x[k]))].map(v=>`<td>${v}</td>`).join('')}</tr>`).join('')}</tbody></table></div>${breakdown(b)}`;
 }).join('');
 document.querySelectorAll('[data-cap]').forEach(b=>b.setAttribute('aria-pressed',String(selected[+b.dataset.cat]===+b.dataset.cap)));
}
function render(){
 for(const [k] of specs){$('out-'+k).value=p[k];$('control-'+k).value=p[k];}
 result=M.solve(p); const b=result.best;
 $('summary').innerHTML=b?`<p><strong>最適利益 ${fmt(b.profit)}、割当 A:B=${b.allocation.join(':')}</strong>。全店の未割当幅は${p.capacity-b.allocation.reduce((a,v)=>a+v,0)}です。最大利益を得るフェイス数の組合せは${b.optimal_face_count}通り。この架空の6商品について、全候補を比べた最大利益です。</p>`:'<p><strong>実行不能</strong>：必要な需要保持率・ブランド数をこの全店容量では満たせません。</p>';
 $('shelf').innerHTML=band(result.proportional,'基礎粗利に比例して幅を決めた案')+band(b,'店全体の最大利益を得る案');
 selected=b?[...b.allocation]:[1,1];
 $('values').innerHTML=result.tables.map((table,i)=>`<div class="card"><h3>カテゴリ${'AB'[i]}</h3><p>割当幅 → 最良利益</p><div class="value-row">${table.map(x=>`<button data-cat="${i}" data-cap="${x.capacity}" aria-pressed="false">${x.capacity} → ${x.best?fmt(x.best.profit):'実行不能'}</button>`).join('')}</div></div>`).join('');
 document.querySelectorAll('[data-cap]').forEach(btn=>btn.addEventListener('click',()=>{selected[+btn.dataset.cat]=+btn.dataset.cap;details();}));
 $('comparisons').innerHTML=[['分解最適化',b],['基礎粗利比例',result.proportional],['代替無視で選んだ解',result.ignored]].map(([name,x])=>`<tr><th>${name}</th><td>${x?x.allocation.join(':'):'—'}</td><td>${x&&x.profit!==null?fmt(x.profit):'実行不能'}</td></tr>`).join('');details();
}
$('reset').addEventListener('click',()=>{Object.assign(p,M.defaults);render();});
$('download').addEventListener('click',()=>{const url=URL.createObjectURL(new Blob([JSON.stringify({synthetic:true,inputs:M.items,parameters:p,selected_detail_widths:selected,capacity_candidates:[1,2,3,4],result},null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='shelf-synthetic-results.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
render();
