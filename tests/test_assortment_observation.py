"""Saved A/B/C regressions applied to the integrated executable plus UI contracts."""
import importlib.util
import sys
import json
import subprocess
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/'papers/assortment-observation-budget'
spec=importlib.util.spec_from_file_location('assortment_run',DIR/'run.py')
model=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=model
spec.loader.exec_module(model)
from fractions import Fraction as F
from itertools import combinations
import unittest

from assortment_run import component_a


class ComponentATests(unittest.TestCase):
    def test_three_products_exact_cuts(self):
        a = component_a((3, 2, 1))
        self.assertEqual([(c.k,c.exclusion,c.inclusion,c.regret) for c in a.cuts],
                         [(1,F(2),F(0),F(2)), (2,F(1),F(1),F(1)),
                          (3,F(0),F(2),F(2))])
        self.assertEqual((a.chosen_k,a.optimal_cuts,a.assortment,a.g0),
                         (2,(2,),(1,2),F(1)))
        self.assertEqual(a.half_revenue_bound,F(3,2))
        self.assertNotEqual(a.g0,a.half_revenue_bound)

    def test_one_product(self):
        a = component_a(('7/3',))
        self.assertEqual((a.g0,a.chosen_k,a.optimal_cuts),(F(0),1,(1,)))
        self.assertEqual(a.cuts[0].exclusion,F(0))

    def test_all_ties_and_strict_corollary_threshold(self):
        a = component_a((2,1))
        self.assertEqual(tuple(c.regret for c in a.cuts),(F(1),F(1)))
        self.assertEqual((a.optimal_cuts,a.chosen_k,a.corollary_k),((1,2),1,1))

    def test_positive_scaling(self):
        original = component_a((3,2,1))
        for scale in (F(1,7),F(3,2),F(10)):
            with self.subTest(scale=scale):
                a = component_a(tuple(scale*x for x in original.revenues))
                self.assertEqual(a.g0,scale*original.g0)
                self.assertEqual(a.optimal_cuts,original.optimal_cuts)
                self.assertEqual(tuple(c.regret for c in a.cuts),
                                 tuple(scale*c.regret for c in original.cuts))

    def test_invalid_input(self):
        for r in ((),[],None,'321',(0,),(-1,),(3,0),(1,2),(2,2),
                  (True,), (3.0,2,1),('NaN',),('1/0',)):
            with self.subTest(revenues=r):
                with self.assertRaises(ValueError):component_a(r)

    def test_exact_strings_and_input_not_mutated(self):
        r = ['3/7','2/7','1/7']; before = r.copy()
        a = component_a(r)
        self.assertEqual(r,before)
        self.assertEqual(a.g0,F(1,7))
        self.assertIsInstance(a.g0,F)

    def test_subset_characterization_and_corollary_finite_cases(self):
        # Independent enumeration of all subsets using Theorem 3.1 alpha/beta.
        # This finite consistency test is not a proof of the supremum theorem.
        for n in range(1,6):
            for ascending in combinations(range(1,7),n):
                r = tuple(map(F,reversed(ascending)))
                losses = []
                for bits in range(1 << n):
                    included = [i for i in range(n) if bits & (1 << i)]
                    excluded = [i for i in range(n) if not bits & (1 << i)]
                    alpha = max([F(0)]+[r[i] for i in excluded])
                    beta = max([F(0)]+[r[0]-r[i] for i in included])
                    losses.append(max(alpha,beta))
                a = component_a(r)
                self.assertEqual(a.g0,min(losses))
                self.assertIn(a.corollary_k,a.optimal_cuts)
                self.assertLessEqual(a.g0,a.half_revenue_bound)
                self.assertEqual(a.chosen_k,min(a.optimal_cuts))



import unittest
import ast
import inspect
from unittest.mock import patch
from fractions import Fraction as F
from assortment_run import *


