// Production handlers under a DOM substitute, not browser/download validation.
'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const f=JSON.parse(fs.readFileSync(process.argv[2],'utf8')), mode=process.argv[3];
assert.equal(f.cards.length,114);
for (const name of ['data-reading-save-text','data-reading-label','data-reading-list','data-reading-save','data-reading-preview','data-reading-json','data-reading-status']) assert.ok(f.fields.includes(name),name+' in generated page');
const form=new EventTarget(),clear=new EventTarget(),win=new EventTarget(),save=new EventTarget(),saveText=new EventTarget();
const label={textContent:''};
const panel={hidden:true},preview={open:false},text={value:''},status={textContent:''},urlStatus={hidden:true,textContent:''};
const origin=mode==='file-origin'?'file:///private/user/paper-lab/index.html':'https://example.test/paper-lab/index.html';
win.location={href:mode==='credentials'?'https://private-user:private-pass@example.test/paper-lab/?unrelated=do-not-export#library':origin+'?unrelated=do-not-export#library'};
if(mode==='multiline'){f.cards[0].dataset.search='line one\nline two \"quote\"';f.cards[0].title='title\nwith\tspaces';f.cards[0].question='question\r\nwith line';}
win.history={state:{preserved:true},replaceState(state,title,url){if(mode==='history-failure')throw Error('history');win.location.href=url;}};
form.elements=Object.fromEntries(Object.entries(f.defaults).map(([k,v])=>[k,{value:v,options:(f.options[k]||[]).map(value=>({value,textContent:f.labels[k][value]})),focus(){}}]));
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
 '[data-reading-list]':panel,'[data-reading-save]':save,'[data-reading-save-text]':saveText,'[data-reading-label]':label,'[data-reading-preview]':preview,'[data-reading-json]':text,'[data-reading-status]':status}[s]},querySelectorAll(){return cards},createElement(tag){assert.equal(tag,'a');return {click(){if(mode==='click')throw Error('click');clicks.push({href:this.href,download:this.download})}}}};
