import hashlib
import json
from pathlib import Path

import pytest
import yaml

from prose_preservation import before_unir2_full_rewrite, unir2_full_rewrite_hash

ROOT = Path(__file__).resolve().parents[1]
P = 'papers/unir2-sequence-unify/'


def test_rewrite_preserves_reviewed_overview_sources_and_results():
    lab = ROOT / (P + 'lab.yaml')
    actual = lab.read_bytes()
    new = yaml.safe_load(actual)
    prior = yaml.safe_load(before_unir2_full_rewrite(ROOT, P + lab.name, actual))
    for key in ('urls', 'verification'):
        assert new[key] == prior[key]
    assert new['sections']['overview'] == prior['sections']['overview']
    assert new['source_review']['pdf_version'] == prior['source_review']['pdf_version'] == 'v1'
    assert new['source_review']['pdf_sha256'] == prior['source_review']['pdf_sha256']
    readme = (ROOT / (P + 'README.md')).read_text()
    assert readme.count(new['sections']['overview']) == 1
    for section in ('problem', 'why_it_might_work', 'evidence', 'executable_understanding', 'results', 'what_we_verified', 'what_we_did_not_verify', 'implementation'):
        assert new['sections'][section] in readme
    for value in ('+1.177%', '+0.655%', '+2.560%', '+0.717%', '+1.567%', '+2.569%', '30.10%増え', '44.39%下がった', '3.83%減った', '7.05%増えた', '54.29%減'):
        assert value in new['sections']['evidence']
    assert '最終順位付けの前' in new['summary']


def test_exact_scope_guard_rejects_unreviewed_content():
    rows = json.loads((ROOT / 'tests/unir2_full_rewrite_hashes.json').read_text())['files']
    assert rows.keys() == {P+i for i in ('lab.yaml','README.md','method.md','mapping.md','figures/isolation.svg','figures/mask.svg','figures/sequence.svg','figures/serving.svg')}
    for path,row in rows.items():
        raw = (ROOT / path).read_bytes()
        for alg, current in [('sha256', hashlib.sha256(raw).hexdigest()),
                             ('blob', hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest())]:
            assert current == row['after_'+alg] == unir2_full_rewrite_hash(ROOT,path,row['before_'+alg],alg)
            with pytest.raises(AssertionError):
                unir2_full_rewrite_hash(ROOT,path,'0'*len(current),alg)
        if path.endswith(('lab.yaml','README.md')):
            assert hashlib.sha256(before_unir2_full_rewrite(ROOT,path,raw)).hexdigest() == row['before_sha256']
            with pytest.raises(AssertionError):
                before_unir2_full_rewrite(ROOT,path,raw+b'\n')
