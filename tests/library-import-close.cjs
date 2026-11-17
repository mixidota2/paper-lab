const {JSDOM}=require('jsdom');
const fs=require('node:fs'),assert=require('node:assert/strict');
const html=fs.readFileSync('site/index.html','utf8');
const source=fs.readFileSync(process.env.LIBRARY_SOURCE || 'paper_lab/templates/library.js','utf8');
const tick=()=>new Promise(r=>setTimeout(r,10));
(async()=>{
 for(const mode of ['close','rapid-reopen','stale-rejection','new-file']) {
  const w=new JSDOM(html,{url:'https://example.test/?keep=1#library',runScripts:'outside-only'}).window;
  try {
   const d=w.document,q=s=>d.querySelector(s),fire=(el,t)=>el.dispatchEvent(new w.Event(t,{bubbles:true}));
   w.eval(source);
   const panel=q('[data-reading-import-panel]'),summary=panel.querySelector('summary'),input=q('[data-reading-import]'),form=q('[data-library-controls]');
   const state=()=>JSON.stringify({url:w.location.href,search:form.elements.search.value,shown:[...d.querySelectorAll('[data-paper]')].filter(c=>!c.hidden).map(c=>c.dataset.title)});
   const before=state(),saved={kind:'paper-lab-reading-list',schema_version:1,filters:{search:'no-such-lab',topic:'',verdict:'',sort:'date'}};
   panel.open=true;await tick();
   let resolve,reject;
   const pending=new Promise((a,b)=>{resolve=a;reject=b});
   const choose=promise=>{const f=new w.File(['{}'],'saved.json');f.text=()=>promise;Object.defineProperty(input,'files',{configurable:true,value:[f]});fire(input,'change')};
   choose(pending);assert.match(q('[data-reading-import-status]').textContent,/読み込んでいます/);
   if(mode==='close') {panel.open=false;await tick();}
   else {summary.click();assert.equal(panel.open,false);summary.click();assert.equal(panel.open,true);}
   assert.equal(q('[data-reading-import-status]').textContent,'','close clears pending state');
   if(mode==='new-file') {choose(Promise.resolve(JSON.stringify({...saved,filters:{...saved.filters,search:'EXAONE'}})));await tick();}
   const newer=state(),status=q('[data-reading-import-status]').textContent;
   if(mode==='stale-rejection') reject(Error('old file failed'));else resolve(JSON.stringify(saved));
   await tick();assert.equal(state(),newer);assert.equal(q('[data-reading-import-status]').textContent,status);
   if(mode!=='new-file') assert.equal(state(),before);
   // Reopening allows a fresh import; cancellation must not permanently disable it.
   panel.open=true;await tick();choose(Promise.resolve(JSON.stringify(saved)));await tick();
   assert.equal(form.elements.search.value,'no-such-lab');assert.match(q('[data-reading-import-status]').textContent,/戻しました/);
   console.log('PASS '+mode);
  } finally {w.close();}
 }
})().catch(e=>{console.error(e);process.exitCode=1});
