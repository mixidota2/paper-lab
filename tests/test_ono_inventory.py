import json
import runpy
from pathlib import Path
from types import SimpleNamespace

from paper_lab.ono_inventory import widget

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers/ono-inventory-forecast-selection"


def test_paired_comparisons_and_toy_reproduce():
    module = SimpleNamespace(**runpy.run_path(str(PAPER / "run.py")))
    frozen = json.loads((PAPER / "results.json").read_text())
    rows = [module.compare(*row) for row in module.REPORTED]
    assert rows == frozen["reported_table7"]
    assert [row["reduction_pct"] for row in rows] == [1.74, 0.97, 0.70, 0.54]
    assert [row["difference"] for row in rows] == [384, 274, 278, 317]
    assert module.compare(None, 85056, 85093) == frozen["reported_table2"]
    assert [module.service(*row) for row in module.TOY] == [
        {**row, "served": tuple(row["served"])} for row in frozen["toy_service"]
    ]
    assert [row["csl_pct"] for row in frozen["toy_service"]] == [90, 60]
    assert [row["fill_pct"] for row in frozen["toy_service"]] == [96, 96]
    html = widget(frozen)
    assert html.count('<details name="ono-penalty"') == 4
    assert html.count('<details name="ono-service"') == 2
    assert html.count(' open><summary>') == 2
    assert "人工例" in html and "論文にない条件は計算しません" in html
