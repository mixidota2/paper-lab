import json
import runpy
from pathlib import Path

import pytest

from paper_lab.deep_cross_division import widget

PAPER = Path(__file__).resolve().parents[1] / "papers/deep-cross-division"
RUN = runpy.run_path(str(PAPER / "run.py"))


@pytest.mark.parametrize(("d", "mask", "expected"), [
    (2, True, (10, 0.5, 2.5, 2.5)),
    (0.005, True, (0.025, 100, 500, 1000)),
    (-0.005, True, (-0.025, -100, -500, -1000)),
    (-0.005, False, (-0.025, 0, 0, -1000)),
    (0, True, (0, 0, 0, None)),
])
def test_score(d, mask, expected):
    assert tuple(RUN["score"](5, d, mask).values()) == expected


def test_holdout_and_persisted_inputs():
    result = RUN["build"]()
    assert result == json.loads((PAPER / "results.json").read_text())
    toy = result["toy"]
    assert {row["d"] for row in toy["train"]}.isdisjoint(row["d"] for row in toy["heldout"])
    assert toy["fits"]["product"]["heldout_rmse"] == pytest.approx(20.047182069522176)
    assert toy["fits"]["term"] == {"weight": 1, "train_rmse": 0, "heldout_rmse": 0}
    assert result["table5"]["rows"]["view_time"] == [5589, 5681, 5152, 5629]
    rendered = widget(PAPER)
    assert '<script type="application/json" id="dcdn-data">' in rendered
    assert (PAPER / "interactive.js").read_text() in rendered


def test_published_standalone_source_contains_exact_widget():
    text = (PAPER / "interactive.html").read_text()
    assert text.count(widget(PAPER)) == 1
