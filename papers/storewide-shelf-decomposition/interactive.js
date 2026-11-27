'use strict';
const M=ShelfModel, p={...M.defaults}, $=id=>document.getElementById(id), fmt=x=>x.toFixed(3);
const specs=[['capacity','店全体で配れる棚幅の上限',2,8,1],['s','代替率 s',0,1,.1],['beta','陳列面数を増やしたときの需要の伸び β',0,1,.05],['r','補充の負担を費用に換算する係数 r',0,12,1],['c','1商品を採用する費用 c',0,10,1],['e','採用する商品で残す基礎需要の割合 e',0,1,.05],['brands','カテゴリ内の最低ブランド数',1,2,1]];
const explanations={capacity:'モデルはAとBに配る幅の合計を、この値以下に抑えます。',s:'代替率は、置かない商品の基礎需要のうち、置く商品に移る割合です。',beta:'βが0なら、陳列面数を増やしても、その商品が売れると見込む数は増えません。',r:'モデルは需要を棚在庫で割り、係数rを掛けて補充費を求めます。rが変わると、利益が最も高い商品構成も変わることがあります。',c:'モデルは棚に置く商品ごとに、1期間に一度、この額を利益から引きます。',e:'モデルは採用商品の基礎需要を足し、全商品の基礎需要で割ります。商品間で移る需要や面数で増えた需要は足しません。',brands:'各カテゴリに最低いくつのブランドを置くかを指定します。上限は2ブランドです。'};
let result, selected=[3,2];
function band(solution,label){if(!solution)return `<h3>${label}</h3><p>この条件を満たす品ぞろえはありません。</p>`;return `<h3>${label}</h3><div class="shelf">`+solution.categories.map((c,i)=>`<div class="slot" style="width:${100*solution.allocation[i]/p.capacity}%"><div class="used" style="width:${100*c.used/solution.allocation[i]}%">${'AB'[i]}</div></div>`).join('')+`</div><p>${solution.categories.map((c,i)=>`${'AB'[i]}：配った幅${solution.allocation[i]}、商品が使う幅${c.used}、その中の空き${solution.allocation[i]-c.used}`).join(' ／ ')}。どのカテゴリにも配っていない幅は${p.capacity-solution.allocation.reduce((a,b)=>a+b,0)}です。</p>`;}
function breakdown(b){const maxD=Math.max(1,...b.rows.map(x=>x.direct+x.transfer)),maxC=Math.max(1,...b.rows.flatMap(x=>[x.gross,x.replenishment,x.fixed]));return '<h4>需要の内訳（個／期間）</h4><p>緑は面数に応じた商品自身の需要、茶色は置かなかった商品から移る需要を表します。</p>'+b.rows.map(x=>`<p>${x.id}：${fmt(x.direct)} ＋ ${fmt(x.transfer)}<br><span class="bar" style="width:${70*x.direct/maxD}%"></span><span class="bar transfer" style="width:${70*x.transfer/maxD}%"></span></p>`).join('')+'<h4>1期間の粗利と費用（教材単位）</h4>'+b.rows.map(x=>`<p>${x.id}</p>`+[['粗利合計','gross'],['補充費','replenishment'],['商品採用費','fixed']].map(([label,k])=>`<p>${label} ${fmt(x[k])}<br><span class="bar ${k==='gross'?'':'cost'}" style="width:${70*x[k]/maxC}%"></span></p>`).join('')).join('');}
for(const [key,label,min,max,step] of specs){const el=document.createElement('label');el.innerHTML=`${label} <output id="out-${key}"></output><small>${explanations[key]}</small><input id="control-${key}" type="range" min="${min}" max="${max}" step="${step}" value="${p[key]}" aria-label="${label}">`;$('controls').append(el);el.querySelector('input').addEventListener('input',e=>{p[key]=Number(e.target.value);render();});}
$('inputs').innerHTML=M.items.map(x=>`<tr>${[x.id,x.brand,x.q,x.p,x.w,x.d].map(v=>`<td>${v}</td>`).join('')}</tr>`).join('');
function details(){
 $('selection').innerHTML=selected.map((cap,i)=>{const row=result.tables[i].find(x=>x.capacity===cap),b=row.best;
 if(!b)return `<h3>${'AB'[i]}：幅${cap}では条件を満たす商品構成がない</h3>`;
 return `<h3>${'AB'[i]}：割当幅${cap}、実使用幅${b.used}、利益${fmt(b.profit)}</h3><p>置かない商品すべての基礎需要 U=${fmt(b.unmet_base)}、別の商品に移らない分 (1−s)U=${fmt(b.lost)}</p><div class="scroll"><table><thead><tr>${['商品ID','フェイス数（面）','商品自身の需要（個／期間）','置かなかった商品から移る需要','粗利合計','補充費','商品採用費'].map(v=>`<th>${v}</th>`).join('')}</tr></thead><tbody>${b.rows.map(x=>`<tr>${[x.id,x.faces,...['direct','transfer','gross','replenishment','fixed'].map(k=>fmt(x[k]))].map(v=>`<td>${v}</td>`).join('')}</tr>`).join('')}</tbody></table></div>${breakdown(b)}`;
 }).join('');
 document.querySelectorAll('[data-cap]').forEach(b=>b.setAttribute('aria-pressed',String(selected[+b.dataset.cat]===+b.dataset.cap)));
}
function render(){
 for(const [k] of specs){$('out-'+k).value=p[k];$('control-'+k).value=p[k];}
 result=M.solve(p); const b=result.best;
 $('summary').innerHTML=b?`<p><strong>最大の利益 ${fmt(b.profit)}、AとBに配る幅 ${b.allocation.join(':')}</strong>。どのカテゴリにも配らなかった幅は${p.capacity-b.allocation.reduce((a,v)=>a+v,0)}です。同じ利益になる陳列面数の組み合わせは${b.optimal_face_count}通りあります。計算は架空の6商品の候補をすべて比べています。</p>`:'<p><strong>実行不能</strong>：この棚幅では、残す基礎需要の割合と最低ブランド数の条件を同時に満たす案がありません。</p>';
 $('shelf').innerHTML=band(result.proportional,'基礎粗利の比で幅を配った案')+band(b,'店全体の最大利益を得る案');
 selected=b?[...b.allocation]:[1,1];
 $('values').innerHTML=result.tables.map((table,i)=>`<div class="card"><h3>カテゴリ${'AB'[i]}</h3><p>幅を選ぶと、その幅で利益が最も高い案を表示します。</p><div class="value-row">${table.map(x=>`<button data-cat="${i}" data-cap="${x.capacity}" aria-pressed="false">${x.capacity} → ${x.best?fmt(x.best.profit):'実行不能'}</button>`).join('')}</div></div>`).join('');
 document.querySelectorAll('[data-cap]').forEach(btn=>btn.addEventListener('click',()=>{selected[+btn.dataset.cat]=+btn.dataset.cap;details();}));
 $('comparisons').innerHTML=[['幅ごとの最大利益を使う案',b],['基礎粗利の比で幅を決める案',result.proportional],['代替率を0として商品を選んだ案',result.ignored]].map(([name,x])=>`<tr><th>${name}</th><td>${x?x.allocation.join(':'):'—'}</td><td>${x&&x.profit!==null?fmt(x.profit):'実行不能'}</td></tr>`).join('');details();
}
$('reset').addEventListener('click',()=>{Object.assign(p,M.defaults);render();});
$('download').addEventListener('click',()=>{const url=URL.createObjectURL(new Blob([JSON.stringify({synthetic:true,inputs:M.items,parameters:p,selected_detail_widths:selected,capacity_candidates:[1,2,3,4],result},null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='shelf-synthetic-results.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
render();
