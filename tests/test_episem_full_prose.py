"""The EpiSEM rewrite preserves the evaluation and its separately labeled, simulated Lab."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import runpy
import yaml

from prose_preservation import before_episem_full_prose

ROOT = Path(__file__).resolve().parents[1]
REL = "papers/episem-missing-evidence-recovery/"
PAPER = ROOT / REL


def old(name):
    return before_episem_full_prose(ROOT, REL + name, (PAPER / name).read_bytes())


def test_rephrasing_preserves_inputs_metrics_and_widget_controls():
    original = json.loads(old("results.json"))
    current = json.loads((PAPER / "results.json").read_text())
    assert original["note"] != current["note"]
    assert {k: v for k, v in original.items() if k != "note"} == {
        k: v for k, v in current.items() if k != "note"
    }
    assert len(current["synthetic"]["cases"]) == 480
    assert runpy.run_path(str(PAPER / "run.py"))["compute"]() == current

    before = yaml.safe_load(old("lab.yaml"))
    after = yaml.safe_load((PAPER / "lab.yaml").read_bytes())
    for key in ("id", "arxiv_id", "urls", "verification", "figures", "interactives"):
        assert before[key] == after[key]
    for a, b in zip(before["teaching_figures"], after["teaching_figures"], strict=True):
        for key in ("id", "kind", "after", "source", "locator"):
            assert a[key] == b[key]
        if a["kind"] == "equations":
            assert [s["formula"] for s in a["steps"]] == [s["formula"] for s in b["steps"]]
        if a["kind"] == "logic":
            assert [len(row["nodes"]) for row in a["rows"]] == [len(row["nodes"]) for row in b["rows"]]

    class Tags(HTMLParser):
        def __init__(self, doc):
            super().__init__()
            self.tags = []
            self.feed(doc)
        def handle_starttag(self, tag, attrs):
            self.tags.append((tag, attrs))

    assert Tags(old("experiment.md").decode()).tags == Tags((PAPER / "experiment.md").read_text()).tags


def test_overview_only_states_paper_question_comparison_results_and_assumption():
    lab = yaml.safe_load((PAPER / "lab.yaml").read_text())
    overview = lab["sections"]["overview"]
    assert len(overview.split("\n\n")) == 2
    for text in ("6分野", "300組", "10モデルすべて", "0.7〜45.3ポイント", "0.0〜58.4%", "すべて正しく返す"):
        assert text in overview
    assert not re.search(r"Lab|教材|<figure|<table|^\s*\|", overview)
    assert "教材" not in lab["summary"]
    evidence = (PAPER / "evidence.md").read_text()
    for text in ("0.6ポイント下がり", "6,052条件", "63課題（21.0%）", "7.9%", "論文の報告"):
        assert text in evidence
    assert "著者が報告したモデルの成績ではありません" in lab["sections"]["results"]
