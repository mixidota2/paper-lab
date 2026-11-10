(function(){'use strict';const get=k=>document.getElementById('grain-'+k),ids=['y2','a2','group','window','q','y','r'],M=GrainModel,defaults=M.defaults;let current=null;
const fmt=x=>x===null?'未定義（分母0）':Number(x.toPrecision(8)).toString();
function number(k){if(get(k).value.trim()==='')throw Error('空欄を埋めてください。');return Number(get(k).value);}
function render(){try{const groups=get('group').value==='together'?[0,0]:[0,1],y2=number('y2'),a2=number('a2'),w=number('window'),q=number('q'),y=number('y'),r=number('r');const A=M.metrics([100,y2],[90,a2],[1,1],[1,1],groups),B=M.metrics([100,y2],[80,0],[1,1],[1,1],groups),WA=M.windows([1,w],[0,w]),WB=M.windows([1,w],[1,Math.max(0,w-10)]),L=M.loss(q,y,r);const text=`自作合成例（原著モデルの再現ではありません）\n旧式 A=${fmt(A.old)}、B=${fmt(B.old)}\n訂正式 A=${fmt(A.corrected)}、B=${fmt(B.corrected)}\n窓平均 A=${fmt(WA.mean)}、B=${fmt(WB.mean)}\npool A=${fmt(WA.pooled)}、B=${fmt(WB.pooled)}\n単期発注損失=${fmt(L)}（不足単価${fmt(r/(1-r))}）`;get('out').textContent=text;const max=Math.max(A.corrected||0,B.corrected||0,1e-12);get('bars').innerHTML=[['A',A.corrected],['B',B.corrected]].map(([name,v])=>`<p>${name} 訂正式 ${fmt(v)}</p><div class="bar" style="width:${v===null?0:100*v/max}%"></div>`).join('');current=M.pack({y2,a2,group:get('group').value,window:w,q,y,r});get('download').disabled=false;get('error').textContent='';return true;}catch(e){current=null;get('download').disabled=true;get('error').textContent=e.message;get('out').textContent='入力が不正なため計算結果を表示しません。';get('bars').innerHTML='';return false;}}
function clearTransferStatus(){get('transfer-status').textContent='';}
for(const k of ids)get(k).addEventListener('input',()=>{clearTransferStatus();render();});
get('reset').addEventListener('click',()=>{for(const k of ids)get(k).value=String(defaults[k]);get('json').value='';clearTransferStatus();render();});
get('download').addEventListener('click',()=>{
  if(!current)return;
  clearTransferStatus();
  const text=JSON.stringify(current,null,2);get('json').value=text;
  let url;
  try{
    url=URL.createObjectURL(new Blob([text],{type:'application/json'}));
    const a=document.createElement('a');a.href=url;a.download='retail-grain-scenario.json';a.click();
    get('transfer-status').textContent='保存用JSONを用意しました。ダウンロードされない場合は下の欄から保存してください。';
  }catch(e){get('transfer-status').textContent='ダウンロードを開始できませんでした。下のJSON欄の内容を保存してください。';}
  finally{if(url)setTimeout(()=>URL.revokeObjectURL(url),1000);}
});
get('import').addEventListener('click',()=>{
  clearTransferStatus();
  try{
    if(get('json').value.length>65536)throw Error('JSONは64 Ki文字以内にしてください。');
    const inputs=M.unpack(JSON.parse(get('json').value));
    for(const k of ids)get(k).value=String(inputs[k]);
    if(render())get('transfer-status').textContent='保存した条件を読み込み、結果を再計算しました。JSON内の結果値は使用していません。';
  }catch(e){get('transfer-status').textContent='条件を読み込めません。現在の入力は変更していません。'+e.message;}
});
get('json').addEventListener('input',clearTransferStatus);
if(render())for(const k of [...ids,'reset','download','import','json'])get(k).disabled=false;
})();
