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
const executable=process.env.NEGATIVE_CONTROL==='disable-search'?source.replace('form.addEventListener("input", edit);',''):process.env.NEGATIVE_CONTROL==='ignore-late-import'?source.replace('if (request !== importRequest || composing) return;','if (composing) return;'):source;
w.eval(executable);
const form=q('[data-library-controls]'),input=form.elements.search,select=form.elements.topic;
const shown=()=>[...d.querySelectorAll('[data-paper]')].filter(x=>!x.hidden).map(x=>x.querySelector('h3 a').getAttribute('href'));
const tick=()=>new Promise(r=>setImmediate(r));const fire=(el,name)=>el.dispatchEvent(new w.Event(name,{bubbles:true}));
const save=()=>{q('[data-reading-save]').click();return JSON.parse(q('[data-reading-json]').value)};
function choose(text){const file=new w.File([text],'reading.json',{type:'application/json'});file.text=()=>Promise.resolve(text);Object.defineProperty(q('[data-reading-import]'),'files',{configurable:true,value:[file]});fire(q('[data-reading-import]'),'change');}
(async()=>{
 const all=shown();assert.ok(all.length>0,'generated catalog must not be empty');assert.equal(q('[data-reading-list]').hidden,false);
 input.value='ＥＸＡＯＮＥ';fire(input,'input');assert.equal(shown().length,1);const saved=save();assert.deepEqual(saved.papers.map(x=>x.lab_path),shown());assert.equal(downloads,1);
 q('[data-clear]').click();assert.equal(shown().length,all.length);assert.equal(d.activeElement,input);assert.equal(q('[data-reading-json]').value,'');
 choose(JSON.stringify(saved));await tick();assert.equal(input.value,'ＥＸＡＯＮＥ');assert.deepEqual(shown(),saved.papers.map(x=>x.lab_path));assert.equal(new URL(w.location).searchParams.get('extra'),'keep');assert.equal(w.location.hash,'#library');
 const original=shown();input.dispatchEvent(new w.CompositionEvent('compositionstart',{bubbles:true}));input.value='欠品';fire(input,'input');assert.deepEqual(shown(),original);assert.equal(q('[data-reading-save]').disabled,true);input.dispatchEvent(new w.CompositionEvent('compositionend',{bubbles:true}));assert.ok(shown().length>1);assert.equal(q('[data-reading-save]').disabled,false);
 let finish;const delayed=new w.File(['x'],'slow.json');delayed.text=()=>new Promise(r=>finish=r);Object.defineProperty(q('[data-reading-import]'),'files',{configurable:true,value:[delayed]});fire(q('[data-reading-import]'),'change');select.value='retail-supply';fire(select,'change');const newer=shown();finish(JSON.stringify(saved));await tick();assert.deepEqual(shown(),newer);assert.equal(select.value,'retail-supply');assert.equal(input.value,'欠品');
 choose('{broken');await tick();assert.deepEqual(shown(),newer);assert.match(q('[data-reading-import-status]').textContent,/変更していません/);
 const out={start,end:new Date().toISOString(),checks:['generated cards initialize','fullwidth search and exact export order','native form reset and focus','JSON restore preserves unrelated URL state','bubbling IME events hold then commit results','late import cannot overwrite newer selection','invalid JSON preserves current results'],status:'PASS',scope:'Generated HTML + real JSDOM 30.1.2 DOM; download transport and File.text shimmed; no rendering, browser picker, network or deployed-site execution claimed',sha256:Object.fromEntries([['index',html],['library',source]].map(([k,v])=>[k,crypto.createHash('sha256').update(v).digest('hex')]))};
 console.log(JSON.stringify(out,null,2));w.close();
})().catch(e=>{console.error(e);w.close();process.exitCode=1});
