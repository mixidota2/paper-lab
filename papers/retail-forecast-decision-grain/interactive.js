(function(){'use strict';const get=k=>document.getElementById('grain-'+k),ids=['y2','a2','group','window','q','y','r'],M=GrainModel,defaults=M.defaults;let current=null,baseline=null;
const fmt=x=>x===null?'未定義（分母0）':Number(x.toPrecision(8)).toString();
const inputLabels={y2:'第2商品の売上',a2:'Aの第2予測',group:'集計する単位',window:'第2窓売上',q:'発注量 q',y:'観測売上 y',r:'臨界比率 r'};
const rows=[['旧式 A','metrics','A','old'],['旧式 B','metrics','B','old'],['訂正式 A','metrics','A','corrected'],['訂正式 B','metrics','B','corrected'],['窓平均 A','windows','A','mean'],['窓平均 B','windows','B','mean'],['pool A','windows','A','pooled'],['pool B','windows','B','pooled'],['単期発注損失','order','loss'],['不足単価','order','shortage_cost']];
function renderComparison(){
  get('pin').disabled=!current;get('clear-baseline').disabled=!baseline;get('comparison-download').disabled=!baseline||!current;
  if(!baseline){get('comparison').innerHTML='';get('comparison-status').textContent='基準はまだありません。比べたい条件で「現在の条件を基準にする」を押してください。';return;}
  if(!current){get('comparison').innerHTML='';get('comparison-status').textContent='基準は保持しています。現在の入力を直すと比較を再開できます。';return;}
  const c=M.compare(baseline,current.inputs),read=(obj,path)=>path.reduce((value,key)=>value[key],obj);
  const values=x=>Object.keys(inputLabels).map(k=>`${inputLabels[k]}=${k==='group'?(x[k]==='together'?'同じカテゴリへ合計':'別カテゴリ'):fmt(x[k])}`).join('、');
  get('comparison-status').textContent='基準：'+values(c.baseline.inputs)+'。変更した項目：'+(c.changed_inputs.length?c.changed_inputs.map(k=>inputLabels[k]).join('、'):'なし')+'。';
  get('comparison').innerHTML='<table><caption>基準と現在の合成例。差は現在−基準。</caption><thead><tr><th scope="col">指標</th><th scope="col">基準</th><th scope="col">現在</th><th scope="col">差</th></tr></thead><tbody>'+rows.map(([label,...path])=>{
    const a=read(c.baseline.output,path),b=read(c.current.output,path),d=read(c.delta,path);
    return `<tr><th scope="row">${label}</th><td>${fmt(a)}</td><td>${fmt(b)}</td><td>${d===null?'比較不可（分母0）':fmt(d)}</td></tr>`;
  }).join('')+'</tbody></table>';
}
function number(k){if(get(k).value.trim()==='')throw Error('空欄を埋めてください。');return Number(get(k).value);}
function render(){try{const groups=get('group').value==='together'?[0,0]:[0,1],y2=number('y2'),a2=number('a2'),w=number('window'),q=number('q'),y=number('y'),r=number('r');const A=M.metrics([100,y2],[90,a2],[1,1],[1,1],groups),B=M.metrics([100,y2],[80,0],[1,1],[1,1],groups),WA=M.windows([1,w],[0,w]),WB=M.windows([1,w],[1,Math.max(0,w-10)]),L=M.loss(q,y,r);const text=`自作合成例（原著モデルの再現ではありません）\n旧式 A=${fmt(A.old)}、B=${fmt(B.old)}\n訂正式 A=${fmt(A.corrected)}、B=${fmt(B.corrected)}\n窓平均 A=${fmt(WA.mean)}、B=${fmt(WB.mean)}\npool A=${fmt(WA.pooled)}、B=${fmt(WB.pooled)}\n単期発注損失=${fmt(L)}（不足単価${fmt(r/(1-r))}）`;get('out').textContent=text;const max=Math.max(A.corrected||0,B.corrected||0,1e-12);get('bars').innerHTML=[['A',A.corrected],['B',B.corrected]].map(([name,v])=>`<p>${name} 訂正式 ${fmt(v)}</p><div class="bar" style="width:${v===null?0:100*v/max}%"></div>`).join('');current=M.pack({y2,a2,group:get('group').value,window:w,q,y,r});get('download').disabled=false;get('error').textContent='';renderComparison();return true;}catch(e){current=null;get('download').disabled=true;get('error').textContent=e.message;get('out').textContent='入力が不正なため計算結果を表示しません。';get('bars').innerHTML='';renderComparison();return false;}}
function clearTransferStatus(){get('transfer-status').textContent='';}
for(const k of ids)get(k).addEventListener('input',()=>{clearTransferStatus();render();});
get('reset').addEventListener('click',()=>{for(const k of ids)get(k).value=String(defaults[k]);get('json').value='';baseline=null;clearTransferStatus();render();});
function download(data,filename){
  clearTransferStatus();
  const text=JSON.stringify(data,null,2);get('json').value=text;
  let url;
  try{
    url=URL.createObjectURL(new Blob([text],{type:'application/json'}));
    const a=document.createElement('a');a.href=url;a.download=filename;a.click();
    get('transfer-status').textContent='保存用JSONを用意しました。ダウンロードされない場合は下の欄から保存してください。';
  }catch(e){get('transfer-status').textContent='ダウンロードを開始できませんでした。下のJSON欄の内容を保存してください。';}
  finally{if(url)setTimeout(()=>URL.revokeObjectURL(url),1000);}
}
get('download').addEventListener('click',()=>{if(current)download(current,'retail-grain-scenario.json');});
get('comparison-download').addEventListener('click',()=>{if(current&&baseline)download(M.packComparison(baseline,current.inputs),'retail-grain-comparison.json');});
get('pin').addEventListener('click',()=>{if(current){baseline=M.unpack(current);clearTransferStatus();renderComparison();}});
get('clear-baseline').addEventListener('click',()=>{baseline=null;clearTransferStatus();renderComparison();});
get('import').addEventListener('click',()=>{
  clearTransferStatus();
  try{
    if(get('json').value.length>65536)throw Error('JSONは64 Ki文字以内にしてください。');
    const data=JSON.parse(get('json').value),isComparison=data&&data.kind==='retail-grain-comparison';
    const restored=isComparison?M.unpackComparison(data):{current:M.unpack(data)},inputs=restored.current;
    for(const k of ids)get(k).value=String(inputs[k]);
    if(isComparison)baseline=restored.baseline;
    if(render())get('transfer-status').textContent=(isComparison?'基準と現在の条件を読み込み、結果と差を再計算しました。':'保存した条件を読み込み、結果を再計算しました。固定した基準は保持します。')+'JSON内の結果値は使用していません。';
  }catch(e){get('transfer-status').textContent='条件を読み込めません。現在の入力は変更していません。'+e.message;}
});
get('json').addEventListener('input',clearTransferStatus);
if(render())for(const k of [...ids,'reset','download','import','json'])get(k).disabled=false;
})();
