/* Local live calculation; no preset-result lookup, no remote calls. */
(() => {
'use strict';
const root=document.querySelector('[data-reference-lab]'),model=window.ReferenceModel;
if(!root||!model)return;
const form=root.querySelector('form'),out=root.querySelector('[data-output]'),error=root.querySelector('[data-error]');
const jsonBox=root.querySelector('[data-json]'),save=root.querySelector('[data-export]');
const num=v=>v===null?'未定義':Number(v).toLocaleString('ja-JP',{maximumFractionDigits:6});
let current=null;
function node(tag,text){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;return n;}
function table(headers,rows,caption){
  const wrap=node('div');wrap.className='reference-scroll';wrap.tabIndex=0;wrap.setAttribute('role','region');wrap.setAttribute('aria-label',caption);
  const t=node('table'),h=node('thead'),hr=node('tr');t.append(node('caption',caption));
  headers.forEach(v=>{const th=node('th',v);th.scope='col';hr.append(th);});h.append(hr);t.append(h);const b=node('tbody');
  rows.forEach(row=>{const tr=node('tr');row.forEach(v=>tr.append(node('td',typeof v==='number'||v===null?num(v):v)));b.append(tr);});t.append(b);wrap.append(t);return wrap;
}
function plot(series,caption){
  const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');svg.setAttribute('viewBox','0 0 640 240');svg.setAttribute('role','img');svg.setAttribute('aria-label',caption+'。正確な値は後続の表。');
  const all=series.flatMap(s=>s.values),lo=Math.min(0,...all),hi=Math.max(1,...all),n=Math.max(...series.map(s=>s.values.length));
  const colors=['#222222','#0072b2','#a74e00','#6846a5'];
  const title=document.createElementNS(ns,'title');title.textContent=caption;svg.append(title);
  [lo,hi].forEach((v,i)=>{const text=document.createElementNS(ns,'text');text.setAttribute('x','2');text.setAttribute('y',i?22:210);text.setAttribute('font-size','12');text.textContent=num(v);svg.append(text);});
  series.forEach((s,j)=>{const line=document.createElementNS(ns,'polyline');line.setAttribute('points',s.values.map((v,i)=>`${95+520*i/Math.max(1,n-1)},${210-190*(v-lo)/(hi-lo)}`).join(' '));line.setAttribute('fill','none');line.setAttribute('stroke',colors[j]);line.setAttribute('stroke-width','3');if(j%2)line.setAttribute('stroke-dasharray','7 4');svg.append(line);});
  const block=node('figure');block.append(svg,node('figcaption',caption+'。横軸は左から日順、縦軸は各値。'+series.map((s,j)=>`${s.label}（${['黒・実線','青・破線','茶・実線','紫・破線'][j]}）`).join('、')));return block;
}
function read(){const x={};for(const [key,value]of Object.entries(model.defaults)){
  const field=form.elements.namedItem(key),raw=field.value.trim();if(!raw)throw Error(key+'を入力してください。');
  x[key]=Array.isArray(value)?raw.split(/[\s,、]+/).map(Number):typeof value==='number'?Number(raw):raw;
}return x;}
function write(x){for(const key of Object.keys(model.defaults))form.elements.namedItem(key).value=Array.isArray(x[key])?x[key].join(', '):x[key];}
function render(){
  try{
    const inputs=read(),result=model.evaluate(inputs);current=model.pack(inputs);out.replaceChildren();error.textContent='';save.disabled=false;
    if(model.kind==='reasoncast'){
      const names=['元予測','常時補正 g=1','選択した補正'];
      out.append(table(['比較','誤差総和','実績分母','WMAPE (%)','元予測との差 (pp)','MAE'],result.rows.map((r,i)=>[names[i],r.error_sum,r.denominator,r.wmape,r.delta_pp,r.mae]),'同じ実績・7日間で比較'));
      const d=result.rows[2].delta_pp;
      out.append(node('p',d===null?'実績の合計が0のためWMAPEと差は未定義です。MAEで誤差を確認してください。':`元予測との差は ${num(d)} pp。${Math.abs(d)<1e-9?'同点（数値誤差の範囲）':d<0?'改善':'悪化'}です。実績を基準にした誤差であり、意味情報を推論できた証拠ではありません。`));
      if(result.negative_prediction)out.append(node('p','警告：補正後に負の予測があります。生の値を表示し、0へ切り上げていません。'));
      out.append(plot([{label:'実績',values:inputs.actual},...result.rows.map((r,i)=>({label:names[i],values:r.prediction}))],'現在条件の7日予測'));
      out.append(table(['日','実績','元予測','常時補正','選択補正','元誤差','常時誤差','選択誤差'],inputs.actual.map((y,i)=>[i+1,y,...result.rows.map(r=>r.prediction[i]),...result.rows.map(r=>r.errors[i])]),'日別の予測と絶対誤差'));
      out.append(node('p',inputs.route==='Skip'?'Skipは補正演算を通さず元配列をコピーします。祝日にもSkipを許すこの比較は、原論文の制約を外した反実仮想教材です。':'選択した補正 = (b + g×a) × exp(g×l)。実績yは採点だけに使い、経路や予測を決めません。'));
    }else{
      out.append(table(['仕入先','単位粗利','最終現金','局所停止日'],result.suppliers.map(s=>[s.supplier,s.margin,s.final_cash,s.stopped===null?'停止なし':s.stopped]),'同じ価格・潜在需要・期間で比較'));
      out.append(node('p',`単位粗利差 B−A = ${num(result.margin_difference)}。会計モードの同点境界は p(r_A−r_B)=c_B−c_A。Bの返品率境界は ${num(result.return_b_tie)}${result.return_b_tie===null?'（価格0なので解けません）':''}。資金制約モードの最終現金の順位は、この境界だけでは決まりません。`));
      out.append(plot(result.suppliers.map(s=>({label:s.supplier,values:[inputs.cash,...s.trace.map(t=>t.cash)]})),'初期現金から日末現金への推移'));
      for(const s of result.suppliers)out.append(table(['日','状態','日初現金','仕入数量','仕入支払','売上総額','返金','家賃','販売','失注','期待返品数','返品比率','日末現金'],s.trace.map(t=>[t.day,t.active?'営業':'停止後',t.opening,t.purchased,t.purchase,t.gross,t.refund,t.rent,t.sold,t.lost,t.expected_returns,t.return_ratio,t.cash]),'仕入先'+s.supplier+'の台帳（通貨・個・比率）'));
      out.append(node('p','日末現金 = 日初現金 − 仕入支払 + 売上総額 − 返金 − 家賃。停止後は取引・家賃とも0。販売ゼロの返品比率は未定義です。返品数の端数は期待値であり、実顧客数ではありません。'));
    }
    root.dataset.ready='true';
  }catch(e){current=null;save.disabled=true;out.replaceChildren();error.textContent=e.message;}
}
form.addEventListener('input',render);form.addEventListener('submit',e=>e.preventDefault());
root.querySelector('[data-reset]').addEventListener('click',()=>{write(model.defaults);root.querySelector('[data-guess]').selectedIndex=0;jsonBox.value='';render();});
save.addEventListener('click',()=>{if(!current)return;const text=JSON.stringify(current,null,2);jsonBox.value=text;const url=URL.createObjectURL(new Blob([text],{type:'application/json'}));const a=node('a');a.href=url;a.download=model.kind+'-comparison.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
root.querySelector('[data-import]').addEventListener('click',()=>{try{const x=model.unpack(JSON.parse(jsonBox.value));write(x);render();}catch(e){error.textContent='読み込み失敗：'+e.message;}});
write(model.defaults);render();
})();
