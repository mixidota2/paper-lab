"""Semantic-ID body revisions preserve both verified overviews and toy diagnostics."""
import hashlib
import json
from pathlib import Path
from xml.etree import ElementTree

import pytest
import yaml

from prose_preservation import before_semantic_id_pair_full_rewrite, semantic_id_pair_full_rewrite_hash

ROOT = Path(__file__).resolve().parents[1]
P = 'papers/sidinspector-mapping-diagnostics/'
S = 'papers/sidscope-diagnostics/'


def identity(data):
    return {'sha256': hashlib.sha256(data).hexdigest(),
            'blob': hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()}


def test_receipt_only_accepts_exact_previous_and_current_source_bytes():
    ledger = ROOT / 'tests/semantic_id_pair_full_rewrite_hashes.json'
    rows = json.loads(ledger.read_text())['files']
    assert rows.keys() == {P+n for n in ('lab.yaml','README.md','mapping.md','method.md','plot.py','mapping-grid.svg')} | {S+n for n in ('lab.yaml','README.md','mapping.md','method.md')}
    for path,row in rows.items():
        current = (ROOT/path).read_bytes()
        prior = before_semantic_id_pair_full_rewrite(ROOT,path,current)
        b,a = identity(prior),identity(current)
        for alg in b:
            assert row['before_'+alg] == b[alg] and row['after_'+alg] == a[alg]
            assert semantic_id_pair_full_rewrite_hash(ROOT,path,b[alg],alg) == a[alg]
            for invalid in (a[alg], '0'*len(a[alg])):
                with pytest.raises(AssertionError):
                    semantic_id_pair_full_rewrite_hash(ROOT,path,invalid,alg)
        with pytest.raises(AssertionError):
            before_semantic_id_pair_full_rewrite(ROOT,path,current+b'\n')


def test_unchanged_overview_toy_and_figure_geometry():
    path = P+'lab.yaml'
    recent = (ROOT/path).read_bytes()
    old = before_semantic_id_pair_full_rewrite(ROOT,path,recent)
    new,before = map(yaml.safe_load,(recent,old))
    assert new['sections']['overview'] == before['sections']['overview']
    assert new['source_review']['version'] == 'v1'
    assert all(n in new['sections']['evidence'] for n in ('23,742','9,922','0.977','0.447','0.109','0.052'))
    assert '2/3' in new['sections']['results']
    for n,o in zip(new['teaching_figures'],before['teaching_figures'],strict=True):
        assert n['id']==o['id'] and n['kind']==o['kind']
        assert [v['formula'] for v in n.get('steps',[])] == [v['formula'] for v in o.get('steps',[])]
    path=P+'mapping-grid.svg'
    updated=(ROOT/path).read_bytes()
    prior=before_semantic_id_pair_full_rewrite(ROOT,path,updated)
    shape=lambda s:[(node.tag, {k:v for k,v in node.attrib.items() if k not in {'aria-label'}}) for node in ElementTree.fromstring(s).iter()]
    assert shape(updated)==shape(prior)
    for name, expected in (
        ('run.py','faa94fa0daac96c9321c32b5797cc03ce84e5e77'),
        ('results.json','2c9a69e9fa95d47660c12fd2f635175ba2df24f0'),
    ):
        assert identity((ROOT/(P+name)).read_bytes())['blob']==expected

def test_sidscope_keeps_overview_figure_formulas_and_data_identity():
    path = S+'lab.yaml'
    current = (ROOT/path).read_bytes()
    old = before_semantic_id_pair_full_rewrite(ROOT,path,current)
    a,b = map(yaml.safe_load,(old,current))
    assert b['source_review']['version']=='v1'
    assert a['sections']['overview']==b['sections']['overview']
    assert (ROOT/(S+'README.md')).read_text().count(b['sections']['overview'])==1
    assert all(q in b['sections']['evidence'] for q in ('0.976','0.900','0.083','9,610','23.6%','275商品'))
    for n,o in zip(b['teaching_figures'],a['teaching_figures'],strict=True):
        assert n['id']==o['id'] and n['kind']==o['kind']
        assert [v['formula'] for v in n.get('steps',[])] == [v['formula'] for v in o.get('steps',[])]
    for name, expected in (
        ('run.py','8f8631c1faf4c3189d98db86ee66ed3c824d5fd1'),
        ('results.json','2a2dc7a3df9ddb62b337e1d4c3ec677d00276fb0'),
    ):
        assert identity((ROOT/(S+name)).read_bytes())['blob']==expected
