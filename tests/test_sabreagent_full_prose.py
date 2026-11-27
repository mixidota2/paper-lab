"""Exact reversible sources and the SabreAgent-specific teaching claims."""
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest
import yaml

from prose_preservation import before_or_transformer_all_full_prose, before_sabreagent_full_prose, sabreagent_full_prose_hash


ROOT = Path(__file__).resolve().parents[1]
SLUG = 'sabreagent-design-time-inventory'
SOURCE = ROOT / 'papers' / SLUG


def test_exact_prior_kept_for_all_readable_sources():
    records = json.loads((ROOT / 'tests/sabreagent_full_prose_hashes.json').read_text())['files']
    assert set(records) == {'paper_lab/batch29.py', *(f'papers/{SLUG}/{n}' for n in
                            ('lab.yaml', 'README.md', 'method.md', 'mapping.md', 'run.py', 'results.json'))}
    for path, record in records.items():
        current = before_or_transformer_all_full_prose(ROOT,path,(ROOT / path).read_bytes())
        prior = before_sabreagent_full_prose(ROOT, path, current)
        for format, value in (
            ('sha256', hashlib.sha256(current).hexdigest()),
            ('blob', hashlib.sha1(f'blob {len(current)}\0'.encode() + current).hexdigest()),
        ):
            assert sabreagent_full_prose_hash(ROOT, path, record['before'][format], format) == value
            with pytest.raises(AssertionError):
                sabreagent_full_prose_hash(ROOT, path, record['after'][format], format)
        assert hashlib.sha256(prior).hexdigest() == record['before']['sha256']
        with pytest.raises(AssertionError):
            before_sabreagent_full_prose(ROOT, path, current + b'\n')


def test_signed_shortage_and_real_order_are_different_quantities():
    spec = importlib.util.spec_from_file_location('sabreagent_standalone', SOURCE / 'run.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    initial, arrivals, demand, target = 0, [0, 8], [5, 2], 3
    stock, lost, _ = module.project(initial, arrivals, demand)
    signed = sum(demand) + target - initial - sum(arrivals), target - stock
    assert (*signed, lost) == (2, -3, 5)
    assert signed[0] - signed[1] == lost
    assert max(0, signed[0]) - max(0, signed[1]) == 2 < lost
    raw = (SOURCE / 'results.json').read_bytes()
    old = json.loads(before_sabreagent_full_prose(ROOT, f'papers/{SLUG}/results.json', raw))
    new = json.loads(raw)
    for q in (old, new):
        del q['note']
        for frame in q['frames']:
            del frame['label']
    assert old == new


def test_sabre_copy_does_not_claim_untouched_test_or_cost_reduction():
    sections = yaml.safe_load((SOURCE / 'lab.yaml').read_bytes())['sections']
    assert '係数そのものは検証データで当てはめました' in sections['evidence']
    assert '4つの集計診断' in sections['evidence']
    assert '開発がテストから完全に独立していたわけではありません' in sections['evidence']
    assert '費用の相対的な削減率ではありません' in sections['evidence']
    assert '次の期は実行しません' in sections['executable_understanding']


def test_shared_renderer_changes_are_confined_to_sabreagent():
    path = 'paper_lab/batch29.py'
    data = before_or_transformer_all_full_prose(ROOT,path,(ROOT / path).read_bytes())
    prior = before_sabreagent_full_prose(ROOT, path, data)
    # The two other branches and the plotting helper are exactly the old source.
    for code in (data, prior):
        assert code.count(b"        elif kind=='or':") == 1
        assert code.count(b'        frames.append(content)') == 1
    before_start = b"        elif kind=='or':"
    before_end = b'        frames.append(content)'
    assert data.split(before_start,1)[1].split(before_end,1)[0] == prior.split(before_start,1)[1].split(before_end,1)[0]
    assert data.split(b'def widget',1)[0] == prior.split(b'def widget',1)[0]
