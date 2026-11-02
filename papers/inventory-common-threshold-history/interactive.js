/* Rendering only: values are produced by independently tested Python, no network. */
(function () {
  'use strict';
  const number = x => x === '∞' ? Infinity : typeof x === 'string' && x.includes('/') ? x.split('/').map(Number).reduce((a,b)=>a/b) : Number(x);
  const fixed = x => number(x).toFixed(6);
  const names = {order:'発注', wait:'待つ', ordered:'発注済'};
  function view(data, state) {
    const s = data.scenarios.find(s=>s.id===state.scenario);
    if (!s) throw Error('unknown scenario');
    const c = s.cases.find(c=>c.mode===state.mode && c.rho===state.rho && c.leaf===Number(state.leaf));
    const t = data.tight[Number(state.epsilon)];
    if (!c || !t) throw Error('unknown condition');
    const rows = c.rows.map(r=>`<tr><td>${r.t} / ${r.u}</td><td>${r.alpha}</td><td>${r.beta}</td><td>${r.increment}</td><td>${r.z}</td><td><span class="clock" style="width:${Math.min(1,number(r.z))*100}%" aria-hidden="true"></span></td><td>${names[r.action]}</td><td>${r.charge}</td></tr>`).join('');
    const ledger = c.ledger.map(r=>`<tr>${['t','demand','order','arrived','inventory','cost'].map(k=>`<td>${r[k]}</td>`).join('')}</tr>`).join('');
    const chosen = state.mode==='historical' ? s.expected.cost : s.comparison.cost;
    const expect = `<p>同じ情報で判断するOPT<br><b>${fixed(s.opt)}</b></p><p>ρと需要を平均したCT費用<br><b>${fixed(s.expected.cost)}</b></p><p>選択した方式の平均費用<br><b>${fixed(chosen)}</b></p>`;
    const summary = `固定ρ=${c.rho}・経路${c.leaf+1}：実費用 ${c.cost} ／ 条件付き費用分解 ${c.conditional_charge}。この経路だけに近似保証はありません。`;
    const tight = `発注確率 ${fixed(t.order_probability)} ／ OPT ${fixed(t.opt)} ／ CT期待費用 ${fixed(t.cost)} ／ 比 ${fixed(t.ratio)}`;
    return {rows,ledger,expect,summary,tight};
  }
  const defaults = ()=>({scenario:'1-0',rho:'1/4',leaf:'0',mode:'historical',epsilon:'3'});
  function mount(doc) {
    const data = JSON.parse(doc.getElementById('ict-data').textContent);
    const keys=['scenario','rho','leaf','mode','epsilon'];
    const state=()=>Object.fromEntries(keys.map(k=>[k,doc.getElementById('ict-'+k).value]));
    function render() {
      const v=view(data,state());
      ['rows','ledger','expect'].forEach(k=>doc.getElementById('ict-'+k).innerHTML=v[k]);
      doc.getElementById('ict-output').textContent=v.summary;
      doc.getElementById('ict-tight').textContent=v.tight;
    }
    keys.forEach(k=>doc.getElementById('ict-'+k).addEventListener('change',render));
    doc.getElementById('ict-reset').addEventListener('click',()=>{
      const initial=defaults(); keys.forEach(k=>doc.getElementById('ict-'+k).value=initial[k]); render();
    });
    render();
  }
  if (typeof module !== 'undefined' && module.exports) module.exports={view,defaults,mount};
  else mount(document);
})();
