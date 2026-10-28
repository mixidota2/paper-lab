"""Preparation checks only: this module never launches a browser."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest
from paper_lab.build import build

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('review_103', ROOT/'tests/review_103.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


@pytest.fixture(scope='module')
def site(tmp_path_factory):
    dst=tmp_path_factory.mktemp('review-103')/'site'
    build(root=ROOT,site_dir=dst)
    return dst


def test_all_pages_links_and_declared_targets_preflight(site):
    p=m.preflight(site)
    assert p['pages']==108 and p['local_targets']>500
    assert len(p['planned_detailed_pages'])==32
    assert m.WRAPPED in p['planned_detailed_pages']
    assert p['browser']=='NOT TESTED'
    assert m.EXPLORERS==['vn2-stockout-catboost','whole-foods-shelf','contextual-deconvolution']
    assert set(m.SHELF)<=set(p['planned_detailed_pages'])


def test_cli_requires_explicit_mode_and_preserves_evidence(site,tmp_path):
    script=ROOT/'tests/review_103.py'
    help_result=subprocess.run([sys.executable,str(script),'--help'],capture_output=True,text=True)
    assert help_result.returncode==0 and '--preflight' in help_result.stdout
    no_mode=subprocess.run([sys.executable,str(script),'--site',str(site),'--out',str(tmp_path/'missing-mode')],capture_output=True)
    assert no_mode.returncode==2
    out=tmp_path/'check'
    result=subprocess.run([sys.executable,str(script),'--preflight','--site',str(site),'--out',str(out)],capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    before=(out/'preflight.json').read_bytes()
    again=subprocess.run([sys.executable,str(script),'--preflight','--site',str(site),'--out',str(out)],capture_output=True)
    assert again.returncode!=0 and (out/'preflight.json').read_bytes()==before


def test_missing_asset_rejected_before_runtime(site):
    asset=site/'assets/interactives.js'
    original=asset.read_bytes()
    try:
        asset.unlink()
        with pytest.raises(AssertionError,match='missing'):m.preflight(site)
    finally:asset.write_bytes(original)


def test_run_gate_refuses_non_macos_without_calling_runtime(site,tmp_path,monkeypatch):
    monkeypatch.setattr(sys,'argv',['review_103','--run','--site',str(site),'--out',str(tmp_path/'not-macos')])
    monkeypatch.setattr(m.platform,'system',lambda:'Linux')
    def forbidden(*args):raise RuntimeError('Runtime must not be called')
    monkeypatch.setattr(m,'runtime',forbidden)
    with pytest.raises(SystemExit) as stopped:m.main()
    assert stopped.value.code==2
    report=json.loads((tmp_path/'not-macos/report.json').read_text())
    assert report['status']=='STOPPED' and report['browser']=='NOT STARTED'
    assert (tmp_path/'not-macos/stopped.json').exists()


def test_existing_protected_launcher_is_unchanged():
    current=(ROOT/'tests/macos_chrome_cdp.py').read_bytes()
    baseline=subprocess.check_output(['git','show','92b23c658f26ea3d92ea431cd1b576967dd177ce:tests/macos_chrome_cdp.py'],cwd=ROOT)
    assert current==baseline
    assert 'chromium.launch(' not in (ROOT/'tests/review_103.py').read_text()


def test_reference_inspection_outside_outer_sync_context():
    import ast
    tree=ast.parse((ROOT/'tests/review_103.py').read_text())
    calls=[]
    def visit(node,inside_sync=False):
        if isinstance(node,ast.With):
            inside_sync=inside_sync or any(isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=='sync_playwright' for item in node.items for x in ast.walk(item.context_expr))
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and isinstance(node.func.value,ast.Name) and node.func.value.id=='reference_browser' and node.func.attr=='inspect':
            calls.append(inside_sync)
        for child in ast.iter_child_nodes(node):visit(child,inside_sync)
    visit(tree)
    assert calls==[False]


@pytest.mark.parametrize('points',['48,160 268,116','48,160 268,116 488,72 708,28','48,160 268,999 488,72'])
def test_series_rejects_missing_extra_or_wrong_points(points):
    with pytest.raises(AssertionError):m.assert_polyline(points,[1,2,3],3,0,4)


def test_series_complete_coordinates():
    assert len(m.assert_polyline('48,160 268,116 488,72',[1,2,3],3,0,4))==3


def test_completed_failure_keeps_evidence_without_stopped(tmp_path):
    e=m.RunEvidence(tmp_path,{})
    class Page:
        url='http://127.0.0.1/example'
        def is_closed(self):return False
        def screenshot(self,**kwargs):raise RuntimeError('injected capture failure')
    e.page=Page()
    def fail():raise AssertionError('injected mismatch')
    e.case('mismatch',fail)
    e.case('later-case',lambda:None)
    r=e.finalize(True)
    assert r['status']=='FAIL' and r['browser']=='EXECUTED'
    assert [x['status'] for x in r['cases']]==['FAIL','PASS']
    assert r['cases'][0]['case']=='mismatch' and r['cases'][0]['page'].endswith('/example')
    assert r['screen_records'][0]['capture_error']['message']=='injected capture failure'
    assert (tmp_path/'index.html').exists() and not (tmp_path/'stopped.json').exists()


@pytest.mark.parametrize('protection',[False,True])
def test_runtime_interruption_restores_environment_and_finalizes(tmp_path,monkeypatch,protection):
    monkeypatch.setenv('LAB_CDP_URL','previous')
    monkeypatch.delenv('LAB_CHROME_PID',raising=False)
    def interrupted(site,out,plan,e):
        import os
        os.environ['LAB_CDP_URL']='temporary';os.environ['LAB_CHROME_PID']='123'
        e.report['browser']='STARTED';e.report['phase']='inspection'
        def fail():
            if protection:raise m.ProtectionStop('guard rejected')
            raise KeyboardInterrupt('interrupted')
        e.case('active-case',fail)
    monkeypatch.setattr(m,'_runtime',interrupted)
    r=m.runtime(None,tmp_path,{})
    assert r['status']=='STOPPED' and r['browser']=='INTERRUPTED'
    assert m.os.environ['LAB_CDP_URL']=='previous' and 'LAB_CHROME_PID' not in m.os.environ
    assert (tmp_path/'index.html').exists() and (tmp_path/'stopped.json').exists()
    if protection:
        assert r['interruption']['case']=='active-case'
        assert r['screen_records'][0]['reason'].startswith('Protection not confirmed')
    else:
        assert r['interruption']['type']=='KeyboardInterrupt'
        assert r['interruption']['case']=='active-case'


def test_events_and_uncovered_actions_change_status(tmp_path):
    e=m.RunEvidence(tmp_path,{})
    e.report['action_checks'].append({'status':'NOT TESTED: unknown output'})
    assert e.finalize(True)['status']=='FAIL'  # Unverified semantic output is mandatory failure.
    e.event('requestfailed','injected network error')
    assert e.finalize(True)['status']=='FAIL'


def test_full_build_has_no_private_absolute_paths(site):
    for p in site.rglob('*'):
        if p.is_file():
            data=p.read_bytes()
            for prefix in (b'/workspace/',b'/Users/',b'/home/'):
                assert prefix not in data,str(p.relative_to(site))
    for name in ('gatesid-coldstart-ranking','agentx-kuaishou','coral-meta-config-harness',
                 'flashtrie-gpu-beam','static-constrained-gr','genpage-netflix-homepage','unirec-chain-of-attribute'):
        original=(ROOT/'papers'/name/'mapping.md').read_bytes()
        matches=list(site.rglob(f'{name}/mapping.md'))
        assert len(matches)==1 and matches[0].read_bytes()==original


def test_guide_navigation_counts_and_canonical_lab_links(site):
    index=m.Document((site/'index.html').read_text())
    assert 'guides/index.html' in index.links
    assert len([a for t,a in index.tags if 'data-paper' in a])==108
    listing=m.Document((site/'guides/index.html').read_text())
    assert 'shelf-decisions.html' in listing.links
    guide=(site/'guides/shelf-decisions.html').read_text()
    links=m.Document(guide).links
    assert '108件のLab ／ 1件のテーマガイド' in guide
    assert 'オンライン公開2023年' in guide and 'オンライン公開2025年' in guide
    assert '追加日は2026年10月16日' in guide
    for slug in m.SHELF:
        assert f'../papers/{slug}.html' in links
        assert '../guides/shelf-decisions.html' in m.Document((site/'papers'/f'{slug}.html').read_text()).links
    p=m.preflight(site)
    assert p['theme_guides']==1 and p['guide_pages']==2
    assert {'index.html','guides/index.html','guides/shelf-decisions.html'} <= set(p['local_paths'])


def test_forgetting_actual_script_initial_and_noninitial_display():
    import re
    from paper_lab.forgetting05 import widget
    data=json.loads((ROOT/'papers/agent-reasoning-forgetting-externalized-state/results.json').read_text())
    html=widget(data)
    script=re.findall(r'<script>(.*?)</script>',html,re.S)[0]
    # Execute the real inline widget with a minimal DOM in Node, without a browser.
    harness=r'''
const vm=require('node:vm'), fs=require('node:fs');
const input=JSON.parse(fs.readFileSync(0,'utf8')), nodes={};
for(const key of ['data-forget','data-case','data-trace','data-summary','data-risk','data-scatter','data-e','data-k','data-bound']){
 nodes[key]={value:'',textContent:'',innerHTML:'',handlers:{},addEventListener(t,f){this.handlers[t]=f}};
}
nodes['data-forget'].textContent=JSON.stringify(input.data);
nodes['data-case'].value=Object.keys(input.data.cases)[0];
nodes['data-e'].value='0.02';nodes['data-k'].value='30';
const root={querySelector(s){return nodes[s.slice(1,-1)]}};
vm.runInNewContext(input.script,{document:{currentScript:{parentElement:root}}});
const results=[nodes['data-bound'].textContent];
for(const [e,k] of [[0.035,17],[0,1],[0.1,100]]){
 nodes['data-e'].value=String(e);nodes['data-k'].value=String(k);
 nodes['data-e'].handlers.input();results.push(nodes['data-bound'].textContent);
}
process.stdout.write(JSON.stringify(results));
'''
    actual=json.loads(subprocess.check_output(['node','-e',harness],input=json.dumps({'data':data,'script':script}),text=True))
    expected=[m.forgetting_bound_text(e,k) for e,k in [(0.02,30),(0.035,17),(0,1),(0.1,100)]]
    assert actual==expected
    assert 'ε=0.020' in actual[0] and actual[0].endswith('0.600')
    assert 'ε=0.035' in actual[1] and actual[1].endswith('0.595')


def test_required_case_manifest_and_regression_sets(site):
    plan=m.preflight(site)
    names=plan['required_cases']
    assert len(names)==len(set(names))
    assert sum(n.startswith('load-') and n.endswith('-768') for n in names)==108
    assert len(m.NOJS)==9 and len(m.LEGACY_SVG)==6
    assert all('nojs-'+s in names for s in m.NOJS)
    assert all('svg-bounds-'+s in names for s in m.LEGACY_SVG)
    assert all(f'library-search-{w}' in names for w in [360,768,1440])
    assert 'reference-independent-metrics-curves-save-reload' in names
    assert {'wrapped-360','wrapped-1440','nojs-'+m.WRAPPED} <= set(names)
    assert all([m.WRAPPED,w] in plan['semantic_groups'] for w in [360,1440])


@pytest.mark.parametrize('mutation',['none','missing','duplicate','not_tested','missing_actions','incomplete','event','failed','missing_report','stale'])
def test_report_gate_cli_fail_closed(site,tmp_path,mutation):
    plan=m.preflight(site)
    report={'preflight':plan,'browser':'EXECUTED','execution_completed':True,'cases':[{'name':n,'status':'PASS'} for n in plan['required_cases']],
            'events':[],'action_checks':[{'slug':s,'width':w,'status':'CONFIRMED: injected local fixture'} for s,w in plan['semantic_groups']],
            'external_status':'PARTIAL / unconfirmed URLs remain','manual_screenshot_review':'NOT TESTED'}
    if mutation=='stale':report['preflight']={**plan,'source_hashes':{}}
    if mutation=='missing':report['cases'].pop()
    if mutation=='duplicate':report['cases'].append(report['cases'][0])
    if mutation=='not_tested':report['action_checks'][0]['status']='NOT TESTED'
    if mutation=='missing_actions':report['action_checks']=[]
    if mutation=='incomplete':report['execution_completed']=False
    if mutation=='event':report['events']=[{'kind':'pageerror'}]
    if mutation=='failed':report['cases'][0]['status']='FAIL'
    source=tmp_path/'report.json';output=tmp_path/'gate.json'
    if mutation!='missing_report':source.write_text(json.dumps(report))
    result=subprocess.run([sys.executable,str(ROOT/'tests/review_103_report.py'),'--site',str(site),'--report',str(source),'--out',str(output)],capture_output=True,text=True)
    outcome=json.loads(output.read_text())
    assert result.returncode==(0 if mutation=='none' else 1)
    assert outcome['automatic_status']==('PASS' if mutation=='none' else 'FAIL')
    assert outcome['publication_decision']=='PENDING'


def test_external_deadline_reaps_child_and_preserves_partial_results(tmp_path):
    import time
    from review_103_external import bounded_check
    output=tmp_path/'external';output.mkdir()
    completed=output/'completed.jsonl'
    # A hanging non-browser worker with a flushed first result; no network request.
    script="from pathlib import Path;import time;Path("+repr(str(completed))+").write_text("+repr(json.dumps({'url':'https://one.invalid','result':'CONFIRMED HTTP reachability only'})+'\n')+");time.sleep(60)"
    start=time.monotonic()
    rows,summary=bounded_check(['https://one.invalid','https://two.invalid'],output,.5,[sys.executable,'-c',script])
    assert time.monotonic()-start<3
    assert summary['timed_out'] and summary['worker_exit']<0 and summary['completed']==1
    assert rows[0]['result'].startswith('CONFIRMED')
    assert rows[1]['result']=='NOT CONFIRMED' and 'budget' in rows[1]['reason']


def test_nojs_does_not_use_timer_wait_and_external_follows_chrome_cleanup():
    import ast
    tree=ast.parse((ROOT/'tests/review_103.py').read_text())
    fallback=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='fallback')
    assert all(not (isinstance(n,ast.Attribute) and n.attr=='wait_for_function') for n in ast.walk(fallback))
    runtime=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_runtime')
    launch=next(n for n in runtime.body if isinstance(n,ast.With) and 'chrome_process' in ast.unparse(n.items[0].context_expr))
    assert 'bounded_check(' not in ast.unparse(launch)
    assert 'reference_browser.inspect' in ast.unparse(launch)
    assert 'bounded_check(' in ast.unparse(runtime)


def test_no_external_budget_starts_no_worker(tmp_path,monkeypatch):
    import review_103_external as external
    def forbidden(*args,**kwargs):raise AssertionError('No subprocess allowed when budget is exhausted')
    monkeypatch.setattr(external.subprocess,'Popen',forbidden)
    rows,summary=external.bounded_check(['https://one.invalid'],tmp_path,0)
    assert summary['worker_started'] is False and rows[0]['result']=='NOT CONFIRMED'
