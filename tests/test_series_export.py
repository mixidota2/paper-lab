"""Real Series CV handlers with synthetic browser APIs, not native download tests."""
import json
import subprocess

import pytest

from test_series_cv import Controls, SOURCE


def fixture():
    nodes = Controls((SOURCE / 'interactive.html').read_text()).nodes
    nodes['scv-table-data'] = {'textContent': (SOURCE / 'table3.json').read_text()}
    return dict(nodes=nodes, model=str(SOURCE / 'model.js'), ui=str(SOURCE / 'interactive.js'))


def run_node(tmp_path, body, **extra):
    data = {**fixture(), **extra}
    script = r"""
const assert=require('node:assert/strict'),fs=require('fs'),vm=require('vm'),f=FIXTURE;
const nodes=f.nodes,blobs=[],anchors=[],created=[],revoked=[],timers=[];let failure=f.failure;
const get=k=>nodes['scv-'+k],M=require(f.model),table=JSON.parse(get('table-data').textContent);
for(const node of Object.values(nodes)){node.events={};node.addEventListener=(e,fn)=>node.events[e]=fn;}
const ctx={document:{getElementById:id=>nodes[id],createElement(tag){assert.equal(tag,'a');if(failure==='anchor')throw Error('anchor');const a={click(){if(failure==='click')throw Error('click');}};anchors.push(a);return a;}},
 setTimeout(fn,ms){assert.equal(ms,1000);timers.push(fn);}};
function install(){
 if(failure==='blob-missing')delete ctx.Blob;
 else ctx.Blob=class{constructor(parts,opt){if(failure==='blob')throw Error('blob');this.text=parts.join('');this.type=opt.type;blobs.push(this);}};
 if(failure==='url-missing')delete ctx.URL;
 else ctx.URL={createObjectURL(){if(failure==='url')throw Error('url');const url='blob:'+created.length;created.push(url);return url;},revokeObjectURL(url){revoked.push(url);if(failure==='revoke')throw Error('revoke');}};
}
install();vm.createContext(ctx);vm.runInContext(fs.readFileSync(f.model,'utf8')+'\n'+fs.readFileSync(f.ui,'utf8'),ctx);
const set=(k,v)=>{get(k).value=String(v);get(k).events.input();};
function expected(){return {toy:M.evaluate(undefined,get('scheme').value,get('q').value==='auto'?null:Number(get('q').value)),table3_sensitivity:M.sensitivity(table,get('method').value,get('weather').checked),display:{stage:get('stage').value,series:get('series').value,origin:Number(get('origin').value)},note:'Synthetic experiment and rounded published table analysis are distinct; not original replication.'};}
function cleared(){assert.equal(get('json').value,'');assert.equal(get('json').disabled,true);assert.equal(get('export-status').textContent,'');}
function save(){assert.doesNotThrow(()=>get('download').events.click());assert.equal(get('json').disabled,false);const data=JSON.parse(get('json').value);assert.deepEqual(data,expected());return data;}
BODY
""".replace('FIXTURE', json.dumps(data, ensure_ascii=False)).replace('BODY', body)
    target = tmp_path / 'series-export.cjs'
    target.write_text(script)
    subprocess.run(['node', str(target)], check=True)


@pytest.mark.parametrize('failure', [None, 'blob-missing', 'blob', 'url-missing',
                                    'url', 'anchor', 'click', 'revoke'])
def test_actual_export_preserves_edited_json_during_api_failure(tmp_path, failure):
    run_node(tmp_path, r"""
set('scheme','time');set('stage','outer');set('series','F');set('origin',96);set('q',2);
set('method','K-MC-CV');get('weather').checked=false;get('weather').events.change();
const before={out:get('out').textContent,split:get('split').innerHTML,table:get('table-out').textContent};
const exported=save();assert.equal(exported.toy.records.length,50);assert.equal(exported.table3_sensitivity.dataset_count,10);
assert.equal(get('out').textContent,before.out);assert.equal(get('split').innerHTML,before.split);assert.equal(get('table-out').textContent,before.table);assert.equal(get('error').textContent,'');
if(failure&&failure!=='revoke')assert(get('export-status').textContent.includes('開始できません'));
else assert(get('export-status').textContent.includes('用意しました'));
assert(!get('export-status').textContent.includes('保存しました'));
assert.equal(revoked.length,0);assert.equal(timers.length,created.length);
while(timers.length)assert.doesNotThrow(()=>timers.shift()());assert.deepEqual(revoked,created);
if(blobs.length){assert.equal(blobs[0].type,'application/json');assert.equal(blobs[0].text,get('json').value);}
failure=null;install();assert.deepEqual(save(),exported);
assert.equal(anchors.at(-1).download,'series-cv-synthetic.json');assert.equal(anchors.at(-1).href,created.at(-1));
assert.equal(blobs.at(-1).text,get('json').value);
while(timers.length)timers.shift()();assert.deepEqual(revoked,created);
""", failure=failure)


def test_export_edits_invalid_reset_and_reordered_cleanup(tmp_path):
    run_node(tmp_path, r"""
cleared();
for(const [key,value] of [['scheme','time'],['stage','inner'],['series','A'],['origin','96'],['q','0'],['method','Time-CV']]){
 get('reset').events.click();save();set(key,value);cleared();save();
}
get('weather').checked=false;get('weather').events.change();cleared();save();
const newest=get('json').value,status=get('export-status').textContent;
assert.equal(revoked.length,0);while(timers.length)timers.pop()();
assert.deepEqual([...revoked].sort(),[...created].sort());assert.equal(get('json').value,newest);assert.equal(get('export-status').textContent,status);
for(const [key,value] of [['origin',''],['origin','97'],['q','1e-400'],['q','5e-324'],['q','101'],['scheme','bad'],['series','Z'],['method','bad']]){
 get('reset').events.click();save();set(key,value);cleared();assert.equal(get('download').disabled,true);
 const count=created.length;get('download').events.click();assert.equal(created.length,count);cleared();
 get('reset').events.click();cleared();assert.equal(get('download').disabled,false);save();
}
get('reset').events.click();cleared();while(timers.length)timers.shift()();cleared();
set('q',0);assert.equal(save().toy.MASE,null);
""")


def test_readonly_fallback_has_label_status_and_initial_guard():
    html = (SOURCE / 'interactive.html').read_text()
    assert 'for="scv-json"' in html
    assert 'readonly disabled spellcheck="false"' in html
    assert 'id="scv-export-status" role="status"' in html
    nodes = Controls(html).nodes
    assert nodes['scv-json']['tag'] == 'textarea' and nodes['scv-json']['disabled']
    assert '<noscript>' in html
