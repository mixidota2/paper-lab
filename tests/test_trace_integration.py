"""Offline JS/semantic/catalog checks; these are not browser acceptance tests."""
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import pytest
from catalog_expectations import BASE, EXISTING, TRACE, EPISEM, assert_catalog
from trace_review import assert_trace_frame

ROOT=Path(__file__).resolve().parents[1]
LAB=ROOT/'papers'/TRACE


def test_current_main_exact_catalog_preserved():
    assert BASE['base']=='38e98ef18dde9a88c14cd12a79827084187eff6c'
    assert len(EXISTING)==104
    assert_catalog([*EXISTING,TRACE,EPISEM])
    with pytest.raises(AssertionError):assert_catalog([*EXISTING,'wrong-id'])
    with pytest.raises(AssertionError):assert_catalog([*EXISTING,TRACE,EPISEM,TRACE])


def test_actual_inline_script_all_states_and_reset():
    html=(LAB/'experiment.md').read_text()
    scripts=re.findall(r'<script>(.*?)</script>',html,re.S)
    assert len(scripts)==1
    harness=r'''
const vm=require('node:vm'),fs=require('node:fs');
const script=fs.readFileSync(0,'utf8'),nodes={};
for(const [id,value] of [['agent','0'],['alias','1'],['normalize','0'],['reset',''],['output','']])
 nodes['trace-'+id]={value,innerHTML:'',handlers:{},addEventListener(t,f){this.handlers[t]=f}};
vm.runInNewContext(script,{document:{getElementById:id=>nodes[id]}});
const frames=[];
for(let a=0;a<3;a++)for(let b=0;b<2;b++)for(let n=0;n<2;n++){
 for(const [key,v] of [['agent',a],['alias',b],['normalize',n]]){
  nodes['trace-'+key].value=String(v);nodes['trace-'+key].handlers.change();
 }
 frames.push(nodes['trace-output'].innerHTML);
}
nodes['trace-reset'].handlers.click();
process.stdout.write(JSON.stringify({frames,reset:nodes['trace-output'].innerHTML,values:['agent','alias','normalize'].map(k=>String(nodes['trace-'+k].value))}));
'''
    actual=json.loads(subprocess.check_output(['node','-e',harness],input=scripts[0],text=True))
    data=json.loads((LAB/'results.json').read_text())
    assert len(actual['frames'])==len(data['synthetic'])==12
    for html,case in zip(actual['frames'],data['synthetic'],strict=True):assert_trace_frame(html,case)
    assert actual['values']==['0','1','0']
    assert_trace_frame(actual['reset'],data['synthetic'][2])
    # Corruption must not pass merely because other labels still match.
    for wrong in [actual['reset'].replace('width:50.0%','width:75.0%'),
                  actual['reset'].replace(data['synthetic'][2]['changed']['state_hash'],'0'*64),
                  actual['reset'].replace('replace_count','wrong_operation')]:
        with pytest.raises(AssertionError):assert_trace_frame(wrong,data['synthetic'][2])


def test_trace_is_mandatory_and_missing_case_or_semantics_fails(tmp_path):
    import review_103 as review
    from review_103_report import automatic_errors
    from paper_lab.build import build
    site=tmp_path/'site';build(root=ROOT,site_dir=site)
    plan=review.preflight(site)
    names=plan['required_cases']
    baseline=json.loads((ROOT/'tests/main_104_review_cases.json').read_text())
    assert baseline['base']==BASE['base']
    assert len(baseline['required_cases'])==391
    assert set(baseline['required_cases']) <= set(names)
    assert all(group in plan['semantic_groups'] for group in baseline['semantic_groups'])
    assert len(names)==406
    assert {f'trace-{w}' for w in (360,390,768,1440)}|{'nojs-'+TRACE} <= set(names)
    assert all([TRACE,w] in plan['semantic_groups'] for w in (360,390,768,1440))
    report={'preflight':plan,'browser':'EXECUTED','execution_completed':True,'cases':[{'name':n,'status':'PASS'} for n in names],
            'events':[],'action_checks':[{'slug':s,'width':w,'status':'CONFIRMED: offline fixture'} for s,w in plan['semantic_groups']]}
    assert not automatic_errors(report,plan)
    report['cases']=[c for c in report['cases'] if c['name']!='trace-390']
    assert automatic_errors(report,plan)
    report['cases']=[{'name':n,'status':'PASS'} for n in names]
    report['action_checks']=[c for c in report['action_checks'] if c['slug']!=TRACE]
    assert automatic_errors(report,plan)
