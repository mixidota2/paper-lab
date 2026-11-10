"""Exercise the shipped initialization handlers with deferred fetch/JSON promises.

The DOM is synthetic. These tests do not establish browser rendering or real network behavior.
"""
from pathlib import Path
import hashlib
from html.parser import HTMLParser
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / 'papers/assortment-replenishment-hard-constraints'
CONTROLS = {'case', 'S', 'f', 't', 'beta', 'lambda', 'mode', 'reset', 'download'}


def test_controls_are_disabled_before_any_javascript():
    class Parser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.controls = {}

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag in {'input', 'select', 'button'}:
                self.controls[attrs['id']] = 'disabled' in attrs

    parser = Parser()
    parser.feed((LAB / 'interactive.html').read_text())
    assert set(parser.controls) == CONTROLS
    assert all(parser.controls.values())


def test_deferred_initialization_and_failure_handlers():
    script = r"""
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const dir='papers/assortment-replenishment-hard-constraints/';
const fixture=JSON.parse(fs.readFileSync(dir+'results.json','utf8'));
const html=fs.readFileSync(dir+'interactive.html','utf8');
const ids=['case','S','f','t','beta','lambda','mode','reset','download'];
const tick=()=>new Promise(setImmediate),plain=x=>JSON.parse(JSON.stringify(x));
function deferred(){let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b;});return {promise,resolve,reject};}
function setup({missingModel=false,renderFailure=false}={}){
 const nodes={};
 for(const m of html.matchAll(/<[^>]+\bid="([^"]+)"[^>]*>/g))nodes[m[1]]={value:m[0].match(/\bvalue="([^"]*)"/)?.[1]||'',disabled:/\sdisabled(?:[\s=>]|$)/.test(m[0]),events:{},addEventListener(e,f){this.events[e]=f;}};
 for(const m of html.matchAll(/<select[^>]*id="([^"]+)"[^>]*>\s*<option[^>]*value="([^"]+)"/g))nodes[m[1]].value=m[2];
 const request=deferred(),json=deferred(),saves=[];
 const ctx=vm.createContext({Blob,console,setTimeout:()=>{},document:{getElementById:id=>nodes[id],createElement:()=>({click(){}})},URL:{createObjectURL:b=>{saves.push(b);return 'blob:test';},revokeObjectURL:()=>{}},fetch:()=>request.promise});
 if(!missingModel)vm.runInContext(fs.readFileSync(dir+'model.js','utf8'),ctx);
 if(renderFailure)Object.defineProperty(nodes.summary,'innerHTML',{set(){throw Error('render interrupted');}});
 vm.runInContext(fs.readFileSync(dir+'interactive.js','utf8'),ctx);
 return {nodes,request,json,saves,ctx};
}
function disabled(s){assert(ids.every(k=>s.nodes[k].disabled));}
function safePendingEvents(s){assert.doesNotThrow(()=>s.nodes.reset.events.click());assert.doesNotThrow(()=>s.nodes.case.events.change());for(const k of ['S','f','t','beta','lambda','mode'])assert.doesNotThrow(()=>s.nodes[k].events.input());s.nodes.download.events.click();assert.equal(s.saves.length,0);}
async function ready(s){s.request.resolve({ok:true,json:()=>s.json.promise});await tick();disabled(s);safePendingEvents(s);s.json.resolve(fixture);await tick();}
(async()=>{
 const s=setup();disabled(s);safePendingEvents(s);assert(s.nodes.summary.textContent.includes('読み込んでいます'));
 await ready(s);assert(ids.every(k=>!s.nodes[k].disabled));assert(s.nodes.summary.innerHTML.includes('利益 24.000'));
 s.nodes.download.events.click();let out=JSON.parse(await s.saves.at(-1).text());assert.equal(out.model_version,'casrp-toy-1');assert.equal(out.result.oracle.best.profit,24);
 for(const name of ['T4','T2','T1']){s.nodes.case.value=name;s.nodes.case.events.change();s.nodes.reset.events.click();s.nodes.download.events.click();out=JSON.parse(await s.saves.at(-1).text());assert.equal(out.result.input.name,name);}
 const failCases=['network','http','json','missing-cases','bad-case','missing-model','render'];
 for(const kind of failCases){
  const f=setup({missingModel:kind==='missing-model',renderFailure:kind==='render'});disabled(f);safePendingEvents(f);
  if(kind==='network')f.request.reject(Error('offline'));
  else if(kind==='http')f.request.resolve({ok:false,json:()=>{throw Error('must not read error body');}});
  else {f.request.resolve({ok:true,json:()=>f.json.promise});await tick();disabled(f);if(kind==='json')f.json.reject(Error('invalid JSON'));else if(kind==='missing-cases')f.json.resolve({model_version:'casrp-toy-1'});else if(kind==='bad-case')f.json.resolve({cases:{},model_version:'casrp-toy-1'});else f.json.resolve(fixture);}
  await tick();disabled(f);safePendingEvents(f);assert(f.nodes.summary.textContent.includes('入力を取得できません'),kind);assert.equal(vm.runInContext('result',f.ctx),null,kind);assert.equal(vm.runInContext('originals',f.ctx),null,kind);
 }
 console.log('deferred fetch and JSON, success/export, 7 failure stages and guarded events passed; synthetic DOM only');
})().catch(e=>{console.error(e);process.exitCode=1;});
"""
    subprocess.run(['node', '-e', script], cwd=ROOT, check=True)


def test_readiness_revision_reverses_to_exact_published_sources():
    manifest = json.loads((ROOT / 'tests/replenishment_readiness_revision.json').read_text())
    assert manifest['base_commit'] == 'ebe169cdc22adfbe4d7f06196343f8118b436532'
    assert set(manifest['files']) == {
        'papers/assortment-replenishment-hard-constraints/interactive.html',
        'papers/assortment-replenishment-hard-constraints/interactive.js',
    }
    for path, row in manifest['files'].items():
        content = (ROOT / path).read_text()
        assert hashlib.sha256(content.encode()).hexdigest() == row['after_sha256']
        for before, after in reversed(row['replacements']):
            assert content.count(after) == 1
            content = content.replace(after, before)
        assert hashlib.sha256(content.encode()).hexdigest() == row['prior_sha256']
