"""Check the published InvEvolve replay and exactly restore its earlier prose."""
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from prose_preservation import before_invevolve_full_prose, invevolve_full_prose_hash


ROOT = Path(__file__).resolve().parents[1]
SLUG = 'invevolve-whitebox-inventory-evolution'
SOURCE = ROOT / 'papers' / SLUG


def test_rewrite_preserves_exact_prior_source():
    rows = json.loads((ROOT / 'tests/invevolve_full_prose_hashes.json').read_text())['files']
    assert set(rows) == {'paper_lab/invevolve30.py', *(f'papers/{SLUG}/{n}' for n in
                 ('README.md', 'lab.yaml', 'mapping.md', 'method.md', 'results.json', 'run.py'))}
    for path, row in rows.items():
        current = (ROOT / path).read_bytes()
        before = before_invevolve_full_prose(ROOT, path, current)
        assert hashlib.sha256(before).hexdigest() == row['before']['sha256']
        assert invevolve_full_prose_hash(ROOT, path, row['before']['sha256']) == hashlib.sha256(current).hexdigest()
        assert invevolve_full_prose_hash(ROOT, path, row['before']['blob'], 'blob') == hashlib.sha1(
            f'blob {len(current)}\0'.encode() + current).hexdigest()
        with pytest.raises(AssertionError):
            before_invevolve_full_prose(ROOT, path, current + b'\n')
        with pytest.raises(AssertionError):
            invevolve_full_prose_hash(ROOT, path, row['after']['sha256'])


def test_fractional_order_overshoot_is_covered_without_changing_replay():
    spec = importlib.util.spec_from_file_location('invevolve_standalone', SOURCE / 'run.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    gap = Fraction(7, 8)
    q = module.order(gap, alpha=.25, kp=.65, pic=True)
    assert q == 1 and 24 - gap + q == Fraction(193, 8)
    data = json.loads((SOURCE / 'results.json').read_text())
    assert data['bound'] == 114
    assert data['replay'][0]['lcb'] == 0
    assert [round(r['lcb'], 3) for r in data['replay'][1:]] == [-18.191, -18.728]
    previous = json.loads(before_invevolve_full_prose(
        ROOT, f'papers/{SLUG}/results.json', (SOURCE / 'results.json').read_bytes()))
    old_scope, new_scope = previous.pop('scope'), data.pop('scope')
    assert old_scope != new_scope and previous == data


def test_active_source_separates_search_from_final_choice():
    import yaml
    lab = yaml.safe_load((SOURCE / 'lab.yaml').read_text())
    why = lab['sections']['why_it_might_work']
    assert '現在の最良方策に対するLCBが ε+ξ 以上' in why
    assert '参照方策に対するLCBが ξ 以上' in why
    assert '同じ参照方策に対する信頼上限（UCB）' in why
    assert '形式上有効で評価を済ませていれば比較の対象になり得ます' in why
