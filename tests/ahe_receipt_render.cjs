const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const data = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
class Element {
  constructor(tag) {
    this.tag = tag; this.children = []; this.events = {}; this.style = {};
  }
  append(...children) { this.children.push(...children); }
  setAttribute(name, val) { this[name] = String(val); }
  addEventListener(name, listener) { this.events[name] = listener; }
  replaceChildren() { this.children = []; }
}
const mount = new Element('mount');
const fallback = new Element('fallback');
const section = {
  dataset: {paperId: 'ahe-beta-receipt'},
  querySelector(name) {
    const key = name.slice(6, -1);
    return key === 'mount' ? mount : key === 'fallback' ? fallback : {
      textContent: JSON.stringify(data[key]),
    };
  },
};
const document = {
  querySelectorAll: selector => selector === '[data-interactive]' ? [section] : [],
  createElement: tag => new Element(tag),
};
vm.runInNewContext(fs.readFileSync(process.argv[2], 'utf8'), {document, console});
assert.equal(section.dataset.ready, 'true');
assert.equal(fallback.hidden, true);
const [, slider, controls, , chart, note, , details] = mount.children;
const [, , reset] = controls.children;
function compare(frame) {
  assert.equal(note.textContent, frame.note);
  assert.deepEqual(chart.children.map(row => row.children[0].children[1].textContent),
                  frame.bars.map(b => String(b.value)));
  const tbody = details.children[1].children[0].children[2];
  assert.deepEqual(tbody.children.map(row => row.children[1].textContent),
                  frame.bars.map(b => String(b.value)));
}
compare(data.results.frames[data.results.default]);
data.results.frames.forEach((frame, i) => {
  slider.value = String(i);
  slider.events.input();
  compare(frame);
});
reset.events.click();
compare(data.results.frames[data.results.default]);
