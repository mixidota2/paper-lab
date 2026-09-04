"""Tests for the deterministic static Research Library build."""

from pathlib import Path

import pytest

from paper_lab.build import build
from paper_lab.models import LabError, load_all_labs, load_lab

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "scaffold-effects-gaia": "2606.08529",
    "case-against-generation-retrieval": "2607.25346",
    "unipinrec": "2606.00422",
}


def test_library_has_exactly_the_three_requested_arxiv_papers():
    labs = load_all_labs(ROOT / "papers")
    assert {lab.id: lab.arxiv_id for lab in labs} == EXPECTED
    assert all(lab.urls.arxiv == f"https://arxiv.org/abs/{lab.arxiv_id}" for lab in labs)
    assert all(lab.authors and all("et al." not in author for author in lab.authors) for lab in labs)


def test_build_is_deterministic_and_has_no_demo_content(tmp_path: Path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    build(root=ROOT, site_dir=first)
    build(root=ROOT, site_dir=second)
    assert sorted(path.relative_to(first) for path in first.rglob("*") if path.is_file()) == sorted(
        path.relative_to(second) for path in second.rglob("*") if path.is_file()
    )
    for path in first.rglob("*"):
        if path.is_file():
            assert path.read_bytes() == (second / path.relative_to(first)).read_bytes()
    html = (first / "index.html").read_text(encoding="utf-8")
    assert 'lang="ja"' in html
    assert "EXAMPLE" not in html
    assert "data-library-controls" in html
    assert (first / "assets" / "library.js").is_file()
    for paper_id, arxiv_id in EXPECTED.items():
        page = (first / "papers" / f"{paper_id}.html").read_text(encoding="utf-8")
        assert arxiv_id in page
        assert f"https://arxiv.org/abs/{arxiv_id}" in page
        assert "論文に書かれていること" in page
        assert "読書メモ" in page


def test_rejects_an_arxiv_url_that_does_not_match_the_identifier(tmp_path: Path):
    paper = tmp_path / "bad"
    paper.mkdir()
    (paper / "lab.yaml").write_text(
        '''
id: bad
arxiv_id: "2606.00422"
submitted: "2026-05-29"
title: Bad
authors: [A]
year: 2026
topics: [x]
urls: {arxiv: https://arxiv.org/abs/2606.99999}
verdict: Must Read
verification: {mechanism: NOT TESTED, performance: NOT TESTED, scaling: NOT TESTED, production_applicability: NOT TESTED}
related_threads: []
status: published
''',
        encoding="utf-8",
    )
    with pytest.raises(LabError, match="must match arxiv_id"):
        load_lab(paper)
