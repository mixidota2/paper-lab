import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

import pytest

from paper_lab.build import build


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "papers" / "ahe-beta-receipt"


def test_ahe_state_machine_and_generated_snapshot():
    spec = importlib.util.spec_from_file_location("ahe_receipt", SOURCE / "run.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    state = module.evaluate
    Case = module.Case
    assert state(Case(True, None, "rev-B"))["toy_change_eligible"]
    assert not state(Case(True, None, "rev-B"))["work_complete"]
    assert not state(Case(True, "accepted", "rev-B"))["work_complete"]
    assert not state(Case(True, "accepted", "rev-B"))["receipt_current"]
    assert state(Case(True, "rev-B", "rev-A"))["work_complete"]
    assert not state(Case(True, "rev-B", "rev-A"))["toy_change_eligible"]
    assert not state(Case(False, "rev-B", "rev-B"))["work_complete"]
    assert not state(Case(True, "rev-A", "rev-B"), requirement_verified=False)["toy_change_eligible"]
    assert state(Case(True, "rev-A", "rev-A"), revision="rev-A")["work_complete"]
    expected = json.dumps(module.generate(), ensure_ascii=False, indent=2) + "\n"
    assert (SOURCE / "results.json").read_text(encoding="utf-8") == expected


def test_ahe_shared_javascript_renders_python_conditions(tmp_path):
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is needed for shared explorer render parity")
    papers = tmp_path / "papers"
    shutil.copytree(SOURCE, papers / SOURCE.name)
    site = tmp_path / "preview"
    build(root=ROOT, papers_dir=papers, site_dir=site)
    html = (site / "papers" / f"{SOURCE.name}.html").read_text(encoding="utf-8")
    assert "requirement-to-review" in html
    assert "execution-versus-user-observation" in html
    blobs = {key: json.loads(re.search(fr'data-{key}>([^<]+)</script>', html)[1])
             for key in ("config", "axes", "results")}
    expected = json.loads((SOURCE / "results.json").read_text(encoding="utf-8"))["explorer"]
    assert blobs["results"] == expected
    payload = tmp_path / "render-input.json"
    payload.write_text(json.dumps(blobs))
    subprocess.run([node, str(Path(__file__).with_name("ahe_receipt_render.cjs")),
                    str(ROOT / "paper_lab/templates/interactives.js"), str(payload)],
                   check=True)
