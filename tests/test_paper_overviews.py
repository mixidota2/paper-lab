"""The reviewed paper summaries change only the overview in source and on the page."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path

import pytest
import yaml

from paper_lab.build import build
from prose_preservation import before_pinterest_full_rewrite, paper_overview_rewrite_hash, restored_before_paper_overview

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
    assert len(rows) == 66
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
        'constrained-deep-inventory-fbsde': ('50商品', '0.001%未満', '81.5%'),
        'deepstock-policy-regularized-inventory-drl': ('2025年4月', '海外商品で1日', '国内商品で2日', 'シミュレーション'),
        'exaone-demand-routed-tsfm': ('22のデータセット', '1.0667', '1.0742', '1.0818'),
        'reasoncast-agentic-demand-forecasting': ('33.10%', '32.63%', '7.91%', '9.59%'),
        'apollopfn': ('モデルの重みは更新しません', '平均5.7%', 'TabPFN-TS'),
        'evaluation-choices-forecasting-leaderboard': ('19手法中2位', '25手法中23位', '買い手別で17位'),
        'forecast-critic': ('0.88', '0.97', '少なくとも10%'),
        'quasid-collision-qualified-sid': ('TIGER', '0.0211', '0.0230'),
        'scope-coupled-supply-chain-policies': ('18のシナリオ', '1.58%', '実現利益'),
        'sidinspector-mapping-diagnostics': ('23,742商品', '97.7%', 'ReSID/GAOQ'),
        'flashtrie-gpu-beam': ('8億件', '46.3 ms', '1.9 ms', '3.3 ms', '0.71%'),
        'invevolve-whitebox-inventory-evolution': ('25件', '13件', '30件中20件', 'シミュレーション'),
        'netflix-counterfactual-observability': ('11件', '0.8212', '新しい枠'),
        'rest-sequence-ranking': ('1.31%', '11.93%', '50 ms', '実収益の増加率ではありません'),
        'angle-tencent-one-step-retrieval': ('2.16%', '5.01%', '精密ランキング'),
        'gr4ad-ads-generative': ('4.28%', '117%', 'DLRM', 'OneRec-V2', '4億人'),
        'gryphon-v2-cascade': ('7分以上', '1.41%', '1.62%', '応答時間は同程度'),
        'proximal-residual-value-inventory-placement': ('5.0%', '0.950', '配送・移送費用'),
        'intervention-paradox': ('0.94', '64%から38%', '5.8%から8.6%'),
        'igpo-huawei-inventory-grounded-search': ('14日間', '3.17%', '1,000件', '38.9%'),
        'isomorph-supply-chain-digital-twin': ('13拠点', '16本', '0.828', '0.721'),
        'agent-reasoning-forgetting-externalized-state': ('67.31%', '36.15%', '0.7376', '0.7178'),
        'autolr-dashen': ('1,586件', '公開判断', '9件', '何割が本番で改善したかは分かりません'),
        'beyond-scalar-dsi-watchtime': ('視聴時間の分布', '1.9〜8.5%', '公開データ3種類'),
        'onetrans-v2-cascade-unification': ('3段階', '利用者を無作為', '9.74%', '共有だけ'),
        'retailbench-long-horizon-store-agents': ('7つのモデル', '180日', '24,350.98', '131,510.42', '平均や実店舗の成績ではありません'),
        'traffic-forecast-to-decision-value': ('29日分', '4.03%', '3.92%', '9交差点のうち2地点', '6.09%', '3.39%', '3.78%', 'すべて0をまたぎました'),
        'vn2-stockout-catboost': ('CatBoost', '全6回の総合で1位', '4.334ユーロ', '3.763ユーロ', '13.2%'),
        'zalando-sales-event-pricing-forecast-optimize': ('12市場', '23件', '無作為に割り付け', '6.00%', '0.79〜11.03%', '対照と同等だったとまでは言えない'),
        'sim2real-policy-conditioned-inbound-forecast': ('同じ構造', '新ルール導入後の入荷実績', '1.2〜3.1ポイント', '12.5〜18.7ポイント'),
        'linkedin-prediction-to-incrementality': ('8週間', '無作為', '7.20%', '0.31〜14.09%', 'Transformer単体'),
        'pinterest-causal-retrieval-shopping': ('しきい値', '約40%', '0.26%', '1.10%', '85%減らしたのは別の群'),
        'otto-gbdt-vs-dnn-ltr': ('8週間', '1.86%', '0.56%', '1.48%', 'A/Bテストには含まれていません'),
        'uvr-wolt-trial-reorder': ('10カ国', '2週間', '5.5%', '0.16%', '6カ国中5カ国'),
    }
    for path, row in rows.items():
        raw = before_pinterest_full_rewrite(ROOT, path, (ROOT / path).read_bytes())
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
    assert set(receipt['mirrored']) == {f'papers/{slug}/README.md' for slug in (
        'bridging-forecast-accuracy-inventory-kpis',
        'constrained-deep-inventory-fbsde',
        'deepstock-policy-regularized-inventory-drl',
        'reasoncast-agentic-demand-forecasting',
        'scope-coupled-supply-chain-policies',
        'flashtrie-gpu-beam',
        'invevolve-whitebox-inventory-evolution',
        'beyond-scalar-dsi-watchtime',
        'onetrans-v2-cascade-unification',
        'angle-tencent-one-step-retrieval',
        'gr4ad-ads-generative',
        'proximal-residual-value-inventory-placement',
        'intervention-paradox',
        'igpo-huawei-inventory-grounded-search',
        'isomorph-supply-chain-digital-twin',
        'agent-reasoning-forgetting-externalized-state',
        'retailbench-long-horizon-store-agents',
        'traffic-forecast-to-decision-value',
        'zalando-sales-event-pricing-forecast-optimize',
        'sim2real-policy-conditioned-inbound-forecast',
        'linkedin-prediction-to-incrementality',
        'pinterest-causal-retrieval-shopping',
        'uvr-wolt-trial-reorder',
    )}
    for path, row in receipt['mirrored'].items():
        source = before_pinterest_full_rewrite(ROOT, row['source'], (ROOT / row['source']).read_bytes())
        previous = restored_before_paper_overview(ROOT, row['source'], source)
        old, new = (yaml.safe_load(raw)['sections']['overview'].encode() for raw in (previous, source))
        if 'prior_mirror' in row:
            slug = Path(path).parent.name
            prior_paragraphs = {
                'proximal-residual-value-inventory-placement': 2,
                'retailbench-long-horizon-store-agents': 1,
                'pinterest-causal-retrieval-shopping': 1,
            }
            assert slug in prior_paragraphs
            old = row['prior_mirror'].encode()
            assert len(old.decode().split('\n\n')) == prior_paragraphs[slug]
        download = before_pinterest_full_rewrite(ROOT, path, (ROOT / path).read_bytes())
        assert download.count(new) == 1
        assert download.count(old) == int(Path(path).parent.name in {
            'reasoncast-agentic-demand-forecasting', 'scope-coupled-supply-chain-policies', 'onetrans-v2-cascade-unification',
        })
        restored = download.replace(new, old)
        for alg, before, after in (
            ('sha256', hashlib.sha256(restored).hexdigest(), hashlib.sha256(download).hexdigest()),
            ('blob', *(hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest() for raw in (restored, download))),
        ):
            assert (before, after) == (row['before_' + alg], row['after_' + alg])
            assert paper_overview_rewrite_hash(ROOT, path, before, alg) == after
            with pytest.raises(AssertionError):
                paper_overview_rewrite_hash(ROOT, path, after, alg)
