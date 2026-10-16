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
