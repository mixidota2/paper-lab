// DOM substitution: verifies rendering text and controls, not browser layout.
const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
const cases=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
class Node {
 constructor(tag,text=''){this.tag=tag;this.textContent=text;this.children=[];this.attrs={};this.events={};this.style={setProperty(){}};this.classList={add(){}};}
 append(...xs){this.children.push(...xs)}
 replaceChildren(...xs){this.children=xs}
 setAttribute(k,v){this.attrs[k]=v}
 addEventListener(k,v){this.events[k]=v}
}
const walk=n=>[n,...n.children.flatMap(walk)],text=n=>walk(n).map(x=>x.textContent).join(' ');
for(const c of cases){
 const mount=new Node('div'),section={dataset:{},querySelector(sel){return {'[data-mount]':mount,'[data-config]':{textContent:'{"kind":"explorer"}'},'[data-results]':{textContent:JSON.stringify(c.data)},'[data-axes]':{textContent:JSON.stringify(c.axes)},'[data-fallback]':{hidden:false}}[sel]}};
 const document={createElement:t=>new Node(t),createElementNS:(ns,t)=>new Node(t),querySelectorAll:sel=>sel==='[data-interactive]'?[section]:[]};
 vm.runInNewContext(fs.readFileSync(process.argv[3],'utf8'),{document,console});
 assert.equal(section.dataset.ready,'true',c.slug);
 const input=walk(mount).find(n=>n.tag==='input');
 for(let i=0;i<c.data.frames.length;i++){
  input.value=String(i);input.events.input();
  assert(text(mount).includes(c.axes.caption),c.slug);
  assert(text(mount).includes('比較対象・指標'),c.slug);
  const tables=walk(mount).filter(n=>n.tag==='table'),rows=tables[1].children[1].children;
  assert.equal(rows[0].children[0].textContent,c.axes.start);
  assert.equal(rows.at(-1).children[0].textContent,c.axes.start+c.data.frames[i].lines[0].values.length-1);
  assert(!/NaN|undefined/.test(text(mount)),c.slug);
 }
 const buttons=walk(mount).filter(n=>n.tag==='button');
 for(const b of buttons)b.events.click();
 assert.equal(input.value,String(c.data.default));
}
console.log(`PASS: ${cases.length} explorer displays, every saved frame, table indices, axis captions and buttons; NOT browser validation.`);
