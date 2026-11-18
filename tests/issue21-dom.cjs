const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {JSDOM}=require('jsdom');
const site=path.resolve('site'), page=path.join(site,'guides/forecast-to-replenishment.html');
const dom=new JSDOM(fs.readFileSync(page,'utf8'),{runScripts:'outside-only'});
const d=dom.window.document;
dom.window.eval(fs.readFileSync(path.join(site,'assets/replenishment-filter.js'),'utf8'));
const rows=d.querySelectorAll('[data-comparison-row]');
assert.equal(rows.length,7);
assert.equal(d.querySelectorAll('.repl-comparison thead th').length,6);
assert.equal(d.querySelector('.repl-comparison-scroll').tabIndex,0);
assert.match(d.querySelector('[data-survey-dates]').textContent,/2026-11-02（5件）、2026-11-17（2件）/);
assert.match(d.querySelector('[data-survey-dates]').textContent,/2026-11-18/);
const cards=[...d.querySelectorAll('[data-evidence-card]')],controls=[...d.querySelectorAll('[data-filter]')];
let combinations=0,links=0;
for(const a of controls[0].options)for(const b of controls[1].options)for(const c of controls[2].options){
 [a,b,c].forEach((o,i)=>{controls[i].value=o.value;controls[i].dispatchEvent(new dom.window.Event('change',{bubbles:true}));});
 for(const card of cards)assert.equal(!card.hidden,controls.every(s=>s.value==='all'||card.dataset[s.dataset.filter]===s.value));
 for(const row of rows)assert.equal(row.hidden,false);
 combinations++;
}
d.querySelector('[data-filter-reset]').click();assert.equal(cards.filter(c=>!c.hidden).length,7);
for(const a of d.querySelectorAll('a[href]')){
 const href=a.getAttribute('href');if(/^(https?:|mailto:)/.test(href))continue;
 const [file,fragment]=href.split('#');const target=file?path.resolve(path.dirname(page),decodeURIComponent(file)):page;
 assert.ok(fs.existsSync(target),href);links++;
 if(fragment&&target.endsWith('.html'))assert.ok(new JSDOM(fs.readFileSync(target,'utf8')).window.document.getElementById(decodeURIComponent(fragment)),href);
}
console.log(JSON.stringify({status:'PASS',rows:rows.length,filterCombinations:combinations,internalLinks:links,scope:'JSDOM actual generated DOM and filter handlers; no browser rendering or width verification'},null,2));
dom.window.close();
