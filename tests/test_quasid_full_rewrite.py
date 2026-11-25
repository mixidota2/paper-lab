"""The QuaSID body revision preserves the paper overview and toy evidence."""
import hashlib
import json
from pathlib import Path
from xml.etree import ElementTree

import pytest
import yaml

from prose_preservation import before_quasid_full_rewrite, quasid_full_rewrite_hash

ROOT = Path(__file__).resolve().parents[1]
P = 'papers/quasid-collision-qualified-sid/'


def identity(data):
    return {'sha256': hashlib.sha256(data).hexdigest(),
            'blob': hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()}


def test_receipt_only_accepts_exact_previous_and_current_source_bytes():
    ledger = ROOT / 'tests/quasid_full_rewrite_hashes.json'
    rows = json.loads(ledger.read_text())['files']
    assert rows.keys() == {P+n for n in ('lab.yaml','README.md','mapping.md','method.md','figures/geometry.svg','figures/online.svg')}
    for path,row in rows.items():
        current = (ROOT/path).read_bytes()
        prior = before_quasid_full_rewrite(ROOT,path,current)
        b,a = identity(prior),identity(current)
        for alg in b:
            assert row['before_'+alg] == b[alg] and row['after_'+alg] == a[alg]
            assert quasid_full_rewrite_hash(ROOT,path,b[alg],alg) == a[alg]
            for invalid in (a[alg], '0'*len(a[alg])):
                with pytest.raises(AssertionError):
                    quasid_full_rewrite_hash(ROOT,path,invalid,alg)
        with pytest.raises(AssertionError):
            before_quasid_full_rewrite(ROOT,path,current+b'\n')


def test_unchanged_overview_toy_and_figure_geometry():
    path = P+'lab.yaml'
    recent = (ROOT/path).read_bytes()
    old = before_quasid_full_rewrite(ROOT,path,recent)
    new,before = map(yaml.safe_load,(recent,old))
    assert new['sections']['overview'] == before['sections']['overview']
    assert new['source_review']['version'] == 'v1'
    assert all(n in new['sections']['evidence'] for n in ('0.0211','0.0230','0.55%','2.38%','6.42%','0.21%'))
    assert all(n in new['sections']['results'] for n in ('全桁一致6組','一部一致16組','約0.823'))
    for n,o in zip(new['teaching_figures'],before['teaching_figures'],strict=True):
        assert n['id']==o['id'] and n['kind']==o['kind']
        assert [v['formula'] for v in n.get('steps',[])] == [v['formula'] for v in o.get('steps',[])]
    path=P+'figures/geometry.svg'
    updated=(ROOT/path).read_bytes()
    prior=before_quasid_full_rewrite(ROOT,path,updated)
    shape=lambda s:[(node.tag, {k:v for k,v in node.attrib.items() if k not in {'aria-label'}}) for node in ElementTree.fromstring(s).iter()]
    assert shape(updated)==shape(prior)
    for name, expected in (
        ('run.py','d8e4715101a54d5601b61ff7810973d9101b1a13'),
        ('results.json','ac4ebc4f1e087556727e036e032700b8afdb0311'),
    ):
        assert identity((ROOT/(P+name)).read_bytes())['blob']==expected
