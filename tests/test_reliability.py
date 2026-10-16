"""Bounded checks of teaching arithmetic and generated data, not paper replication."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest
import yaml

from paper_lab.build import build
from paper_lab.models import load_lab

ROOT = Path(__file__).resolve().parents[1]


def module(path):
    spec = importlib.util.spec_from_file_location('reliability_toy', ROOT / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def test_sparse_ap_finite_domain_without_training():
    toy = module('papers/tsfm-sparse-event-ranking/run.py')
    result = toy.validate()
    assert result['enumerated_labelings'] > 2000
    assert result['max_ap0_error'] < 1e-12
    assert result['pooled_counterexample_skill'] == pytest.approx(1/15)
    assert toy.metric([0, 0], [1, 2]) is None
    assert toy.metric([1, 1], [1, 2]) is None


@pytest.mark.parametrize('cap,expected', [(0, None), (12, None), (18, None), (19, 18), (23, 20)])
def test_stockout_missing_is_not_zero(cap, expected):
    toy = module('papers/_toy_common.py')
    value = toy.stockout(cap)['bars'][2]['value']
    assert value == expected
    assert json.loads(json.dumps(value)) == expected
    assert toy.bar('実測のゼロ', 0)['value'] == 0


def test_spotify_threshold_unit_and_regeneration(tmp_path):
    source = ROOT / 'papers/spotify-incremental-recommendation-causal'
    shutil.copy2(source / 'run.py', tmp_path / 'run.py')
    subprocess.run([sys.executable, str(tmp_path / 'run.py')], check=True, capture_output=True)
    actual = json.loads((tmp_path / 'results.json').read_text())
    assert actual == json.loads((source / 'results.json').read_text())
    explorer = actual['explorer']
    assert explorer['unit'] == '（確率）'
    assert explorer['frames'][explorer['default']]['value'] == .5
    assert explorer['frames'][0]['bars'][1]['value'] == 0
    assert explorer['frames'][-1]['bars'][1]['value'] == 3


def test_zalando_overall_status_preserves_narrow_checks():
    source = ROOT / 'papers/zalando-sales-event-pricing-forecast-optimize'
    results = json.loads((source / 'results.json').read_text())
    lab = yaml.safe_load((source / 'lab.yaml').read_text())
    assert results['verification']['mechanism'] == lab['verification']['mechanism'] == 'PARTIAL'
    assert all(results['checks'].values())
    assert "'mechanism':'PARTIAL'" in (source / 'run.py').read_text()


def test_browser_scripts_request_protected_chromium():
    scripts = list((ROOT / 'tests').glob('browser*'))
    assert len(scripts) == 17
    for path in scripts:
        text = path.read_text()
        assert '--no-sandbox' not in text
        assert ('chromiumSandbox: true' if path.suffix == '.cjs' else 'chromium_sandbox=True') in text


def test_generated_downloads_and_embedded_explorer_match_sources(tmp_path):
    from html.parser import HTMLParser
    from urllib.parse import unquote, urlsplit

    class Links(HTMLParser):
        def __init__(self):
            super().__init__()
            self.links = []
            self.explorers = []
            self.in_results = False
        def handle_starttag(self, tag, attrs):
            self.links.extend(v for k, v in attrs if k in ('href', 'src') and v)
            self.in_results = tag == 'script' and 'data-results' in dict(attrs)
        def handle_data(self, data):
            if self.in_results:
                self.explorers.append(json.loads(data))
        def handle_endtag(self, tag):
            if tag == 'script':
                self.in_results = False

    build(root=ROOT, site_dir=tmp_path / 'site')
    site = tmp_path / 'site'
    labs = sorted((ROOT / 'papers').glob('*/lab.yaml'))
    assert len(labs) == 100
    assert len(list((site / 'papers').glob('*.html'))) == 100
    for path in labs:
        slug = path.parent.name
        for name in ('results.json', 'run.py', 'lab.yaml'):
            source = path.parent / name
            if source.exists():
                assert source.read_bytes() == (site / 'downloads' / slug / name).read_bytes()
        load_lab(path.parent)  # Includes null/finite-value schema checks.
    for html in site.rglob('*.html'):
        parser = Links()
        parser.feed(html.read_text())
        if parser.explorers:
            source = json.loads((ROOT / "papers" / html.stem / "results.json").read_text())
            assert all(data == source["explorer"] for data in parser.explorers)
        for link in parser.links:
            url = urlsplit(link)
            if not url.scheme and not url.netloc and url.path:
                target = html.parent / unquote(url.path)
                assert target.exists(), (html, link)
    spotify = (site / 'papers/spotify-incremental-recommendation-causal.html').read_text()
    assert '0.5（確率）' in spotify
    assert '0.5件' not in spotify


def test_missing_value_fallback(tmp_path):
    source = tmp_path / 'root' / 'papers' / 'vn2-stockout-catboost'
    shutil.copytree(ROOT / 'papers/vn2-stockout-catboost', source)
    path = source / 'results.json'
    data = json.loads(path.read_text())
    data['explorer']['default'] = 0
    path.write_text(json.dumps(data))
    build(root=tmp_path / 'root', site_dir=tmp_path / 'site')
    html = (tmp_path / 'site/papers/vn2-stockout-catboost.html').read_text()
    assert '非欠品日のみ：平均：推定不能' in html
    assert '非欠品日のみ：平均：None' not in html


def test_required_gate_rejects_skip(tmp_path):
    shutil.copy2(ROOT / 'tests/conftest.py', tmp_path / 'conftest.py')
    (tmp_path / 'test_skip.py').write_text('import pytest\ndef test_missing():\n    pytest.skip("missing dependency")\n')
    run = subprocess.run([sys.executable, '-m', 'pytest', '-q', '--fail-on-skip', str(tmp_path)], cwd=tmp_path, capture_output=True, text=True)
    assert run.returncode == 1, run.stdout + run.stderr
    assert '1 skipped' in run.stdout
