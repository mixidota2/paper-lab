const {JSDOM}=require('jsdom');
const fs=require('node:fs'),assert=require('node:assert/strict'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(process.argv[2]||path.join(__dirname,'..'));
const html=fs.readFileSync(path.join(root,'site/index.html'),'utf8');
let source=fs.readFileSync(path.join(root,'paper_lab/templates/library.js'),'utf8');
assert.equal(source,fs.readFileSync(path.join(root,'site/assets/library.js'),'utf8'));
const digest=crypto.createHash('sha256').update(source).digest('hex');
const mutations={timer:['}, 1000);','}, 500);'],route:['saveReadingList("text")','saveReadingList()'],order:['payload.papers.forEach','payload.papers.slice().reverse().forEach'],mime:['text/plain;charset=utf-8','application/json'],cleanup:['URL.revokeObjectURL(url)','void url']};
if(process.env.NEGATIVE_CONTROL){const pair=mutations[process.env.NEGATIVE_CONTROL];assert.ok(pair);assert.ok(source.includes(pair[0]));source=source.replace(...pair);}
const start=new Date().toISOString();
async function check(url,failClick){
 const dom=new JSDOM(html,{url,runScripts:'outside-only'}),w=dom.window,d=w.document,q=s=>d.querySelector(s);
 const blobs=[],links=[],revoked=[],timers=[];w.URL.createObjectURL=blob=>{blobs.push(blob);return 'blob:test-'+blobs.length};w.URL.revokeObjectURL=url=>revoked.push(url);
 w.setTimeout=(fn,delay)=>{assert.ok(Number.isFinite(delay)&&delay>=0);timers.push(fn);return timers.length};
 w.HTMLAnchorElement.prototype.click=function(){links.push({name:this.download,href:this.href});if(failClick)throw Error('download unavailable')};
 w.eval(source);const form=q('[data-library-controls]');form.elements.sort.value='title';form.elements.sort.dispatchEvent(new w.Event('change',{bubbles:true}));
 const cards=[...d.querySelectorAll('[data-paper]')].filter(x=>!x.hidden);assert.ok(cards.length>1,'order coverage needs multiple cards');
 q('[data-reading-save-text]').click();assert.equal(blobs.length,1);assert.equal(blobs[0].type,'text/plain;charset=utf-8');assert.equal(links[0].name,'paper-lab-reading-list.txt');
 const actual=await new Promise((resolve,reject)=>{const r=new w.FileReader();r.onload=()=>resolve(r.result);r.onerror=reject;r.readAsText(blobs[0])});
 assert.equal(q('[data-reading-json]').value,actual,'copy fallback matches full UTF-8 decoded download text');assert.ok(q('[data-reading-preview]').open);assert.match(q('[data-reading-label]').textContent,/テキスト/);assert.match(actual,new RegExp('表示件数: '+cards.length+'件'));
 const lines=actual.split('\n');assert.equal(lines.filter(x=>/^\d+\. /.test(x)).length,cards.length);
 const clean=s=>s.replace(/\s+/g,' ').trim();
 cards.forEach((card,i)=>{assert.equal(lines.filter(x=>/^\d+\. /.test(x))[i],`${i+1}. ${clean(card.querySelector('.paper-title').textContent)}`)});
 const exported=lines.filter(x=>/^Lab (URL|相対パス): /.test(x));
 assert.deepEqual(exported,cards.map(c=>{const p=c.querySelector('h3 a').getAttribute('href');return url.startsWith('file:')?'Lab 相対パス: '+p:'Lab URL: '+new URL(p,'https://example.test/paper-lab/').href}));
 assert.ok(!actual.includes('fakeuser')&&!actual.includes('fakepass'));assert.equal(revoked.length,0);assert.equal(timers.length,1);timers.shift()();assert.deepEqual(revoked,['blob:test-1']);
 if(failClick)assert.match(q('[data-reading-status]').textContent,/開始できません/);
 form.elements.sort.value='date';form.elements.sort.dispatchEvent(new w.Event('change',{bubbles:true}));assert.equal(q('[data-reading-json]').value,'');assert.equal(q('[data-reading-preview]').open,false);
 dom.window.close();return {cards:cards.length,mode:url.startsWith('file:')?'portable':'https',downloadFailure:failClick};
}
(async()=>{const cases=[];cases.push(await check('https://fakeuser:fakepass@example.test/paper-lab/?unrelated=keep',false));cases.push(await check('https://example.test/paper-lab/',true));cases.push(await check('file:///tmp/lab/index.html',true));console.log(JSON.stringify({status:'PASS',start,end:new Date().toISOString(),sourceSha256:digest,cases,scope:'Generated HTML with real JSDOM/FileReader; download transport and timer controlled, not native browser download'},null,2))})().catch(e=>{console.error(e);process.exitCode=1});
