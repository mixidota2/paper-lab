"""A language rewrite must preserve the checked experiment and figure structure."""
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import runpy
import yaml

from prose_preservation import before_execution_state_unlearning_full_prose

ROOT=Path(__file__).resolve().parents[1]
REL="papers/execution-state-unlearning/"
PAPER=ROOT/REL

def previous(name):
    return before_execution_state_unlearning_full_prose(ROOT,REL+name,(PAPER/name).read_bytes())

def test_independent_replay_constraints_and_all_json_measurements_are_preserved():
    data=json.loads((PAPER/"results.json").read_bytes())
    prior=json.loads(previous("results.json"))
    assert data.keys()==prior.keys()
    assert {k:v for k,v in data.items() if k not in ("note","probe_contract")} == {
        k:v for k,v in prior.items() if k not in ("note","probe_contract")
    }
    assert all(data[k]!=prior[k] for k in ("note","probe_contract"))
    code=runpy.run_path(str(PAPER/"run.py"))
    assert data==code["compute"]()
    for tau in range(1,13):
        for checkpoint in range(tau):
            r=code["experiment"](12,tau,checkpoint)["metrics"]
            replay=r["選択的再実行"]
            assert replay["same_runtime_as_reference"]
            assert replay["safe_total"]==78 and replay["recomputed_steps"]==12-checkpoint
            assert replay["leak_at_probes"]==replay["behavioral_mismatch"]==0
            assert r["全文字列の除去"]["behavioral_mismatch"]==1

def test_figures_only_change_words_and_paper_overview_excludes_own_experiment():
    a=yaml.safe_load(previous("lab.yaml"))
    b=yaml.safe_load((PAPER/"lab.yaml").read_bytes())
    assert a["verification"]==b["verification"] and a["urls"]==b["urls"]
    for x,y in zip(a["figures"],b["figures"],strict=True):
        assert x["path"]==y["path"] and x["after"]==y["after"] and x["title"]!=y["title"]
        z=x["path"]
        xx,yy=[ET.fromstring(t) for t in (previous(z),(PAPER/z).read_bytes())]
        assert [(e.tag,e.attrib,e.text if (e.text or "").isnumeric() else None) for e in xx.iter()] == [
                (e.tag,e.attrib,e.text if (e.text or "").isnumeric() else None) for e in yy.iter()]
    for x,y in zip(a["teaching_figures"],b["teaching_figures"],strict=True):
        assert x["id"]==y["id"] and x["after"]==y["after"] and x["source"]==y["source"]
        assert [s["formula"] for s in x["steps"]]==[s["formula"] for s in y["steps"]]
    t=b["sections"]["overview"]
    assert len(t.split("\n\n"))==2
    for phrase in ("80%","32%","モデルの重みは変えません","選択への影響","候補を避けた割合"):
        assert phrase in t
    assert not any(phrase in t for phrase in ("Lab","教材","操作図","<table","<figure"))
