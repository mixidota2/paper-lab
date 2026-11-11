"""Saved values remain inspectable without downloading JSON. Not browser QA."""
import json
from pathlib import Path
import subprocess

import pytest

from paper_lab.display_labels import explorer_axes, explorer_view

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def cases():
    result = []
    for path in sorted((ROOT / "papers").glob("*/results.json")):
        data = json.loads(path.read_text())
        if isinstance(data, dict) and data.get("explorer"):
            slug = path.parent.name
            result.append({"slug": slug, "data": explorer_view(slug, data["explorer"]),
                           "axes": explorer_axes(slug)})
    result.append({"slug": "precision-boundaries", "axes": None, "data": {
        "default": 1, "label": "condition", "unit": "", "metric": "saved value",
        "frames": [
            {"value": 0.123456789123456, "bars": [
                {"label": "first", "value": 0.123456789123456},
                {"label": "adjacent", "value": 0.123456789123457},
                {"label": "unavailable", "value": None}],
             "lines": [{"label": "full", "values": [0.000000000123456789, -0.000000000123456789, 9007199254740991]},
                       {"label": "short", "values": [0, 1.7976931348623157e308]}], "note": "first"},
            {"value": 1, "bars": [{"label": "tiny", "value": 5e-324}, {"label": "zero", "value": 0}],
             "lines": [{"label": "single", "values": [0.3333333333333333]}], "note": "default"},
        ]}})
    return result


@pytest.mark.parametrize("scope", ["saved", "boundaries"])
def test_current_condition_table_preserves_saved_precision(cases, tmp_path, scope):
    selected = cases[:-1] if scope == "saved" else cases[-1:]
    payload = tmp_path / "cases.json"
    payload.write_text(json.dumps(selected, ensure_ascii=False))
    subprocess.run(["node", str(ROOT / "tests/explorer_precision_smoke.cjs"),
                    str(payload), str(ROOT / "paper_lab/templates/interactives.js")], check=True)
