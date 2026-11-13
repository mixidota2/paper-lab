// Production handlers in a minimal DOM; does not verify native download or layout.
'use strict';
const fs = require('node:fs'), vm = require('node:vm'), assert = require('node:assert/strict');
const payload = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const source = fs.readFileSync(process.argv[3], 'utf8');
const mode = process.argv[4];
class Element {
  constructor(tag) {
    this.tag = tag; this.textContent = ''; this.children = []; this.attrs = {};
    this.events = {}; this.style = {setProperty() {}}; this.classList = {add() {}};
  }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this.children = nodes; }
  setAttribute(key, value) { this.attrs[key] = String(value); }
  addEventListener(key, handler) { this.events[key] = handler; }
}
const walk = node => [node, ...node.children.flatMap(walk)];
let total = 0;
for (const c of payload) {
  const before = JSON.stringify(c);
  const mount = new Element('div'), fallback = {hidden: false};
  const section = {dataset: {paperId:c.slug}, querySelector(selector) {
    return {'[data-mount]':mount, '[data-config]':{textContent:'{"kind":"explorer"}'},
      '[data-results]':{textContent:JSON.stringify(c.data)},
      '[data-axes]':{textContent:JSON.stringify(c.axes)}, '[data-fallback]':fallback}[selector];
  }};
  const created = [], clicks = [], revoked = [], timers = [], blobs = [];
  let failures = mode;
  const document = {createElement:tag => {
    const el = new Element(tag);
    el.click = () => { if(failures==='click') throw Error('click unavailable'); clicks.push({href:el.href,download:el.download}); };
    return el;
  }, createElementNS:(_,tag) => new Element(tag), querySelectorAll:s => s==='[data-interactive]'?[section]:[]};
  class Blob {
    constructor(parts,options) { if(failures==='blob') throw Error('Blob unavailable'); this.text=parts.join(''); this.type=options.type; blobs.push(this); }
  }
  const URL = {
    createObjectURL(blob) { if(failures==='create') throw Error('URL unavailable'); const url='blob:test/'+created.length;created.push({url,blob});return url; },
    revokeObjectURL(url) { revoked.push(url); if(mode==='revoke') throw Error('cleanup unavailable'); }
  };
  const context = {document,console,setTimeout:(f,ms)=>{assert.equal(ms,1000);timers.push(f);}};
  if(mode!=='missing-blob')context.Blob=Blob;
  if(mode!=='missing-url')context.URL=URL;
  vm.runInNewContext(source,context);
  assert.equal(section.dataset.ready,'true');
  const all = walk(mount), input = all.find(n=>n.tag==='input');
  const buttons = all.filter(n=>n.tag==='button');
  const save = buttons.find(n=>n.textContent==='現在の条件を保存（JSON）');
  assert.ok(save, 'Current-condition export must be available');
  const text = all.find(n=>n.tag==='textarea');
  const detail = all.find(n=>n.className==='explorer-export');
  const status = all.find(n=>n.attrs.role==='status');
  assert.equal(text.readOnly,true);assert.equal(text.rows,10);
  assert.ok(all.find(n=>n.tag==='label'&&n.htmlFor===text.id));
  assert.equal(text.value,'');assert.equal(detail.open,false);
  function exportAt(i) {
    input.value=String(i);input.events.input();
    assert.equal(text.value,'','changed condition clears stale snapshot');
    assert.equal(detail.open,false);assert.equal(status.textContent,'');
    save.events.click();
    const result=JSON.parse(text.value);
    assert.equal(result.schema_version,1);assert.equal(result.kind,'paper-lab-explorer-condition');
    assert.equal(result.synthetic,true);assert.equal(result.paper_id,c.slug);assert.equal(result.experiment_id,'experiment-0');
    assert.equal(result.condition_index,i);assert.equal(result.condition_label,c.data.label);
    assert.equal(result.condition_unit,c.data.unit);assert.equal(result.metric,c.data.metric);
    assert.deepEqual(result.frame,c.data.frames[i]);assert.deepEqual(result.axes,c.axes);
    assert.match(result.note,/人工データ/);assert.match(result.note,/原論文/);
    assert.equal(detail.open,true);
    if(['success','revoke','repeated'].includes(mode)) {
      assert.equal(created.at(-1).blob.text,text.value);assert.equal(created.at(-1).blob.type,'application/json');
      assert.equal(clicks.at(-1).href,created.at(-1).url);
      assert.equal(clicks.at(-1).download,`${c.slug}-experiment-0-condition-${i+1}.json`);
      assert.match(status.textContent,/ファイルがダウンロードされない場合/);
      assert.doesNotMatch(status.textContent,/保存しました/);
    } else { assert.match(status.textContent,/開始できませんでした/); }
    total++;
  }
  const frames = mode==='success'?c.data.frames.map((_,i)=>i):[c.data.default];
  frames.forEach(exportAt);
  if(mode==='repeated') {
    const first=text.value;
    save.events.click();assert.equal(text.value,first);
    const next=(c.data.default+1)%c.data.frames.length;exportAt(next);
    const latest=text.value;
    timers.splice(0).forEach(f=>f());
    assert.equal(text.value,latest,'earlier cleanup cannot erase newer preview');
    assert.deepEqual(revoked,created.map(x=>x.url));
  }
  buttons[2].events.click();assert.equal(input.value,String(c.data.default));
  assert.equal(text.value,'');assert.equal(status.textContent,'');assert.equal(detail.open,false);
  save.events.click();assert.deepEqual(JSON.parse(text.value).frame,c.data.frames[c.data.default]);
  buttons[3].events.click();assert.equal(text.value,'');
  save.events.click();assert.deepEqual(JSON.parse(text.value).frame,c.data.frames[c.data.default],'scale changes never alter saved numbers');
  timers.splice(0).forEach(f=>f());
  assert.deepEqual(revoked,created.map(x=>x.url),'every URL cleaned once, including failed clicks');
  assert.equal(JSON.stringify(c),before,'export must never mutate saved data');
}
console.log(`PASS ${mode}: ${payload.length} configurations, ${total} frame exports, exact payload and fallback checks.`);
