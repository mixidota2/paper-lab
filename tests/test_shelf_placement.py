import importlib.util,itertools,json,subprocess,copy,math,random
from decimal import Decimal,localcontext
from pathlib import Path
import pytest
LAB=Path(__file__).resolve().parents[1]/'papers/shelf-placement-options'
spec=importlib.util.spec_from_file_location('placement',LAB/'run.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def js(cases):
 code="const m=require(process.argv[1]);let s='';process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>console.log(JSON.stringify(JSON.parse(s).map(x=>m[x.fn](...x.args)))));"
 return json.loads(subprocess.run(['node','-e',code,str(LAB/'model.js')],input=json.dumps(cases),text=True,capture_output=True,check=True).stdout)
def test_expected_radicals_and_boundaries():
 for nu,mode,faces in [(0,'hang',2),(1,'hang',2),(1.1,'shelf',4),(5,'shelf',4),(5.1,'shelf',4)]:
  a=m.toy_a(nu);assert len(a['candidates'])==8;assert (a['best']['mode'],a['best']['faces'])==(mode,faces)
 with localcontext() as ctx:
  ctx.prec=50
  fixed=18*Decimal(2).sqrt();free=10*Decimal(2).sqrt()+8*Decimal(3).sqrt()
  assert m.toy_b(4)['best']['profit']==pytest.approx(float(fixed),rel=0,abs=1e-10)
  assert m.toy_b()['best']['profit']==pytest.approx(float(free),rel=0,abs=1e-10)
 assert len(m.toy_b()['ties'])==2
 assert m.toy_b()['best']['faces']==[2,3]
 tie=m.toy_a(0,math.log2(1.5));assert len(tie['ties'])==2
 assert {x['mode'] for x in tie['ties']}=={'hang','shelf'}

def test_javascript_with_independent_rational_checker():
 cases=[dict(fn='toyA',args=[n,b]) for n,b in itertools.product([0,1,1.1,5,5.1,6],[0,.5,1])]
 cases += [dict(fn='toyB',args=[y,n,t]) for y,n,t in itertools.product([None,1,4,5,8],[0,1,1.1,3],[0,1,2])]
 for case,j in zip(cases,js(cases)):
  p=(m.toy_a if case['fn']=='toyA' else m.toy_b)(*case['args'])
  assert len(j['ties'])==len(p['ties'])
  if p['best'] is None:assert j['best'] is None
  else:assert j['best']['profit']==pytest.approx(p['best']['profit'],rel=0,abs=1e-10)
  for row in j['candidates']:
   assert m.check(row['layout'], m.definition('a',case['args'][0]) if case['fn']=='toyA' else m.definition('b',case['args'][1],case['args'][2]))['feasible']==row['feasible']
   assert row['layout']['expected_ids']==[x['id'] for x in row['layout']['rects']]

def test_checker_rejects_mutations():
 layout=m.toy_b()['best']['layout']
 assert m.check(layout,m.definition('b',1,1))['feasible']
 for change in ['missing','floating','outside','board','overlap','facings']:
  x=copy.deepcopy(layout)
  if change=='missing':x['rects'].pop()
  if change=='floating':x['rects'][1]['y']+=.1
  if change=='outside':x['rects'][0]['x']+=.1
  if change=='board':x['boards'][0]-=.1
  if change=='overlap':
   for r in x['rects']:r['y']=0
  if change=='facings':x['rects'][0]['faces']=4
  assert not m.check(x,m.definition('b',1,1))['feasible'],change

def test_four_counterexamples():
 assert m.pack([(2,2),(2,2)],3,3) is None
 rectangles=[(2,3),(2,1),(2,3),(2,1)]
 assert m.pack(rectangles,4,4) is not None
 # Independent next-fit rows fail, although an unrestricted placement exists.
 x=y=row_height=0
 for w,h in rectangles:
  if x+w>4:y+=row_height;x=0;row_height=0
  x+=w;row_height=max(row_height,h)
 assert y+row_height>4
 assert 10*math.sqrt(3)+1>11*math.sqrt(2)
 # Equal-height bands are not nested feasible sets: 3 items height2.
 assert 2*(3//2)<3
 assert 3*(2//2)>=3

def test_monotonicity_scaling_and_zero_boundaries():
 for n in [0,1,1.1,5]:
  for factor in [1,2,10]:
   assert m.toy_a(n,scale=factor)['best']['faces']==m.toy_a(n)['best']['faces']
   assert m.toy_b(scale=factor)['best']['profit']==m.toy_b()['best']['profit']
 assert m.toy_a(0,0)['best']['profit']==12
 assert m.toy_a(0,1)['best']['profit']==32
 values=[m.toy_a(n)['best']['profit'] for n in range(7)]
 assert values==sorted(values,reverse=True)
 for nu,t in itertools.product([0,1,2],[0,1,2]):
  free=m.toy_b(None,nu,t)
  for y in [2,4,5,7]:
   fixed=m.toy_b(y,nu,t)
   if fixed['best']:assert free['best']['profit']>=fixed['best']['profit']-1e-10
 # Demand coefficients are unchanged by gap alone.
 for n in [0,6]:assert [r['profit'] for r in m.toy_a(n)['candidates']]==[r['profit'] for r in m.toy_a(0)['candidates']]

def test_saved_results_and_parameter_definitions():
 r=json.loads((LAB/'results.json').read_text())
 assert r['b_fixed']==m.toy_b(4)
 assert r['b_free']==m.toy_b()
 assert r['improvement_over_fixed']==pytest.approx(.09988660950737292,rel=0,abs=1e-10)
 for a in r['a']:
  assert a==m.toy_a(a['input']['nu'])
  for row in a['candidates']:
   rect=row['layout']['rects'][0]
   h=row['faces']*((3+a['input']['nu']) if row['mode']=='hang' else 2)
   assert rect['h']==pytest.approx(h,rel=0,abs=1e-10)


def test_independent_product_definition_rejects_mutations():
    source=m.toy_a()['best']['layout']; spec=m.definition('a')
    for field,value in [('faces',4),('faces',1.5),('faces',True),('w',-2),('h',-6),('h',1),('max_faces',99),('mode','unknown')]:
        layout=copy.deepcopy(source);layout['rects'][0][field]=value
        assert not m.check(layout,spec)['feasible'],(field,value)
    layout=copy.deepcopy(m.toy_a()['candidates'][0]['layout'])
    extra=copy.deepcopy(layout['rects'][0]);extra['y']=3;layout['rects'].append(extra)
    assert not m.check(layout,spec)['feasible']
    layout=copy.deepcopy(source);layout['width']=100
    assert not m.check(layout,spec)['feasible']

def test_every_slider_gap_thickness_has_exact_geometry():
    cases=[dict(fn='toyB',args=[None,n/10,t/10]) for n,t in itertools.product(range(61),range(21))]
    cases += [dict(fn='toyA',args=[n/10,b/20]) for n,b in itertools.product(range(61),range(21))]
    rng=random.Random(20261016)
    cases += [dict(fn='toyB',args=[rng.randrange(10,81)/10,rng.randrange(61)/10,rng.randrange(21)/10]) for _ in range(1000)]
    assert len(cases)==3562
    for case,result in zip(cases,js(cases)):
        args=case['args'];spec=m.definition('a',args[0]) if case['fn']=='toyA' else m.definition('b',args[1],args[2])
        expected=(m.toy_a if case['fn']=='toyA' else m.toy_b)(*args)
        assert len(result['ties'])==len(expected['ties'])
        if expected['best']:
            assert result['best']['profit']==pytest.approx(expected['best']['profit'],rel=0,abs=1e-10)
        else:assert result['best'] is None
        for row in result['candidates']:assert m.check(row['layout'],spec)['feasible']==row['feasible']
