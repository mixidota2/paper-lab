const {JSDOM}=require('jsdom');
const fs=require('node:fs'),assert=require('node:assert/strict'),crypto=require('node:crypto'),path=require('node:path');
const root=path.resolve(process.argv[2] || process.cwd());
const html=fs.readFileSync(root+'/site/index.html','utf8'),original=fs.readFileSync(root+'/paper_lab/templates/library.js','utf8');
assert.equal(original,fs.readFileSync(root+'/site/assets/library.js','utf8'));
let source=original;
if(process.env.NEGATIVE_CONTROL==='text') source=source.replace('text.length > maxBytes','false');
if(process.env.NEGATIVE_CONTROL==='size') source=source.replace('file.size > maxBytes','false');
if(process.env.NEGATIVE_CONTROL==='kind') source=source.replace('saved.kind !== "paper-lab-reading-list"','false');
if(process.env.NEGATIVE_CONTROL) assert.notEqual(source,original);
const w=new JSDOM(html,{url:'https://example.test/?extra=keep#library',runScripts:'outside-only'}).window,d=w.document,q=s=>d.querySelector(s),fire=(el,t)=>el.dispatchEvent(new w.Event(t,{bubbles:true}));
let network=0;w.fetch=()=>{network++;throw Error('must not fetch')};w.eval(source);
const form=q('[data-library-controls]'),control=q('[data-reading-import]'),tick=()=>new Promise(r=>setImmediate(r));
const state=()=>JSON.stringify({filters:Object.fromEntries(['search','topic','verdict','sort'].map(k=>[k,form.elements[k].value])),shown:[...d.querySelectorAll('[data-paper]')].filter(c=>!c.hidden).map(c=>c.querySelector('h3 a').getAttribute('href')),href:w.location.href});
const start=new Date().toISOString();const results=[];
async function choose(text,size){let reads=0;const file=new w.File([text],'list.json');file.text=()=>{reads++;return Promise.resolve(text)};if(size!==undefined)Object.defineProperty(file,'size',{value:size});Object.defineProperty(control,'files',{configurable:true,value:[file]});fire(control,'change');await tick();return reads;}
(async()=>{
 // Keep real generated cards populated, with a nondefault sort, to detect resets.
 const sortOption=[...form.elements.sort.options].find(o=>o.value!=='date');
 assert.ok(sortOption,'a nondefault sort is required');
 form.elements.sort.value=sortOption.value;fire(form.elements.sort,'change');
 assert.ok(JSON.parse(state()).shown.length>=2,'boundary ordering test requires at least two generated cards');
 const before=state();
 const valid={kind:'paper-lab-reading-list',schema_version:1,filters:{search:'',topic:'',verdict:'',sort:'date'}};
 const cases=[{...valid,kind:'foreign-list'},{...valid,schema_version:2},{...valid,filters:[]},{...valid,filters:{...valid.filters,extra:'x'}},{...valid,filters:{...valid.filters,topic:'unknown-topic'}},{...valid,filters:{...valid.filters,search:3}}];
 for(const payload of cases){await choose(JSON.stringify(payload));assert.equal(state(),before);assert.match(q('[data-reading-import-status]').textContent,/変更していません/);}
 results.push('six invalid schema/filter forms preserve populated results and nondefault sort');
 const reads=await choose(JSON.stringify(valid),2*1024*1024+1);assert.equal(reads,0,'oversized file must be rejected before reading');assert.equal(state(),before);results.push('oversized file rejected before File.text');
 await choose(JSON.stringify(valid)+' '.repeat(2*1024*1024+1),1);assert.equal(state(),before);assert.match(q('[data-reading-import-status]').textContent,/変更していません/);results.push('oversized returned text rejected despite dishonest size metadata');
// Exact boundary must remain accepted: valid ASCII JSON padded with whitespace.
 const encoded=JSON.stringify(valid);await choose(encoded+' '.repeat(2*1024*1024-encoded.length));
 assert.match(q('[data-reading-import-status]').textContent,/戻しました/);
 assert.equal(form.elements.sort.value,'date');
 results.push('exact 2 MiB valid JSON accepted');
 const marker='untrusted-import-marker';const hostile={...valid,papers:[{title:`<img data-${marker} src=\"https://evil.invalid/x\">`,lab_url:'https://evil.invalid/',question:marker}],html:`<script>${marker}</script>`,url:'https://evil.invalid/'};
 await choose('\uFEFF'+JSON.stringify(hostile));assert.equal(form.elements.search.value,'');assert.ok([...d.querySelectorAll('[data-paper]')].some(c=>!c.hidden));assert.match(q('[data-reading-import-status]').textContent,/戻しました/);assert.equal(d.documentElement.outerHTML.includes(marker),false);assert.equal(network,0);assert.equal(w.location.origin,'https://example.test');assert.equal(new URL(w.location).searchParams.get('extra'),'keep');results.push('BOM valid filter import ignores extra titles HTML and external URLs');
 console.log(JSON.stringify({start,end:new Date().toISOString(),status:'PASS',results,sha256:{html:crypto.createHash('sha256').update(html).digest('hex'),source:crypto.createHash('sha256').update(original).digest('hex')},scope:'JSDOM actual generated HTML and handlers. File.text shimmed; no native browser or full XSS security assurance claimed.'},null,2));
})().catch(e=>{console.error(e);process.exitCode=1}).finally(()=>w.close());
