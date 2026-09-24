"""Tests for the deterministic static Research Library build."""

from pathlib import Path

import pytest

from paper_lab.build import build
from paper_lab.models import LabError, load_all_labs, load_lab

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "spotify-incremental-recommendation-causal": "2608.26804",
    "pinterest-causal-retrieval-shopping": "2607.14161",
    "swe-serve-inference-serving-agents": "2609.26777",
    "sam-d2q-aliexpress-doc2query": "2609.04961",
    "igpo-huawei-inventory-grounded-search": "2609.04813",
    "youtube-music-llm-rationales-discovery": "2609.23877",
    "muser-baidu-long-sequence-multi-interest": "2609.23677",
    "hgenpush-kuaishou-heterogeneous-push-gr": "2607.03362",
    "t0-tsfm-forecasting-with-context": "2609.24559",

    "netflix-counterfactual-observability": "2609.22747",
    "unique-baidu-unified-retrieval-ranking": "2609.23718",
    "flashvector-unity-serving-stack-agent": "2609.17391",
    "grace-meta-ads-gtm-serving": "2608.00938",
    "icegr-baidu-intent-generative-retrieval": "2608.29652",
    "evopilot-verify-dont-trust-autoresearch": "2609.21257",
    "sidinspector-mapping-diagnostics": "2606.10375",
    "varg-tmall-value-generative-retrieval": "2609.14493",
    "accuracy-not-service-intermittent-demand": "2609.13840",
    "aura-disney-agentic-rec-diagnosis": "2609.16625",
    "lige-gr-meta-listwise": "2609.18148",
    "sona-yandex-music": "2608.11015",
    "uvr-wolt-trial-reorder": "2609.16407",
    "pushdualgen-kuaishou": "2608.07989",
    "snaplgr-snapchat": "2607.28895",
    "sidscope-diagnostics": "2608.18779",
    "ogr-once-generated-ranked": "2608.17613",
    "dream-taobao-agentic-control": "2608.09408",
    "pilot-experiment-lifecycle": "2608.18637",
    'genpage-netflix-homepage': '2606.31031',
    'unirec-chain-of-attribute': '2604.12234',
    'agentx-kuaishou': '2606.26859',
    'static-constrained-gr': '2602.22647',
    'flashtrie-gpu-beam': '2607.10044',
    'gatesid-coldstart-ranking': '2603.22916',
    'coral-meta-config-harness': '2609.02730',

    "univa-commercial-sid-gar": "2605.05803",
    "cq-sid-eg-grpo-tmall": "2605.14434",
    "intervention-paradox": "2602.03338",
    "oxygenrec-v2-idgr": "2607.24255",
    "recevolve-autonomous-rec": "2609.01622",
    "quasid-collision-qualified-sid": "2603.00632",
    "unir2-sequence-unify": "2607.24439",
    "gr4ad-ads-generative": "2602.22732",
    "auto-recsys-harness": "2609.10922",
    "oneranker-ads": "2603.02999",
    "tagr-live-sid": "2608.24034",
    "agenttether-repair": "2607.06273",
    "gryphon-ilsm": "2606.08604",
    "gryphon-v2-cascade": "2608.06213",
    "revise-recovery": "2609.00643",
    "otto-gbdt-vs-dnn-ltr": "2507.20753",
    "multi-harness-rl": "2609.04518",
    "autolr-dashen": "2609.04871",
    "sid-ope-hierarchy": "2608.28905",
    "walmart-demand-transfer": "2608.12680",
    "harness-r1": "2608.02276",
    "scaffold-effects-gaia": "2606.08529",
    "case-against-generation-retrieval": "2607.25346",
    "unipinrec": "2606.00422",
    "tgr": "2609.00986",
    "harness-bench": "2605.27922",
    "rest-sequence-ranking": "2609.01240",
    "apollopfn": "2603.15802",
    "vn2-stockout-catboost": "2601.18919",
    "contextual-deconvolution": "2607.25664",
    "forecast-critic": "2512.12059",
    "glide-spotify-sid": "2603.17540",
    "understanding-sids-isd": "2607.24995",
    "execution-state-unlearning": "2609.04875",
}


def test_library_has_the_full_registry_catalog_and_a_doi_only_paper():
    labs = load_all_labs(ROOT / "papers")
    arxiv_labs = {lab.id: lab.arxiv_id for lab in labs if lab.arxiv_id}
    assert arxiv_labs == EXPECTED
    assert len(labs) == 70
    assert all(lab.urls.arxiv == f"https://arxiv.org/abs/{lab.arxiv_id}" for lab in labs if lab.arxiv_id)
    shelf = next(lab for lab in labs if lab.id == "whole-foods-shelf")
    assert not shelf.arxiv_id
    assert shelf.doi == "10.1145/3764919.3770880"
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
    assert "2つの操作図" not in html
    assert "data-library-controls" in html
    assert (first / "assets" / "library.js").is_file()
    for paper_id, arxiv_id in EXPECTED.items():
        page = (first / "papers" / f"{paper_id}.html").read_text(encoding="utf-8")
        assert arxiv_id in page
        assert f"https://arxiv.org/abs/{arxiv_id}" in page
        assert "論文に書かれていること" in page
        assert "読書メモ" in page
        assert 'class="teaching teaching--' in page or 'class="paper-svg teaching"' in page
        assert 'id="method"' in page
        assert "モデル / 手法" in page
        assert (first / "downloads" / paper_id / "method.md").is_file()
    shelf_html = (first / "papers" / "whole-foods-shelf.html").read_text(encoding="utf-8")
    assert "10.1145/3764919.3770880" in shelf_html


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
