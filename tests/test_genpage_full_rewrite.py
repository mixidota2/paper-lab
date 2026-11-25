import hashlib
import json
from pathlib import Path
import re

import pytest
import yaml

from prose_preservation import before_genpage_full_rewrite, genpage_full_rewrite_hash

ROOT = Path(__file__).resolve().parents[1]
P = 'papers/genpage-netflix-homepage/'


def test_rewrite_preserves_overview_links_formula_and_figure_data():
    lab = ROOT / (P + 'lab.yaml')
    actual = lab.read_bytes()
    state = yaml.safe_load(actual)
    prior = yaml.safe_load(before_genpage_full_rewrite(ROOT, P + lab.name, actual))
    for key in ('urls', 'verification'):
        assert state[key] == prior[key]
    assert state['sections']['overview'] == prior['sections']['overview']
    assert state['source_review']['version'] == prior['source_review']['version'] == '2606.31031v2'
    assert state['source_review']['pdf_sha256'] == prior['source_review']['pdf_sha256']
    equations = lambda y: [v['formula'] for v in y['teaching_figures'][0]['steps']]
    assert equations(state) == equations(prior)
    plain, _ = state['sections']['overview'].split('\n\n<figure', 1)
    assert (ROOT / (P + 'README.md')).read_text().count(plain) == 1
    tr = re.compile(r'<tbody>.*?</tbody>', re.S)
    assert tr.findall(state['sections']['executable_understanding']) == tr.findall(prior['sections']['executable_understanding'])
    evidence = state['sections']['evidence']
    assert all(x in evidence for x in ('0.17%', '0.30%', '20%短く', '0.321と0.333', '0.884と0.879', '0.920と0.910'))


def test_exact_rewrite_guard_rejects_unreviewed_bytes():
    data = json.loads((ROOT / 'tests/genpage_full_rewrite_hashes.json').read_text())['files']
    assert data.keys() == {P+n for n in ('lab.yaml','README.md','method.md','mapping.md')}
    for path, row in data.items():
        raw = (ROOT / path).read_bytes()
        for alg, current in (('sha256', hashlib.sha256(raw).hexdigest()),
                             ('blob', hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest())):
            assert current == row['after_'+alg] == genpage_full_rewrite_hash(ROOT,path,row['before_'+alg],alg)
            with pytest.raises(AssertionError):
                genpage_full_rewrite_hash(ROOT,path,'0'*len(current),alg)
        if path.endswith(('lab.yaml','README.md')):
            assert hashlib.sha256(before_genpage_full_rewrite(ROOT,path,raw)).hexdigest() == row['before_sha256']
            with pytest.raises(AssertionError):
                before_genpage_full_rewrite(ROOT,path,raw+b'\n')
