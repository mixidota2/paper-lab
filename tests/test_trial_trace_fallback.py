"""Verify static Trial by Trace content and JS progressive enhancement without a browser."""
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "papers" / "trial-by-trace-evidence-boundaries"
CONTROL_IDS = ("a", "h", "g", "b", "q", "reset")
INITIAL = ("成果 100%／基盤 50%／総合 75点\n"
           "成果全項目合格：true\n両層全項目合格：false\n"
           "調整前の基盤不合格：true\n迂回調整後：true\n"
           "候補関係：false\n因果伝播の検証：未実施")


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.nodes = {}
        self.active_pre = None
        self.in_script = False
        self.scripts = []
        self.no_script = False
        self.explanation = ""
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.nodes[attrs["id"]] = {"tag": tag, "attrs": attrs, "text": ""}
        if tag == "pre":
            self.active_pre = attrs.get("id")
        elif tag == "script":
            self.in_script = True
            self.scripts.append("")
        elif tag == "noscript":
            self.no_script = True

    def handle_endtag(self, tag):
        if tag == "pre":
            self.active_pre = None
        elif tag == "script":
            self.in_script = False
        elif tag == "noscript":
            self.no_script = False

    def handle_data(self, text):
        if self.active_pre:
            self.nodes[self.active_pre]["text"] += text
        if self.in_script:
            self.scripts[-1] += text
        if self.no_script:
            self.explanation += text


def surfaces():
    spec = importlib.util.spec_from_file_location("trial_widget", ROOT / "paper_lab/trial_trace.py")
    renderer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(renderer)
    standalone = Document((SOURCE / "index.html").read_text(encoding="utf-8"))
    script = "\n".join((SOURCE / name).read_text(encoding="utf-8") for name in ("model.js", "ui.js"))
    return [(standalone, "", script),
            (Document(renderer.widget(SOURCE)), "tt-", None)]


class TrialFallbackTests(unittest.TestCase):
    def test_static_initial_result_on_both_surfaces(self):
        for doc, prefix, _ in surfaces():
            with self.subTest(surface=prefix or "standalone"):
                self.assertEqual(doc.nodes[prefix + "out"]["text"], INITIAL)
                self.assertIn("初期条件の結果のみ", doc.explanation)
                self.assertIn("条件の変更はできません", doc.explanation)

    def test_controls_disabled_before_scripts_run(self):
        for doc, prefix, _ in surfaces():
            for name in CONTROL_IDS:
                with self.subTest(surface=prefix or "standalone", control=name):
                    self.assertIn("disabled", doc.nodes[prefix + name]["attrs"])

    def test_actual_script_all_conditions_reset_and_failed_initialization(self):
        cases = json.loads((SOURCE / "results.json").read_text(encoding="utf-8"))["cases"]
        for doc, prefix, script in surfaces():
            controls = {prefix + name: {"disabled": "disabled" in doc.nodes[prefix + name]["attrs"]}
                        for name in CONTROL_IDS}
            code = script if script is not None else "\n".join(doc.scripts)
            fixture = {"controls": controls, "prefix": prefix, "code": code,
                       "initial": INITIAL, "cases": cases}
            runner = """const assert=require('node:assert/strict'), vm=require('node:vm');
const f=FIXTURE;
function setup(broken=false){
 const nodes={}; for(const [id,attrs] of Object.entries(f.controls)) {
   const name=id.slice(f.prefix.length);
   nodes[id]={...attrs,value:name==='a'?'1':'0',checked:name==='g',events:{},
     addEventListener(e,fn){this.events[e]=fn;}};
 }
 nodes[f.prefix+'out']={textContent:f.initial};
 if(broken)nodes[f.prefix+'h'].value='invalid';
 const ctx={document:{getElementById:id=>nodes[id]}};vm.createContext(ctx);
 return {nodes,ctx};
}
const {nodes,ctx}=setup();vm.runInContext(f.code,ctx);
const get=name=>nodes[f.prefix+name];
for(const id of Object.keys(f.controls))assert.equal(nodes[id].disabled,false,id);
assert.equal(get('out').textContent,f.initial);
function expected(r){return r.admitted?
 `成果 ${r.agent*100}%／基盤 ${r.harness*100}%／総合 ${r.score}点\n成果全項目合格：${r.success}\n両層全項目合格：${r.clean}\n調整前の基盤不合格：${r.raw}\n迂回調整後：${r.adjusted}\n候補関係：${r.link}\n因果伝播の検証：未実施`:
 '測定不備：採点・帰属を保留';}
for(const c of f.cases){
 get('a').value=String(c.a);get('h').value=String(c.h);
 for(const id of ['g','b','q'])get(id).checked=c[id];
 for(const id of ['a','h','g','b','q']){
  get(id).events.change();assert.equal(get('out').textContent,expected(c.result),JSON.stringify({c,id}));
 }
 for(let repeat=0;repeat<2;repeat++){
  get('reset').events.click();assert.equal(get('out').textContent,f.initial);
  assert.equal(get('a').value,'1');assert.equal(get('h').value,'0');
  assert.equal(get('g').checked,true);assert.equal(get('b').checked,false);assert.equal(get('q').checked,false);
 }
}
const broken=setup(true);assert.throws(()=>vm.runInContext(f.code,broken.ctx));
for(const id of Object.keys(f.controls))assert.equal(broken.nodes[id].disabled,true,id);
assert.equal(broken.nodes[f.prefix+'out'].textContent,f.initial);
console.log('PASS: '+(f.prefix||'standalone')+'; 64 conditions × 5 change events; repeated reset; failed initialization');
""".replace("FIXTURE", json.dumps(fixture, ensure_ascii=False))
            with tempfile.TemporaryDirectory() as temp:
                path = Path(temp) / "trial-fallback.cjs"
                path.write_text(runner, encoding="utf-8")
                subprocess.run(["node", str(path)], check=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
