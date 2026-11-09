"""Static fallback and actual inline JS, exercised in a DOM fixture (not a browser)."""
import json
import math
from pathlib import Path
import re
import subprocess

from paper_lab.exaone05 import widget

ROOT = Path(__file__).resolve().parents[1]


def rendered():
    return widget(json.loads((ROOT / 'papers/exaone-demand-routed-tsfm/results.json').read_text()))


def fixture():
    html = rendered()
    return {
        'code': re.search(r'<script>(.*?)</script>', html, re.S)[1],
        'weights': re.search(r'data-weights aria-live="polite">(.*?)</div><p>', html, re.S)[1],
        'series': re.search(r'<svg data-series[^>]*>(.*?)</svg>', html, re.S)[1],
        'lost': re.search(r'data-lost aria-live="polite">(.*?)</p>', html)[1],
        'cx': re.search(r'data-point cx="([^"]+)', html)[1],
        'cy': re.search(r'data-point[^>]*cy="([^"]+)', html)[1],
    }


def expected_stock(stock, promo):
    available, arrival = stock, {}
    latent, observed = [], []
    for t in range(30):
        if t in arrival:
            available = stock
        multiplier = 1
        if promo:
            multiplier = 1.4 if 9 <= t <= 11 else 2.4 if 12 <= t <= 15 else .65 if 16 <= t <= 19 else 1
        demand = int(math.floor((7 + 3 * math.sin(1.3 * t)) * multiplier + .5))
        sales = min(available, demand)
        available -= sales
        latent.append(demand); observed.append(sales)
        if available < 8 and not any(k > t for k in arrival):
            arrival[t + 3] = True
    return latent, observed, sum(latent) - sum(observed)


def test_initial_html_has_results_and_disabled_controls():
    html = rendered()
    for key in ('a', 'c', 'stock', 'promo'):
        assert re.search(r'<input data-' + key + r'\b[^>]*\bdisabled', html)
    f = fixture()
    assert f['weights'].count('25.0% → 25.0%') == 4
    assert f['series'].count('stroke-width="3"') == 2
    assert f['lost'] == '潜在需要 246 個のうち、観測されなかった需要は 61 個。'
    assert '<noscript>' in html and '初期条件の結果のみ' in html
    assert '公式生成器や欠品復元モデルの再現ではない' in html
    assert '学習済みの振り分け器（router）のqを表示するものではない' in html


