"""Arithmetic and source-DOM tests, not author replication or real browser tests."""
from pathlib import Path
import importlib.util
import json
import subprocess
import pytest

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'papers/retail-forecast-decision-grain'
spec=importlib.util.spec_from_file_location('grain',P/'run.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def test_exact_examples_and_regeneration():
    r=m.results()
    assert r==json.loads((P/'results.json').read_text())
    assert r['zero_sales']['A']=={'old':500000000.05,'corrected':.11}
    assert r['zero_sales']['B']=={'old':.1,'corrected':.2}
    assert r['window_order']['A']=={'mean':.5,'pooled':1/101}
    assert r['window_order']['B']=={'mean':.05,'pooled':10/101}
    assert [m.loss(8,10,r) for r in [.5,.8,.95]]==[2,8,38]
    assert m.metrics([50,50],[60,40],[1,1],[1,1],[0,0])['corrected']==0
    assert m.metrics([50,50],[60,40],[1,1],[1,1],[0,1])['corrected']==.2
    assert m.windows([0,1],[1,1])=={'mean':None,'pooled':1}
    assert m.metrics([0],[1],[1],[1],[0])['corrected'] is None
    with pytest.raises(ValueError):m.loss(-1,2,.8)
    with pytest.raises(ValueError):m.loss(1,2,1)


def test_actual_controls_and_python_js_equivalence():
    cases=[{'a':[100,y],'f':[90,f],'p':[1,1],'w':[1,1],'g':g,
            'expected':m.metrics([100,y],[90,f],[1,1],[1,1],g)}
           for y in [0,1,100] for f in [0,1,10] for g in [[0,1],[0,0]]]
    script=r'''
const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
const dir=process.argv[1],cases=JSON.parse(process.argv[2]);
const M=require(dir+'/model.js');
for(const c of cases){const r=M.metrics(c.a,c.f,c.p,c.w,c.g);for(const k of ['old','corrected'])assert(Math.abs(r[k]-c.expected[k])<=1e-12*Math.max(1,Math.abs(c.expected[k])));}
const html=fs.readFileSync(dir+'/interactive.html','utf8'),nodes={};
for(const tag of html.matchAll(/<[^>]+\bid="([^"]+)"[^>]*>/g)){const s=tag[0];nodes[tag[1]]={value:s.match(/value="([^"]*)"/)?.[1]||'',disabled:/\bdisabled\b/.test(s),events:{},textContent:'',innerHTML:'',addEventListener(e,f){this.events[e]=f}};}
for(const s of html.matchAll(/<select[^>]*id="([^"]+)"[^>]*>([\s\S]*?)<\/select>/g)){const opts=[...s[2].matchAll(/<option([^>]*)value="([^"]+)"([^>]*)>/g)];nodes[s[1]].value=(opts.find(o=>/selected/.test(o[1]+o[3]))||opts[0])[2];}
const ctx=vm.createContext({document:{getElementById:id=>nodes[id]},GrainModel:M});
assert(html.includes('単期発注損失=8'));assert(html.includes('<noscript>'));
for(const id of ['y2','a2','group','window','q','y','r','reset'])assert(nodes['grain-'+id].disabled);
vm.runInContext(fs.readFileSync(dir+'/interactive.js','utf8'),ctx);
const n=id=>nodes['grain-'+id],event=(id,v)=>{n(id).value=String(v);n(id).events.input();};
const initial=n('out').textContent;assert(initial.includes('単期発注損失=8'));
for(const id of ['y2','a2','group','window','q','y','r','reset'])assert.equal(n(id).disabled,false);
// Three event cycles; synthetic DOM has no viewport layout.
for(let repeat=0;repeat<3;repeat++){event('group','together');event('y2',100);event('a2',20);assert(n('out').textContent.includes('訂正式'));for(const r of [.5,.8,.95]){event('r',r);assert(n('out').textContent.includes('単期発注損失='+Number(M.loss(8,10,r).toPrecision(8))));}n('reset').events.click();assert.equal(n('out').textContent,initial);}
for(const v of ['',-1,10001,'NaN']){event('q',v);assert(n('error').textContent);assert.equal(n('bars').innerHTML,'');n('reset').events.click();assert.equal(n('out').textContent,initial);}
event('window',0);assert(n('out').textContent.includes('未定義'));
for(let i=0;i<3;i++){event('q',10);assert(n('out').textContent.includes('単期発注損失=0'));n('reset').events.click();assert.equal(n('out').textContent,initial);}
assert(html.includes('minmax(min(100%,230px),1fr)'));assert(html.includes('max-width:100%'));
'''
    subprocess.run(['node','-e',script,str(P),json.dumps(cases)],check=True)


def test_new_catalog_and_downloads(tmp_path):
    from paper_lab.build import build
    labs=build(root=ROOT,site_dir=tmp_path/'site')
    assert len(labs)==114
    page=(tmp_path/'site/papers/retail-forecast-decision-grain.html').read_text()
    for needle in ['grain-lab','2610.25170','casrp']:
        if needle=='casrp':assert needle not in page
        else:assert needle in page
    for name in ['run.py','README.md','mapping.md','method.md','results.json','model.js','interactive.js','evidence.md']:
        assert (tmp_path/'site/downloads/retail-forecast-decision-grain'/name).read_bytes()==(P/name).read_bytes()


def test_js_vector_shape_and_nonfinite_fail_before_serialization():
    script=r'''
const assert=require('node:assert/strict'),M=require(process.argv[1]);
const good=[[1,2],[1,1],[1,1],[1,1],[0,1]];
for(let i=0;i<5;i++)for(const length of [0,1,3]){
 const xs=good.map(x=>x.slice());xs[i]=Array(length).fill(i===4?0:1);
 assert.throws(()=>M.metrics(...xs),/同じ長さ/);
}
assert.throws(()=>M.metrics([],[],[],[],[]),/同じ長さ/);
for(const args of [[[],[]],[[1,2],[1]],[[1],[1,2]],[[1],null]])assert.throws(()=>M.windows(...args),/同じ長さ/);
for(const value of [-1,NaN,Infinity,-Infinity,10001]){
 for(let i=0;i<4;i++){const xs=good.map(x=>x.slice());xs[i][0]=value;assert.throws(()=>M.metrics(...xs));}
 assert.throws(()=>M.windows([value],[1]));assert.throws(()=>M.windows([1],[value]));
 assert.throws(()=>M.loss(value,1,.8));assert.throws(()=>M.loss(1,value,.8));
}
for(const g of [undefined,NaN,Infinity,null,{}])assert.throws(()=>M.metrics([1],[1],[1],[1],[g]));
for(const r of [0,1,-1,.6,NaN,Infinity])assert.throws(()=>M.loss(1,2,r));
assert.deepEqual(M.metrics([0],[1],[1],[0],[0]),{old:null,corrected:null});
assert.deepEqual(M.windows([0],[1]),{mean:null,pooled:null});
assert.deepEqual(M.windows([0,1],[1,1]),{mean:null,pooled:1});
for(const r of [M.metrics([10000],[0],[10000],[10000],[0]),M.windows([10000],[0])])
 for(const v of Object.values(r))assert.ok(v===null||(typeof v==='number'&&Number.isFinite(v)));
assert.equal(M.loss(10000,0,.95),10000);
console.log('shape errors throw; null reserved for valid zero denominators');
'''
    subprocess.run(['node','-e',script,str(P/'model.js')],check=True)


def test_common_domain_all_three_apis_strict_null_and_finite():
    cases=[]
    for a in ([0,0],[0,1],[1,2],[10000,10000]):
        for f in ([0,0],[1,1],[10000,0]):
            for group in ([0,0],[0,1]):
                args=[a,f,[1,1],[1,1],group]
                cases.append({'api':'metrics','args':args,'expected':m.metrics(*args)})
            cases.append({'api':'windows','args':[a,f],'expected':m.windows(a,f)})
    for q in (0,1,10000):
        for y in (0,2,10000):
            for r in (.5,.8,.95):cases.append({'api':'loss','args':[q,y,r],'expected':m.loss(q,y,r)})
    script=r'''
const assert=require('node:assert/strict'),M=require(process.argv[1]),cases=JSON.parse(process.argv[2]);
function equal(actual,expected){
 if(expected===null){assert.equal(actual,null);return;}
 if(typeof expected==='object'){assert.deepEqual(Object.keys(actual),Object.keys(expected));for(const k of Object.keys(expected))equal(actual[k],expected[k]);return;}
 assert.equal(typeof actual,'number');assert.ok(Number.isFinite(actual));
 assert.ok(Math.abs(actual-expected)<=2e-14*Math.max(1,Math.abs(expected)));
}
for(const c of cases)equal(M[c.api](...c.args),c.expected);
console.log(cases.length+' common-domain cases, strict null and finite checks');
'''
    subprocess.run(['node','-e',script,str(P/'model.js'),json.dumps(cases,allow_nan=False)],check=True)


def test_python_domain_is_explicitly_broader_and_invalid_numbers_rejected():
    assert m.loss(1,2,.6)==1.5
    assert m.windows([10001],[0])=={'mean':1.,'pooled':1.}
    assert m.metrics([10001],[0],[1],[1],[0])=={'old':1.,'corrected':1.}
    for value in (-1,float('nan'),float('inf'),-float('inf')):
        for call in (lambda:m.metrics([value],[1],[1],[1],[0]),
                     lambda:m.windows([value],[1]),lambda:m.loss(value,1,.8)):
            with pytest.raises(ValueError):call()
    for r in (0,1,-1,float('nan'),float('inf')):
        with pytest.raises(ValueError):m.loss(1,2,r)
    for xs in (([],[],[],[],[]),([1,2],[1],[1,1],[1,1],[0,1])):
        with pytest.raises(ValueError):m.metrics(*xs)
    for xs in (([],[]),([1,2],[1])):
        with pytest.raises(ValueError):m.windows(*xs)


def test_csv_provenance_exact_extra_lf_and_unmatched(tmp_path):
    import hashlib
    raw=b'key,model,cost\npanel,A,1\n'
    expected=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    p=tmp_path/'data.csv'
    for data,match in [(raw,'exact'),(raw+b'\n','one_added_trailing_lf'),
                       (raw+b'\n\n','unmatched'),(raw.replace(b',1',b',2'),'unmatched')]:
        p.write_bytes(data);r=m.input_provenance(p,expected)
        assert r['match']==match and r['matches_expected_blob']==(match!='unmatched')
        assert r['bytes']==len(data) and r['sha256']==hashlib.sha256(data).hexdigest()


def test_alternate_csv_never_claims_expected_snapshot(tmp_path):
    (tmp_path/'category_cost.csv').write_text('key,model,cost,variant\n'+''.join(f'p{i},A,1,dollars\n' for i in range(8)))
    (tmp_path/'decisions.csv').write_text('key,model,cost,set,decision\n'+''.join(f'p{i},A,1,rolling,replenish_0.8\n' for i in range(8)))
    r=m.table_results(tmp_path)
    assert r['source_snapshot'] is None
    assert r['expected_source_snapshot']=='b7c182730a7744ce655fb467af36b951baca629a'
    assert r['source_verification']=='unverified_inputs'
    assert r['category']['counts']=={'A':8} and r['replenishment']['counts']=={'A':8}
    assert all(x['match']=='unmatched' for x in r['inputs'].values())


def test_numeric_range_error_is_visible_and_reset_recovers():
    """Actual renderer with a model-call fault fixture; no native browser claim."""
    script=r'''
const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict'),dir=process.argv[1];
const html=fs.readFileSync(dir+'/interactive.html','utf8'),nodes={};
for(const tag of html.matchAll(/<[^>]+\bid="([^"]+)"[^>]*>/g)){
 const s=tag[0];nodes[tag[1]]={value:s.match(/value="([^"]*)"/)?.[1]||'',events:{},textContent:'',innerHTML:'',addEventListener(e,f){this.events[e]=f;}};
}
for(const s of html.matchAll(/<select[^>]*id="([^"]+)"[^>]*>([\s\S]*?)<\/select>/g)){
 const opts=[...s[2].matchAll(/<option([^>]*)value="([^"]+)"([^>]*)>/g)];nodes[s[1]].value=(opts.find(o=>/selected/.test(o[1]+o[3]))||opts[0])[2];
}
const M=require(dir+'/model.js');let fault=false;
const ctx=vm.createContext({document:{getElementById:id=>nodes[id]},GrainModel:{...M,metrics(...xs){
 return fault?M.metrics([1e-200],[0],[1e-200],[1],[0]):M.metrics(...xs);
}}});
vm.runInContext(fs.readFileSync(dir+'/interactive.js','utf8'),ctx);
const n=id=>nodes['grain-'+id],initial=n('out').textContent;
for(let repeat=0;repeat<3;repeat++){
 fault=true;n('y2').events.input();
 assert(n('error').textContent.includes('入力の尺度を見直してください'));
 assert.equal(n('out').textContent,'入力が不正なため計算結果を表示しません。');
 assert.equal(n('bars').innerHTML,'');assert(!n('out').textContent.includes('未定義（分母0）'));
 fault=false;n('reset').events.click();assert.equal(n('out').textContent,initial);assert.equal(n('error').textContent,'');
}
// This UI has no download control; saved results and distributed model are tested separately.
assert(!html.includes('download='));
'''
    subprocess.run(['node','-e',script,str(P)],check=True)
