"""URL-backed library controls against generated cards; not native browser QA."""
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess

import pytest

from paper_lab.build import build

ROOT = Path(__file__).resolve().parents[1]


class LibraryHTML(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.cards, self.defaults, self.options = [], {}, {}
        self.select = None
        self.has_status = False
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'data-paper' in attrs:
            self.cards.append({k[5:]: v for k, v in attrs.items() if k.startswith('data-')})
        if 'data-filter-url-status' in attrs:
            self.has_status = attrs.get('role') == 'status' and 'hidden' in attrs
        if tag == 'input' and attrs.get('name') == 'search':
            self.defaults['search'] = attrs.get('value', '')
        if tag == 'select':
            self.select = attrs['name']
            self.options[self.select] = []
        if tag == 'option' and self.select:
            value = attrs.get('value', '')
            self.options[self.select].append(value)
            if self.select not in self.defaults or 'selected' in attrs:
                self.defaults[self.select] = value

    def handle_endtag(self, tag):
        if tag == 'select':
            self.select = None


@pytest.fixture(scope='module')
def library(tmp_path_factory):
    site = tmp_path_factory.mktemp('library-navigation') / 'site'
    build(root=ROOT, site_dir=site)
    parsed = LibraryHTML((site / 'index.html').read_text())
    assert len(parsed.cards) == 114
    assert parsed.defaults == dict(search='', topic='', verdict='', sort='date')
    return dict(cards=parsed.cards, defaults=parsed.defaults, options=parsed.options,
                has_status=parsed.has_status, source=(site / 'assets/library.js').read_text())


RUNNER = r"""
const assert = require('node:assert/strict'), vm = require('node:vm'), f = FIXTURE;
const origin = 'https://example.test/paper-lab/index.html';
function app(href = origin, mode = {}) {
  const form = new EventTarget(), clear = new EventTarget(), win = new EventTarget();
  const doc = {activeElement:null}, count = {textContent:''}, empty = {hidden:true};
  const status = {hidden:true, textContent:''};
  form.elements = Object.fromEntries(Object.entries(f.defaults).map(([name, initial]) => {
    let value = initial;
    return [name, {
      options: (f.options[name] || []).map(value => ({value})),
      get value(){return value},
      set value(v){value = name === 'search' || f.options[name].includes(v) ? v : ''},
      focus(){doc.activeElement = this}
    }];
  }));
  form.reset = () => Object.entries(f.defaults).forEach(([k,v]) => form.elements[k].value = v);
  form.querySelector = () => clear;
  const cards = f.cards.map((dataset,id) => ({id,dataset,hidden:false}));
  const parent = {children:[...cards],append(card){
    this.children.splice(this.children.indexOf(card),1);this.children.push(card);
  }};
  cards.forEach(c => c.parentElement=parent);
  doc.querySelector = s => ({'[data-library-controls]':form, '[data-result-count]':count,
    '[data-empty]':empty, '[data-filter-url-status]':status}[s]);
  doc.querySelectorAll = () => cards;
  const state = {keep: {scroll: 42}}, calls = [];
  win.location = {href};
  win.history = {
    state,
    replaceState(newState, title, next){
      if(mode.throwWrite) throw new Error('History write unavailable');
      assert.equal(newState,state,'retain existing history.state identity');
      assert.equal(title,'');
      assert.equal(new URL(next).origin,new URL(win.location.href).origin);
      calls.push(next);win.location.href = next;
    },
    pushState(){assert.fail('filter edits must not push history entries')}
  };
  const context = {document:doc, URL};
  if(!mode.noWindow) context.window = win;
  vm.runInNewContext(f.source,context);
  const e=form.elements;
  function visible(){return parent.children.filter(c=>!c.hidden).map(c=>c.id)}
  function values(){return Object.fromEntries(Object.entries(e).map(([k,v])=>[k,v.value]))}
  function check(){
    const expected=cards.filter(c=>(!e.search.value.trim() ||
      c.dataset.search.includes(e.search.value.trim().toLocaleLowerCase('ja'))) &&
      (!e.topic.value || c.dataset.topics.split('|').includes(e.topic.value)) &&
      (!e.verdict.value || c.dataset.verdict===e.verdict.value))
      .sort((a,b)=>e.sort.value==='title'?a.dataset.title.localeCompare(b.dataset.title):
        e.sort.value==='date'?b.dataset.date.localeCompare(a.dataset.date):
        Number(b.dataset.priority)-Number(a.dataset.priority)).map(c=>c.id);
    assert.deepEqual(visible(),expected);
    assert.equal(count.textContent,expected.length+'件');
    assert.equal(empty.hidden,expected.length!==0);
    assert.equal(parent.children.length,114);
    assert.equal(new Set(parent.children).size,114);
  }
  function edit(values,type='input'){
    Object.entries(values).forEach(([k,v])=>e[k].value=v);
    const event=new Event(type,{cancelable:true});form.dispatchEvent(event);check();
    if(type==='submit')assert.equal(event.defaultPrevented,true);
  }
  function travel(next,type='popstate'){
    win.location.href=next;
    const event=new Event(type);event.persisted=true;
    const before=calls.length;win.dispatchEvent(event);check();
    assert.equal(calls.length,before,'restoration must not write history');
  }
  check();
  return {e,win,form,clear,doc,status,calls,values,visible,check,edit,travel};
}
CASE
"""


CASES = {
    'open_saved_filters': r"""
assert.ok(f.has_status,'generated page exposes status for URL save failure');
const url=origin+'?search=recommend&topic=recommender-systems&verdict=Worth+Reading&sort=title#library';
const a=app(url);
assert.deepEqual(a.values(),{search:'recommend',topic:'recommender-systems',verdict:'Worth Reading',sort:'title'});
assert.ok(a.visible().length>1 && a.visible().length<114);
assert.equal(a.calls.length,0);
assert.equal(a.win.location.href,url);
""",
    'reload_unicode_and_reserved_characters': r"""
const a=app(origin+'?keep=one&keep=two&x=a%20b#library');
a.edit({search:' 日本語 + % & ? # / 🧪 ',topic:'retail-supply',verdict:'Must Read',sort:'priority'});
const url=new URL(a.win.location.href);
assert.equal(url.searchParams.get('search'),a.e.search.value);
assert.deepEqual(url.searchParams.getAll('keep'),['one','two']);
assert.equal(url.searchParams.get('x'),'a b');
assert.equal(url.hash,'#library');
const b=app(a.win.location.href);
assert.deepEqual(b.values(),a.values());assert.deepEqual(b.visible(),a.visible());
assert.equal(b.visible().length,0);
assert.equal(a.status.hidden,false);assert.match(a.status.textContent,/URL/);
""",
    'invalid_duplicate_and_literal_input': r"""
const a=app(origin+'?topic=no-such-topic&topic=retail-supply&verdict=%3Cscript%3E&sort=missing&search=%3Cimg+src%3Dx%3E');
assert.deepEqual(a.values(),{search:'<img src=x>',topic:'',verdict:'',sort:'date'});
assert.equal(a.visible().length,0);
a.edit({search:'EXAONE',topic:'recommender-systems',sort:'title'});
const url=new URL(a.win.location.href);
assert.deepEqual(url.searchParams.getAll('topic'),['recommender-systems']);
assert.equal(url.searchParams.has('verdict'),false);
assert.deepEqual(url.searchParams.getAll('sort'),['title']);
const b=app(origin+'?search=EXAONE&search=does-not-exist&sort=date');
assert.equal(b.e.search.value,'EXAONE');assert.equal(b.visible().length,1);
""",
    'clear_preserves_unrelated_context': r"""
const a=app(origin+'?keep=one&keep=two&search=EXAONE&topic=recommender-systems&verdict=Must+Read&sort=title#library');
a.clear.dispatchEvent(new Event('click'));a.check();
assert.deepEqual(a.values(),f.defaults);assert.equal(a.visible().length,114);
assert.equal(a.doc.activeElement,a.e.search);
const url=new URL(a.win.location.href);
for(const key of Object.keys(f.defaults))assert.equal(url.searchParams.has(key),false);
assert.deepEqual(url.searchParams.getAll('keep'),['one','two']);assert.equal(url.hash,'#library');
const n=a.calls.length;a.clear.dispatchEvent(new Event('click'));assert.equal(a.calls.length,n);
""",
    'submit_and_repeated_edit_history': r"""
const a=app();a.e.search.focus();
a.edit({search:'EXAONE'},'submit');
assert.equal(new URL(a.win.location.href).searchParams.get('search'),'EXAONE');
assert.equal(a.visible().length,1);assert.equal(a.doc.activeElement,a.e.search);
const n=a.calls.length;
for(let i=0;i<10;i++)a.edit({search:'EXAONE'},i%2?'change':'input');
assert.equal(a.calls.length,n,'identical edits must not rewrite history');
for(const sort of ['title','priority','date']){
  a.edit({sort},'change');const b=app(a.win.location.href);assert.deepEqual(b.values(),a.values());
}
""",
    'back_forward_and_bfcache': r"""
const a=app();a.edit({search:'EXAONE',sort:'title'});const first=a.win.location.href;
a.edit({search:'',topic:'retail-supply',sort:'priority'});const second=a.win.location.href;
a.travel(first);assert.equal(a.visible().length,1);assert.equal(a.e.topic.value,'');assert.equal(a.e.sort.value,'title');
a.travel(second);assert.equal(a.e.search.value,'');assert.equal(a.e.topic.value,'retail-supply');
// Browsers may revive stale input fields separately from the document.
a.e.search.value='stale';a.e.topic.value='ai-agents';
a.travel(second,'pageshow');assert.equal(a.e.search.value,'');assert.equal(a.e.topic.value,'retail-supply');
a.travel(origin);assert.deepEqual(a.values(),f.defaults);assert.equal(a.visible().length,114);
""",
    'history_failure_keeps_search_usable': r"""
const a=app(origin,{throwWrite:true});
a.edit({search:'EXAONE'});assert.equal(a.visible().length,1);
assert.equal(a.win.location.href,origin);assert.equal(a.status.hidden,false);
assert.match(a.status.textContent,/URLに残せません/);
a.travel(origin,'pageshow');assert.equal(a.e.search.value,'EXAONE');assert.equal(a.visible().length,1);
a.edit({search:'no-such-paper'});assert.equal(a.visible().length,0);
a.clear.dispatchEvent(new Event('click'));a.check();assert.equal(a.visible().length,114);
assert.equal(a.doc.activeElement,a.e.search);
""",
    'restricted_url_and_no_browser': r"""
const a=app('not a usable absolute URL');
a.edit({search:'EXAONE'});assert.equal(a.visible().length,1);
assert.equal(a.status.hidden,false);assert.match(a.status.textContent,/URLに残せません/);
const b=app(origin,{noWindow:true});b.edit({search:'EXAONE'},'submit');
assert.equal(b.visible().length,1);assert.equal(b.calls.length,0);
b.clear.dispatchEvent(new Event('click'));b.check();assert.equal(b.visible().length,114);
const c=app('file:///tmp/lab%20copy/index.html?search=EXAONE#library');
assert.equal(c.visible().length,1);c.edit({search:'recommend',sort:'priority'});
assert.deepEqual(app(c.win.location.href).values(),c.values());
""",
}


@pytest.mark.parametrize('case', CASES)
def test_library_navigation(case, library, tmp_path):
    source = RUNNER.replace('FIXTURE', json.dumps(library, ensure_ascii=False)).replace('CASE', CASES[case])
    path = tmp_path / f'{case}.cjs'
    path.write_text(source)
    subprocess.run(['node', str(path)], check=True)
