"""Actual library source/cards; synthetic submit dispatch, not native Enter/browser QA."""
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess

from paper_lab.build import build

ROOT = Path(__file__).resolve().parents[1]


class LibraryHTML(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.cards, self.defaults = [], {}
        self.select = None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'data-paper' in a:
            self.cards.append({k[5:]: v for k, v in a.items() if k.startswith('data-')})
        if tag == 'input' and a.get('name') == 'search':
            self.defaults['search'] = a.get('value', '')
        if tag == 'select':
            self.select = a['name']
        if tag == 'option' and self.select:
            if self.select not in self.defaults or 'selected' in a:
                self.defaults[self.select] = a.get('value', '')

    def handle_endtag(self, tag):
        if tag == 'select':
            self.select = None


def test_submit_preserves_actual_library_state(tmp_path):
    site = tmp_path / 'site'
    build(root=ROOT, site_dir=site)
    parsed = LibraryHTML((site / 'index.html').read_text())
    assert len(parsed.cards) == 111
    assert parsed.defaults == dict(search='', topic='', verdict='', sort='date')
    fixture = dict(cards=parsed.cards, defaults=parsed.defaults,
                   source=(site / 'assets/library.js').read_text())
    runner = r"""
const assert=require('node:assert/strict'),vm=require('node:vm'),f=FIXTURE;
const form=new EventTarget(),clear=new EventTarget(),empty={hidden:true};
const doc={activeElement:null};
form.elements=Object.fromEntries(Object.entries(f.defaults).map(([k,v])=>[k,{
 value:v,focus(){doc.activeElement=this}
}]));
form.reset=()=>Object.entries(f.defaults).forEach(([k,v])=>form.elements[k].value=v);
form.querySelector=()=>clear;
const cards=f.cards.map((dataset,id)=>({id,dataset,hidden:false}));
const parent={children:[...cards],append(card){
 this.children.splice(this.children.indexOf(card),1);this.children.push(card);
}};
cards.forEach(c=>c.parentElement=parent);
let activeSubmit=null,countText='';
const count={get textContent(){return countText},set textContent(v){
 if(activeSubmit)assert.equal(activeSubmit.defaultPrevented,true,'cancel before refresh');
 countText=v;
}};
doc.querySelector=s=>({'[data-library-controls]':form,'[data-result-count]':count,'[data-empty]':empty}[s]);
doc.querySelectorAll=()=>cards;
vm.runInNewContext(f.source,{document:doc});
const e=form.elements;
function visible(){return parent.children.filter(c=>!c.hidden).map(c=>c.id)}
function snapshot(){return {values:Object.values(e).map(x=>x.value),ids:visible(),count:countText,empty:empty.hidden}}
function expected(){
 return cards.filter(c=>(!e.search.value.trim()||c.dataset.search.includes(e.search.value.trim().toLocaleLowerCase('ja'))) &&
 (!e.topic.value||c.dataset.topics.split('|').includes(e.topic.value)) &&
 (!e.verdict.value||c.dataset.verdict===e.verdict.value))
 .sort((a,b)=>e.sort.value==='title'?a.dataset.title.localeCompare(b.dataset.title):
 e.sort.value==='date'?b.dataset.date.localeCompare(a.dataset.date):+b.dataset.priority-+a.dataset.priority).map(c=>c.id);
}
function submit(){
 const focus=doc.activeElement,ev=new Event('submit',{cancelable:true});
 activeSubmit=ev;const allowed=form.dispatchEvent(ev);activeSubmit=null;
 assert.equal(ev.defaultPrevented,true,'synthetic submit must be cancelled');
 assert.equal(allowed,false);assert.equal(doc.activeElement,focus);
 assert.deepEqual(visible(),expected());
 assert.equal(countText,visible().length+'件');assert.equal(empty.hidden,visible().length!==0);
 assert.equal(parent.children.length,111);assert.equal(new Set(parent.children).size,111);
}
function repeated(){
 const before=snapshot();
 for(let i=0;i<5;i++){submit();assert.deepEqual(snapshot(),before)}
}
e.search.value='EXAONE';e.search.focus();form.dispatchEvent(new Event('input'));
assert.equal(visible().length,1);assert.match(cards[visible()[0]].dataset.title,/exaone/i);repeated();
e.search.value='recommend';e.topic.value='recommender-systems';e.verdict.value='Worth Reading';e.sort.value='title';
e.sort.focus();form.dispatchEvent(new Event('change'));assert.ok(visible().length>1);repeated();
e.search.value='no-such-paper-987654321';form.dispatchEvent(new Event('input'));
assert.equal(visible().length,0);assert.equal(empty.hidden,false);repeated();
// Submit must refresh, not merely cancel, even without an input/change dispatch.
e.search.value='EXAONE';e.topic.value='';e.verdict.value='';submit();assert.equal(visible().length,1);
clear.dispatchEvent(new Event('click'));
assert.deepEqual(Object.fromEntries(Object.entries(e).map(([k,v])=>[k,v.value])),f.defaults);
assert.equal(visible().length,111);assert.equal(e.sort.value,'date');assert.equal(doc.activeElement,e.search);
assert.deepEqual(visible(),expected());repeated();
console.log('PASS:111 actual cards; synthetic submit, combined filters, zero, repeated, refresh, clear and focus');
"""
    path = tmp_path / 'library-submit.cjs'
    path.write_text(runner.replace('FIXTURE', json.dumps(fixture, ensure_ascii=False)))
    subprocess.run(['node', str(path)], check=True)
