// Production handlers under a DOM substitute, not browser/download validation.
'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const f=JSON.parse(fs.readFileSync(process.argv[2],'utf8')), mode=process.argv[3];
assert.equal(f.cards.length,114);
for (const name of ['data-reading-list','data-reading-save','data-reading-preview','data-reading-json','data-reading-status']) assert.ok(f.fields.includes(name),name+' in generated page');
const form=new EventTarget(),clear=new EventTarget(),win=new EventTarget(),save=new EventTarget();
const panel={hidden:true},preview={open:false},text={value:''},status={textContent:''},urlStatus={hidden:true,textContent:''};
const origin=mode==='file-origin'?'file:///private/user/paper-lab/index.html':'https://example.test/paper-lab/index.html';
win.location={href:origin+'?unrelated=do-not-export#library'};
win.history={state:{preserved:true},replaceState(state,title,url){if(mode==='history-failure')throw Error('history');win.location.href=url;}};
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
 '[data-reading-list]':panel,'[data-reading-save]':save,'[data-reading-preview]':preview,'[data-reading-json]':text,'[data-reading-status]':status}[s]},querySelectorAll(){return cards},createElement(tag){assert.equal(tag,'a');return {click(){if(mode==='click')throw Error('click');clicks.push({href:this.href,download:this.download})}}}};
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
function snapshot(){
 save.dispatchEvent(new Event('click'));assert.equal(preview.open,true);const result=JSON.parse(text.value);
 assert.equal(result.schema_version,1);assert.equal(result.kind,'paper-lab-reading-list');
 const visible=parent.children.filter(c=>!c.hidden);
 assert.equal(result.paper_count,visible.length);assert.equal(result.papers.length,visible.length);
 assert.deepEqual(result.filters,Object.fromEntries(Object.entries(form.elements).map(([k,v])=>[k,v.value])));
 visible.forEach((c,i)=>{const raw=f.cards[c.id],out=result.papers[i];
  assert.equal(out.title,raw.title);assert.equal(out.question,raw.question);assert.equal(out.lab_path,raw.href);
  assert.equal(out.id,raw.href.split('/').pop().replace(/\.html$/,''));
  assert.equal(out.published_date,raw.dataset.date);assert.equal(out.reading_priority,raw.dataset.verdict);
  assert.deepEqual(out.topics,raw.dataset.topics.split('|'));
  assert.equal(out.lab_url,['file-origin','no-window','missing-url'].includes(mode)?null:new URL(raw.href,origin).href);
 });
 assert.match(result.note,/性能順位/);assert.match(result.note,/発表・公開時期/);
 assert.ok(!text.value.includes('do-not-export'));assert.ok(!text.value.includes('/private/user/'));
 if(['missing-blob','missing-url','blob','create','click'].includes(mode))assert.match(status.textContent,/開始できませんでした/);
 else {assert.match(status.textContent,/ダウンロードされない場合/);assert.equal(created.at(-1).blob.text,text.value);assert.equal(clicks.at(-1).download,'paper-lab-reading-list.json')}
 return result;
}
if(mode==='filters'){
 for(const sort of ['title','priority','date']){edit({topic:'retail-supply',sort});const r=snapshot();assert.ok(r.paper_count>1&&r.paper_count<114)}
 edit({search:'ＥＸＡＯＮＥ',topic:'',verdict:'',sort:'title'});assert.equal(snapshot().paper_count,1);
}else if(mode==='empty'){
 edit({search:'DOES_NOT_EXIST_123'});assert.equal(save.disabled,true);save.dispatchEvent(new Event('click'));assert.equal(text.value,'');assert.equal(created.length,0);
 clear.dispatchEvent(new Event('click'));assert.equal(save.disabled,false);snapshot();
}else if(mode==='ime'){
 snapshot();event('compositionstart');form.elements.search.value='draft';event('input',{isComposing:true});
 assert.equal(save.disabled,true);save.dispatchEvent(new Event('click'));assert.equal(text.value,'');
 form.elements.search.value='EXAONE';event('compositionend');assert.equal(snapshot().paper_count,1);
}else if(mode==='navigation'){
 snapshot();win.location.href=origin+'?topic=retail-supply&sort=title';win.dispatchEvent(new Event('popstate'));
 assert.equal(text.value,'');assert.equal(preview.open,false);snapshot();
 form.elements.search.value='stale';const e=new Event('pageshow');e.persisted=true;win.dispatchEvent(e);snapshot();
}else if(mode==='repeat'){
 const a=snapshot();snapshot();edit({search:'EXAONE'});assert.equal(text.value,'');assert.equal(preview.open,false);
 const b=snapshot();timers.splice(0).forEach(f=>f());assert.deepEqual(JSON.parse(text.value),b);assert.equal(a.paper_count,114);assert.equal(b.paper_count,1);
 clear.dispatchEvent(new Event('click'));assert.equal(text.value,'');assert.equal(snapshot().paper_count,114);
}else{if(mode==='history-failure')edit({search:'EXAONE'});snapshot()}
timers.splice(0).forEach(f=>f());assert.deepEqual(revoked,created.map(x=>x.url));
console.log(`PASS ${mode}: exact generated titles, order, filters, links, fallback and cleanup; no native download claim.`);
