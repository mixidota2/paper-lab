"""WRAPPED readable prose, original results and uncertainty boundaries."""
from ast import parse, dump, FunctionDef
from hashlib import sha1,sha256
import json
from pathlib import Path
import re

import pytest
import yaml

from prose_preservation import before_wrapped_all_full_prose, before_wrapped_produce_full_rewrite, wrapped_produce_full_rewrite_hash

ROOT=Path(__file__).resolve().parents[1]
P='papers/wrapped-produce-placement-controlled-trial/'
NAMES=('lab.yaml','README.md','method.md','mapping.md','evidence.md','experiment.md','run.py')

def identities(data):
    return {'blob':sha1(f'blob {len(data)}\0'.encode()+data).hexdigest(),'sha256':sha256(data).hexdigest()}

def prior(path):
    return before_wrapped_all_full_prose(ROOT, path, (ROOT/path).read_bytes())

def test_wrapped_produce_exact_document_transitions():
    rows=json.loads((ROOT/'tests/wrapped_produce_full_rewrite_hashes.json').read_text())['files']
    assert set(rows)=={P+x for x in NAMES}
    for path,row in rows.items():
        after=prior(path)
        before=before_wrapped_produce_full_rewrite(ROOT,path,after)
        for alg in ('blob','sha256'):
            a,b=identities(before)[alg],identities(after)[alg]
            assert a==row['before_'+alg] and b==row['after_'+alg]
            assert wrapped_produce_full_rewrite_hash(ROOT,path,a,alg)==b
            with pytest.raises(AssertionError):
                wrapped_produce_full_rewrite_hash(ROOT,path,b,alg)
        with pytest.raises(AssertionError):
            before_wrapped_produce_full_rewrite(ROOT,path,after+b'\n')
        links=lambda x:set(re.findall(rb'\]\(([^)]*)\)',x))
        assert links(before)==links(after)

def test_wrapped_produce_preserves_numerics_and_distinguishes_estimates():
    new=prior(P+'lab.yaml')
    orig=before_wrapped_produce_full_rewrite(ROOT,P+'lab.yaml',new)
    a,b=map(yaml.safe_load,(orig,new))
    assert a['sections']['overview']==b['sections']['overview']
    for key in ('source_review','urls','verification','figures','interactives','related_threads','status'):
        assert a[key]==b[key]
    for name in ('method','evidence','executable_understanding'):
        assert a['sections'][name]==b['sections'][name]
    assert '無作為割付ではない' in b['summary']
    assert '店舗販売、健康への影響、配置だけの効果を独立に検証していない' in b['sections']['what_we_did_not_verify']
    assert '2,525食分' in prior(P+'method.md').decode()
    assert '家庭で食べた量ではありません' in prior(P+'method.md').decode()
    assert 'Labはこの表から介入前の差を引き直していません' in prior(P+'evidence.md').decode()
    assert identities(prior(P+'results.json'))['sha256']=='fac1e412327dd3a14b6f8da8d358db2d71859b4f419917140d43ea43adc2027b'
    new=prior(P+'run.py')
    orig=before_wrapped_produce_full_rewrite(ROOT,P+'run.py',new)
    numerical=lambda x:[dump(n) for n in parse(x).body if isinstance(n,FunctionDef) and n.name in ('line_fit','simulate')]
    assert len(numerical(orig))==2 and numerical(orig)==numerical(new)
