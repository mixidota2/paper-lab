(() => {
'use strict';
const data=JSON.parse(document.getElementById('arc-data').textContent);
const scenario=document.getElementById('arc-scenario'), repair=document.getElementById('arc-repair');
let stage=0;
const status=x=>x?'PASS':'FAIL';
const val=x=>JSON.stringify(x);
const suite=(label,s)=>`<section class="arc-suite"><h4>${label} <b data-gate="${label}">${status(s.passed)}</b></h4>${s.checks.map(c=>`<p class="arc-check"><strong>${c.name}：${status(c.passed)}</strong><br><code>${c.op}(${val(c.values)}, 閾値 ${c.threshold}, 上限 ${c.limit})</code><br>${label==='自己テスト'?'自己テストの期待値':'仕様の期待値'} <code>${val(c.expected)}</code> ／ 実際 <code>${val(c.actual)}</code></p>`).join('')}</section>`;
const stateText=s=>`絞込み=${s.filter?'実装済み':'未実装'} ／ 制限=${s.cap?'実装済み':'未実装'} ／ 表示=${s.render?'実装済み':'未実装'} ／ 境界=${s.inclusive?'含む':'除く'} ／ 合計=${s.signed?'符号を保持':'絶対値へ変更'}`;
function render(){
 const c=data.synthetic.find(c=>c.scenario===scenario.value&&c.repair===repair.checked),s=c.stages[stage];
 const history=c.stages.slice(0,stage+1).map(s=>`<li>第${s.stage+1}段階：自己テスト ${status(s.self_test.passed)} ／ stage gate ${status(s.gate)}</li>`).join('');
 document.getElementById('arc-output').innerHTML=`<h3>第${stage+1}段階：${['境界を含む絞込み','絞込み結果の件数制限','制限結果の文字列表示'][stage]}</h3><p data-stage="${stage}">前の状態：${stateText(s.before)}<br>変更後：${stateText(s.after)}</p><p>仮想修正：${repair.checked?'第3段階で境界と合計を直す（教材独自）':'なし'}</p><ol>${history}</ol><p>失敗してもこの状態を次へ渡す。ここに見える判定は読者用で、実装の更新処理には渡していない。</p><div class="arc-grid">${suite('自己テスト',s.self_test)}${suite('stage F2P',s.f2p)}${suite('stage P2P',s.p2p)}</div><p class="arc-verdict">stage gate：<b data-stage-gate>${status(s.gate)}</b></p>${stage===2?`<div class="arc-grid">${suite('chain F2P',c.chain.f2p)}${suite('chain P2P',c.chain.p2p)}</div><p class="arc-verdict">最終合格（両suiteのAND）：<b data-chain-gate>${status(c.chain.gate)}</b></p>`:'<p data-chain-pending>chain gate：未実行。第3段階の最終コードを待つ。</p>'}`;
 document.getElementById('arc-prev').disabled=stage===0;
 document.getElementById('arc-next').disabled=stage===2;
}
scenario.addEventListener('change',()=>{stage=0;render();});
repair.addEventListener('change',()=>{stage=0;render();});
document.getElementById('arc-next').addEventListener('click',()=>{stage=Math.min(2,stage+1);render();});
document.getElementById('arc-prev').addEventListener('click',()=>{stage=Math.max(0,stage-1);render();});
document.getElementById('arc-reset').addEventListener('click',()=>{scenario.value='inherited';repair.checked=false;stage=0;render();});
render();
})();
