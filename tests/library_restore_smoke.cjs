// Production handlers under a DOM substitute, not browser/download validation.
'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const f=JSON.parse(fs.readFileSync(process.argv[2],'utf8')), mode=process.argv[3];
assert.equal(f.cards.length,114);
for (const name of ['data-reading-list','data-reading-save','data-reading-preview','data-reading-json','data-reading-status','data-reading-import','data-reading-import-status']) assert.ok(f.fields.includes(name),name+' in generated page');
const form=new EventTarget(),clear=new EventTarget(),win=new EventTarget(),save=new EventTarget();
const importer=new EventTarget(),importStatus={textContent:''}; importer.value=''; importer.files=[];
const panel={hidden:true},preview={open:false},text={value:''},status={textContent:''},urlStatus={hidden:true,textContent:''};
const origin=mode==='file-origin'?'file:///private/user/paper-lab/index.html':'https://example.test/paper-lab/index.html';
win.location={href:origin+'?unrelated=do-not-export#library'};
win.history={state:{preserved:true},replaceState(state,title,url){if(['history-failure','pending-history-pageshow'].includes(mode))throw Error('history');win.location.href=url;}};
form.elements=Object.fromEntries(Object.entries(f.defaults).map(([k,v])=>[k,{value:v,options:(f.options[k]||[]).map(value=>({value})),focus(){}}]));
form.reset=()=>Object.entries(f.defaults).forEach(([k,v])=>form.elements[k].value=v);
form.querySelector=()=>clear;
const cards=f.cards.map((row,i)=>({id:i,dataset:row.dataset,hidden:false,querySelector(s){
 if(s==='h3 a')return {textContent:row.question,getAttribute:()=>row.href};
 if(s==='.paper-title')return {textContent:row.title};
 throw Error('unexpected card selector: '+s);
}}));
const parent={children:[...cards],append(card){this.children.splice(this.children.indexOf(card),1);this.children.push(card)}};
cards.forEach(c=>c.parentElement=parent);
const clicks=[],created=[],revoked=[],timers=[];
const document={querySelector(s){return {'[data-library-controls]':form,'[data-result-count]':{textContent:''},'[data-empty]':{hidden:true},'[data-filter-url-status]':urlStatus,
 '[data-reading-import]':importer,'[data-reading-import-status]':importStatus,'[data-reading-list]':panel,'[data-reading-save]':save,'[data-reading-preview]':preview,'[data-reading-json]':text,'[data-reading-status]':status}[s]},querySelectorAll(){return cards},createElement(tag){assert.equal(tag,'a');return {click(){if(mode==='click')throw Error('click');clicks.push({href:this.href,download:this.download})}}}};
class Blob {constructor(parts,options){if(mode==='blob')throw Error('blob');this.text=parts.join('');this.type=options.type;}}
class FakeURL extends URL {}
FakeURL.createObjectURL=blob=>{if(mode==='create')throw Error('create');const value={url:'blob:test/'+created.length,blob};created.push(value);return value.url};
FakeURL.revokeObjectURL=url=>{revoked.push(url);if(mode==='revoke')throw Error('revoke')};
const context={document,console,setTimeout(f,ms){assert.equal(ms,1000);timers.push(f)}};
if(mode!=='no-window')context.window=win;
if(mode!=='missing-url')context.URL=FakeURL;
if(mode!=='missing-blob')context.Blob=Blob;
vm.runInNewContext(f.source,context);
assert.equal(panel.hidden,false);assert.equal(save.disabled,false);
function event(type,props={}){const e=new Event(type);Object.assign(e,props);form.dispatchEvent(e)}
function edit(values){for(const [k,v]of Object.entries(values))form.elements[k].value=v;event('input')}

