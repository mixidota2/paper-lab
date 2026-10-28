"""Independent toy invariants and real JS execution; no browser claim."""
import importlib.util
import json
from pathlib import Path
import subprocess
from fractions import Fraction
import hashlib
import pytest
from catalog_expectations import CURRENT,EPISEM,assert_catalog
from episem_review import assert_episem_frame
ROOT=Path(__file__).resolve().parents[1];LAB=ROOT/'papers'/EPISEM
spec=importlib.util.spec_from_file_location('episem_toy',LAB/'run.py');toy=importlib.util.module_from_spec(spec);spec.loader.exec_module(toy)
DATA=json.loads((LAB/'results.json').read_text())


def test_recompute_and_independent_arithmetic():
    assert toy.compute()==DATA
    assert len(DATA['synthetic']['cases'])==480
    assert DATA['reported']['fixed_conditions_per_model']==600+4*(944+419)==6052
    m=toy.metrics('single_audit','before');a=m['aggregate']
    assert [t['q'] for t in m['tasks']]==[3,7]
    assert [t['paired_count'] for t in m['tasks']]==[2,3]
    assert a['pur']==pytest.approx(float(Fraction(23,42)))
    assert a['pur']!=sum(t['paired_count'] for t in m['tasks'])/sum(t['q'] for t in m['tasks'])
    visible=toy.metrics('visible','before')['aggregate']
    assert visible['sbm']==pytest.approx(float(Fraction(7,24)))
    assert visible['critical_ucr']==1
    assert visible['failure_frequency']==pytest.approx(float(Fraction(13,21)))
    for p,expected in [('refuse',(0,1,0,0)),('execute',(1,0,1,0)),('recover',(0,1,1,1))]:
        a=toy.metrics(p,'before')['aggregate'];assert tuple(a[k] for k in ['full_ucr','sbm','full_sws','pur'])==expected
    assert toy.metrics('recover','after')['aggregate']['pur']==0


@pytest.mark.parametrize('case',DATA['synthetic']['cases'],ids=lambda c: '-'.join(map(str,c['args'])))
def test_world_observation_recovery_and_terminal_invariants(case):
    args=case['args'];task,mask,irrelevant,policy,setting,timing=args
    p=toy.pair(*args);assert p==case['result']
    # Same request/task/schema/policy/mask for both twins; only the permission
    # atom differs in complete state. No change in schema or allowed tool list.
    u,s=p['unsafe'],p['safe'];assert u['hidden']==s['hidden']
    assert set(u['world'])==set(s['world'])
    assert [k for k in u['world'] if u['world'][k]!=s['world'][k]]==[toy.TASKS[task]['unsafe_atom']]
    assert not u['allowed'] and s['allowed']
    for r in (u,s):
        assert r['trace'][0]['visible']==r['trace'][1]['visible']
        assert set(r['trace'][0]['visible'])==set(r['world'])-set(r['hidden'])
        for event in r['trace']:
            for key,value in event.get('visible',{}).items():assert value==r['world'][key]
        audits=[e for e in r['trace'] if e['op']=='audit']
        assert bool(audits)==r['recovered']
        if audits:
            assert setting=='RE' and timing=='before'
            assert set(audits[0]['returned'])==set(r['hidden'])
            assert audits[0]['visible']==r['world']
        terminal=next(i for i,e in enumerate(r['trace']) if e['op'] in ('commit','stop'))
        assert all(e['op']=='audit_not_executed' for e in r['trace'][terminal+1:])
        if timing=='after':assert not r['recovered']
    assert p['paired']==(u['strict'] and s['strict'])
    if policy in ('refuse','execute'):assert not p['paired']


def test_boundary_coverage_and_nonmonotone_witness():
    assert toy.boundary({0:True},3)==0
    assert toy.boundary({0:False,1:True},3)==1
    # Failure need not persist at larger masks.
    assert toy.boundary({0:False,1:True,2:False,3:False},2)==1
    assert toy.boundary(dict.fromkeys(range(8),False),3)==4
    with pytest.raises(AssertionError):toy.boundary({0:False,1:False},3)
    with pytest.raises(AssertionError):toy.boundary({0:False,3:True},3)


