"""The reviewed paper summaries change only the overview in source and on the page."""
from html.parser import HTMLParser
import json
from pathlib import Path

import pytest
import yaml

from paper_lab.build import build
from prose_preservation import paper_overview_rewrite_hash, restored_before_paper_overview

ROOT = Path(__file__).resolve().parents[1]


class OverviewText(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.active = False
        self.parts = []
        self.feed(html)

    def handle_starttag(self, name, attrs):
        if name == 'section' and dict(attrs).get('id') == 'overview':
            self.active = True

    def handle_endtag(self, name):
        if name == 'section' and self.active:
            self.active = False

    def handle_data(self, text):
        if self.active:
            self.parts.append(text)


def test_scoped_source_transition_and_rendered_overviews(tmp_path):
    rows = json.loads((ROOT / 'tests/paper_overview_hashes.json').read_text())['files']
    assert len(rows) == 8
    site = tmp_path / 'site'
    build(root=ROOT, site_dir=site)
    anchors = {
        'ahe-beta-receipt': ('38課題', '21.9%', '33.3%'),
        'assortment-observation-budget': ('顧客1人', '同じ品揃え', 'ゼロに近づく'),
        'discounted-perishables-forecast': ('676店舗', '1,077商品', '92.2%'),
        'hasterad-retail-substitution': ('54店舗', 'ブランド', '10.9%'),
        'shelf-placement-options': ('5店舗・6カテゴリ', '4.0%', '推定利益'),
        'storewide-shelf-decomposition': ('16条件', '0.10〜0.29秒', '計算は含まれません'),
        'unipinrec': ('約1%', '11.1%', '63.6%'),
        'wrapped-produce-placement-controlled-trial': ('36店舗', '0.32標準偏差', '3.3ポイント'),
    }
    for path, row in rows.items():
        raw = (ROOT / path).read_bytes()
        previous = restored_before_paper_overview(ROOT, path, raw)
        old, new = map(yaml.safe_load, (previous, raw))
        overview = new['sections'].pop('overview')
        assert overview != old['sections'].pop('overview')
        assert new == old
        for alg in ('sha256', 'blob'):
            assert paper_overview_rewrite_hash(ROOT, path, row['before_' + alg], alg) == row['after_' + alg]
            with pytest.raises(AssertionError):
                paper_overview_rewrite_hash(ROOT, path, row['after_' + alg], alg)
        slug = Path(path).parent.name
        html = (site / 'papers' / f'{slug}.html').read_text()
        parsed = OverviewText(html)
        text = ''.join(parsed.parts)
        assert '概要' in text
        assert overview.split('\n')[0] in text
        assert all(value in text for value in anchors[slug])
        with pytest.raises(AssertionError):
            restored_before_paper_overview(ROOT, path, raw + b'\n')
