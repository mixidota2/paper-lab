/* Local live calculation; no preset-result lookup, no remote calls. */
(() => {
'use strict';
function plotCoordinates(series){
  const all=series.flatMap(s=>s.values);
  if(!all.length||!all.every(Number.isFinite))throw Error('図には有限な値が必要です。');
  const lo=Math.min(0,...all),hi=Math.max(1,...all),scale=Math.max(Math.abs(lo),Math.abs(hi));
  // Normalize before subtraction and multiplication: neither hi-lo nor 190*v may overflow.
  const low=lo/scale,span=hi/scale-low,n=Math.max(...series.map(s=>s.values.length));
  const points=series.map(s=>s.values.map((v,i)=>[95+520*(i/Math.max(1,n-1)),210-190*((v/scale-low)/span)]));
  if(!points.flat(2).every(Number.isFinite))throw Error('図の座標が対応範囲を超えました。');
  return {lo,hi,points};
}
function metricText(v,undefinedDenominator=false){return v===null?(undefinedDenominator?'未定義':'計算不能'):v;}
function stopDayText(mode,stopped){return mode==='accounting'?'対象外（負現金でも継続）':stopped===null?'停止判断なし':stopped;}
function inputErrorText(message){
  const names={"base": "基準予測b", "actual": "実績y", "additive": "加算量a", "level": "対数倍率l", "gate": "補正の強さg", "route": "補正するかどうかの経路", "price": "販売価格p", "demand": "1日の潜在需要q", "rent": "1日の家賃R", "cash": "初期現金C₀", "days": "日数H", "cost_a": "Aの仕入原価c_A", "cost_b": "Bの仕入原価c_B", "return_a": "Aの返品率r_A", "return_b": "Bの返品率r_B", "mode": "会計モード"};
  let text=String(message);
  for(const [key,label] of Object.entries(names))text=text.replace(new RegExp('\\b'+key+'\\b','g'),label);
  return text.replace('実績分母が有限値を超えました。','実績の合計が計算できる範囲を超えました。').replace('schema 2','保存形式2')
    .replace('は有限な7日分の値が必要です。','は、計算で扱える範囲の数値を7日分入力してください。')
    .replace('強さは0〜1、経路はSkipまたは補正です。','補正の強さgは0〜1、経路は「補正しない（Skip）」または「補正」を選んでください。')
    .replace('配列は有限な数値で入力してください。','入力欄には、計算で扱える範囲の数値を入力してください。')
    .replace('は有限の数値が必要です。','は、計算で扱える範囲の数値を入力してください。')
    .replace('金額が有限値を超えました。','金額が計算できる範囲を超えました。')
    .replace('境界計算が有限値を超えました。','仕入先を比較する境界の計算が、計算できる範囲を超えました。');
}
function parseInputValue(model,key,raw,value){
  try{return Array.isArray(value)?model.parseArray(raw):typeof value==='number'?Number(raw):raw;}
  catch(e){throw Error(inputErrorText(key)+'：'+inputErrorText(e.message));}
}
if(typeof module!=='undefined'){module.exports={plotCoordinates,metricText,stopDayText,inputErrorText,parseInputValue};return;}
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
  const {lo,hi,points}=plotCoordinates(series);
  const colors=['#222222','#0072b2','#a74e00','#6846a5'];
  const title=document.createElementNS(ns,'title');title.textContent=caption;svg.append(title);
  [lo,hi].forEach((v,i)=>{const text=document.createElementNS(ns,'text');text.setAttribute('x','2');text.setAttribute('y',i?22:210);text.setAttribute('font-size','12');text.textContent=num(v);svg.append(text);});
  series.forEach((s,j)=>{const line=document.createElementNS(ns,'polyline');line.setAttribute('points',points[j].map(pair=>pair.join(',')).join(' '));line.setAttribute('fill','none');line.setAttribute('stroke',colors[j]);line.setAttribute('stroke-width','3');if(j%2)line.setAttribute('stroke-dasharray','7 4');svg.append(line);});
  const block=node('figure');block.append(svg,node('figcaption',caption+(model.kind==='reasoncast'?'。横軸は1〜7日目、縦軸は実績・予測の数量（入力と同じ単位）。':'。横軸は開始時点（0日目）と1〜H日目、縦軸は現金（教材内の通貨単位）。')+series.map((s,j)=>`${s.label}（${['黒・実線','青・破線','茶・実線','紫・破線'][j]}）`).join('、')));return block;
}
function read(){const x={};for(const [key,value]of Object.entries(model.defaults)){
  const field=form.elements.namedItem(key),raw=field.value.trim();if(!raw)throw Error(inputErrorText(key+'を入力してください。'));
  x[key]=parseInputValue(model,key,raw,value);
}return x;}
function write(x){for(const key of Object.keys(model.defaults))form.elements.namedItem(key).value=Array.isArray(x[key])?x[key].join(', '):x[key];}
function render(){
  try{
    const inputs=read(),result=model.evaluate(inputs);current=model.pack(inputs);out.replaceChildren();error.textContent='';save.disabled=false;
    if(model.kind==='reasoncast'){
      const names=['元予測','常時補正 g=1','選択した補正'];
      out.append(table(['比較','計算状態','誤差総和','実績の合計','WMAPE (%)','元予測との差（ポイント）','MAE'],result.rows.map((r,i)=>[names[i],r.status==='ok'?'計算済み':'計算不能（数値範囲超過）',metricText(r.error_sum),metricText(r.denominator),metricText(r.wmape,r.denominator===0),metricText(r.delta_pp,r.denominator===0),metricText(r.mae)]),'同じ実績・7日間で比較'));
      const d=result.rows[2].delta_pp;
      out.append(node('p',d===null?(result.rows[0].denominator===0?'実績の合計が0のためWMAPEと差は未定義です。MAEで誤差を確認してください。':'計算できない指標は「計算不能」と表示します。計算できる値は表示を続けます。'):`元予測との差は ${num(d)}ポイント。${Math.abs(d)<1e-9?'同点（数値誤差の範囲）':d<0?'改善':'悪化'}です。実績を基準にした誤差であり、意味情報を推論できた証拠ではありません。`));
      if(result.rows.some(r=>r.status==='unavailable'))out.append(node('p','計算不能の行は数値範囲を超えています。予測自体が計算不能なら曲線を描きません。Skipの元予測保持とは別です。'));
      if(result.negative_prediction)out.append(node('p','警告：元予測を含む比較行に負の予測があります。生の値を表示し、0へ切り上げていません。'));
      out.append(plot([{label:'実績',values:inputs.actual},...result.rows.map((r,i)=>({label:names[i],values:r.prediction})).filter(s=>s.values!==null)],'現在条件の7日予測'));
      out.append(table(['日','実績','元予測','常時補正','選択補正','基準予測の絶対誤差','常時誤差','選択誤差'],inputs.actual.map((y,i)=>[i+1,y,...result.rows.map(r=>r.prediction===null?'計算不能':r.prediction[i]),...result.rows.map(r=>r.errors===null?'計算不能':r.errors[i])]),'日別の予測と絶対誤差'));
      out.append(node('p',inputs.route==='Skip'?'Skipは補正演算を通さず元配列をコピーします。祝日にもSkipを許すこの比較は、原論文の制約を外した反実仮想教材です。':'選択した補正 = (b + g×a) × exp(g×l)。実績yは採点だけに使い、経路や予測を決めません。'));
    }else{
      out.append(table(['仕入先','単位粗利（通貨／個）','最終現金（通貨）','資金制約モードの停止判断日（翌日から営業停止）'],result.suppliers.map(s=>[s.supplier,s.margin,s.final_cash,stopDayText(inputs.mode,s.stopped)]),'同じ価格・潜在需要・期間で比較'));
      out.append(node('p',`単位粗利差 B−A = ${num(result.margin_difference)}。会計モードの同点境界は p(r_A−r_B)=c_B−c_A。Bの返品率境界は ${num(result.return_b_tie)}${result.return_b_tie===null?'（価格0なので解けません）':''}。資金制約モードの最終現金の順位は、この境界だけでは決まりません。`));
      out.append(plot(result.suppliers.map(s=>({label:s.supplier,values:[inputs.cash,...s.trace.map(t=>t.cash)]})),'初期現金から日末現金への推移'));
      for(const s of result.suppliers)out.append(table(['日','状態','日初現金（通貨）','仕入数量（個）','仕入支払（通貨）','売上総額（通貨）','返金（通貨）','家賃（通貨）','販売（個）','失注（個）','期待返品数（個）','返品比率（0〜1）','日末現金（通貨）'],s.trace.map(t=>[t.day,t.active?'営業':'この教材での停止後',t.opening,t.purchased,t.purchase,t.gross,t.refund,t.rent,t.sold,t.lost,t.expected_returns,t.return_ratio,t.cash]),'仕入先'+s.supplier+'の台帳（通貨・個・比率）'));
      out.append(node('p','日末現金 = 日初現金 − 仕入支払 + 売上総額 − 返金 − 家賃。停止後は取引・家賃とも0。販売ゼロの返品比率は未定義です。返品数の端数は期待値であり、実顧客数ではありません。'));
    }
    root.dataset.ready='true';
  }catch(e){current=null;save.disabled=true;out.replaceChildren();error.textContent=inputErrorText(e.message);}
}
form.addEventListener('input',render);form.addEventListener('submit',e=>e.preventDefault());
root.querySelector('[data-reset]').addEventListener('click',()=>{write(model.defaults);root.querySelector('[data-guess]').selectedIndex=0;jsonBox.value='';render();});
save.addEventListener('click',()=>{if(!current)return;const text=JSON.stringify(current,null,2);jsonBox.value=text;const url=URL.createObjectURL(new Blob([text],{type:'application/json'}));const a=node('a');a.href=url;a.download=model.kind+'-comparison.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
root.querySelector('[data-import]').addEventListener('click',()=>{try{const x=model.unpack(JSON.parse(jsonBox.value));write(x);render();}catch(e){error.textContent='入力条件を読み込めません。JSONの形式と教材仕様を確認してください。詳細：'+inputErrorText(e.message);}});
write(model.defaults);render();
})();