class ComponentsTests(unittest.TestCase):
    def test_revenues_and_oracle(self):
        self.assertEqual([revenue(s) for s in PREFIXES], [F(3,2), F(5,3), F(3,2)])
        self.assertEqual(oracle(), F(5,3))

    def test_b_golden(self):
        self.assertEqual(component_b(2), F(1,24))
        self.assertEqual(component_b(8), F(37,1536))
        self.assertEqual(b_choice(3,2), (1,))
        self.assertEqual(b_choice(3,1), (1,2))

    def test_c_golden(self):
        q = component_c(2)
        self.assertEqual(q['distribution'], {(1,):F(1,2),(1,2):F(1,3),(1,2,3):F(1,6)})
        self.assertEqual(q['expected_revenue'], F(14,9))
        self.assertEqual(q['expected_regret'], F(1,9))
        # One path selecting [1] has regret 1/6, not the mean regret 1/9.
        self.assertEqual(oracle()-revenue(c_choice((1,), (0,))), F(1,6))

    def test_threshold_and_tie(self):
        self.assertEqual(c_choice((1,), (1,)), (1,))
        self.assertEqual(c_choice((0,0), (2,0)), (1,2))  # mean exactly 1
        self.assertEqual(c_choice((0,), (0,)), (1,2,3))

    def test_probabilities_and_budgets(self):
        for s in PREFIXES:
            p = probabilities(s)
            self.assertEqual(sum(p.values()), 1)
            self.assertEqual(set(p), {0,*s})
        for m in range(2,10):
            q = component_c(m)
            self.assertEqual(sum(q['distribution'].values()), 1)
            self.assertEqual(q['effective_budget']+q['unused_budget'], m)
        a,b=component_c(8),component_c(9)
        self.assertEqual(a['distribution'],b['distribution'])
        self.assertEqual((b['effective_budget'],b['total_budget']), (8,9))

    def test_zero_preferences(self):
        self.assertEqual(probabilities((1,2), (0,0,0)), {0:F(1),1:F(0),2:F(0)})
        self.assertEqual(component_b(2, v=(0,0,0)), 0)
        q=component_c(2,v=(0,0,0))
        self.assertEqual(q['distribution'][(1,2,3)],1)
        self.assertEqual(q['expected_regret'],0)

    def test_scaling(self):
        # C's absolute threshold must scale with revenue units.
        for factor in [F(1,2),F(2),F(3)]:
            r=tuple(factor*i for i in (3,2,1))
            self.assertEqual(component_b(8,r=r),factor*component_b(8))
            q=component_c(4,r=r,threshold=factor)
            base=component_c(4)
            self.assertEqual(q['distribution'],base['distribution'])
            self.assertEqual(q['expected_regret'],factor*base['expected_regret'])

    def test_revenue_contract(self):
        for r in [(1,1,9), (4,2,1), (0,0,0), (3,2,0)]:
            for call in [lambda: parameters(r), lambda: oracle(r),
                         lambda: revenue((1,), r), lambda: component_b(2, r),
                         lambda: component_c(2, r), lambda: c_choice((1,), (0,), r)]:
                with self.subTest(r=r):
                    with self.assertRaises(ValueError):
                        call()

    def test_enumeration_cap_before_power(self):
        tree = ast.parse(inspect.getsource(component_c))
        guard = next(n for n in tree.body[0].body if isinstance(n, ast.If))
        self.assertEqual(ast.dump(guard.test), ast.dump(ast.parse('tau > 4', mode='eval').body))
        self.assertIsInstance(guard.body[0], ast.Raise)
        powers = [n for n in ast.walk(tree) if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Pow)]
        loops = [n for n in ast.walk(tree) if isinstance(n, ast.For)]
        self.assertTrue(powers and loops)
        self.assertTrue(all(n.lineno > guard.end_lineno for n in powers + loops))
        self.assertEqual(MAX_PATHS, 6**4)
        self.assertEqual(component_c(9)['enumerated_paths'], MAX_PATHS)
        for m in (10, 10**100):
            with self.assertRaises(ValueError):
                component_c(m)

    def test_b_exact_budget_cap(self):
        self.assertEqual(MAX_B_BUDGET, 128)
        result = component_b(128, v=(1,1,1))
        expected = F(sum(comb(128, x) for x in range(86, 129)), 6 * 2**128)
        self.assertIsInstance(result, F)
        self.assertEqual(result, expected)
        with patch('assortment_run.parameters', side_effect=AssertionError('setup reached')) as setup:
            with patch('assortment_run.probabilities', side_effect=AssertionError('probabilities reached')) as probs:
                with patch('assortment_run.comb', side_effect=AssertionError('comb reached')) as choose:
                    for m in (129, 10**100):
                        with self.assertRaises(ValueError):
                            component_b(m)
                    setup.assert_not_called()
                    probs.assert_not_called()
                    choose.assert_not_called()
        self.assertEqual(b_choice(10**100, 10**100), (1,))

    def test_bad_inputs(self):
        for m in [True,0,-1, F(2),2.5]:
            with self.assertRaises(ValueError): component_b(m)
        for m in [1,10,True]:
            with self.assertRaises(ValueError): component_c(m)
        for x in [-1,3,True]:
            with self.assertRaises(ValueError): b_choice(2,x)
        for ids in [(2,),(-1,),(True,)]:
            with self.assertRaises(ValueError): c_choice(ids,(0,))
        for s in [(),(1,1),(4,),(True,)]:
            with self.assertRaises(ValueError): probabilities(s)
        for r,v in [((1,2),(1,1,1)), ((-1,2,3),(1,1,1)), ((1,2,3),(1,-1,1)), ((1.,2,3),(1,1,1))]:
            with self.assertRaises(ValueError): component_c(2,r,v)
        with self.assertRaises(ValueError): c_choice((),())
        with self.assertRaises(ValueError): c_choice((0,),(0,0))
        with self.assertRaises(ValueError): component_c(2,threshold=-1)



