"""Keep the paper's evidence and the local example separate."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

from paper_lab.models import load_lab

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "papers" / "bitemporal-inventory-replay"


def test_paper_identity_source_and_scope():
    lab = load_lab(SRC)
    assert lab.arxiv_id == "2611.14671"
    assert lab.verification.performance == "NOT TESTED"
    overview = lab.sections["overview"]
    assert all(x in overview for x in ("56.8%", "86.5%", "36,672件", "94.8%"))
    assert all(x not in overview for x in ("Lab", "2日目", "3日目"))
    assert len(lab.figures) == len(lab.teaching_figures) == 1


def test_exact_standalone_replay_with_late_report_and_revisions(tmp_path):
    shutil.copyfile(SRC / "run.py", tmp_path / "run.py")
    subprocess.run([sys.executable, "-S", tmp_path / "run.py"], check=True)
    assert (tmp_path / "results.json").read_bytes() == (SRC / "results.json").read_bytes()
    out = json.loads((tmp_path / "results.json").read_bytes())
    assert [c["cutoff"] for c in out["cases"]] == [2, 4, 6]
    assert [c["answer"] for c in out["cases"]] == [
        [0, 3, 1, 3, 4], [3, 3, 1, 0, -1], [5, 0, 3, 0, -1]]
    assert [[(r[0], r[1]) for r in c["selected"]] for c in out["cases"]] == [
        [("A", 1)], [("A", 1), ("B", 1), ("C", 1)], [("A", 2), ("B", 1)]]
    for c in out["cases"]:
        assert [step[:3] for step in c["future"]] == out["schedule"]
        stock, _, last, lost, _ = c["answer"]
        assert last - lost == stock - 2
