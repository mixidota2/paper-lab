"""Pinned synthetic scenarios: exact arithmetic, transfer safety, actual source handlers.

The DOM fixture does not exercise a browser, layout, OS downloads, or screen readers.
"""
from pathlib import Path
import importlib.util
import json
import subprocess

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'papers/retail-forecast-decision-grain'


def node(script,*args):
    subprocess.run(['node','-e',script,str(P)],input=args[0] if args else None,text=True,check=True)


def test_comparison_deltas_against_independent_python_arithmetic():
    spec=importlib.util.spec_from_file_location('retail_comparison_oracle',P/'run.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    def result(x):
        group=[0,0] if x['group']=='together' else [0,1]
        return {'metrics':{'A':m.metrics([100,x['y2']],[90,x['a2']],[1,1],[1,1],group),
                           'B':m.metrics([100,x['y2']],[80,0],[1,1],[1,1],group)},
                'windows':{'A':m.windows([1,x['window']],[0,x['window']]),
                           'B':m.windows([1,x['window']],[1,max(0,x['window']-10)])},
                'order':{'loss':m.loss(x['q'],x['y'],x['r']),
                         'shortage_cost':m.loss(0,1,x['r'])}}
    base=dict(y2=0,a2=1,group='separate',window=100,q=8,y=10,r=.8)
    def delta(a,b):
        if a is None or b is None:return None
        if isinstance(a,dict):return {k:delta(a[k],b[k]) for k in a}
        return b-a
    cases=[]
    for group in ['together','separate']:
        for y2 in [0,.5,10000]:
            for a2 in [0,20,10000]:
                for window in [0,.01,10000]:
                    for q in [0,10,10000]:
                        for r in [.5,.8,.95]:
                            current=dict(y2=y2,a2=a2,group=group,window=window,q=q,y=10,r=r)
                            for baseline,target in [(base,current),(current,base)]:
                                cases.append({'baseline':baseline,'current':target,'delta':delta(result(baseline),result(target))})
    node(r'''
const assert=require('node:assert/strict'),M=require(process.argv[1]+'/model.js'),cases=JSON.parse(require('fs').readFileSync(0,'utf8'));
function close(a,b){if(b===null){assert.equal(a,null);return;}if(typeof b==='object'){assert.deepEqual(Object.keys(a),Object.keys(b));for(const k of Object.keys(b))close(a[k],b[k]);return;}assert(Number.isFinite(a));assert(Math.abs(a-b)<=3e-13*Math.max(1,Math.abs(b)),a+' != '+b);}
for(const c of cases){
 const before=JSON.stringify(c),r=M.compare(c.baseline,c.current);close(r.delta,c.delta);
 assert.deepEqual(r.baseline,M.pack(c.baseline));assert.deepEqual(r.current,M.pack(c.current));
 assert.deepEqual(r.changed_inputs,Object.keys(M.defaults).filter(k=>c.baseline[k]!==c.current[k]));
 const packed=M.packComparison(c.baseline,c.current),restored=M.unpackComparison(JSON.parse(JSON.stringify(packed)));
 assert.deepEqual(restored,{baseline:c.baseline,current:c.current});assert.deepEqual(M.packComparison(restored.baseline,restored.current),packed);
 assert.equal(JSON.stringify(c),before);
}
const same=M.compare(M.defaults,M.defaults);assert.deepEqual(same.changed_inputs,[]);
console.log(cases.length+' directional comparison / roundtrip / Python-delta cases');
''',json.dumps(cases))


def test_comparison_schema_rejects_both_sides_and_recomputes_untrusted_fields():
    node(r'''
const assert=require('node:assert/strict'),M=require(process.argv[1]+'/model.js'),copy=x=>JSON.parse(JSON.stringify(x));
const base=M.packComparison(M.defaults,{...M.defaults,window:0,q:10});
for(const d of [undefined,null,[],{},1,'text'])assert.throws(()=>M.unpackComparison(d));
for(const [key,value] of [['schema',2],['schema','1'],['kind','retail-grain-scenario'],['model_version','future'],['synthetic',false]]){
 const d=copy(base);d[key]=value;assert.throws(()=>M.unpackComparison(d));
}
for(const side of ['baseline','current']){
 for(const bad of [null,{},[],{...base[side],schema:2},{...base[side],synthetic:false},{...base[side],inputs:{...M.defaults,q:-1}},{...base[side],inputs:{...M.defaults,window:NaN}},{...base[side],inputs:{...M.defaults,group:'<script>'}}]){
  const d=copy(base);d[side]=bad;assert.throws(()=>M.unpackComparison(d));
 }
 const d=copy(base);delete d[side];assert.throws(()=>M.unpackComparison(d));
}
const poison=copy(base);poison.baseline.output={html:'<img onerror=bad()>',x:-999};delete poison.current.output;poison.delta='untrusted';poison.changed_inputs=['x'];
const restored=M.unpackComparison(poison);assert.deepEqual(M.packComparison(restored.baseline,restored.current),base);
restored.baseline.q=99;restored.current.q=98;assert.equal(base.baseline.inputs.q,8);assert.equal(base.current.inputs.q,10);
const b={...M.defaults},c={...M.defaults};const packed=M.packComparison(b,c);b.q=99;c.q=98;assert.equal(packed.baseline.inputs.q,8);assert.equal(packed.current.inputs.q,8);
const zero=M.compare({...M.defaults,window:0},{...M.defaults,window:0});assert.equal(zero.delta.windows.A.mean,null);assert.equal(zero.delta.windows.B.mean,null);
''')


def test_pin_change_save_restore_invalid_reset_and_download_failure_flows():
    node(r'''
const assert=require('node:assert/strict'),fs=require('fs'),vm=require('vm'),dir=process.argv[1],M=require(dir+'/model.js');
const html=fs.readFileSync(dir+'/interactive.html','utf8'),nodes={};
for(const match of html.matchAll(/<[^>]+\bid="([^"]+)"[^>]*>/g)){
 const tag=match[0];nodes[match[1]]={value:tag.match(/value="([^"]*)"/)?.[1]||'',disabled:/\bdisabled\b/.test(tag),events:{},textContent:'',innerHTML:'',addEventListener(k,f){this.events[k]=f;}};
}
for(const s of html.matchAll(/<select[^>]*id="([^"]+)"[^>]*>([\s\S]*?)<\/select>/g)){
 const opts=[...s[2].matchAll(/<option([^>]*)value="([^"]+)"([^>]*)>/g)];nodes[s[1]].value=(opts.find(o=>/selected/.test(o[1]+o[3]))||opts[0])[2];
}
const n=k=>nodes['grain-'+k],click=k=>n(k).events.click(),edit=(k,v)=>{n(k).value=String(v);n(k).events.input();};
const inputs=()=>Object.fromEntries(Object.keys(M.defaults).map(k=>[k,k==='group'?n(k).value:Number(n(k).value)]));
const blobs=[],anchors=[],revoked=[],timers=[];let failure=false;
const ctx=vm.createContext({GrainModel:M,document:{getElementById:id=>nodes[id],createElement(tag){assert.equal(tag,'a');const a={click(){if(failure)throw Error('download unavailable');}};anchors.push(a);return a;}},
 Blob:class{constructor(parts,opts){this.parts=parts;this.type=opts.type;}},URL:{createObjectURL(b){blobs.push(b);return 'blob:'+blobs.length;},revokeObjectURL(u){revoked.push(u);}},setTimeout(fn,ms){assert.equal(ms,1000);timers.push(fn);}});
for(const k of ['pin','clear-baseline','comparison-download'])assert.equal(n(k).disabled,true);
vm.runInContext(fs.readFileSync(dir+'/interactive.js','utf8'),ctx);
assert.equal(n('pin').disabled,false);assert.equal(n('clear-baseline').disabled,true);assert.equal(n('comparison-download').disabled,true);
assert(n('comparison-status').textContent.includes('まだありません'));
const initial=n('out').textContent;
function compareTable(){const cells=[...n('comparison').innerHTML.matchAll(/<tr><th scope="row">([^<]+)<\/th><td>([^<]+)<\/td><td>([^<]+)<\/td><td>([^<]+)<\/td><\/tr>/g)];assert.equal(cells.length,10);return Object.fromEntries(cells.map(x=>[x[1],x.slice(2)]));}
for(let repeat=0;repeat<3;repeat++){
 click('pin');assert.equal(n('clear-baseline').disabled,false);assert.equal(n('comparison-download').disabled,false);
 assert(n('comparison-status').textContent.includes('変更した項目：なし'));assert.deepEqual(compareTable()['単期発注損失'],['8','8','0']);
 edit('q',10);edit('window',0);edit('group','together');
 assert.deepEqual(compareTable()['単期発注損失'],['8','0','-8']);assert.equal(compareTable()['窓平均 A'][2],'比較不可（分母0）');
 assert(n('comparison-status').textContent.includes('集計する単位、第2窓売上、発注量 q'));
 click('comparison-download');const saved=JSON.parse(n('json').value);assert.deepEqual(saved,M.packComparison(M.defaults,inputs()));
 assert.equal(anchors.at(-1).download,'retail-grain-comparison.json');assert.equal(blobs.at(-1).parts[0],n('json').value);timers.shift()();
 // A one-scenario export remains the original backwards-compatible format.
 click('download');assert.equal(JSON.parse(n('json').value).kind,'retail-grain-scenario');timers.shift()();
 // Re-pinning copies conditions, rather than aliasing later changes.
 click('pin');edit('q',9);assert.deepEqual(compareTable()['単期発注損失'],['0','4','4']);
 // Restore both sides, ignoring fabricated results and changes.
 saved.baseline.output={bad:'<script>'};saved.current.output={bad:999};saved.delta=-999;saved.changed_inputs=['fake'];
 n('json').value=JSON.stringify(saved);click('import');assert.deepEqual(compareTable()['単期発注損失'],['8','0','-8']);assert(n('transfer-status').textContent.includes('結果と差を再計算'));assert(!n('comparison').innerHTML.includes('script'));
 const text=n('comparison').innerHTML,status=n('comparison-status').textContent,before=inputs();
 for(const side of ['baseline','current']){
  const bad=JSON.parse(JSON.stringify(saved));bad[side].inputs.q=-1;n('json').value=JSON.stringify(bad);click('import');
  assert.deepEqual(inputs(),before);assert.equal(n('comparison').innerHTML,text);assert.equal(n('comparison-status').textContent,status);assert(n('transfer-status').textContent.includes('変更していません'));
 }
 // Incomplete input never displays the last comparison, but it preserves the baseline.
 edit('q','');assert.equal(n('comparison').innerHTML,'');assert.equal(n('pin').disabled,true);assert.equal(n('comparison-download').disabled,true);assert.equal(n('clear-baseline').disabled,false);
 const count=blobs.length;click('comparison-download');click('pin');assert.equal(blobs.length,count);
 edit('q',11);assert.deepEqual(compareTable()['単期発注損失'],['8','1','-7']);
 // Single scenario import retains the baseline, including when recovering invalid input.
 edit('q','');n('json').value=JSON.stringify(M.pack({...M.defaults,q:12}));click('import');assert.deepEqual(compareTable()['単期発注損失'],['8','2','-6']);
 click('clear-baseline');assert.equal(n('comparison').innerHTML,'');assert.equal(n('comparison-download').disabled,true);assert.equal(n('clear-baseline').disabled,true);
 edit('q',8);click('pin');click('reset');assert.equal(n('out').textContent,initial);assert.equal(n('comparison').innerHTML,'');assert.equal(n('json').value,'');assert.equal(n('comparison-download').disabled,true);
}
// Clear is always available when a baseline exists, including invalid current input.
click('pin');edit('q','');click('clear-baseline');edit('q',8);assert.equal(n('comparison').innerHTML,'');
click('pin');failure=true;click('comparison-download');assert(n('transfer-status').textContent.includes('開始できません'));
assert.deepEqual(JSON.parse(n('json').value),M.packComparison(M.defaults,M.defaults));timers.shift()();assert.equal(revoked.length,blobs.length);
assert(html.includes('scope="col"')===false); // Headers are generated by the actual renderer.
assert(n('comparison').innerHTML.includes('<caption>'));assert(n('comparison').innerHTML.includes('scope="col"'));assert(html.includes('overflow-x:auto'));
''')
