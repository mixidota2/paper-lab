"""Exact historical identities and scientific/experiment boundaries on the live rewrite."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess

import pytest
import yaml

from prose_preservation import before_forecast_critic_all_full_prose, before_apollopfn_full_prose, contextual_full_rewrite_hash, restored_before_paper_overview

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'papers/contextual-deconvolution'
BASE = 'f7793bc88ab49a347b43e74a9ff45e77bb6fe5ad'
NAMES = {'mapping.md', 'method.md', 'lab.yaml'}


def historical(path):
    return subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT)


def test_rewrite_retains_source_urls_equations_metadata_and_code():
    files = [f'{SLUG}/{n}' for n in NAMES]
    for path in files:
        def links(raw):
            return Counter(re.findall(rb'https?://[^\s)\x27]+', raw))
        assert links((ROOT / path).read_bytes()) == links(historical(path))
    path = f'{SLUG}/lab.yaml'
    a, b = map(yaml.safe_load, [historical(path), (ROOT / path).read_bytes()])
    reader = {'summary','question','core_idea','sections','interactives','source_review','teaching_figures'}
    assert {k:v for k,v in a.items() if k not in reader} == {k:v for k,v in b.items() if k not in reader}
    assert a['sections'].keys() == b['sections'].keys()
    assert [a['sections'][k] for k in ('method','mapping')] == [b['sections'][k] for k in ('method','mapping')]
    assert [a['source_review'][k] for k in ('checked','url')] == [b['source_review'][k] for k in ('checked','url')]
    assert [i['kind'] for i in a['interactives']] == [i['kind'] for i in b['interactives']]
    for x,y in zip(a['teaching_figures'], b['teaching_figures'], strict=True):
        assert all(x[k] == y[k] for k in ('id','kind','after','source','locator'))
        assert [s['formula'] for s in x.get('steps',())] == [s['formula'] for s in y.get('steps',())]
    for path in (f'{SLUG}/run.py', f'{SLUG}/results.json', 'papers/_toy_common.py'):
        current = before_apollopfn_full_prose(ROOT, path, before_forecast_critic_all_full_prose(ROOT,path,(ROOT / path).read_bytes()))
        assert current == historical(path)
    assert a['teaching_figures'][1]['rows'] == b['teaching_figures'][1]['rows']
    assert a['teaching_figures'][1]['columns'] == b['teaching_figures'][1]['columns']
    evidence = b['sections']['evidence']
    assert all(x in evidence for x in ('Tuned XGBoost','約0.20','0.17〜0.25','1000 SKU','100 SKU','対象件数は確定しない','非負の比','負値','Favorita'))


@pytest.mark.parametrize('algo', ['sha256', 'blob'])
def test_archive_and_current_text_identities_are_exact(algo):
    manifest = json.loads((ROOT / 'tests/contextual_full_rewrite_hashes.json').read_text())
    assert manifest['base'] == BASE
    assert set(manifest['files']) == {f'{SLUG}/{n}' for n in NAMES}
    def digest(raw):
        if algo == 'sha256':
            return hashlib.sha256(raw).hexdigest()
        return hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()
    for path in manifest['files']:
        current = restored_before_paper_overview(ROOT, path, (ROOT / path).read_bytes())
        assert contextual_full_rewrite_hash(ROOT,path,digest(historical(path)),algo) == digest(current)
        with pytest.raises(AssertionError):
            contextual_full_rewrite_hash(ROOT,path,digest(current+b'\n'),algo)
