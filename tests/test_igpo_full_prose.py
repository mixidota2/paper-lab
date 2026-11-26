"""Keep IGPO's catalog terminology and toy numerical semantics scoped."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest
import yaml

from paper_lab.build import build
from prose_preservation import before_traffic_value_full_prose, before_igpo_full_prose, igpo_full_prose_hash


ROOT = Path(__file__).resolve().parents[1]
SLUG = 'igpo-huawei-inventory-grounded-search'
SOURCE = ROOT / 'papers' / SLUG


def test_exact_both_directions_and_shared_scope():
    rows = json.loads((ROOT / 'tests/igpo_full_prose_hashes.json').read_bytes())['files']
    assert set(rows) == {'paper_lab/display_labels.py', *(f'papers/{SLUG}/{n}' for n in
                         ('README.md', 'lab.yaml', 'method.md', 'mapping.md', 'results.json', 'run.py'))}
    for path, row in rows.items():
        current = before_traffic_value_full_prose(ROOT, path, (ROOT / path).read_bytes())
        prior = before_igpo_full_prose(ROOT, path, current)
        assert hashlib.sha256(prior).hexdigest() == row['before']['sha256']
        for key, digest in (
            ('sha256', hashlib.sha256(current).hexdigest()),
            ('blob', hashlib.sha1(f'blob {len(current)}\0'.encode() + current).hexdigest()),
        ):
            assert igpo_full_prose_hash(ROOT, path, row['before'][key], key) == digest
            with pytest.raises(AssertionError):
                igpo_full_prose_hash(ROOT, path, row['after'][key], key)
        with pytest.raises(AssertionError):
            before_igpo_full_prose(ROOT, path, current + b'\n')
    path = 'paper_lab/display_labels.py'
    now = before_traffic_value_full_prose(ROOT, path, (ROOT / path).read_bytes())
    prior = before_igpo_full_prose(ROOT, path, now)
    def map_except_target(raw):
        node = next(n for n in ast.parse(raw).body if isinstance(n, ast.Assign) and n.targets[0].id == 'LABELS')
        labels = ast.literal_eval(node.value)
        labels.pop(SLUG)
        return labels
    assert map_except_target(now) == map_except_target(prior)


def test_overview_only_changes_the_two_catalog_references(tmp_path):
    path = f'papers/{SLUG}/lab.yaml'
    raw = (ROOT / path).read_bytes()
    old = yaml.safe_load(before_igpo_full_prose(ROOT, path, raw))['sections']['overview']
    new = yaml.safe_load(raw)['sections']['overview']
    assert new == old.replace('確認した在庫に該当候補が見つからない',
                             '検索で確認できた商品情報からは該当候補が見つからない').replace(
                             '検索時に在庫を調べる', '検索時に商品カタログを調べる')
    assert new in (SOURCE / 'README.md').read_text()
    build(ROOT, site_dir=tmp_path)
    html = (tmp_path / 'papers' / f'{SLUG}.html').read_text()
    section = html.split('<section id="overview"', 1)[1].split('</section>', 1)[0]
    assert all(p in section for p in new.split('\n\n'))
    assert 'Lab' not in new and '在庫' not in new


def test_wrong_selected_item_can_evade_both_error_rates(monkeypatch):
    spec = importlib.util.spec_from_file_location('igpo_standalone', SOURCE / 'run.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    original = module.search
    def wrong_wedding(query, items, guided, ids):
        if query == 'wedding':
            return {'id': 'a', 'decision': 'match', 'fields': ['description']}
        return original(query, items, guided, ids)
    monkeypatch.setattr(module, 'search', wrong_wedding)
    result = module.evaluate(module.BASE, True)
    assert result['supported'] == 3 and result['absent'] == 1
    assert result['fni_pct'] == result['fm_pct'] == 0
    assert result['correct'] == 3
    decision = next(x for x in result['decisions'] if x['query'] == 'wedding')
    assert decision['id'] == 'a' and decision['targets_for_evaluation'] == ['c']


def test_download_diff_changes_readable_labels_only():
    path = f'papers/{SLUG}/results.json'
    raw = (ROOT / path).read_bytes()
    prior = json.loads(before_igpo_full_prose(ROOT, path, raw))
    current = json.loads(raw)
    for r in (prior, current):
        for scenario in r['scenarios']:
            del scenario['label']
        explorer = r['explorer']
        del explorer['label'], explorer['metric']
        for frame in explorer['frames']:
            del frame['note']
            for bar in frame['bars']:
                del bar['label']
    assert prior == current
