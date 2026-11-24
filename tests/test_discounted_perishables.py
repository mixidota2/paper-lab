import importlib.util
import json
import pathlib
import subprocess
import shutil

import pytest

P=pathlib.Path(__file__).resolve().parents[1] / "papers/discounted-perishables-forecast"
spec=importlib.util.spec_from_file_location("discount_toy",P/"run.py")
toy=importlib.util.module_from_spec(spec)
spec.loader.exec_module(toy)

def test_two_step_identity_and_observational_counterexample():
    r=toy.compute()
    assert r==json.loads((P/"results.json").read_text())
    aa=list(toy.rows("increment"))
    bb=list(toy.rows("selection"))
    assert [x[:-1] for x in aa]==[x[:-1] for x in bb]
    assert any(r[3]==0 and r[5] for r in aa)
    for mode, (slope, regular_slope, inc, resid) in {
        "increment":(1,0,2,2), "selection":(1,0,0,2), "substitution":(0,-1,0,0)
    }.items():
        d=r["modes"][mode]
        assert (d["slope"],d["regular_slope"],d["true_increment"],d["mean_residual"])==(slope,regular_slope,inc,resid)
        assert d["total_slope"]==d["slope"]==1+d["regular_slope"]
        assert d["base_rows"]==112 and d["positive_ds_rows"]==56 and d["sticker_only_rows"]==28

@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_js_model_and_controls_match_python():
    js="""
    const vm=require('node:vm'),fs=require('node:fs'),assert=require('node:assert/strict');
    const path=process.argv[1], model=require(path+'/model.js');
    const expected=JSON.parse(fs.readFileSync(path+'/results.json')).modes;
    for(const m of model.modes){assert.deepEqual(model.evaluate(m),expected[m]);}
    const html=fs.readFileSync(path+'/interactive.html','utf8');
    const elements=Object.fromEntries([...html.matchAll(/id="([^"]+)"/g)].map(m=>[m[1],{textContent:'',handlers:{},addEventListener(k,v){this.handlers[k]=v;}}]));
    elements.mode.value='increment';
    const ctx={MarkdownToy:model,document:{getElementById:id=>elements[id]}};
    vm.runInNewContext(fs.readFileSync(path+'/interactive.js','utf8'), ctx);
    assert.equal(elements.slope.textContent,'1');
    assert.equal(elements.true_increment.textContent,'2');
    elements.mode.value='selection'; elements.mode.handlers.change();
    assert.equal(elements.slope.textContent,'1');
    assert.equal(elements.true_increment.textContent,'0');
    elements.mode.value='substitution'; elements.mode.handlers.change();
    assert.equal(elements.regular_slope.textContent,'-1');
    elements.reset.handlers.click(); assert.equal(elements.mode.value,'increment');
    assert.match(elements.counts.textContent,/112.*28.*56/);
    """
    subprocess.run(["node","-e",js,str(P)],check=True)
