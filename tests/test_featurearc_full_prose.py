"""Verify reader-only changes without weakening the benchmark's behavior checks."""
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import yaml

from prose_preservation import before_featurearc_full_prose

ROOT=Path(__file__).resolve().parents[1]
REL="papers/featurearc-inherited-defects-chain-gates/"
PAPER=ROOT/REL

def before(name):
    return before_featurearc_full_prose(ROOT, REL+name, (PAPER/name).read_bytes())

class Tags(HTMLParser):
    def __init__(self, raw):
        super().__init__()
        self.events=[]
        self.feed(raw)
    def handle_starttag(self,tag,attrs):self.events.append((tag,attrs))
    def handle_endtag(self,tag):self.events.append((tag,()))

def test_reader_rewrite_preserves_numeric_records_and_full_widget_contract():
    old,new=[json.loads(s) for s in (before("results.json"),(PAPER/"results.json").read_bytes())]
    assert old.keys()==new.keys() and old["note"]!=new["note"]
    assert all(old[k]==new[k] for k in old if k!="note")
    assert len(new["synthetic"])==10 and sum(len(x["stages"]) for x in new["synthetic"])==30
    for data in new["synthetic"]:
        for x,y in zip(data["stages"],data["stages"][1:]):
            assert x["after"]==y["before"]
        assert data["chain"]["gate"]==(data["chain"]["f2p"]["passed"] and data["chain"]["p2p"]["passed"])
    a,b=[x.decode() for x in (before("experiment.md"),(PAPER/"experiment.md").read_bytes())]
    assert Tags(a).events==Tags(b).events
    embedded=re.search(r'<script id="arc-data" type="application/json">(.*?)</script>',b,re.S)
    assert embedded and json.loads(embedded[1])==new
    assert "<style>" in a and a.split("<style>",1)[1].split("</style>",1)[0]==b.split("<style>",1)[1].split("</style>",1)[0]

def test_overview_reports_paper_only_and_explains_latest_stage_vs_final_code():
    a,b=[yaml.safe_load(x) for x in (before("lab.yaml"),(PAPER/"lab.yaml").read_bytes())]
    for key in ("id","arxiv_id","urls","verification","figures","interactives"):
        assert a[key]==b[key]
    for x,y in zip(a["teaching_figures"],b["teaching_figures"],strict=True):
        for key in ("id","kind","source","locator","after"):
            assert x[key]==y[key]
        if x["kind"]=="equations":assert [s["formula"] for s in x["steps"]]==[s["formula"] for s in y["steps"]]
    overview=b["sections"]["overview"]
    assert len(overview.split("\n\n"))==2
    for s in ("73課題","263段階","62.7%","28.5%","273回のうち、69回"):
        assert s in overview
    assert not re.search(r"Lab|教材|<figure|<table",overview)
    evidence=(PAPER/"evidence.md").read_text()
    for s in ("69÷273","25.3%","72.9%","94.9%","70.2%","22.6%"):
        assert s in evidence
