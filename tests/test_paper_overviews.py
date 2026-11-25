"""The reviewed paper summaries change only the overview in source and on the page."""
import hashlib
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
    assert len(rows) == 32
    site = tmp_path / 'site'
    build(root=ROOT, site_dir=site)
    anchors = {
        'accuracy-not-service-intermittent-demand': ('20,330件', '−0.555', '63%'),
        'ahe-beta-receipt': ('38課題', '21.9%', '33.3%'),
        'assortment-observation-budget': ('顧客1人', '同じ品揃え', 'ゼロに近づく'),
        'contextual-deconvolution': ('約2割', 'XGBoost', '在庫シミュレーション'),
        'deep-cross-division': ('40.1%', '3.25%', '16.26%'),
        'discounted-perishables-forecast': ('676店舗', '1,077商品', '92.2%'),
        'episem-missing-evidence-recovery': ('6領域', '300組', '10モデル'),
        'featurearc-inherited-defects-chain-gates': ('62.7%', '28.5%', '273実行'),
        'glide-spotify-sid': ('21日間', '5.4%', '14.3%'),
        'grace-meta-ads-gtm-serving': ('23.55%', '40.42%', '条件を満たした候補'),
        'hasterad-retail-substitution': ('54店舗', 'ブランド', '10.9%'),
        'inventory-common-threshold-history': ('約1.58倍', '2倍', '累積需要の条件付き確率'),
        'ono-inventory-forecast-selection': ('85,056', '85,093', '約0.04%'),
        'query-prefix-reuse': ('44,225件', '85.82%', '71.45 ms'),
        'retail-forecast-decision-grain': ('4つ', '9つのうち7つ', 'カテゴリの計画費用'),
        'sabreagent-design-time-inventory': ('1,320事例', '0.6311', '0.5380'),
        'series-wise-validation': ('11のデータセット', '10種類', '未学習の系列'),
        'shelf-placement-options': ('5店舗・6カテゴリ', '4.0%', '推定利益'),
        'storewide-shelf-decomposition': ('16条件', '0.10〜0.29秒', '計算は含まれません'),
        'switch-hurdle-intermittent-demand': ('WRMSSE', '0.6307', '0.6403'),
        'trace-verifier-brittleness': ('25件', '0.250', '15〜36%'),
        'trajectory-deletion-prefix-cost': ('42条件', '9,400回', '26条件'),
        'trial-by-trace-evidence-boundaries': ('95課題', '3,420回', '31.1%'),
        'tsfm-sparse-event-ranking': ('5つ', '最大0.031', '30組中29組'),
        'unipinrec': ('0.95%', '0.91%', '11.1%', '63.6%'),
        'walmart-demand-transfer': ('50カテゴリ', '代表5拠点', '誤差が小さくなった'),
        'whole-foods-shelf': ('7.5%', '6.7%', 'シミュレーション'),
        'wrapped-produce-placement-controlled-trial': ('36店舗', '0.32標準偏差', '3.3ポイント'),
        'bridging-forecast-accuracy-inventory-kpis': ('0.43', '0.52', '供給量に上限がない'),
        'case-against-generation-retrieval': ('Recall@10', '4.3〜35.3%', '同じモデル規模'),
        'orpr-or-guided-pretrain-reinforce-inventory': ('331商品', '5.27日', '29.95%', '無作為割り付けではなく'),
        'spotify-incremental-recommendation-causal': ('2日以内', '7.1%', '0.37%', '統計的に有意な差はありません'),
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


def test_download_mirror_replaces_only_the_overview():
    receipt = json.loads((ROOT / 'tests/paper_overview_hashes.json').read_text())
    assert set(receipt['mirrored']) == {'papers/bridging-forecast-accuracy-inventory-kpis/README.md'}
    for path, row in receipt['mirrored'].items():
        source = (ROOT / row['source']).read_bytes()
        previous = restored_before_paper_overview(ROOT, row['source'], source)
        old, new = (yaml.safe_load(raw)['sections']['overview'].encode() for raw in (previous, source))
        download = (ROOT / path).read_bytes()
        assert download.count(new) == 1 and old not in download
        restored = download.replace(new, old)
        for alg, before, after in (
            ('sha256', hashlib.sha256(restored).hexdigest(), hashlib.sha256(download).hexdigest()),
            ('blob', *(hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest() for raw in (restored, download))),
        ):
            assert (before, after) == (row['before_' + alg], row['after_' + alg])
            assert paper_overview_rewrite_hash(ROOT, path, before, alg) == after
            with pytest.raises(AssertionError):
                paper_overview_rewrite_hash(ROOT, path, after, alg)
