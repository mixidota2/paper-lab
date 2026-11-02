"""Independent inventory costs/oracle boundaries and executable renderer contract."""
import importlib.util
import json
import math
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import subprocess
import pytest

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT/'papers/inventory-common-threshold-history'
spec = importlib.util.spec_from_file_location('inventory_ct_run', DIR/'run.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

@pytest.mark.parametrize('signal,lead', list(product((True,False),(0,1))))
def test_finite_oracle_and_optimum(signal,lead):
    tree=m.fixture(signal,lead)
    for t in range(1,4):
        for i in range(4):
            group=tree.group(i,t)
            assert sum(tree.leaves[j].probability for j in group)>0
            for r in range(t,4):
                for u in range(1,4):
                    expected=F(sum(sum(tree.leaves[j].demand[:r])<u for j in group),len(group))
                    assert tree.probability_below(i,t,r,u)==expected
                    for j in group:
                        assert tree.charges(i,t,u)==tree.charges(j,t,u) if t<=3-lead else True
    # Independent per-unit optimal-stopping recursion, not inventory DP.
    def stop_cost(t, group, u):
        if t>3-lead:return F(0)
        a,b=tree.charges(group[0],t,u)
        continuation=F(0)
        if t<3-lead:
            next_groups={tree.group(i,t+1) for i in group}
            for g in next_groups:
                continuation+=F(len(g),len(group))*stop_cost(t+1,g,u)
        return min(a,b+continuation)
    unavoidable=sum(tree.leaves[i].probability*sum(tree.p[t-1]*sum(tree.leaves[i].demand[:t])
                     for t in range(1,lead+1)) for i in range(4))
    independent=unavoidable+sum(stop_cost(1,(0,1,2,3),u) for u in range(1,4))
    assert m.optimum(tree)==independent
    e=m.expected(tree)
    assert math.isclose(e['cost'],e['decomposition'],abs_tol=1e-12)
    assert float(independent)<=e['cost']<=math.e/(math.e-1)*float(independent)+1e-12
    assert math.isclose(sum(x['mass'] for x in e['intervals']),1)

@pytest.mark.parametrize('signal,lead,rho', list(product((True,False),(0,1),(F(1,4),F(1,2),F(3,4)))))
def test_policy_prefix_charges_and_nonanticipation(signal,lead,rho):
    tree=m.fixture(signal,lead)
    weighted_cost=weighted_charge=F(0)
    for i in range(4):
        result=m.simulate(tree,i,rho)
        assert all(r['order']==0 for r in result['ledger'] if r['t']>tree.T-tree.L)
        stops=list(result['stop'].values())
        assert stops==sorted(stops)
        clock={}
        for row in result['rows']:
            u=row['u']
            assert row['z']>=clock.get(u,0)
            clock[u]=row['z']
            assert row['charge']==({'order':row['alpha'],'wait':row['beta'],'ordered':0}[row['action']])
            for j in tree.group(i,row['t']):
                other=m.simulate(tree,j,rho)
                assert other['ledger'][row['t']-1]['order']==result['ledger'][row['t']-1]['order']
        # Direct physical inventory check, independent of stored cumulative arrivals.
        inventory=0
        for t,row in enumerate(result['ledger']):
            incoming=result['ledger'][t-lead]['order'] if t>=lead else 0
            inventory+=incoming-row['demand']
            assert row['inventory']==inventory
            assert row['cost']==2*max(inventory,0)+max(-inventory,0)
        weighted_cost+=result['cost']/4
        weighted_charge+=result['conditional_charge']/4
    assert weighted_cost==weighted_charge


def test_history_retained_and_recomputation_changes_action():
    t=m.fixture(False,0)
    old=m.simulate(t,0,F(3,4))
    wrong=m.simulate(t,0,F(3,4),'recomputed')
    row=next(r for r in old['rows'] if r['t']==2 and r['u']==1)
    alt=next(r for r in wrong['rows'] if r['t']==2 and r['u']==1)
    assert row['z']==F(5,6) and alt['z']==F(1,2)
    assert row['action']=='order' and alt['action']=='wait'
    assert t.charges(0,1,1)==(F(3,2),F(1,2))
    assert t.charges(0,1,1,2)==(F(3),F(0))


def test_zero_denominators_equal_threshold_and_never_order():
    assert m.ratio(0,0)==0 and math.isinf(m.ratio(1,0))
    t=m.Tree((m.Leaf(F(1,2),(0,),('x',)),m.Leaf(F(1,2),(1,),('x',))),holding=(1,),backlog=(1,))
    assert m.simulate(t,0,1)['stop']=={1:1}  # equality, alpha only
    assert m.simulate(t,0,1)['conditional_charge']==F(1,2)
    zero=m.Tree((m.Leaf(F(1),(1,),('x',)),),holding=(0,),backlog=(0,))
    assert m.simulate(zero,0,F(1,2))['stop']=={1:2}
    positive=m.Tree((m.Leaf(F(1),(1,),('x',)),),holding=(0,),backlog=(1,))
    assert m.simulate(positive,0,F(1,2))['stop']=={1:1}
    empty=m.Tree((m.Leaf(F(1),(0,),('x',)),),holding=(1,),backlog=(1,))
    assert m.optimum(empty)==0 and m.expected(empty)['cost']==0


def test_opt_is_adapted_not_clairvoyant():
    # One period: optimal cost .5; hindsight can order exactly demand at zero cost.
    t=m.Tree((m.Leaf(F(1,2),(0,),('x',)),m.Leaf(F(1,2),(1,),('x',))),holding=(1,),backlog=(1,))
    assert m.optimum(t)==F(1,2)
    # If information truly arrives before the order, optimal cost becomes zero.
    informed=m.Tree((m.Leaf(F(1,2),(0,),('none',)),m.Leaf(F(1,2),(1,),('one',))),holding=(1,),backlog=(1,))
    assert m.optimum(informed)==0


def test_small_policy_enumeration_independent():
    leaves=tuple(m.Leaf(F(1,4),d,('x','x')) for d in product((0,1),repeat=2))
    t=m.Tree(leaves,holding=(2,2),backlog=(1,1))
    costs=[]
    # Each tuple gives initial order, then order after D1=0 / D1=1.
    for q0,q10,q11 in product(range(3),repeat=3):
        if max(q0+q10,q0+q11)>2:continue
        total=0
        for d1,d2 in product((0,1),repeat=2):
            i1=q0-d1;i2=i1+(q10 if d1==0 else q11)-d2
            total+=sum(2*max(i,0)+max(-i,0) for i in (i1,i2))
        costs.append(F(total,4))
    assert m.optimum(t)==min(costs)

@pytest.mark.parametrize('epsilon',(.001,.01,.1,.25,.49))
def test_tight_from_finite_model(epsilon):
    e=F(str(epsilon))
    tree=m.Tree((m.Leaf(1-e,(0,),('x',)),m.Leaf(e,(1,),('x',))),holding=(1,),backlog=(1,))
    result=m.tight(e)
    assert m.optimum(tree)==e
    assert math.isclose(m.expected(tree)['cost'],result['cost'],abs_tol=1e-13)
    assert result['ratio']<math.e/(math.e-1)
    if e==F(1,4):
        assert math.isclose(result['cost'],0.36511860817409525,abs_tol=1e-15)
        assert math.isclose(result['ratio'],1.460474432696381,abs_tol=1e-15)


def test_invalid_inputs_and_bounds():
    for e in (0,.5,1,-1,float('nan'),float('inf')):
        with pytest.raises(ValueError):m.tight(e)
    for leaf in (-1,4,True):
        with pytest.raises(ValueError):m.simulate(m.fixture(),leaf,F(1,2))
    for rho in (0,-1,2):
        with pytest.raises(ValueError):m.simulate(m.fixture(),0,rho)
    for lead in (-1,3,True):
        with pytest.raises(ValueError):m.fixture(lead=lead)
    for demand in ((-1,), (5,), (1.5,)):
        with pytest.raises(ValueError):m.Tree((m.Leaf(F(1),demand,('x',)),),holding=(1,),backlog=(1,))
    with pytest.raises(ValueError):m.Tree((m.Leaf(F(1,2),(0,),('x',)),),holding=(1,),backlog=(1,))
    with pytest.raises(ValueError):m.clocks(m.fixture(),0,'unknown')


def test_results_reproducible_and_all_cases_derived():
    saved=json.loads((DIR/'results.json').read_text())
    assert saved==m.generate()
    assert sum(len(s['cases']) for s in saved['scenarios'])==96
    assert saved['budget']['monte_carlo'] is False


def test_javascript_all_states_reset_and_nojs(tmp_path):
    script=r'''
const assert=require('node:assert/strict'),fs=require('fs');
const ui=require(process.argv[2]),data=JSON.parse(fs.readFileSync(process.argv[3]));
let checked=0;
for(const s of data.scenarios)for(const c of s.cases)for(let epsilon=0;epsilon<5;epsilon++){
 const v=ui.view(data,{scenario:s.id,rho:c.rho,leaf:String(c.leaf),mode:c.mode,epsilon:String(epsilon)});
 assert.equal((v.rows.match(/<tr>/g)||[]).length,c.rows.length);
 for(const r of c.rows){assert(v.rows.includes(`<td>${r.t} / ${r.u}</td><td>${r.alpha}</td><td>${r.beta}</td><td>${r.increment}</td><td>${r.z}</td>`));}
 assert(v.summary.includes(`実費用 ${c.cost} ／ 条件付き費用分解 ${c.conditional_charge}`));
 assert(v.tight.includes(data.tight[epsilon].cost.toFixed(6)));checked++;
}
assert.equal(checked,480);
assert.throws(()=>ui.view(data,{...ui.defaults(),scenario:'invalid'}));
const nodes={};for(const k of ['scenario','rho','leaf','mode','epsilon','rows','ledger','expect','output','tight','reset','data'])
 nodes['ict-'+k]={value:ui.defaults()[k],textContent:k==='data'?JSON.stringify(data):'',innerHTML:'',events:{},addEventListener(name,fn){this.events[name]=fn;}};
ui.mount({getElementById:id=>nodes[id]});
const initial=nodes['ict-output'].textContent;
nodes['ict-rho'].value='3/4';nodes['ict-scenario'].value='0-0';nodes['ict-rho'].events.change();
assert.notEqual(nodes['ict-output'].textContent,initial);
nodes['ict-reset'].events.click();assert.equal(nodes['ict-output'].textContent,initial);
console.log(JSON.stringify(ui.view(data,ui.defaults())));
'''
    runner=tmp_path/'check.cjs';runner.write_text(script)
    result=subprocess.run(['node',str(runner),str(DIR/'interactive.js'),str(DIR/'results.json')],capture_output=True,text=True,check=True)
    v=json.loads(result.stdout)
    from paper_lab.inventory_ct import widget
    html=widget(json.loads((DIR/'results.json').read_text()),DIR)
    for key in ('summary','expect','tight','ledger'):assert v[key] in html
    # Floating CSS percentage formatting may differ; values/row structure agree.
    import re
    strip=lambda x:re.sub(r'style="width:[^"]+"','',x)
    assert strip(v['rows']) in strip(html)
    assert '__DATA__' not in html and '<noscript>' in html
    assert 'min-width:740px' in html and 'white-space:nowrap' in html and 'overflow-x:auto' in html


def test_cdf_fixed_precision_independent_of_ambient_decimal_context():
    from decimal import localcontext, ROUND_UP
    points = (F(1,1000), F(1,3), F(49,51))
    expected = [m.cdf(x) for x in points]
    with localcontext() as ctx:
        ctx.prec = 7
        ctx.rounding = ROUND_UP
        assert [m.cdf(x) for x in points] == expected
    for x, actual in zip(points, expected):
        assert math.isclose(actual, math.expm1(float(x))/math.expm1(1), rel_tol=1e-15)
    assert m.cdf(0) == 0 and m.cdf(1) == 1
