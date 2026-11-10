"""Actual source, finite oracles and synthetic DOM; not real-browser acceptance."""
import importlib.util
import itertools
import json
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import pytest

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'papers/query-prefix-reuse'
spec=importlib.util.spec_from_file_location('reuse_toy',SOURCE/'run.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


def test_published_arithmetic_and_no_quantile_projection():
    r=m.checks()
    assert r['prepared_stages_ms']==pytest.approx(71.45)
    assert r['refresh_gpu_hours']==pytest.approx(22/9)
    assert r['saving_ms']==pytest.approx(45.55) and r['compute_hits']==2
    assert r['positive_depth_within_prepared_percent']==pytest.approx(83.16336913510457)
    for row in m.PRESETS:
        v=m.projection(row['p']/100)
        assert round(v['mean_ms'],2)==row['ms']
        if row['quality']!='measured partition': assert round(v['hr_percent'],2)==row['hr']
        assert not any('95' in k or '99' in k or 'rpm' in k for k in v)
    assert m.PRESETS[2]['q']==m.PRESETS[3]['q'] and m.PRESETS[2]['p']==m.PRESETS[3]['p']
    assert m.PRESETS[2]['hr']==82.38 and m.projection(.3687)['hr_percent']==pytest.approx(83.402121)
    assert m.projection(0)['mean_ms']==117 and m.projection(1)['mean_ms']==71.45
    assert m.TABLE1[2]['hr']>m.TABLE1[1]['hr'] and m.TABLE1[2]['recall']<m.TABLE1[1]['recall']
    assert json.loads((SOURCE/'results.json').read_text())==r


def test_reachability_route_and_admission_invariants():
    deep=m.toy(True,3,'wide','right',8)
    assert deep['reachable']==['0000','0001','1000','1001'] and not deep['target_reachable']
    root=m.toy(True,0,'wide','right',8); cold=m.toy(False,0,'wide','right',8)
    assert root['route']=='prepared-root' and cold['route']=='cold-e2e'
    assert root['target_returned'] and not cold['async_prepare']
    assert m.toy(False,3)['async_prepare']
    for prepared,depth,query,history in itertools.product([True,False],range(4),['wide','narrow'],['left','right']):
        rows=[m.toy(prepared,depth,query,history,b) for b in range(9)]
        assert len({r['l4_scored'] for r in rows})==1
        for b,r in enumerate(rows):
            assert r['waits_for_planner'] is False
            assert len(r['ranking'])==2*len(r['admitted'])
            assert len(r['admitted'])==(min(b,len(r['branches'])) if prepared else len(r['branches']))
            assert len(r['reachable'])==r['layer_nodes'][3]==r['l4_scored']
            assert all(v['sid'] in r['reachable'] for v in r['ranking'])
            assert all(v['score']<=10 for v in r['ranking'])
        if prepared: assert rows[0]['ranking']==[]


def test_python_js_exact_toy_and_projection_common_domain(tmp_path):
    args=list(itertools.product([True,False],range(4),['wide','narrow'],['left','right'],range(9)))
    ps=[0,.0001,.2097,.3687,.584,.842,.9999,1]
    code="const m=require("+json.dumps(str(SOURCE/'model.js'))+");console.log(JSON.stringify({toy:"+json.dumps(args)+".map(a=>m.toy(...a)),p:"+json.dumps(ps)+".map(m.projection),table:m.table1,presets:m.presets}));"
    got=json.loads(subprocess.check_output(['node','-e',code],text=True))
    assert got['toy']==[m.toy(*a) for a in args]
    assert got['p']==[m.projection(p) for p in ps]
    assert got['table']==m.TABLE1 and got['presets']==m.PRESETS


@pytest.mark.parametrize('x',[None,True,'0',[],{},-1,1.01,float('nan'),float('inf'),1e308])
def test_projection_invalid(x):
    with pytest.raises(ValueError): m.projection(x)


def test_invalid_arguments_and_js_sparse_arrays_are_rejected():
    bad=[None,True,'1',[],{},-1,.5,9,float('nan'),float('inf'),1e308]
    for x in bad:
        with pytest.raises(ValueError): m.toy(depth=x)
        with pytest.raises(ValueError): m.toy(budget=x)
    for x in [0,1,None,[],{},'yes']:
        with pytest.raises(ValueError): m.toy(prepared=x)
    for x in [None,[],{},'other',1]:
        with pytest.raises(ValueError): m.toy(query=x)
        with pytest.raises(ValueError): m.toy(history=x)
    code="""const m=require(MODEL),assert=require('node:assert/strict');
for(const x of [null,true,'0',[],{},-1,1.01,NaN,Infinity,1e308,Array(3)])assert.throws(()=>m.projection(x));
for(const x of [null,true,'1',[],{},-1,.5,9,NaN,Infinity,1e308,Array(3)]){
 assert.throws(()=>m.toy(true,x));assert.throws(()=>m.toy(true,1,'wide','left',x));}
for(const x of [0,1,null,[],{},'yes'])assert.throws(()=>m.toy(x));
for(const x of [null,[],{},'other',1]){assert.throws(()=>m.toy(true,1,x));assert.throws(()=>m.toy(true,1,'wide',x));}
assert.equal(JSON.stringify(m.toy(true,1,'wide','left',0).ranking),'[]');
""".replace('MODEL',json.dumps(str(SOURCE/'model.js')))
    subprocess.run(['node','-e',code],check=True)


class Controls(HTMLParser):
    def __init__(self,text):
        super().__init__();self.nodes={};self.select=None;self.option=None;self.current=None;self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:
            self.current=a['id'];self.nodes[self.current]=dict(value=a.get('value',''),disabled='disabled' in a,textContent='',innerHTML='')
        if tag=='select': self.select=a['id'];self.first=True
        if tag=='option': self.option=[a,'']
    def handle_data(self,text):
        if self.option is not None:self.option[1]+=text
        if self.current:self.nodes[self.current]['textContent']+=text
    def handle_endtag(self,tag):
        if tag=='option':
            a,text=self.option
            if self.first or 'selected' in a:self.nodes[self.select]['value']=a.get('value',text)
            self.first=False;self.option=None
        if tag=='select':self.select=None
        if tag in ('p','pre','ol','tbody','select','button'):self.current=None


def test_actual_ui_static_controls_events_json_invalid_reset_failure(tmp_path):
    html=(SOURCE/'interactive.html').read_text();nodes=Controls(html).nodes
    ids=['prepared','depth','query','history','budget','preset','p','metric','reset','download']
    assert all(nodes['rg-'+k]['disabled'] for k in ids)
    assert '<noscript>' in html and 'overflow-x:auto' in html and 'min-width:520px' in html
    code=r"""const assert=require('node:assert/strict'),fs=require('fs'),vm=require('vm');
const fixture=FIXTURE, blobs=[],anchors=[],revoked=[];
function setup(fail){const nodes=structuredClone(fixture);for(const [id,n] of Object.entries(nodes)){n.events={};n.addEventListener=(ev,fn)=>{if(fail===id)throw Error('registration');n.events[ev]=fn;};}
const ctx={document:{getElementById:id=>nodes[id],createElement:()=>({click(){anchors.push({...this});}})},Blob:class{constructor(a,o){this.text=a.join('');this.type=o.type;}},URL:{createObjectURL:b=>{blobs.push(b);return 'blob:local';},revokeObjectURL:u=>revoked.push(u)}};
vm.createContext(ctx);return {ctx,nodes};}
const model=fs.readFileSync(MODEL,'utf8'),ui=fs.readFileSync(UI,'utf8');
const {ctx,nodes}=setup(),get=k=>nodes['rg-'+k];vm.runInContext(model+'\n'+ui,ctx);
const m=require(MODEL);
for(const k of ['route','rank','budget-result','mix','preset-note','metric-label'])assert.equal(get(k).textContent,fixture['rg-'+k].textContent,k);
function fire(k,v,e='change'){get(k).value=String(v);get(k).events[e]();}
function save(){const n=blobs.length;get('download').events.click();assert.equal(blobs.length,n+1);const v=JSON.parse(blobs.at(-1).text);assert.equal(blobs.at(-1).type,'application/json');assert.equal(anchors.at(-1).download,'query-prefix-reuse-synthetic.json');assert.equal(revoked.at(-1),'blob:local');
assert.deepEqual(v.toy,m.toy(v.toy.input.prepared,v.toy.input.depth,v.toy.input.query,v.toy.input.history,v.toy.input.budget));assert.deepEqual(v.projection,m.projection(v.projection.p));assert.equal(v.synthetic,true);assert.equal(v.model_version,m.version);assert(Object.values(v.projection).every(x=>typeof x!=='number'||Number.isFinite(x)));assert(!JSON.stringify(v.toy).includes('null')); return v;}
save();for(const p of ['yes','no'])for(const d of [0,1,3])for(const b of [0,4,8]){fire('prepared',p);fire('depth',d);fire('history','right');fire('query','narrow');fire('budget',b,'input');save();}
for(let k=0;k<6;k++){fire('preset',k);assert.equal(get('p').value,String(m.presets[k].p));assert.equal(save().preset.name,m.presets[k].name);}
for(const p of [0,36.87,100]){fire('p',p,'input');assert.equal(save().preset,null);}
fire('metric','recall');assert(get('table-body').innerHTML.includes('50.96%'));assert.equal(save().metric,'recall');
for(const [k,v] of [['budget',-1],['depth',''],['p',101],['query','bad']]){const before=get('rank').textContent;fire(k,v);assert(get('error').textContent.includes('入力エラー'));assert(get('download').disabled);const n=blobs.length;get('download').events.click();assert.equal(blobs.length,n);assert.equal(get('rank').textContent,before);get('reset').events.click();}
for(let i=0;i<3;i++){get('reset').events.click();assert.deepEqual(save().toy,m.toy());assert.equal(get('metric').value,'hr');assert.equal(get('preset').value,'0');}
for(const id of ['rg-prepared','rg-depth','rg-query','rg-history','rg-budget','rg-preset','rg-p','rg-metric','rg-reset','rg-download']){const f=setup(id);assert.throws(()=>vm.runInContext(model+'\n'+ui,f.ctx));assert(f.nodes['rg-prepared'].disabled);assert.equal(f.nodes['rg-rank'].textContent,fixture['rg-rank'].textContent);}
const missing=setup();vm.runInContext(ui,missing.ctx);assert(missing.nodes['rg-error'].textContent.includes('入力エラー'));assert(missing.nodes['rg-prepared'].disabled);
assert.equal(blobs.length,32);
console.log('synthetic DOM saves='+blobs.length+'; no native browser or viewport test');
""".replace('FIXTURE',json.dumps(nodes,ensure_ascii=False)).replace('MODEL',json.dumps(str(SOURCE/'model.js'))).replace('UI',json.dumps(str(SOURCE/'interactive.js')))
    runner=tmp_path/'ui.cjs';runner.write_text(code);subprocess.run(['node',str(runner)],check=True)


def test_renderer_links_mapping_and_source_boundaries():
    from paper_lab.reusegr import widget
    html=widget(SOURCE)
    assert 'const ReuseGR=' in html and 'rg-tree' in html
    assert 'P95/P99やオンライン売上効果は補間しません' in html
    text=(SOURCE/'method.md').read_text()
    for phrase in ['頻度表','採点した後','別の0.5B','原著ではd=3','query-macro']:
        assert phrase in text
    assert 'logged query-match mask' in (SOURCE/'README.md').read_text()