def test_all_results_regenerate_and_independent_subset_oracle():
    data=json.loads((DIR/'results.json').read_text())
    assert data==model.generate()
    assert len(data['cases'])==96
    for c in data['cases']:
        r=[F(c['scale'])*x for x in (3,2,1)];v=c['v']
        # All 8 subsets, including empty: independent of model.oracle.
        values=[]
        for bits in range(8):
            ids=[i for i in range(3) if bits&(1<<i)]
            values.append(sum((r[i]*v[i] for i in ids),F(0))/(1+sum(v[i] for i in ids)))
        assert F(c['oracle'])==max(values)
        for p in c['policies']:
            assert sum(map(F,p['distribution']))==1
            expected=sum(F(p['distribution'][k-1])*sum(r[i]*v[i] for i in range(k))/(1+sum(v[:k])) for k in (1,2,3))
            assert F(p['expected'])==expected
            assert F(p['regret'])==max(values)-expected>=0
        assert c['total']==c['effective']+c['unused']
    for m in (0,1,10,10**100,True,2.5):
        with pytest.raises(ValueError):model.integrated_case(m,0,F(1))
    for v in (-1,4,True):
        with pytest.raises(ValueError):model.integrated_case(2,v,F(1))
    for s in (0,3,True):
        with pytest.raises(ValueError):model.integrated_case(2,0,s)


