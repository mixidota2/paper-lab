"""Portable Retail scenarios. Synthetic DOM assertions are not browser validation."""
from pathlib import Path
import importlib.util
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'papers/retail-forecast-decision-grain'


def node(script, *args):
    subprocess.run(['node', '-e', script, str(P), *args], check=True)


def test_roundtrip_recomputes_all_three_panels_against_python():
    spec = importlib.util.spec_from_file_location('retail_scenario_oracle', P / 'run.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    cases = []
    for group in ['separate', 'together']:
        for y2 in [0, .5, 10000]:
            for a2 in [0, .1, 10000]:
                for window in [0, .01, 10, 10000]:
                    for r in [.5, .8, .95]:
                        x = dict(y2=y2, a2=a2, group=group, window=window, q=.5, y=10000, r=r)
                        g = [0, 0] if group == 'together' else [0, 1]
                        expected = dict(metrics={
                            'A': m.metrics([100, y2], [90, a2], [1, 1], [1, 1], g),
                            'B': m.metrics([100, y2], [80, 0], [1, 1], [1, 1], g)},
                            windows={'A': m.windows([1, window], [0, window]),
                                     'B': m.windows([1, window], [1, max(0, window-10)])},
                            order={'loss': m.loss(.5, 10000, r), 'shortage_cost': m.loss(0, 1, r)})
                        cases.append(dict(inputs=x, expected=expected))
    node(r'''
const assert=require('node:assert/strict'),M=require(process.argv[1]+'/model.js'),cases=JSON.parse(process.argv[2]);
function close(a,b){if(b===null){assert.equal(a,null);return;}
 if(typeof b==='object'){assert.deepEqual(Object.keys(a),Object.keys(b));for(const k of Object.keys(b))close(a[k],b[k]);return;}
 assert.equal(typeof a,'number');assert(Number.isFinite(a));assert(Math.abs(a-b)<=2e-14*Math.max(1,Math.abs(b)));}
for(const c of cases){
 const packed=M.pack(c.inputs);assert.equal(packed.schema,1);assert.equal(packed.synthetic,true);
 assert.equal(packed.kind,'retail-grain-scenario');assert.equal(packed.model_version,'retail-grain-1');
 close(packed.output,c.expected);const serialized=JSON.stringify(packed);const restored=M.unpack(JSON.parse(serialized));
 assert.deepEqual(restored,c.inputs);assert.deepEqual(M.pack(restored),packed);
 assert.equal(JSON.stringify(c.inputs),JSON.stringify(packed.inputs));
}
console.log(cases.length+' scenario roundtrips and Python arithmetic comparisons');
''', json.dumps(cases))


def test_schema_rejections_and_untrusted_outputs():
    node(r'''
const assert=require('node:assert/strict'),M=require(process.argv[1]+'/model.js'),base=M.pack(M.defaults);
const clone=x=>JSON.parse(JSON.stringify(x));
for(const bad of [null,[],{},1,'text',undefined])assert.throws(()=>M.unpack(bad));
for(const [k,v] of [['schema',2],['schema','1'],['kind','other'],['model_version','retail-grain-2'],['synthetic',false]]){
 const x=clone(base);x[k]=v;assert.throws(()=>M.unpack(x));
}
for(const k of ['y2','a2','window','q','y'])for(const v of [null,'1',true,-1,10001,Infinity,NaN,{},[]]){
 const x=clone(base);x.inputs[k]=v;assert.throws(()=>M.unpack(x));
}
for(const k of Object.keys(M.defaults)){
 const x=clone(base);delete x.inputs[k];assert.throws(()=>M.unpack(x));
}
for(const [k,v] of [['r',.6],['r','0.8'],['group','<script>'],['group',null]]){
 const x=clone(base);x.inputs[k]=v;assert.throws(()=>M.unpack(x));
}
for(const bad of [null,[],Object.create(M.defaults),{...M.defaults,extra:'ignored?'}]){
 const x=clone(base);x.inputs=bad;assert.throws(()=>M.unpack(x));
}
const poison=clone(base);poison.output={metrics:{A:{corrected:-999999}},html:'<img onerror="bad()">'};
assert.deepEqual(M.pack(M.unpack(poison)),base);delete poison.output;
assert.deepEqual(M.pack(M.unpack(poison)),base);
const inputs={...M.defaults},packed=M.pack(inputs);inputs.q=999;assert.equal(packed.inputs.q,8);
const unpacked=M.unpack(packed);unpacked.y=0;assert.equal(packed.inputs.y,10);
assert.deepEqual(M.defaults,{y2:0,a2:1,group:'separate',window:100,q:8,y:10,r:.8});
''')


def test_save_import_invalid_edits_reset_and_download_fallback():
    node(r'''
const assert=require('node:assert/strict'),fs=require('fs'),vm=require('vm'),dir=process.argv[1],M=require(dir+'/model.js');
const html=fs.readFileSync(dir+'/interactive.html','utf8'),nodes={};
for(const match of html.matchAll(/<[^>]+\bid="([^"]+)"[^>]*>/g)){
 const tag=match[0];nodes[match[1]]={value:tag.match(/value="([^"]*)"/)?.[1]||'',disabled:/\bdisabled\b/.test(tag),events:{},textContent:'',innerHTML:'',addEventListener(k,f){this.events[k]=f;}};
}
for(const s of html.matchAll(/<select[^>]*id="([^"]+)"[^>]*>([\s\S]*?)<\/select>/g)){
 const opts=[...s[2].matchAll(/<option([^>]*)value="([^"]+)"([^>]*)>/g)];nodes[s[1]].value=(opts.find(o=>/selected/.test(o[1]+o[3]))||opts[0])[2];
}
const n=k=>nodes['grain-'+k],controls=['y2','a2','group','window','q','y','r','reset','download','json','import'];
controls.forEach(k=>assert.equal(n(k).disabled,true));
const blobs=[],anchors=[],revoked=[],timers=[];let downloadFailure=false;
const ctx=vm.createContext({GrainModel:M,document:{getElementById:id=>nodes[id],createElement(tag){assert.equal(tag,'a');const a={click(){if(downloadFailure)throw Error('download unavailable');}};anchors.push(a);return a;}},
 Blob:class{constructor(parts,opts){this.parts=parts;this.type=opts.type;}},URL:{createObjectURL(b){blobs.push(b);return 'blob:'+blobs.length;},revokeObjectURL(u){revoked.push(u);}},
 setTimeout(fn,ms){assert.equal(ms,1000);timers.push(fn);}});
vm.runInContext(fs.readFileSync(dir+'/interactive.js','utf8'),ctx);
controls.forEach(k=>assert.equal(n(k).disabled,false));const initial=n('out').textContent;
const event=(k,v)=>{n(k).value=String(v);n(k).events.input();},readInputs=()=>Object.fromEntries(Object.keys(M.defaults).map(k=>[k,k==='group'?n(k).value:Number(n(k).value)]));
for(let repeat=0;repeat<3;repeat++){
 event('y2',.5);event('a2',1.25);event('group','together');event('window',0);event('q',12);event('y',10);event('r',.95);
 n('download').events.click();const saved=JSON.parse(n('json').value),text=n('out').textContent;
 assert.deepEqual(saved,M.pack(readInputs()));assert(text.includes('未定義'));assert.equal(anchors.at(-1).download,'retail-grain-scenario.json');
 assert.equal(blobs.at(-1).type,'application/json');assert.equal(blobs.at(-1).parts[0],n('json').value);
 assert(n('transfer-status').textContent.includes('用意'));assert.equal(revoked.length,2*repeat);timers.shift()();assert.equal(revoked.length,2*repeat+1);
 n('reset').events.click();assert.equal(n('out').textContent,initial);assert.equal(n('json').value,'');assert.equal(n('transfer-status').textContent,'');
 saved.output={fake:-999};n('json').value=JSON.stringify(saved);n('import').events.click();assert.equal(n('out').textContent,text);assert(n('transfer-status').textContent.includes('再計算'));
 n('download').events.click();assert.deepEqual(JSON.parse(n('json').value).output,M.scenario(saved.inputs));timers.shift()();
 // Failed imports preserve a valid current scenario and leave export usable.
 const before=readInputs(),beforeText=n('out').textContent;
 for(const bad of ['{','null',JSON.stringify({...saved,schema:2}),JSON.stringify({...saved,inputs:{...saved.inputs,q:-1}}),' '.repeat(65537)]){
   n('json').value=bad;n('import').events.click();assert.deepEqual(readInputs(),before);assert.equal(n('out').textContent,beforeText);assert.equal(n('download').disabled,false);assert(n('transfer-status').textContent.includes('変更していません'));
 }
 event('q','');assert.equal(n('download').disabled,true);assert.equal(n('bars').innerHTML,'');assert.equal(n('transfer-status').textContent,'');
 const count=blobs.length;n('download').events.click();assert.equal(blobs.length,count);
 // A valid import recovers an invalid edit and replaces every condition.
 n('json').value=JSON.stringify(M.pack(M.defaults));n('import').events.click();assert.equal(n('out').textContent,initial);assert.equal(n('download').disabled,false);
 n('reset').events.click();
}
downloadFailure=true;n('download').events.click();assert(n('transfer-status').textContent.includes('開始できません'));assert.deepEqual(JSON.parse(n('json').value),M.pack(M.defaults));timers.shift()();
n('json').events.input();assert.equal(n('transfer-status').textContent,'');
''')
