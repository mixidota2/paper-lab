// Execute the production handlers. DOM substitution does not test native layout or input.
'use strict';
const fs = require('node:fs'), vm = require('node:vm'), assert = require('node:assert/strict');
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
const snapshot = mount => JSON.stringify(walk(mount).map(n => ({
  tag: n.tag, text: n.textContent, value: n.value, attrs: n.attrs,
  width: n.style.width, disabled: n.disabled,
})));
const cases = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const source = fs.readFileSync(process.argv[3], 'utf8');
let checkedFrames = 0;
for (const c of cases) {
  const mount = new Element('div'), fallback = {hidden: false};
  const section = {dataset: {}, querySelector(selector) {
    return {'[data-mount]': mount, '[data-config]': {textContent: '{"kind":"explorer"}'},
      '[data-results]': {textContent: JSON.stringify(c.data)},
      '[data-axes]': {textContent: JSON.stringify(c.axes)}, '[data-fallback]': fallback}[selector];
  }};
  const document = {createElement: tag => new Element(tag), createElementNS: (_, tag) => new Element(tag),
    querySelectorAll: selector => selector === '[data-interactive]' ? [section] : []};
  vm.runInNewContext(source, {document, console});
  assert.equal(section.dataset.ready, 'true', c.slug);
  const input = walk(mount).find(n => n.tag === 'input');
  const [previous, next, reset, scale] = walk(mount).filter(n => n.tag === 'button');
  const initial = snapshot(mount);
  const assertReset = () => {
    assert.equal(input.value, String(c.data.default), `${c.slug}: reset condition`);
    assert.equal(scale.attrs['aria-pressed'], 'false', `${c.slug}: reset scale state`);
    assert.equal(scale.textContent, '棒の尺度：全条件で固定', `${c.slug}: reset scale label`);
    assert.equal(snapshot(mount), initial, `${c.slug}: all values, bars, lines, tables and controls reset`);
  };
  for (let i = 0; i < c.data.frames.length; i++) {
    input.value = String(i); input.events.input();
    scale.events.click();
    assert.equal(scale.attrs['aria-pressed'], 'true');
    assert.equal(scale.textContent, '棒の尺度：この条件の最大値に合わせる');
    if (c.slug === 'scale-regression-fixture' && i === c.data.default) {
      const fill = walk(mount).find(n => n.className === 'bar-fill');
      assert.equal(fill.style.width, '100%');
    }
    reset.events.click(); assertReset();
    reset.events.click(); assertReset(); // Reset is idempotent.
    scale.events.click(); scale.events.click();
    reset.events.click(); assertReset(); // Toggle still works after reset.
    checkedFrames++;
  }
  previous.events.click(); reset.events.click(); assertReset();
  next.events.click(); scale.events.click(); reset.events.click(); assertReset();
  if (c.slug === 'scale-regression-fixture') {
    assert.equal(walk(mount).find(n => n.className === 'bar-fill').style.width, '20%');
  }
}
console.log(`PASS: ${cases.length} explorer configurations, ${checkedFrames} frames; reset restores condition and fixed scale. DOM substitution, not browser QA.`);
