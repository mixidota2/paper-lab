const {JSDOM}=require('jsdom');
const fs=require('node:fs');const crypto=require('node:crypto');const assert=require('node:assert/strict');
const root=require('node:path').resolve(process.argv[2] || require('node:path').join(__dirname,'..'));
const html=fs.readFileSync(root+'/site/index.html','utf8');
const source=fs.readFileSync(root+'/paper_lab/templates/library.js','utf8');
assert.equal(source,fs.readFileSync(root+'/site/assets/library.js','utf8'));
const start=new Date().toISOString();
const dom=new JSDOM(html,{url:'https://mixidota2.github.io/paper-lab/?extra=keep#library',runScripts:'outside-only'});
const w=dom.window,d=w.document,q=s=>d.querySelector(s);let downloads=0;
w.URL.createObjectURL=()=>{downloads++;return 'blob:test'};w.URL.revokeObjectURL=()=>{};
w.HTMLAnchorElement.prototype.click=function(){}; // Download transport only; use actual generated DOM/events/forms.
const executable=process.env.NEGATIVE_CONTROL==='disable-search'?source.replace('form.addEventListener("input", edit);',''):process.env.NEGATIVE_CONTROL==='ignore-late-import'?source.replace('if (request !== importRequest || composing) return;','if (composing) return;'):process.env.NEGATIVE_CONTROL==='disable-normalization'?source.replace('.normalize("NFKC")',''):source;
w.eval(executable);
const form=q('[data-library-controls]'),input=form.elements.search,select=form.elements.topic;
const shown=()=>[...d.querySelectorAll('[data-paper]')].filter(x=>!x.hidden).map(x=>x.querySelector('h3 a').getAttribute('href'));
const tick=()=>new Promise(r=>setImmediate(r));const fire=(el,name)=>el.dispatchEvent(new w.Event(name,{bubbles:true}));
const save=()=>{q('[data-reading-save]').click();return JSON.parse(q('[data-reading-json]').value)};
function choose(text){const file=new w.File([text],'reading.json',{type:'application/json'});file.text=()=>Promise.resolve(text);Object.defineProperty(q('[data-reading-import]'),'files',{configurable:true,value:[file]});fire(q('[data-reading-import]'),'change');}
(async()=>{
 // Production catalog tests require at least one searchable card and one topic option.
 // Empty-catalog rendering is a separate contract, not silently skipped here.
 const cards=[...d.querySelectorAll('[data-paper]')];
 assert.ok(cards.length>0,'generated catalog must contain at least one card');
 // A fixed synthetic Japanese-only card keeps NFKC coverage independent of titles.
 const jp=new JSDOM(html,{url:'https://example.test/',runScripts:'outside-only'});
 try {
  const jd=jp.window.document,jcards=[...jd.querySelectorAll('[data-paper]')];
  jcards.slice(1).forEach(c=>c.remove());jcards[0].dataset.search='検証 カタカナ';
  jp.window.eval(executable);
  const ji=jd.querySelector('[data-library-controls]').elements.search;
  ji.value='ｶﾀｶﾅ';ji.dispatchEvent(new jp.window.Event('input',{bubbles:true}));
  assert.equal(jcards[0].hidden,false,'Japanese single-card fixture must match halfwidth katakana via NFKC');
  ji.value='不存在';ji.dispatchEvent(new jp.window.Event('input',{bubbles:true}));
  assert.equal(jcards[0].hidden,true,'Japanese fixture must reject an absent query');
 } finally { jp.window.close(); }
 const token=cards[0]?.getAttribute('data-search').split(/\s+/)[0];assert.ok(token,'catalog needs searchable identity');
 const fullwidth=token.replace(/[!-~]/g,c=>String.fromCharCode(c.charCodeAt(0)+0xfee0));
 const expected=cards.filter(c=>c.getAttribute('data-search').includes(token)).map(c=>c.querySelector('h3 a').getAttribute('href'));
 let absent='__not_in_catalog__';while(cards.some(c=>c.getAttribute('data-search').includes(absent)))absent+='_';
 const topicOption=[...select.options].find(o=>o.value);assert.ok(topicOption,'catalog must expose a topic filter');
 const all=shown();assert.ok(all.length>0,'generated catalog must not be empty');assert.equal(q('[data-reading-list]').hidden,false);
 input.value=absent;fire(input,'input');assert.equal(shown().length,0,'input event must apply absent query even for one-card catalogs');
 input.value=fullwidth;fire(input,'input');assert.deepEqual([...shown()].sort(),[...expected].sort());const saved=save();assert.deepEqual(saved.papers.map(x=>x.lab_path),shown());assert.equal(downloads,1);
 q('[data-clear]').click();assert.equal(shown().length,all.length);assert.equal(d.activeElement,input);assert.equal(q('[data-reading-json]').value,'');
 choose(JSON.stringify(saved));await tick();assert.equal(input.value,fullwidth);assert.deepEqual(shown(),saved.papers.map(x=>x.lab_path));assert.equal(new URL(w.location).searchParams.get('extra'),'keep');assert.equal(w.location.hash,'#library');
 const original=shown();input.dispatchEvent(new w.CompositionEvent('compositionstart',{bubbles:true}));input.value=absent;fire(input,'input');assert.deepEqual(shown(),original);assert.equal(q('[data-reading-save]').disabled,true);input.dispatchEvent(new w.CompositionEvent('compositionend',{bubbles:true}));assert.equal(shown().length,0);assert.equal(q('[data-reading-save]').disabled,true);
 let finish;const delayed=new w.File(['x'],'slow.json');delayed.text=()=>new Promise(r=>finish=r);Object.defineProperty(q('[data-reading-import]'),'files',{configurable:true,value:[delayed]});fire(q('[data-reading-import]'),'change');select.value=topicOption.value;fire(select,'change');const newer=shown();finish(JSON.stringify(saved));await tick();assert.deepEqual(shown(),newer);assert.equal(select.value,topicOption.value);assert.equal(input.value,absent);
 choose('{broken');await tick();assert.deepEqual(shown(),newer);assert.match(q('[data-reading-import-status]').textContent,/変更していません/);
 const out={start,end:new Date().toISOString(),checks:['Japanese-only synthetic single-card NFKC search','generated cards initialize','fullwidth search and exact export order','native form reset and focus','JSON restore preserves unrelated URL state','bubbling IME events hold then commit results','late import cannot overwrite newer selection','invalid JSON preserves current results'],status:'PASS',scope:'Generated HTML + real JSDOM 30.1.2 DOM; download transport and File.text shimmed; no rendering, browser picker, network or deployed-site execution claimed',sha256:Object.fromEntries([['index',html],['library',source]].map(([k,v])=>[k,crypto.createHash('sha256').update(v).digest('hex')]))};
 console.log(JSON.stringify(out,null,2));w.close();
})().catch(e=>{console.error(e);w.close();process.exitCode=1});
