/* Evidence filtering only. No requests, scoring, or effect-size ranking. */
(function () {
  'use strict';
  const allowed={period:['all','current','legacy'],domain:['all','retail','maintenance'],evaluation:['all','backtest','model','observational']};
  const defaults=()=>({period:'all',domain:'all',evaluation:'all'});
  function matches(card,state) {
    return Object.keys(allowed).map(key=>{
      if(!allowed[key].includes(state[key])) throw Error('unknown filter');
      return state[key]==='all'||card[key]===state[key];
    }).every(Boolean);
  }
  function mount(root) {
    const keys=Object.keys(allowed),cards=[...root.querySelectorAll('[data-evidence-card]')];
    const controls=Object.fromEntries(keys.map(k=>[k,root.querySelector(`[data-filter="${k}"]`)]));
    function update() {
      const state=Object.fromEntries(keys.map(k=>[k,controls[k].value]));
      let visible=0;
      for(const card of cards){card.hidden=!matches(card.dataset,state);if(!card.hidden)visible++;}
      for(const group of root.querySelectorAll('[data-card-group]'))group.hidden=!cards.some(c=>c.dataset.period===group.dataset.cardGroup&&!c.hidden);
      root.querySelector('[data-filter-count]').textContent=`${visible}件 / 全${cards.length}件`;
      root.querySelector('[data-filter-empty]').hidden=visible!==0;
    }
    keys.forEach(k=>controls[k].addEventListener('change',update));
    root.querySelector('[data-filter-reset]').addEventListener('click',()=>{const initial=defaults();keys.forEach(k=>controls[k].value=initial[k]);update();});
    update();
  }
  if(typeof module!=='undefined'&&module.exports)module.exports={matches,defaults,mount};
  else {const root=document.querySelector('[data-replenishment-survey]');if(root)mount(root);}
})();
