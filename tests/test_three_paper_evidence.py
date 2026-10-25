"""Regression checks for evidence boundaries, not scientific reproduction."""
import importlib.util
import json
from pathlib import Path
import pytest
from paper_lab.build import build

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('review_toy', ROOT/'papers/_toy_common.py')
toy=importlib.util.module_from_spec(spec);spec.loader.exec_module(toy)

def test_precision_without_alerts_is_undefined_and_saved():
    assert toy.critic(10)['bars'][0]['value'] is None
    assert toy.critic(10)['bars'][1]['value']==0
    saved=json.loads((ROOT/'papers/forecast-critic/results.json').read_text())
    assert saved==toy.compute('forecast-critic')
    assert saved['explorer']['default']==5
    assert saved['experiments'][0]['metrics']['適合率 (%)']==100
    assert saved['experiments'][0]['metrics']['再現率 (%)']==83.3333

def test_cost_crossover_is_toy_not_author_threshold():
    values=[b['value'] for b in toy.cost(8/9)['bars']]
    assert values[0]==pytest.approx(values[1])
    assert toy.cost(.2)['bars'][0]['value']!=toy.cost(.2)['bars'][1]['value']

def test_shelf_optimum_includes_equal_split():
    for exponent in [0,.5,1]:
        bars=toy.shelf(exponent)['bars']
        assert bars[1]['value']>=bars[0]['value']

def test_rendered_evidence_and_honest_cta(tmp_path):
    build(root=ROOT,site_dir=tmp_path/'site')
    pages=tmp_path/'site/papers'
    f=(pages/'forecast-critic.html').read_text()
    for text in ['小実験のコードを見る','閾値5','陽性6/10','334','weighted F1','120日','28日','未定義']:
        assert text in f
    assert '>実験を動かす ↓</a>' not in f
    assert 'data-interactive="explorer"' not in f
    c=(pages/'contextual-deconvolution.html').read_text()
    for text in ['Favoritaへ','1000','100 SKU','Appendix U','不整合','2607.25664v1']:
        assert text in c
    w=(pages/'whole-foods-shelf.html').read_text()
    for text in ['集計分母','CI','構成上の性質','10.1145/3764919.3770880']:
        assert text in w


def test_mapping_files_reach_rendered_sections_and_promotion_conditions(tmp_path):
    import re
    import yaml
    from paper_lab.models import load_lab
    slugs=('contextual-deconvolution','whole-foods-shelf','forecast-critic')
    for slug in slugs:
        directory=ROOT/'papers'/slug
        raw=yaml.safe_load((directory/'lab.yaml').read_text())
        assert raw['sections']['mapping']=='mapping.md'
        assert load_lab(directory).mapping_markdown==(directory/'mapping.md').read_text()
    build(root=ROOT,site_dir=tmp_path/'site')
    pages=tmp_path/'site/papers'
    def section(slug,key):
        html=(pages/f'{slug}.html').read_text()
        return re.search(r'<section[^>]*id="'+key+r'"[^>]*>(.*?)</section>',html,re.S).group(1)
    w=section('whole-foods-shelf','mapping')
    for text in ['改装の部門面積変化に上限下限','新店に過去の面積分布・費用条件','構成上の性質','継承した値']:
        assert text in w
    c=section('contextual-deconvolution','mapping')
    for text in ['SKU別平均日次費用の中央値','100 paired SKU、28日累積費用','日次費用の中央値と混ぜない','再計算をしていない']:
        assert text in c
    f=section('forecast-critic','mapping')
    assert '原典バイト列のハッシュは未取得' in f
    assert '履歴で売上増なしなら山なしを妥当・山ありを不適切' in f
    why=section('forecast-critic','why_it_might_work')
    assert '過去の販促で売上増があり' in why
    assert '過去の販促で売上増がなければ' in why
    html=(pages/'forecast-critic.html').read_text()
    assert '「販促予定があるのに山がない」' not in html
    assert '人工的に加えた局所的な突出が不自然か' in html
    assert '外生販促の4条件（Exogenous Feature Injection）は別実験' in html
    assert 'この表のSpikeのラベル作成とは区別する' in html
