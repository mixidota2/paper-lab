// Actual rendering handlers with a DOM substitute: not native browser/layout QA.
'use strict';
const fs = require('node:fs'), vm = require('node:vm'), assert = require('node:assert/strict');
const cases = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const source = fs.readFileSync(process.argv[3], 'utf8');
class Element {
  constructor(tag) { this.tag = tag; this.textContent = ''; this.children = []; this.attrs = {}; this.events = {};
    this.style = {setProperty() {}}; this.classList = {add() {}}; }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this.children = nodes; }
  setAttribute(key, value) { this.attrs[key] = String(value); }
  addEventListener(key, value) { this.events[key] = value; }
}
const walk = node => [node, ...node.children.flatMap(walk)];
let frames = 0, values = 0;
for (const c of cases) {
  const original = JSON.stringify(c), mount = new Element('div'), fallback = {hidden:false};
  const section = {dataset:{paperId:c.slug}, querySelector(selector) {
    return {'[data-mount]':mount, '[data-config]':{textContent:'{"kind":"explorer"}'},
      '[data-results]':{textContent:JSON.stringify(c.data)}, '[data-axes]':{textContent:JSON.stringify(c.axes)},
      '[data-fallback]':fallback}[selector];
  }};
  const document = {createElement:tag => new Element(tag), createElementNS:(_, tag) => new Element(tag),
    querySelectorAll:selector => selector === '[data-interactive]' ? [section] : []};
  vm.runInNewContext(source, {document,console});
  assert.equal(section.dataset.ready, 'true', c.slug);
  const controls = walk(mount), input = controls.find(n => n.tag === 'input');
  const buttons = controls.filter(n => n.tag === 'button');
  const save = buttons.find(n => n.textContent === '現在の条件を保存（JSON）');
  function check(index) {
    const frame = c.data.frames[index], tables = walk(mount).filter(n => n.tag === 'table');
    const barRows = tables[0].children.find(n => n.tag === 'tbody').children;
    assert.equal(barRows.length, frame.bars.length);
    function exact(cell, raw) {
      assert.equal(cell.textContent, raw === null ? '推定不能' : String(raw), `${c.slug}: saved ${raw}`);
      if (raw !== null) assert.equal(Number(cell.textContent), raw);
      values++;
    }
    frame.bars.forEach((bar, i) => exact(barRows[i].children[1], bar.value));
    if (frame.lines && frame.lines.length) {
      const rows = tables[1].children.find(n => n.tag === 'tbody').children;
      rows.forEach((row, index) => frame.lines.forEach((line, j) => {
        if (line.values[index] === undefined) assert.equal(row.children[j+1].textContent, '—');
        else exact(row.children[j+1], line.values[index]);
      }));
    }
    save.events.click();
    assert.deepEqual(JSON.parse(walk(mount).find(n => n.tag === 'textarea').value).frame, frame);
    frames++;
  }
  for (let index = 0; index < c.data.frames.length; index++) {
    input.value = String(index); input.events.input(); check(index);
    buttons[3].events.click(); check(index);
    buttons[3].events.click(); check(index);
  }
  buttons[2].events.click(); check(c.data.default);
  assert.equal(JSON.stringify(c), original, 'Rendering must not change saved research data');
}
console.log(`PASS: ${cases.length} configurations, ${frames} frame/scale states, ${values} exact numeric/null cells; exports and Reset agree. NOT native browser validation.`);
