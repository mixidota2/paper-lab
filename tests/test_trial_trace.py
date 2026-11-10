"""New Lab registration, packaged executable and independent display check."""
from pathlib import Path
import hashlib,json,subprocess,shutil
from html.parser import HTMLParser
from paper_lab.build import build
from catalog_expectations import assert_catalog
from prose_preservation import revised_hash
ROOT=Path(__file__).resolve().parents[1];SLUG='trial-by-trace-evidence-boundaries';P=ROOT/'papers'/SLUG

def test_existing_catalog_sources_and_new_plan(tmp_path):
    baseline=json.loads((ROOT/'tests/trial_trace_baseline.json').read_text())
    assert baseline['base']=='d97532ffce0461af70347f8380da1b2a4466b22a'
    for path,digest in baseline['sources'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==revised_hash(ROOT,path,digest),path
    assert len(baseline['ids'])==110
    assert_catalog([*baseline['ids'],SLUG,'query-prefix-reuse','retail-forecast-decision-grain','series-wise-validation'])
    from review_103 import preflight
    site=tmp_path/'site';build(root=ROOT,site_dir=site);plan=preflight(site)
    added=[f'load-{slug}-{w}' for slug in (SLUG,'query-prefix-reuse','retail-forecast-decision-grain','series-wise-validation') for w in (360,768,1440)]
    assert len(plan['required_cases'])==438
    assert set(plan['required_cases'])==set(baseline['cases'])|set(added)
    assert [x for x in plan['required_cases'] if x not in added]==baseline['cases']
    for name in ('run.py','model.js','ui.js','test.cjs','results.json'):
        assert (site/'downloads'/SLUG/name).read_bytes()==(P/name).read_bytes()
    # Real distributed entrypoint; execution occurs only in a temporary copy.
    out=tmp_path/'package';shutil.copytree(site/'downloads'/SLUG,out)
    subprocess.run(['uv','run','--no-project','python','run.py'],cwd=out,check=True)
    assert json.loads((out/'results.json').read_text())==json.loads((P/'results.json').read_text())

def test_scoped_widget_initial_output_and_reset(tmp_path):
    from paper_lab.trial_trace import widget
    html=widget(P)
    class Script(HTMLParser):
        def __init__(self):super().__init__();self.active=False;self.code='';self.ids=[]
        def handle_starttag(self,t,a):
            a=dict(a)
            if 'id' in a:self.ids.append(a['id'])
            if t=='script':self.active=True
        def handle_endtag(self,t):
            if t=='script':self.active=False
        def handle_data(self,s):
            if self.active:self.code+=s
    p=Script();p.feed(html);assert len(p.ids)==len(set(p.ids));assert all(x.startswith('tt-') for x in p.ids)
    script="""const assert=require('node:assert/strict'),vm=require('node:vm');const nodes={};for(const k of ['a','h','g','b','q','reset','out'])nodes['tt-'+k]={value:k==='a'?'1':'0',checked:k==='g',events:{},addEventListener(e,f){this.events[e]=f;}};let ctx={document:{getElementById:id=>nodes[id]}};vm.createContext(ctx);vm.runInContext(CODE,ctx);assert(nodes['tt-out'].textContent.includes('75点'));assert.equal(ctx.evaluate,undefined);nodes['tt-a'].value='0';nodes['tt-a'].events.change();assert(nodes['tt-out'].textContent.includes('50点'));nodes['tt-reset'].events.click();assert(nodes['tt-out'].textContent.includes('75点'));""".replace('CODE',json.dumps(p.code))
    runner=tmp_path/'ui.cjs';runner.write_text(script);subprocess.run(['node',str(runner)],check=True)