def test_js_model_and_actual_widget_all_480_states_and_reset():
    harness=r'''
const fs=require('node:fs'),vm=require('node:vm');const {cases,metrics}=JSON.parse(fs.readFileSync(0,'utf8'));
const M=require(process.argv[1]+'/model.js'),nodes={};
for(const [key,value] of Object.entries({task:'0',mask:'1',irrelevant:'0',setting:'RE',policy:'visible',timing:'before',next:'',end:'',reset:'',output:''}))nodes['ep-'+key]={value,innerHTML:'',handlers:{},addEventListener(t,f){this.handlers[t]=f}};
vm.runInNewContext(fs.readFileSync(process.argv[1]+'/interactive.js','utf8'),{window:{EpiSEM:M},document:{getElementById:id=>nodes[id]}});
const frames=[],pairs=cases.map(c=>M.pair(...c.args)),computed={};
for(const p of M.policies)computed[p]={before:M.metrics(p,'before'),after:M.metrics(p,'after')};
for(const c of cases){
 for(const [i,k] of ['task','mask','irrelevant','policy','setting','timing'].entries()){nodes['ep-'+k].value=String(typeof c.args[i]==='boolean'?+c.args[i]:c.args[i]);nodes['ep-'+k].handlers.change();}
 const stages=[nodes['ep-output'].innerHTML];for(let i=0;i<2;i++){nodes['ep-next'].handlers.click();stages.push(nodes['ep-output'].innerHTML);}
 nodes['ep-end'].handlers.click();stages.push(nodes['ep-output'].innerHTML);frames.push(stages);
}
nodes['ep-reset'].handlers.click();process.stdout.write(JSON.stringify({pairs,computed,frames,reset:nodes['ep-output'].innerHTML,values:['task','mask','irrelevant','policy','setting','timing'].map(k=>nodes['ep-'+k].value)}));
'''
    d=DATA['synthetic'];actual=json.loads(subprocess.check_output(['node','-e',harness,str(LAB)],input=json.dumps(d),text=True))
    assert actual['pairs']==[c['result'] for c in d['cases']]
    assert actual['computed']==d['metrics']
    for case,frames in zip(d['cases'],actual['frames'],strict=True):
        for step,frame in zip([0,1,2,99],frames,strict=True):assert_episem_frame(frame,case,d['metrics'],step)
    initial=next(c for c in d['cases'] if c['args']==[0,1,False,'visible','RE','before'])
    assert actual['values']==['0','1','0','visible','RE','before']
    assert_episem_frame(actual['reset'],initial,d['metrics'],0)
    # A stale frame, false metric, swapped world or incorrect operation fails.
    for wrong in [actual['reset'].replace('100.00%','99.00%'),actual['reset'].replace('data-ep-world="safe"','data-ep-world="unsafe"'),actual['frames'][0][2].replace('通常readを繰り返す','audit')]:
        with pytest.raises(AssertionError):assert_episem_frame(wrong,initial,d['metrics'],0)


def test_105_source_files_and_exact_catalog_preserved():
    assert len(CURRENT['ids'])==105
    for path,sha in CURRENT['source_hashes'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha,path
    ids=[p.parent.name for p in (ROOT/'papers').glob('*/lab.yaml')];assert_catalog(ids)
    with pytest.raises(AssertionError):assert_catalog([*CURRENT['ids']])
    with pytest.raises(AssertionError):assert_catalog([*CURRENT['ids'][:-1],EPISEM,'invented'])


def test_399_existing_cases_retained_and_new_gates_required(tmp_path):
    from paper_lab.build import build
    from review_103 import preflight
    from review_103_report import automatic_errors
    site=tmp_path/'site';build(root=ROOT,site_dir=site);plan=preflight(site)
    baseline=json.loads((ROOT/'tests/main_105_review_cases.json').read_text())
    assert len(baseline['required_cases'])==399
    assert set(baseline['required_cases'])<=set(plan['required_cases'])
    assert all(g in plan['semantic_groups'] for g in baseline['semantic_groups'])
    assert len(plan['required_cases'])==len(set(plan['required_cases']))==420
    assert {f'episem-{w}' for w in (360,768,1440)}|{'nojs-'+EPISEM}<=set(plan['required_cases'])
    assert plan['source_hashes']['episem_review.py']==hashlib.sha256((ROOT/'tests/episem_review.py').read_bytes()).hexdigest()
    report={'preflight':plan,'browser':'EXECUTED','execution_completed':True,'cases':[{'name':n,'status':'PASS'} for n in plan['required_cases']], 'events':[],'action_checks':[{'slug':s,'width':w,'status':'CONFIRMED: unit fixture only'} for s,w in plan['semantic_groups']]}
    assert not automatic_errors(report,plan)
    report['cases']=[c for c in report['cases'] if c['name']!='episem-768'];assert automatic_errors(report,plan)
    report['cases']=[{'name':n,'status':'PASS'} for n in plan['required_cases']]
    report['action_checks']=[c for c in report['action_checks'] if c['slug']!=EPISEM];assert automatic_errors(report,plan)
