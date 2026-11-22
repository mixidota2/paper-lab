"""Verify the synthetic choice example and the actual generated explorer payload."""
import importlib.util
import itertools
import json
import math
from pathlib import Path
import re
import subprocess
import sys

from paper_lab.build import build

ROOT = Path(__file__).resolve().parents[1]
SLUG = "hasterad-retail-substitution"
PAPER = ROOT / "papers" / SLUG

spec = importlib.util.spec_from_file_location("hasterad", PAPER / "run.py")
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


def test_shares_sum_to_one_for_every_subset():
    for size in range(5):
        for chosen in itertools.combinations(model.PRODUCTS, size):
            for exponent in (1.0, 0.5):
                shares = model.shares(chosen, exponent)
                assert math.isclose(sum(shares.values()), 1.0)
                assert all(0.0 <= value <= 1.0 for value in shares.values())
                assert all(shares[p] == 0 for p in model.PRODUCTS if p not in chosen)
    for exponent in (1.0, 0.5):
        assert model.shares((), exponent)["なし"] == 1.0
        assert model.shares(model.PRODUCTS, exponent) == {k: 0.2 for k in model.OPTIONS}


def test_held_out_assortment_can_reverse_decision():
    flat = model.shares(("A2", "B1", "B2"), 1)
    nest = model.shares(("A2", "B1", "B2"), 0.5)
    assert flat["A2"] == flat["なし"] == 0.25
    expected_a2 = (0.4 / math.sqrt(2)) / (0.6 + 0.4 / math.sqrt(2))
    assert math.isclose(nest["A2"], expected_a2)
    assert nest["A2"] > flat["A2"]
    assert nest["なし"] < flat["なし"]
    assert model.shares(("B1", "B2"), 1) == model.shares(("B1", "B2"), 0.5)
    flat_order = model.rank_pairs(1)
    nest_order = model.rank_pairs(0.5)
    assert len(flat_order) == len(nest_order) == 6
    assert flat_order[0][0] == ("A1", "A2")
    assert nest_order[0][0] == ("A1", "B1")
    assert math.isclose(flat_order[0][1], 10 / 3)
    assert math.isclose(nest_order[0][1], 9.5 / (2 + math.sqrt(0.5)))


def test_cli_regenerates_saved_results(tmp_path):
    script = tmp_path / "run.py"
    script.write_bytes((PAPER / "run.py").read_bytes())
    subprocess.run([sys.executable, str(script)], check=True)
    assert (tmp_path / "results.json").read_bytes() == (PAPER / "results.json").read_bytes()


def test_generated_explorer_registers_all_scenarios(tmp_path):
    site = tmp_path / "site"
    build(root=ROOT, site_dir=site)
    html = (site / "papers" / f"{SLUG}.html").read_text()
    assert "10.1002/joom.70058" in html
    assert "10.9%" in html
    assert 'data-fallback' in html and "20.0" in html
    rendered = json.loads(re.search(r'<script type="application/json" data-results>(.+?)</script>', html).group(1))
    saved = model.result()["explorer"]
    assert rendered == saved
    assert [frame["value"] for frame in rendered["frames"]] == list(range(1, 6))
    downloads = site / "downloads" / SLUG
    for name in ("lab.yaml", "run.py", "results.json"):
        assert (downloads / name).read_bytes() == (PAPER / name).read_bytes()
