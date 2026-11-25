import hashlib
import json
from pathlib import Path

import pytest
import yaml

from prose_preservation import before_sona_full_rewrite, sona_full_rewrite_hash

ROOT = Path(__file__).resolve().parents[1]
P = 'papers/sona-yandex-music/'


def test_rewrite_preserves_overview_sources_and_evaluation_data():
    lab = ROOT / (P + 'lab.yaml')
    actual = lab.read_bytes()
    state = yaml.safe_load(actual)
    prior = yaml.safe_load(before_sona_full_rewrite(ROOT, P + lab.name, actual))
    for key in ('urls','verification'):
        assert state[key] == prior[key]
    assert state['sections']['overview'] == prior['sections']['overview']
    assert state['source_review']['version'] == prior['source_review']['version'] == 'v2'
    assert state['source_review']['html_sha256'] == prior['source_review']['html_sha256']
    proof = lambda y: ([v['formula'] for v in y['teaching_figures'][0]['steps']],
                       [v['cells'] for v in y['teaching_figures'][1]['rows']])
    assert proof(state) == proof(prior)
    assert (ROOT / (P + 'README.md')).read_text().count(state['sections']['overview']) == 1
    for text in ('6.30%', '11.42%', '17.99%', '7.37%', '3.12ポイント', '0.6586', '0.6474'):
        assert text in state['sections']['evidence']


def test_exact_body_and_download_transition_rejects_unreviewed_bytes():
    data = json.loads((ROOT / 'tests/sona_full_rewrite_hashes.json').read_text())['files']
    assert data.keys() == {P+n for n in ('lab.yaml','README.md','method.md','mapping.md')}
    for path, row in data.items():
        raw = (ROOT / path).read_bytes()
        for alg, current in (('sha256', hashlib.sha256(raw).hexdigest()),
                             ('blob', hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest())):
            assert current == row['after_'+alg] == sona_full_rewrite_hash(ROOT,path,row['before_'+alg],alg)
            with pytest.raises(AssertionError):
                sona_full_rewrite_hash(ROOT,path,'0'*len(current),alg)
        if path.endswith(('lab.yaml','README.md')):
            assert hashlib.sha256(before_sona_full_rewrite(ROOT,path,raw)).hexdigest() == row['before_sha256']
            with pytest.raises(AssertionError):
                before_sona_full_rewrite(ROOT,path,raw+b'\n')
