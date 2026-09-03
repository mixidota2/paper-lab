"""Smoke tests for the Interactive Research Library generator."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from paper_lab.build import build, main
from paper_lab.models import (
    STANDARD_SECTIONS,
    VERIFICATION_KEYS,
    LabError,
    load_all_labs,
    load_lab,
)

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_DIR = ROOT / "papers" / "_example_demo"


def test_example_lab_yaml_loads():
    lab = load_lab(EXAMPLE_DIR)
    assert lab.id == "example-demo"
    assert lab.example is True
    assert lab.status == "published"
    assert lab.year == 2026
    assert "example" in lab.topics
    assert lab.urls.present() == []
    for key in VERIFICATION_KEYS:
        assert lab.verification.as_dict()[key] == "NOT TESTED"
    assert lab.core_idea.author_claim
    assert lab.core_idea.research_bot_interpretation
    assert lab.results is not None
    assert lab.results.get("fictional") is True
    assert "fictional" in lab.mapping_markdown.lower()
    assert "EXAMPLE" in lab.title


def test_discover_example_among_papers():
    labs = load_all_labs(ROOT / "papers")
    ids = [lab.id for lab in labs]
    assert "example-demo" in ids


def test_build_writes_index_and_paper(tmp_path: Path):
    site = tmp_path / "site"
    labs = build(root=ROOT, site_dir=site)
    assert labs
    index = site / "index.html"
    paper = site / "papers" / "example-demo.html"
    css = site / "assets" / "style.css"
    assert index.is_file()
    assert paper.is_file()
    assert css.is_file()
    assert (site / ".nojekyll").is_file()

    index_html = index.read_text(encoding="utf-8")
    assert 'id="q"' in index_html
    assert 'id="topic"' in index_html
    assert 'id="verdict"' in index_html
    assert 'id="vstatus"' in index_html
    assert "data-topics=" in index_html
    assert "data-verification=" in index_html
    assert "EXAMPLE" in index_html
    catalog = json.loads(
        index_html.split('<script type="application/json" id="catalog">', 1)[1]
        .split("</script>", 1)[0]
    )
    assert any(entry["id"] == "example-demo" for entry in catalog)

    paper_html = paper.read_text(encoding="utf-8")
    for _key, title in STANDARD_SECTIONS:
        assert f">{title}</h2>" in paper_html
        assert f'id="{_key}"' in paper_html
    assert "Author claim" in paper_html
    assert "Research Bot interpretation" in paper_html
    assert "Inference — not an author claim" in paper_html
    assert "EXAMPLE / fictional" in paper_html
    assert "Not provided in this lab." not in paper_html


def test_build_rejects_bad_verification(tmp_path: Path):
    papers = tmp_path / "papers" / "bad"
    papers.mkdir(parents=True)
    (papers / "lab.yaml").write_text(
        """
id: bad-lab
title: Bad
authors: [X]
year: 2026
topics: [x]
urls: {}
verdict: skip
verification:
  mechanism: YES
  performance: NOT TESTED
  scaling: NOT TESTED
  production_applicability: NOT TESTED
related_threads: []
status: draft
""",
        encoding="utf-8",
    )
    with pytest.raises(LabError, match="verification.mechanism"):
        load_lab(papers)


def test_main_build_to_out(tmp_path: Path):
    out = tmp_path / "out"
    code = main(["--root", str(ROOT), "--out", str(out)])
    assert code == 0
    assert (out / "index.html").is_file()
