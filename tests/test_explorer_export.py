"""Current-condition export on real saved data; no native-browser download claim."""
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess

import pytest

from paper_lab.build import build
from paper_lab.display_labels import explorer_axes, explorer_view

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def explorers():
    cases = []
    for path in sorted((ROOT / 'papers').glob('*/results.json')):
        data = json.loads(path.read_text())
        if isinstance(data, dict) and data.get('explorer'):
            slug = path.parent.name
            cases.append({'slug': slug, 'data': explorer_view(slug, data['explorer']),
                          'axes': explorer_axes(slug)})
    cases.append({'slug': 'export-edge-fixture', 'axes': {'start': -2, 'label': '時点', 'caption': '人工系列'}, 'data': {
        'default': 1, 'label': '条件 <test> & "日本語"', 'unit': '%', 'metric': '保存値', 'frames': [
            {'value': 0, 'bars': [{'label': '不明', 'value': None}], 'note': '先頭\n改行'},
            {'value': 0.123456789123, 'bars': [{'label': '=SUM(A1)', 'value': 0.00000000123456789}],
             'lines': [{'label': '系列', 'values': [-0.00000001, 1.234567891234]}], 'note': '末尾'}]}})
    return cases


@pytest.mark.parametrize('mode', ['success', 'repeated', 'missing-blob', 'missing-url', 'blob', 'create', 'click', 'revoke'])
def test_explorer_current_condition_export(mode, explorers, tmp_path):
    payload = tmp_path / 'explorers.json'
    payload.write_text(json.dumps(explorers, ensure_ascii=False))
    subprocess.run(['node', str(ROOT / 'tests/explorer_export_smoke.cjs'), str(payload),
                    str(ROOT / 'paper_lab/templates/interactives.js'), mode], check=True)


def test_generated_explorers_identify_source_paper(tmp_path):
    build(root=ROOT, site_dir=tmp_path / 'site')
    found = []
    class Sections(HTMLParser):
        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if attrs.get('data-interactive') == 'explorer':
                found.append((page.stem, attrs.get('data-paper-id')))
    for page in (tmp_path / 'site/papers').glob('*.html'):
        Sections().feed(page.read_text())
    assert found
    assert all(slug == paper_id for slug, paper_id in found)
