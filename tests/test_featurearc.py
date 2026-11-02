"""Independent behavior, reference validation, display parity and preservation."""
import copy
import hashlib
import importlib.util
import json
import re
from pathlib import Path
import subprocess
import sys
import pytest

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'papers/featurearc-inherited-defects-chain-gates'
spec=importlib.util.spec_from_file_location('arc_model',P/'run.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

@pytest.mark.parametrize('scenario',m.SCENARIOS)
@pytest.mark.parametrize('repair',[False,True])
def test_actual_behavior_and_history(scenario,repair):
 c=m.simulate(scenario,repair)
 assert len(c['stages'])==3
 for before,after in zip(c['stages'],c['stages'][1:]):assert before['after']==after['before']
 assert c['stages'][-1]['gate']  # Benign local sample intentionally misses boundary and signed sum.
 assert c['chain']['gate']==(repair or scenario=='correct')
 assert c['chain']['gate']==(c['chain']['f2p']['passed'] and c['chain']['p2p']['passed'])
 if scenario=='legacy' and not repair:
  assert c['chain']['f2p']['passed'] and not c['chain']['p2p']['passed']
 if scenario in ('inherited','oracle'):
  assert not c['stages'][0]['gate'] and not c['stages'][1]['gate']
  assert c['stages'][0]['after']['inclusive'] is False
 if scenario=='regression':
  assert c['stages'][0]['gate'] and c['stages'][1]['gate']
 assert all(s['self_test']['passed'] for s in c['stages'])


def test_wrong_expectation_is_literal_and_does_not_change_acceptance():
 c=m.simulate('oracle')
 assert c['stages'][0]['self_test']['checks'][0]['expected']==[3]
 assert c['stages'][0]['f2p']['checks'][0]['expected']==[2,3]
 for s in m.SCENARIOS:
  assert m.simulate(s)['stages'][0]['f2p']['checks'][0]['expected']==[2,3]


def test_reference_before_after_validation():
 state=m.initial();start=copy.deepcopy(state)
 for k in range(3):
  assert not m.check(state,m.F2P[k])['passed']
  assert m.check(state,m.P2P[k])['passed']
  m.edit(state,k,'correct',False)
  assert m.check(state,m.F2P[k])['passed']
  assert m.check(state,m.P2P[k])['passed']
 assert not m.check(start,m.CHAIN)['passed'] and m.check(state,m.CHAIN)['passed']
 assert m.check(start,m.BASE)['passed'] and m.check(state,m.BASE)['passed']


def test_metrics_denominators_and_recovery():
 cases=[m.simulate(s) for s in m.SCENARIOS]
 d=m.metrics(cases)
 assert d['first']==m.ratio(3,5)
 assert d['chain']==m.ratio(1,5)
 assert d['last_pass_chain_fail']==m.ratio(4,5)
 assert d['continuation']==m.ratio(6,6)
 assert d['recovery']==m.ratio(0,2)
 fixed=m.metrics([m.simulate(s,True) for s in m.SCENARIOS])
 assert fixed['recovery']==m.ratio(2,2) and fixed['chain']==m.ratio(5,5)
 assert all(v['value'] is None for v in m.metrics([]).values())
 assert m.metrics([m.simulate('correct')])['recovery']['value'] is None
 assert round(69/273*100,1)==25.3


def test_regeneration_exact_and_compact():
 assert json.loads((P/'results.json').read_text())==m.results()
 sys.path.insert(0,str(P))
 try:
  spec=importlib.util.spec_from_file_location('arc_render',P/'render.py');renderer=importlib.util.module_from_spec(spec);spec.loader.exec_module(renderer)
  assert (P/'experiment.md').read_text()==renderer.document(m.results())
 finally:sys.path.remove(str(P))
 assert (P/'results.json').read_text()==json.dumps(m.results(),ensure_ascii=False,separators=(',',':'))+'\n'


def test_107_sources_and_guides_preserved():
 b=json.loads((ROOT/'tests/main_107_catalog.json').read_text())
 assert b['base']=='ad841a1965bab4e19cce2aa1ed7613b71b4bf922'
 from shelf_guide_preservation import verify_preserved_source
 for path,h in b['source_hashes'].items():verify_preserved_source(ROOT,path,h)
 assert len(b['ids'])==107
 from catalog_expectations import assert_catalog
 ids=[p.parent.name for p in (ROOT/'papers').glob('*/lab.yaml')];assert_catalog(ids)
 with pytest.raises(AssertionError):assert_catalog(ids[:-1])


def test_all_old_cases_and_new_semantics(tmp_path):
 from paper_lab.build import build
 from review_103 import preflight
 site=tmp_path/'site';build(root=ROOT,site_dir=site);plan=preflight(site)
 b=json.loads((ROOT/'tests/main_107_catalog.json').read_text())
 added={f'load-{P.name}-{w}' for w in (360,768,1440)}|{f'featurearc-{w}' for w in (360,768,1440)}|{'nojs-'+P.name}
 assert len(b['required_cases'])==413
 assert set(plan['required_cases'])==set(b['required_cases'])|added
 assert len(plan['required_cases'])==len(set(plan['required_cases']))==420
 assert all([P.name,w] in plan['semantic_groups'] for w in (360,768,1440))
 assert plan['source_hashes']['featurearc_review.py']==hashlib.sha256((ROOT/'tests/featurearc_review.py').read_bytes()).hexdigest()
 assert (site/'downloads'/P.name/'results.json').read_bytes()==(P/'results.json').read_bytes()
 html=(site/'papers'/f'{P.name}.html').read_text()
 assert '<noscript>' in html and 'arc-data' in html and 'stage F2P' in html


def test_js_all_records_and_reset_are_python_outputs(tmp_path):
 # DOM fixture checks renderer consistency, not real layout/native input.
 harness=r'''
const fs=require('fs'),vm=require('vm'),data=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const elements={};
for(const id of ['scenario','repair','prev','next','reset','output'])elements['arc-'+id]={value:id==='scenario'?'inherited':'',checked:false,disabled:false,innerHTML:'',events:{},addEventListener(k,f){this.events[k]=f;}};
elements['arc-data']={textContent:JSON.stringify(data)};
global.document={getElementById:id=>elements[id]};
vm.runInThisContext(fs.readFileSync(process.argv[3],'utf8'));
const initial=elements['arc-output'].innerHTML,frames=[];
for(const c of data.synthetic){
 elements['arc-scenario'].value=c.scenario;elements['arc-repair'].checked=c.repair;
 elements['arc-scenario'].events.change();
 for(let k=0;k<3;k++){
  if(k)elements['arc-next'].events.click();
  frames.push(elements['arc-output'].innerHTML);
 }
 if(!elements['arc-next'].disabled)throw Error('Final next must disable');
 elements['arc-prev'].events.click();
 if(!elements['arc-output'].innerHTML.includes('data-stage="1"'))throw Error('Previous record');
}
elements['arc-reset'].events.click();
if(elements['arc-output'].innerHTML!==initial||elements['arc-repair'].checked||elements['arc-scenario'].value!=='inherited')throw Error('Reset');
process.stdout.write(JSON.stringify(frames));
'''
 js=tmp_path/'test.cjs';js.write_text(harness)
 frames=json.loads(subprocess.check_output(['node',str(js),str(P/'results.json'),str(P/'interactive.js')],text=True))
 from html.parser import HTMLParser
 class Text(HTMLParser):
  def __init__(self,html):super().__init__();self.text='';self.feed(html)
  def handle_data(self,d):self.text+=d
 assert len(frames)==30
 for frame,(case,stage) in zip(frames,((c,k) for c in m.results()['synthetic'] for k in range(3))):
  text=Text(frame).text;s=case['stages'][stage]
  assert f'data-stage="{stage}"' in frame
  assert f'data-stage-gate>{"PASS" if s["gate"] else "FAIL"}' in frame
  suites=[('自己テスト',s['self_test']),('stage F2P',s['f2p']),('stage P2P',s['p2p'])]+([('chain F2P',case['chain']['f2p']),('chain P2P',case['chain']['p2p'])] if stage==2 else [])
  cards=re.findall(r'<section class="arc-suite">(.*?)</section>',frame)
  assert len(cards)==len(suites)
  for card,(label,suite) in zip(cards,suites):
   text=Text(card).text
   expectation='自己テストの期待値' if label=='自己テスト' else '仕様の期待値'
   assert ('仕様の期待値' if label=='自己テスト' else '自己テストの期待値') not in text
   for c in suite['checks']:
    v=lambda x:json.dumps(x,ensure_ascii=False,separators=(',',':'))
    assert f'{expectation} {v(c["expected"])} ／ 実際 {v(c["actual"])}' in text
  assert ('data-chain-gate' in frame)==(stage==2)


def dom_fixture(case,stage):
 from featurearc_review import assert_arc_dom
 s=case['stages'][stage];suites=[('自己テスト',s['self_test']),('stage F2P',s['f2p']),('stage P2P',s['p2p'])]
 if stage==2:suites += [('chain F2P',case['chain']['f2p']),('chain P2P',case['chain']['p2p'])]
 v=lambda x:json.dumps(x,ensure_ascii=False,separators=(',',':'))
 d=dict(stage=str(stage),stageGate='PASS' if s['gate'] else 'FAIL',chainGate=('PASS' if case['chain']['gate'] else 'FAIL') if stage==2 else None,pending=stage!=2,geometry=[dict(box=[0,0,100,20],text=[[1,1,99,19]])],suites=[])
 for label,suite in suites:
  expectation='自己テストの期待値' if label=='自己テスト' else '仕様の期待値'
  d['suites'].append(dict(label=label,gate='PASS' if suite['passed'] else 'FAIL',checks=[f'{c["name"]}：'+('PASS' if c['passed'] else 'FAIL')+f' {c["op"]}({v(c["values"])}, 閾値 {c["threshold"]}, 上限 {c["limit"]}) {expectation} {v(c["expected"])} ／ 実際 {v(c["actual"])}' for c in suite['checks']]))
 assert_arc_dom(d,case,stage)
 return d


@pytest.mark.parametrize('mutation',['stage','chain','missing','extra','value','geometry'])
def test_browser_assertion_rejects_false_success(mutation):
 from featurearc_review import assert_arc_dom
 c=m.simulate();d=dom_fixture(c,2)
 if mutation=='stage':d['stage']='1'
 if mutation=='chain':d['chainGate']='PASS'
 if mutation=='missing':d['suites'].pop()
 if mutation=='extra':d['suites'].append(d['suites'][0])
 if mutation=='value':d['suites'][0]['checks'][0]='invented'
 if mutation=='geometry':d['geometry'][0]['text'][0][2]=120
 with pytest.raises(AssertionError):assert_arc_dom(d,c,2)


def test_initial_nojs_and_wrong_oracle_card_labels():
 sys.path.insert(0,str(P))
 try:
  spec=importlib.util.spec_from_file_location('arc_label_render',P/'render.py')
  renderer=importlib.util.module_from_spec(spec);spec.loader.exec_module(renderer)
 finally:sys.path.remove(str(P))
 initial=(P/'experiment.md').read_text().split('<script id="arc-data"')[0]
 cards=re.findall(r'<section class="arc-suite">(.*?)</section>',initial)
 assert len(cards)==3
 assert '自己テストの期待値' in cards[0] and '仕様の期待値' not in cards[0]
 for card in cards[1:]:
  assert '仕様の期待値' in card and '自己テストの期待値' not in card
 oracle=m.simulate('oracle')['stages'][0]
 wrong=renderer.suite('自己テスト',oracle['self_test'])
 accepted=renderer.suite('stage F2P',oracle['f2p'])
 assert '自己テストの期待値 <code>[3]</code>' in wrong
 assert '仕様の期待値' not in wrong
 assert '仕様の期待値 <code>[2,3]</code>' in accepted


@pytest.mark.parametrize('suite_index',[0,1,2,3,4])
def test_browser_gate_rejects_swapped_expectation_labels(suite_index):
 from featurearc_review import assert_arc_dom
 case=m.simulate('oracle');actual=dom_fixture(case,2)
 old,new=('自己テストの期待値','仕様の期待値') if suite_index==0 else ('仕様の期待値','自己テストの期待値')
 actual['suites'][suite_index]['checks']=[s.replace(old,new) for s in actual['suites'][suite_index]['checks']]
 with pytest.raises(AssertionError):assert_arc_dom(actual,case,2)