class Blob {constructor(parts,options){if(mode==='blob')throw Error('blob');this.text=parts.join('');this.type=options.type;}}
class FakeURL extends URL {}
FakeURL.createObjectURL=blob=>{if(mode==='create')throw Error('create');const value={url:'blob:test/'+created.length,blob};created.push(value);return value.url};
FakeURL.revokeObjectURL=url=>{revoked.push(url);if(mode==='revoke')throw Error('revoke')};
const context={document,console,setTimeout(f,ms){assert.equal(ms,1000);timers.push(f)}};
if(mode!=='no-window')context.window=win;
if(mode!=='missing-url')context.URL=FakeURL;
if(mode!=='missing-blob')context.Blob=Blob;
vm.runInNewContext(f.source,context);
assert.equal(panel.hidden,false);assert.equal(save.disabled,false);assert.equal(saveText.disabled,false);
function event(type,props={}){const e=new Event(type);Object.assign(e,props);form.dispatchEvent(e)}
function edit(values){for(const [k,v]of Object.entries(values))form.elements[k].value=v;event('input')}
function snapshot(){
 save.dispatchEvent(new Event('click'));
 const result=JSON.parse(text.value); assert.match(label.textContent,/JSON$/);
 saveText.dispatchEvent(new Event('click'));assert.equal(preview.open,true);assert.match(label.textContent,/テキスト$/);
 const visible=parent.children.filter(c=>!c.hidden), lines=text.value.split('\n');
 assert.equal(result.paper_count,visible.length);
 assert.equal(lines[0],'研究ライブラリ 読書リスト');
 assert.equal(lines[1],`表示件数: ${visible.length}件`);
 assert.equal(lines[2],`検索語: ${JSON.stringify(form.elements.search.value)}`);
 assert.equal(lines[3],`テーマ: ${f.labels.topic[form.elements.topic.value]}`);
 assert.equal(lines[4],`読む優先度: ${f.labels.verdict[form.elements.verdict.value]}`);
 assert.equal(lines[5],`並べ替え: ${f.labels.sort[form.elements.sort.value]}`);
 assert.equal(lines[7],result.note.replace("lab_pathは", "Lab 相対パスは"));assert.match(lines[7],/性能順位/);assert.match(lines[7],/発表・公開時期/);
 const line=value=>String(value).replace(/\s+/g,' ').trim();
 assert.equal(lines.length,9+visible.length*6);
 visible.forEach((card,i)=>{
   const raw=f.cards[card.id],out=result.papers[i],offset=9+i*6;
   assert.equal(lines[offset],`${i+1}. ${line(raw.title)}`);
   assert.equal(lines[offset+1],`問い: ${line(raw.question)}`);
   assert.equal(lines[offset+2],`テーマ: ${raw.dataset.topics.split('|').map(t=>f.labels.topic[t]).join('、')}`);
   assert.equal(lines[offset+3],`読む優先度: ${out.reading_priority} / 発表・公開時期: ${out.published_date}`);
   assert.equal(lines[offset+4],`${out.lab_url?'Lab URL':'Lab 相対パス'}: ${out.lab_url||out.lab_path}`);
   assert.equal(lines[offset+5],'');
 });
 assert.ok(!text.value.includes('do-not-export'));assert.ok(!text.value.includes('/private/user/'));
 assert.ok(!text.value.includes('private-user'));assert.ok(!text.value.includes('private-pass'));
 if(['missing-blob','missing-url','blob','create','click'].includes(mode))assert.match(status.textContent,/開始できませんでした/);
 else {assert.match(status.textContent,/件の保存用テキスト/);assert.match(status.textContent,/ダウンロードされない場合/);assert.equal(created.at(-1).blob.text,text.value);assert.equal(created.at(-1).blob.type,'text/plain;charset=utf-8');assert.equal(clicks.at(-1).download,'paper-lab-reading-list.txt')}
 const plain=text.value;
 save.dispatchEvent(new Event('click'));assert.deepEqual(JSON.parse(text.value),result);assert.match(label.textContent,/JSON$/);
 saveText.dispatchEvent(new Event('click'));assert.equal(text.value,plain);
 return result;
}
if(mode==='filters'){
 for(const sort of ['title','priority','date']){edit({topic:'retail-supply',sort});const r=snapshot();assert.ok(r.paper_count>1&&r.paper_count<114)}
 edit({search:'ＥＸＡＯＮＥ',topic:'',verdict:'',sort:'title'});assert.equal(snapshot().paper_count,1);
}else if(mode==='empty'){
 edit({search:'DOES_NOT_EXIST_123'});assert.equal(save.disabled,true);assert.equal(saveText.disabled,true);saveText.dispatchEvent(new Event('click'));save.dispatchEvent(new Event('click'));assert.equal(text.value,'');assert.equal(created.length,0);
 clear.dispatchEvent(new Event('click'));assert.equal(save.disabled,false);snapshot();
}else if(mode==='ime'){
 snapshot();event('compositionstart');form.elements.search.value='draft';event('input',{isComposing:true});
 assert.equal(save.disabled,true);assert.equal(saveText.disabled,true);saveText.dispatchEvent(new Event('click'));save.dispatchEvent(new Event('click'));assert.equal(text.value,'');
 form.elements.search.value='EXAONE';event('compositionend');assert.equal(snapshot().paper_count,1);
}else if(mode==='navigation'){
 snapshot();win.location.href=origin+'?topic=retail-supply&sort=title';win.dispatchEvent(new Event('popstate'));
 assert.equal(text.value,'');assert.equal(preview.open,false);snapshot();
 form.elements.search.value='stale';const e=new Event('pageshow');e.persisted=true;win.dispatchEvent(e);snapshot();
}else if(mode==='repeat'){
 const a=snapshot();snapshot();edit({search:'EXAONE'});assert.equal(text.value,'');assert.equal(preview.open,false);
 const b=snapshot();const latest=text.value;timers.splice(0).forEach(f=>f());assert.equal(text.value,latest);assert.equal(a.paper_count,114);assert.equal(b.paper_count,1);
 clear.dispatchEvent(new Event('click'));assert.equal(text.value,'');assert.equal(snapshot().paper_count,114);
}else if(mode==='multiline'){edit({search:'line one\nline two \"quote\"'});assert.equal(snapshot().paper_count,1);
}else{if(mode==='history-failure')edit({search:'EXAONE'});snapshot()}
timers.splice(0).forEach(f=>f());assert.deepEqual(revoked,created.map(x=>x.url));
console.log(`PASS ${mode}: text/JSON format switching, visible order, translated labels, privacy, fallback and cleanup; no native download claim.`);
