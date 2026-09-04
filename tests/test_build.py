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
SAMPLE_DIR = ROOT / "papers" / "scaffold-effects-gaia"
EXPECTED_IDS = {
    "scaffold-effects-gaia",
    "case-against-generation-retrieval",
    "unipinrec",
}


def test_sample_lab_yaml_loads():
    lab = load_lab(SAMPLE_DIR)
    assert lab.id == "scaffold-effects-gaia"
    assert lab.example is False
    assert lab.status == "published"
    assert lab.status_label == "公開"
    assert lab.year == 2026
    assert "ai-agent-systems" in lab.topics
    assert lab.urls.arxiv
    for key in VERIFICATION_KEYS:
        assert lab.verification.as_dict()[key] in {
            "CONFIRMED",
            "PARTIAL",
            "NOT OBSERVED",
            "NOT TESTED",
        }
    assert lab.core_idea.author_claim
    assert lab.core_idea.research_bot_interpretation
    assert lab.results is not None
    assert lab.mapping_markdown
    assert "Scaffold Effects" in lab.title
    assert "最大差は28ポイントだった" in lab.sections["overview"]


def test_discover_three_real_papers():
    labs = load_all_labs(ROOT / "papers")
    ids = {lab.id for lab in labs}
    assert ids == EXPECTED_IDS
    assert all(not lab.example for lab in labs)


def test_build_writes_index_and_paper(tmp_path: Path):
    site = tmp_path / "site"
    labs = build(root=ROOT, site_dir=site)
    assert len(labs) == 3
    index = site / "index.html"
    paper = site / "papers" / "scaffold-effects-gaia.html"
    css = site / "assets" / "style.css"
    assert index.is_file()
    assert paper.is_file()
    assert css.is_file()
    assert (site / ".nojekyll").is_file()

    index_html = index.read_text(encoding="utf-8")
    assert 'lang="ja"' in index_html
    assert 'id="q"' in index_html
    assert 'id="topic"' in index_html
    assert 'id="verdict"' in index_html
    assert 'id="vstatus"' in index_html
    assert "data-topics=" in index_html
    assert "data-verification=" in index_html
    assert "EXAMPLE" not in index_html
    assert "example-demo" not in index_html
    assert "インタラクティブ研究ライブラリ" in index_html
    assert "すべてのトピック" in index_html
    assert "未検証" in index_html
    catalog = json.loads(
        index_html.split('<script type="application/json" id="catalog">', 1)[1]
        .split("</script>", 1)[0]
    )
    catalog_ids = {entry["id"] for entry in catalog}
    assert catalog_ids == EXPECTED_IDS
    assert all(not entry.get("example") for entry in catalog)

    paper_html = paper.read_text(encoding="utf-8")
    assert 'lang="ja"' in paper_html
    for _key, title in STANDARD_SECTIONS:
        assert f">{title}</h2>" in paper_html
        assert f'id="{_key}"' in paper_html
    assert "著者の主張" in paper_html
    assert "Research Bot の解釈" in paper_html
    assert "推論 — 著者の主張ではない" in paper_html
    assert "EXAMPLE / 架空" not in paper_html
    assert "このラボでは提供されていません。" not in paper_html
    assert "概要" in paper_html
    assert "問題設定" in paper_html
    assert "原論文・公式コード対応" in paper_html
    assert "このラボの読み" in paper_html
    assert "検証の境界" in paper_html
    assert "最大差は28ポイントだった" in paper_html


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
