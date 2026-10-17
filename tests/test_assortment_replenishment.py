import importlib.util,itertools,json,subprocess,copy
from pathlib import Path
import pytest
LAB=Path(__file__).resolve().parents[1]/'papers/assortment-replenishment-hard-constraints'
spec=importlib.util.spec_from_file_location('casrp',LAB/'run.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def js(cases):
 code="const m=require(process.argv[1]);let s='';process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>console.log(JSON.stringify(JSON.parse(s).map(m.experiment))));"
 return json.loads(subprocess.run(['node','-e',code,str(LAB/'model.js')],input=json.dumps(cases),text=True,capture_output=True,check=True).stdout)
def test_hand_examples_and_persisted_results():
 r={n:m.experiment(m.case(n)) for n in ['T1','T2','T3','T4']}
 assert r['T1']['oracle']['candidates']==27
 assert r['T1']['oracle']['width_feasible']==10
 assert r['T1']['oracle']['feasible_count']==7
 assert r['T1']['oracle']['best']['k']==[2,0,0]
 assert r['T1']['oracle']['best']['profit']==24
 assert r['T1']['reevaluated']['profit']==21
 assert r['T1']['gap'] is None
 assert r['T1']['fixed_assortment']['best'] is None
 assert r['T2']['gap']==.375
 assert r['T3']['oracle']['best']['profit']==1
 assert json.loads((LAB/'results.json').read_text())['cases']==r
 assert m.evaluate(m.case('T4'),[0,1,0])['rows'][1]['demand']==5

def test_cross_language_all_controls():
 cases=[]
 for name,S,f,beta,t,lam in itertools.product(['T1','T2','T3','T4'],[0,2,5],[0,.8,1],[0,.2,.5],[0,1],[0,1]):
  d=m.case(name);d['S']=S
  for x in d['items']:x.update(f=f,beta=beta,lam=x['lam']*lam)
  d['mu']=[[v*t for v in row] for row in d['mu']];cases.append(d)
 for d,j in zip(cases,js(cases)):
  p=m.experiment(d)
  for key in ['oracle','fixed_assortment']:
   assert j[key]['ties']==p[key]['ties']
   assert j[key]['feasible_count']==p[key]['feasible_count']
   if p[key]['best']:assert j[key]['best']['profit']==pytest.approx(p[key]['best']['profit'],rel=0,abs=1e-9)
   else:assert j[key]['best'] is None
  assert j['reevaluated']['feasible']==p['reevaluated']['feasible']
  assert j['gap']==pytest.approx(p['gap'],rel=0,abs=1e-9) if p['gap'] is not None else j['gap'] is None

def test_equal_boundary_and_zero_demand():
 d=m.case('T2');d['items']=[dict(d['items'][0],alpha=10,g=8,f=.8)];d['mu']=[[0]]
 assert m.evaluate(d,[1])['feasible']
 d['items'][0]['g']=7;assert not m.evaluate(d,[1])['feasible']
 d['items'][0].update(alpha=0,c=0)
 assert m.evaluate(d,[1])['rows'][0]['ratio'] is None
 assert m.oracle(d)['best']['profit']==0
 assert m.oracle(d)['ties']==[[0],[1]]

def test_fixed_mu_loss_and_no_second_transfer():
 d=m.case('T4');o=m.evaluate(d,[0,1,0]);f=o['flows']
 assert next(x for x in f if x['source']=='A' and x['target']=='B')['amount']==4
 assert next(x for x in f if x['source']=='A' and x['target']=='C')['amount']==pytest.approx(2.4,rel=0,abs=1e-9)
 assert sum(x['amount'] for x in f if x['source']=='A')==8
 assert o['rows'][0]['demand']==0

def test_monotonic_feasible_sets_and_substitution_counterexample():
 d=m.case('T1')
 profits=[]
 for S in range(7):d['S']=S;profits.append(m.oracle(d)['best']['profit'])
 assert profits==sorted(profits)
 profits=[];d=m.case('T1')
 for f in [0,.4,.8,1]:
  for x in d['items']:x['f']=f
  profits.append(m.oracle(d)['best']['profit'])
 assert profits==sorted(profits,reverse=True)
 d=m.case('T3');d['mu'][1][0]=0;assert m.oracle(d)['best']['profit']==20
 d['mu'][1][0]=.5;assert m.oracle(d)['best']['profit']==1

def test_f_can_increase_number_adopted_and_permutation():
 d=m.case('T1');d['mu']=[[0,0,0],[1,0,0],[1,0,0]]
 for x,a,p,g in zip(d['items'],[1,10,10],[10,1,1],[5,10,10]):x.update(alpha=a,p=p,g=g,f=.4)
 assert m.oracle(d)['best']['k']==[2,0,0]
 for x in d['items']:x['f']=1
 assert m.oracle(d)['best']['k']==[0,1,1]
 old=m.oracle(d)['best']['profit'];d['items'].reverse();d['mu']=[row[::-1] for row in d['mu'][::-1]]
 assert m.oracle(d)['best']['profit']==old