def test_actual_js_initial_failure_and_all_boundary_combinations(tmp_path):
    f = fixture()
    f['cases'] = []
    for a in (1, 1.31, 1.32, 1.33, 12):
        for c in (.01, .48, .49, .50, 4):
            aa = 1 / (1 + math.exp(-math.log(a / 1.32) / .35))
            cc = 1 / (1 + math.exp(-math.log(c / .49) / .6))
            p = [(1-aa)*(1-cc), aa*(1-cc), (1-aa)*cc, aa*cc]
            den = sum(x*x for x in p)
            for stock in (10, 15, 40, 95, 100):
                for promo in (False, True):
                    latent, observed, lost = expected_stock(stock, promo)
                    f['cases'].append(dict(a=a, c=c, stock=stock, promo=promo,
                        percentages=[v for x in p for v in (100*x, 100*x*x/den)],
                        latent=latent, observed=observed, lost=lost))
    runner = r"""
const assert=require('node:assert/strict'),vm=require('node:vm');
const f=FIXTURE;
function run(failKind='', failAt=0) {
 const counts={query:0,event:0,write:0};
 function hit(kind){if(++counts[kind]===failAt && kind===failKind)throw Error('injected '+kind);}
 function node(value='',html='',text=''){
  let val=value,inner=html,txt=text,disabled=true,hidden=false;
  return {events:{},attrs:{},
   get value(){return val},set value(v){hit('write');val=String(v)},
   get innerHTML(){return inner},set innerHTML(v){hit('write');inner=v},
   get textContent(){return txt},set textContent(v){hit('write');txt=v},
   get disabled(){return disabled},set disabled(v){hit('write');disabled=v},
   get hidden(){return hidden},set hidden(v){hit('write');hidden=v},
   addEventListener(k,fn){hit('event');this.events[k]=fn},
   setAttribute(k,v){hit('write');this.attrs[k]=String(v)}
  };
 }
 const nodes={a:node('1.32'),c:node('.49'),stock:node('40'),promo:node(),
  adi:node('1.32'),cv:node('0.49'),'stock-label':node('40'),
  weights:node('',f.weights),series:node('',f.series),lost:node('','',f.lost),
  point:node(),'ex-status':node()};
 nodes.promo.checked=true;nodes.point.attrs={cx:f.cx,cy:f.cy};
 const root={querySelector(q){hit('query');return nodes[q.slice(6,-1)]}};
 const ctx={document:{currentScript:{closest:()=>root}}};
 try{vm.runInNewContext(f.code,ctx)}catch(e){assert.match(e.message,/injected/)}
 return {nodes,counts};
}
function assertStatic(n){
 assert.equal(n.weights.innerHTML,f.weights);assert.equal(n.series.innerHTML,f.series);
 assert.equal(n.lost.textContent,f.lost);
 assert.equal(n.a.value,'1.32');assert.equal(n.c.value,'.49');assert.equal(n.stock.value,'40');assert.equal(n.promo.checked,true);
 assert.equal(n.adi.value,'1.32');assert.equal(n.cv.value,'0.49');assert.equal(n['stock-label'].value,'40');
 assert.ok(Math.abs(+n.point.attrs.cx-(+f.cx))<1e-12);
 assert.ok(Math.abs(+n.point.attrs.cy-(+f.cy))<1e-12);
}
const normal=run(),n=normal.nodes,initialCounts={...normal.counts};assertStatic(n);
for(const k of ['a','c','stock','promo'])assert.equal(n[k].disabled,false);
for(const kind of ['query','event','write']){
 for(let i=1;i<=initialCounts[kind];i++){
  const failed=run(kind,i).nodes;assertStatic(failed);
  for(const k of ['a','c','stock','promo'])assert.equal(failed[k].disabled,true,kind+':'+i+':'+k);
  // Registered callbacks cannot act when initialization was incomplete.
  for(const k of ['a','c','stock','promo'])for(const callback of Object.values(failed[k].events))callback();
  assertStatic(failed);
 }
}
function points(svg,color){
 const d=svg.match(new RegExp('<path d="([^"]+)" fill="none" stroke="'+color+'"'))[1];
 return [...d.matchAll(/[ML]([0-9]+),(-?[0-9]+)/g)].map((m,i)=>{
  assert.equal(+m[1],42+i*19);return (195-(+m[2]))/6;
 });
}
for(const c of f.cases){
 n.a.value=c.a;n.c.value=c.c;n.stock.value=c.stock;n.promo.checked=c.promo;
 n.a.events.input();n.c.events.input();n.stock.events.input();n.promo.events.change();
 const percentages=[...n.weights.innerHTML.matchAll(/([0-9.]+)%/g)].map(m=>+m[1]);
 assert.equal(percentages.length,8);
 percentages.forEach((v,i)=>assert.ok(Math.abs(v-c.percentages[i])<=.0500000001));
 assert.deepEqual(points(n.series.innerHTML,'#316d99'),c.latent);
 assert.deepEqual(points(n.series.innerHTML,'#c27035'),c.observed);
 assert.equal(n.lost.textContent,'潜在需要 '+c.latent.reduce((s,v)=>s+v,0)+' 個のうち、観測されなかった需要は '+c.lost+' 個。');
}
console.log(JSON.stringify({cases:f.cases.length,initializationFailurePositions:initialCounts,staticDynamicEqual:true}));
"""
    path = tmp_path / 'exaone.cjs'
    path.write_text(runner.replace('FIXTURE', json.dumps(f, ensure_ascii=False)))
    subprocess.run(['node', str(path)], check=True)
