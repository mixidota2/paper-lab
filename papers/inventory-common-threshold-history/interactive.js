/* Pythonで計算した保存値を表示する。ブラウザーでは再計算や通信をしない。 */
(function () {
  'use strict';
  const number = x => x === '∞' ? Infinity : typeof x === 'string' && x.includes('/') ? x.split('/').map(Number).reduce((a,b)=>a/b) : Number(x);
  const fixed = x => number(x).toFixed(6);
  const names = {order:'発注', wait:'待つ', ordered:'発注済'};
  function view(data, state) {
    const s = data.scenarios.find(s=>s.id===state.scenario);
    if (!s) throw Error('指定した信号と納期の組み合わせが見つかりません');
    const c = s.cases.find(c=>c.mode===state.mode && c.rho===state.rho && c.leaf===Number(state.leaf));
    const t = data.tight[Number(state.epsilon)];
    if (!c || !t) throw Error('指定した実験条件が見つかりません');
    const rows = c.rows.map(r=>`<tr><td>${r.t} / ${r.u}</td><td>${r.alpha}</td><td>${r.beta}</td><td>${r.increment}</td><td>${r.z}</td><td><span class="clock" style="width:${Math.min(1,number(r.z))*100}%" aria-hidden="true"></span></td><td>${names[r.action]}</td><td>${r.charge}</td></tr>`).join('');
    const ledger = c.ledger.map(r=>`<tr>${['t','demand','order','arrived','inventory','cost'].map(k=>`<td>${r[k]}</td>`).join('')}</tr>`).join('');
    const chosen = state.mode==='historical' ? s.expected.cost : s.comparison.cost;
    const expect = `<p>同じ情報を使った最小の平均費用（OPT）<br><b>${fixed(s.opt)}</b></p><p>閾値と需要を変えたときの論文方式の平均費用（CT）<br><b>${fixed(s.expected.cost)}</b></p><p>閾値と需要を変えたときの、選択中の方式の平均費用<br><b>${fixed(chosen)}</b></p>`;
    const summary = `選んだ閾値ρ=${c.rho}・需要経路${c.leaf+1}：経路から計算した費用 ${c.cost} ／ 当時の情報で見積もった費用の合計 ${c.conditional_charge}。論文は需要経路1本ごとの費用倍率を保証していません。`;
    const tight = `発注する確率 ${fixed(t.order_probability)} ／ 最小の平均費用（OPT） ${fixed(t.opt)} ／ 論文方式の平均費用（CT） ${fixed(t.cost)} ／ CTをOPTで割った倍率 ${fixed(t.ratio)}`;
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
