"""Capture the actual export handler's Blob; this is not a browser save test."""
from pathlib import Path
import subprocess


def test_export_preserves_model_version_and_effective_input():
    root = Path(__file__).resolve().parents[1]
    script = r"""
const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
const dir='papers/assortment-replenishment-hard-constraints/';
const fixture=JSON.parse(fs.readFileSync(dir+'results.json','utf8'));
const html=fs.readFileSync(dir+'interactive.html','utf8'),nodes={};
for(const m of html.matchAll(/<[^>]+\bid="([^"]+)"[^>]*>/g))nodes[m[1]]={value:m[0].match(/\bvalue="([^"]*)"/)?.[1]||'',events:{},addEventListener(e,f){this.events[e]=f;}};
for(const m of html.matchAll(/<select[^>]*id="([^"]+)"[^>]*>\s*<option[^>]*value="([^"]+)"/g))nodes[m[1]].value=m[2];
let blob,anchor,saves=0;const timers=[];
const ctx=vm.createContext({Blob,console,document:{getElementById:id=>nodes[id],createElement:()=>({click(){anchor=this;saves++;}})},URL:{createObjectURL:b=>{blob=b;return 'blob:test'},revokeObjectURL:u=>assert.equal(u,'blob:test')},setTimeout:f=>timers.push(f),fetch:async url=>{assert.equal(url,'results.json');return {ok:true,json:async()=>fixture}}});
for(const f of ['model.js','interactive.js'])vm.runInContext(fs.readFileSync(dir+f,'utf8'),ctx);
const model=require(process.cwd()+'/'+dir+'model.js');
const plain=x=>JSON.parse(JSON.stringify(x));
function event(id,type,value){if(value!==undefined)nodes[id].value=String(value);nodes[id].events[type]({target:nodes[id]});}
async function save(){event('download','click');assert.equal(anchor.download,'replenishment-synthetic.json');assert.equal(anchor.href,'blob:test');assert.equal(blob.type,'application/json');const out=JSON.parse(await blob.text());assert.equal(out.synthetic,true);assert.equal(out.model_version,fixture.model_version);assert.equal(out.model_version,'casrp-toy-1');assert.equal(out.selected_mode,nodes.mode.value);assert.deepEqual(out.result.input,plain(vm.runInContext('data',ctx)));assert.deepEqual(out.result,model.experiment(out.result.input));timers.splice(0).forEach(f=>f());return out;}
(async()=>{await new Promise(setImmediate);
for(const name of ['T1','T2','T3','T4']){event('case','change',name);await save();}
event('mode','input','t4');const t4=await save();assert.deepEqual(model.evaluate(t4.result.input,[0,1,0]).k,[0,1,0]);
for(const [id,v] of [['t',.5],['lambda',.5],['S',0]])event(id,'input',v);await save();
event('reset','click');const first=await save();assert.deepEqual(await save(),first);assert.equal(saves,8);
})().catch(e=>{console.error(e);process.exitCode=1;});
"""
    subprocess.run(["node", "-e", script], cwd=root, check=True)


def test_export_revision_preserves_version_metadata_after_readiness_change():
    import hashlib
    import json
    root = Path(__file__).resolve().parents[1]
    path = 'papers/assortment-replenishment-hard-constraints/interactive.js'
    data = (root / path).read_text()
    replacements = [
        ('let originals,data,result;', 'let originals,data,result,modelVersion;'),
        ('JSON.stringify({synthetic:true,selected_mode:',
         'JSON.stringify({synthetic:true,model_version:modelVersion,selected_mode:'),
        ('originals=d.cases;setup();', 'originals=d.cases;modelVersion=d.model_version;setup();'),
    ]
    row = json.loads((root / 'tests/prose_revision_hashes.json').read_text())['files'][path]
    assert hashlib.sha256(data.encode()).hexdigest() == row['after_sha256']
    readiness = json.loads((root / 'tests/replenishment_readiness_revision.json').read_text())['files'][path]
    for before, after in reversed(readiness['replacements']):
        assert data.count(after) == 1
        data = data.replace(after, before)
    assert hashlib.sha256(data.encode()).hexdigest() == readiness['prior_sha256']
    for before, after in replacements:
        assert data.count(after) == 1
        data = data.replace(after, before)
    assert hashlib.sha256(data.encode()).hexdigest() == row['before_sha256']