def test_js_choices_all_states_reset_errors_and_initial_html(tmp_path):
    script=r'''
const assert=require('node:assert/strict'),fs=require('fs'),ui=require(process.argv[2]);
const data=JSON.parse(fs.readFileSync(process.argv[3]));let count=0;
for(const c of data.cases)for(let a=0;a<data.a.length;a++)for(let o=0;o<4;o++){
 const v=ui.view(data,{a:String(a),m:String(c.m),preference:String(c.preference),scale:c.scale,observation:String(o)});
 for(const p of c.policies)assert(v.comparison.includes(`<td>${p.expected}</td><td>${p.regret}</td>`));
 assert(v.aSummary.includes(`g₀=${data.a[a].g0}`));count++;
}
assert.equal(count,2304);
const nodes={};for(const k of [...Object.keys(ui.defaults()),'rows','comparison','bars','aSummary-output','summary-output','observation-output','data','error','reset'])nodes['aob-'+k]={value:ui.defaults()[k],textContent:k==='data'?JSON.stringify(data):'',innerHTML:'',events:{},addEventListener(e,f){this.events[e]=f;}};
ui.mount({getElementById:id=>nodes[id]});let original=nodes['aob-summary-output'].textContent;
nodes['aob-m'].value='9';nodes['aob-m'].events.change();assert.notEqual(nodes['aob-summary-output'].textContent,original);
for(const bad of ['10','1','NaN','2.5','9e99','']){nodes['aob-m'].value=bad;nodes['aob-m'].events.change();assert(nodes['aob-error'].textContent);}
nodes['aob-reset'].events.click();assert.equal(nodes['aob-summary-output'].textContent,original);assert.equal(nodes['aob-error'].textContent,'');
for(const [key,value]of [['a','99'],['scale','<img>'],['preference','-1'],['observation','4']])assert.throws(()=>ui.view(data,{...ui.defaults(),[key]:value}));
console.log(JSON.stringify({initial:ui.view(data,ui.defaults()),decisions:Array.from({length:8},(_,i)=>Array.from({length:4},(_,j)=>ui.decision(i+2,j)))}));
'''
    runner=tmp_path/'check.cjs';runner.write_text(script)
    result=subprocess.run(['node',str(runner),str(DIR/'interactive.js'),str(DIR/'results.json')],text=True,capture_output=True,check=True)
    observed=json.loads(result.stdout)
    for m,items in enumerate(observed['decisions'],2):
        for item in items:
            assert model.b_choice(m,item['x'])==tuple(range(1,item['b']+1))
            assert model.c_choice(item['first'],item['second'])==tuple(range(1,item['c']+1))
    from paper_lab.assortment_observation import widget
    html=widget(json.loads((DIR/'results.json').read_text()),DIR)
    for key in ('rows','comparison','aSummary','summary','observation'):assert observed['initial'][key] in html
    assert '__DATA__' not in html and '<noscript>' in html


@pytest.mark.parametrize('viewport',(360,768,1440))
def test_responsive_static_contract(viewport):
    # CSS contract, not browser CSSOM/pixel or physical-device evidence.
    html=(DIR/'interactive.html').read_text()
    assert '#aob .aob-scroll {max-width:100%;overflow-x:auto}' in html
    assert 'min-width:640px;table-layout:auto' in html
    assert '#aob td {white-space:nowrap' in html
    assert 'flex-wrap:wrap' in html and 'max-width:100%' in html
    if viewport<480:assert '@media(max-width:480px)' in html and 'flex-direction:column' in html
    assert html.count('tabindex="0"')==2
    assert 'role="alert"' in html and 'min="2" max="9" step="1"' in html


def test_preexisting_sources_and_case_ids_preserved(tmp_path):
    import hashlib
    base='2dcd139222067425c39d753a999bc9c4223c6d18'
    listing=subprocess.check_output(['git','ls-tree','-r',base,'papers','guides'],cwd=ROOT,text=True)
    count=0
    for line in listing.splitlines():
        left,path=line.split('\t');sha=left.split()[2]
        content=(ROOT/path).read_bytes()
        assert hashlib.sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest()==sha,path
        count+=1
    assert count>=750
    from paper_lab.build import build
    from review_103 import preflight
    site=tmp_path/'site';build(root=ROOT,site_dir=site)
    p=preflight(site)
    assert p['pages']==111 and len(p['required_cases'])==429
    new={f'load-{slug}-{w}' for slug in ('assortment-observation-budget','trial-by-trace-evidence-boundaries') for w in (360,768,1440)}
    assert new<=set(p['required_cases'])
    # The pinned baseline plan is captured before the addition and checked below.
    baseline=json.loads((ROOT/'tests/assortment_baseline_cases.json').read_text())
    assert baseline['base']==base
    assert len(baseline['ids'])==423
    assert set(p['required_cases'])==set(baseline['ids'])|new
    for name in ('run.py','results.json','lab.yaml','README.md','mapping.md','interactive.js'):
        assert (site/'downloads/assortment-observation-budget'/name).read_bytes()==(DIR/name).read_bytes()

    # This is a widget template, not a standalone HTML document for download.
    assert not (site/'downloads/assortment-observation-budget/interactive.html').exists()
    html=(site/'papers/assortment-observation-budget.html').read_text()
    assert '__DATA__' not in html and '__JS__' not in html
