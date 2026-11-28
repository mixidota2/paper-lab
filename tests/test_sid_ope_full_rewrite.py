"""The SID OPE body revision preserves the paper overview and toy evidence."""
import hashlib
import json
from pathlib import Path
from xml.etree import ElementTree

import pytest
import yaml

from prose_preservation import before_sid_ope_reader_full_prose, before_sid_ope_full_rewrite, sid_ope_full_rewrite_hash

ROOT = Path(__file__).resolve().parents[1]
P = 'papers/sid-ope-hierarchy/'


def prior_reader(path):
    return before_sid_ope_reader_full_prose(ROOT,path,(ROOT/path).read_bytes())


def identity(data):
    return {'sha256': hashlib.sha256(data).hexdigest(),
            'blob': hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()}


def test_receipt_only_accepts_exact_previous_and_current_source_bytes():
    ledger = ROOT / 'tests/sid_ope_full_rewrite_hashes.json'
    rows = json.loads(ledger.read_text())['files']
    assert rows.keys() == {P+n for n in ('lab.yaml','mapping.md','method.md','figures/sid-tree.svg','figures/decoder-mass.svg','figures/ess.svg')}
    for path,row in rows.items():
        current = prior_reader(path)
        prior = before_sid_ope_full_rewrite(ROOT,path,current)
        b,a = identity(prior),identity(current)
        for alg in b:
            assert row['before_'+alg] == b[alg] and row['after_'+alg] == a[alg]
            assert sid_ope_full_rewrite_hash(ROOT,path,b[alg],alg) == a[alg]
            for invalid in (a[alg], '0'*len(a[alg])):
                with pytest.raises(AssertionError):
                    sid_ope_full_rewrite_hash(ROOT,path,invalid,alg)
        with pytest.raises(AssertionError):
            before_sid_ope_full_rewrite(ROOT,path,current+b'\n')


def test_unchanged_overview_toy_and_figure_geometry():
    path = P+'lab.yaml'
    recent = prior_reader(path)
    old = before_sid_ope_full_rewrite(ROOT,path,recent)
    new,before = map(yaml.safe_load,(recent,old))
    assert new['sections']['overview'] == before['sections']['overview']
    assert new['source_review']['url'].endswith('v1') and new['source_review'] == before['source_review']
    assert all(n in new['sections']['evidence'] for n in ('29,000','0.167','0.300','16種類の方策','2608.28905v1'))
    assert all(n in new['sections']['results'] for n in ('5.519','151.423','0.280','0.102'))
    for n,o in zip(new['teaching_figures'],before['teaching_figures'],strict=True):
        assert n['id']==o['id'] and n['kind']==o['kind']
        assert [v['formula'] for v in n.get('steps',[])] == [v['formula'] for v in o.get('steps',[])]
    path=P+'figures/ess.svg'
    updated=(ROOT/path).read_bytes()
    prior=before_sid_ope_full_rewrite(ROOT,path,updated)
    shape=lambda s:[(node.tag, {k:v for k,v in node.attrib.items() if k not in {'aria-label'}}) for node in ElementTree.fromstring(s).iter()]
    assert shape(updated)==shape(prior)
    for name, expected in (
        ('run.py','00a33aadbe5eafa11bb585477a115504ceb12e62'),
        ('results.json','79efd53c8a7258fe96094efb8eae15f2f54e94e5'),
    ):
        assert identity(prior_reader(P+name))['blob']==expected