function visible(){return parent.children.filter(c=>!c.hidden).map(c=>c.id)}
function filters(){return Object.fromEntries(Object.entries(form.elements).map(([k,v])=>[k,v.value]))}
function exported(){save.dispatchEvent(new Event('click'));return JSON.parse(text.value)}
function fixture(values={}){return {kind:'paper-lab-reading-list',schema_version:1,filters:{...f.defaults,...values}}}
const tick=()=>new Promise(resolve=>setImmediate(resolve));
function deferred(){let resolve,reject;const promise=new Promise((yes,no)=>{resolve=yes;reject=no});return {promise,resolve,reject}}
function choose(content,size){let calls=0;const body=typeof content==='string'?content:JSON.stringify(content);
 importer.files=[{size:size??Buffer.byteLength(body),text(){calls++;return body}}]; importer.value='fakepath';
 importer.dispatchEvent(new Event('change'));assert.equal(importer.value,'');return ()=>calls;
}
function pending(){const d=deferred();importer.files=[{size:100,text:()=>d.promise}];importer.dispatchEvent(new Event('change'));return d}
function state(){return JSON.stringify({filters:filters(),visible:visible(),url:win.location.href,preview:preview.open,text:text.value})}
(async()=>{
 if(mode==='roundtrip'){
   for(const sort of ['title','priority','date']){
    edit({search:'',topic:'retail-supply',verdict:'',sort});const original=exported();const ids=visible();
    clear.dispatchEvent(new Event('click'));choose(original);await tick();assert.deepEqual(filters(),original.filters);assert.deepEqual(visible(),ids);
    assert.equal(text.value,'');assert.equal(preview.open,false);assert.deepEqual(exported(),original);assert.match(importStatus.textContent,/検索条件を戻しました/);
   }
 }else if(['fullwidth','zero','bom','file-origin','history-failure','no-window','missing-url'].includes(mode)){
  const query=mode==='zero'?'NO_MATCH_123':'ＥＸＡＯＮＥ';const expected=mode==='zero'?0:1;
  const obj=fixture({search:query,sort:'title'});choose(mode==='bom'?'\ufeff'+JSON.stringify(obj):obj);await tick();
  assert.equal(form.elements.search.value,query);assert.equal(visible().length,expected);assert.equal(save.disabled,expected===0);
  assert.match(importStatus.textContent,/検索条件を戻しました/);
  if(mode==='history-failure')assert.match(urlStatus.textContent,/URLに残せません/);
  if(!['file-origin','history-failure','no-window','missing-url'].includes(mode))assert.equal(new URL(win.location.href).searchParams.get('search'),query);
 }else if(mode==='untrusted-extra'){
  const obj=fixture({search:'EXAONE'});obj.papers=[{title:'<script>throw 1</script>',lab_url:'https://attacker.invalid/secret'}];obj.note='malicious note';
  choose(obj);await tick();assert.equal(visible().length,1);const out=exported();assert.ok(!JSON.stringify(out).includes('attacker.invalid'));assert.ok(!JSON.stringify(out).includes('<script>'));
 }else if(mode.startsWith('invalid-')){
  edit({topic:'retail-supply',sort:'priority'});exported();const before=state();let obj=fixture({search:'EXAONE'}),size;
  switch(mode){
   case 'invalid-json':obj='{bad';break;case 'invalid-null':obj=null;break;case 'invalid-array':obj=[];break;
   case 'invalid-kind':obj.kind='other';break;case 'invalid-version':obj.schema_version=2;break;
   case 'invalid-missing':delete obj.filters.sort;break;case 'invalid-extra-filter':obj.filters.other='x';break;
   case 'invalid-filter-type':obj.filters.search={html:'x'};break;case 'invalid-array-filters':obj.filters=[];break;
   case 'invalid-topic':obj.filters.topic='not-current';break;case 'invalid-verdict':obj.filters.verdict='wrong';break;
   case 'invalid-sort':obj.filters.sort='script';break;case 'invalid-size':size=2*1024*1024+1;break;
   case 'invalid-size-negative':size=-1;break;case 'invalid-size-nan':size=NaN;break;
   case 'invalid-body-size':obj=' '.repeat(2*1024*1024+1);size=1;break;
   case 'invalid-prototype':obj=JSON.stringify(obj).replace('"sort":"date"','"__proto__":"date"');break;
  }
  const calls=choose(obj,size);await tick();assert.equal(state(),before);assert.match(importStatus.textContent,/変更していません/);
  if(['invalid-size','invalid-size-negative','invalid-size-nan'].includes(mode))assert.equal(calls(),0);
 }else if(['read-error','read-unsupported','read-nonstring'].includes(mode)){
  edit({search:'EXAONE'});exported();const before=state();
  importer.files=[{size:5,...(mode==='read-unsupported'?{}:{text:()=>mode==='read-error'?Promise.reject(Error('read')):null})}];
  importer.dispatchEvent(new Event('change'));await tick();assert.equal(state(),before);assert.match(importStatus.textContent,/読み込めませんでした/);
 }else if(mode==='pending-new-file'){
  const first=pending();const second=pending();second.resolve(JSON.stringify(fixture({search:'EXAONE'})));await tick();const before=state(),statusBefore=importStatus.textContent;
  first.resolve(JSON.stringify(fixture({topic:'retail-supply'})));await tick();assert.equal(state(),before);assert.equal(importStatus.textContent,statusBefore);
 }else if(mode==='pending-old-error'){
  const first=pending();choose(fixture({search:'EXAONE'}));await tick();const before=state(),statusBefore=importStatus.textContent;
  first.reject(Error('old'));await tick();assert.equal(state(),before);assert.equal(importStatus.textContent,statusBefore);
 }else if(mode.startsWith('pending-')){
  if(mode==='pending-history-pageshow')edit({search:'EXAONE'});
  const job=pending();
  switch(mode){
   case 'pending-edit':edit({search:'new search'});break;
   case 'pending-change':form.elements.topic.value='retail-supply';event('change');break;
   case 'pending-reset':clear.dispatchEvent(new Event('click'));break;
   case 'pending-submit':event('submit');break;
   case 'pending-compose':event('compositionstart');break;
   case 'pending-popstate':win.location.href=origin+'?search=EXAONE';win.dispatchEvent(new Event('popstate'));break;
   case 'pending-history-pageshow':
   case 'pending-pageshow':{const e=new Event('pageshow');e.persisted=true;win.dispatchEvent(e);break;}
   case 'pending-native-cancel':importer.dispatchEvent(new Event('cancel'));break;
   case 'pending-cancel':importer.files=[];importer.dispatchEvent(new Event('change'));break;
  }
  const before=state();job.resolve(JSON.stringify(fixture({topic:'retail-supply'})));await tick();assert.equal(state(),before);assert.equal(importStatus.textContent,'');
 }else if(mode==='ime'){
  event('compositionstart');form.elements.search.value='draft';event('input',{isComposing:true});const before=state();
  const calls=choose(fixture({search:'EXAONE'}));await tick();assert.equal(calls(),0);assert.equal(state(),before);assert.match(importStatus.textContent,/確定してから/);
  form.elements.search.value='';event('compositionend');choose(fixture({search:'EXAONE'}));await tick();assert.equal(visible().length,1);
 }else if(mode==='repeat'){
  const obj=fixture({search:'EXAONE'});choose(obj);await tick();const before=state();choose(obj);await tick();assert.equal(state(),before);
 }else if(mode==='preserve-url'){
  choose(fixture({search:'EXAONE'}));await tick();const url=new URL(win.location.href);assert.equal(url.searchParams.get('unrelated'),'do-not-export');assert.equal(url.hash,'#library');assert.equal(win.history.state.preserved,true);
 }else throw Error('Unknown mode '+mode);
 console.log('PASS '+mode+': generated library filters restored atomically; DOM substitute, native picker NOT TESTED.');
})().catch(error=>{console.error(error);process.exitCode=1});
