"""Check exact body-only revision without altering DCDN's reported or toy data."""
from hashlib import sha1, sha256
from pathlib import Path
import json
import re

import pytest
import yaml
from prose_preservation import before_dcdn_full_prose, dcdn_full_prose_hash
from prose_preservation import before_dcdn_reader_assets

ROOT = Path(__file__).resolve().parents[1]
P = 'papers/deep-cross-division/'
NAMES = (
    'README.md','method.md','evidence.md','experiment.md','mapping.md','lab.yaml',
    'widget.html','interactive.html','interactive.js',
)


def identities(data):
    return {'blob':sha1(f'blob {len(data)}\0'.encode()+data).hexdigest(),'sha256':sha256(data).hexdigest()}


def test_exact_dcdn_prose_mapping_and_mutation_guard():
    snapshots=json.loads((ROOT/'tests/dcdn_full_prose_hashes.json').read_text())['files']
    assert set(snapshots)=={P+name for name in NAMES}
    for path,row in snapshots.items():
        after=before_dcdn_reader_assets(ROOT,path,(ROOT/path).read_bytes())
        before=before_dcdn_full_prose(ROOT,path,after)
        for alg in ('blob','sha256'):
            a,b=identities(before)[alg],identities(after)[alg]
            assert (a,b)==(row['before_'+alg],row['after_'+alg])
            assert dcdn_full_prose_hash(ROOT,path,a,alg)==b
            with pytest.raises(AssertionError):
                dcdn_full_prose_hash(ROOT,path,b,alg)
        with pytest.raises(AssertionError):
            before_dcdn_full_prose(ROOT,path,after+b'\n')
        assert re.findall(rb'\]\(([^)]+)\)',before)==re.findall(rb'\]\(([^)]+)\)',after)


def test_overview_mechanism_source_and_controls_unchanged():
    def pair(n):
        after=before_dcdn_reader_assets(ROOT,P+n,(ROOT/(P+n)).read_bytes())
        return before_dcdn_full_prose(ROOT,P+n,after),after
    a,b=map(yaml.safe_load,pair('lab.yaml'))
    assert a.keys()==b.keys()
    assert all(a[k]==b[k] for k in a if k not in ('core_idea','sections','teaching_figures'))
    assert a['sections'].keys()==b['sections'].keys()
    assert all(a['sections'][k]==b['sections'][k] for k in ('overview','method','evidence','executable_understanding'))
    for x,y in zip(a['teaching_figures'],b['teaching_figures'],strict=True):
        assert x.keys()==y.keys()
        assert all(x[k]==y[k] for k in ('id','kind','after','source','locator'))
    a,b=pair('method.md')
    assert re.findall(rb'^`x_next.*`$',a,re.M)==re.findall(rb'^`x_next.*`$',b,re.M)
    assert b.count(b'0.01')==a.count(b'0.01')
    for name in ('widget.html','interactive.html'):
        a,b=pair(name)
        expr=rb'(?:\bid|\bhref|\bvalue|\baria-labelledby|\btype)="([^"]+)"'
        assert re.findall(expr,a)==re.findall(expr,b)
        if name=='interactive.html':
            expr=rb'<script type="application/json" id="dcdn-data">(.*?)</script>'
            assert re.findall(expr,a,re.S)==re.findall(expr,b,re.S)
    expression=re.compile(r'"[^"\n]*[\u3000-\uffff][^"\n]*"')
    a,b=map(bytes.decode,pair('interactive.js'))
    assert expression.sub('""',a)==expression.sub('""',b)
    assert len(expression.findall(a))==len(expression.findall(b))
    for path,digest in (
        ('results.json','3bfe3935043973faafdaa6a5d867a46d5135e98d0f575c4ebda9825ce990b4f6'),
        ('run.py','a425e7f236407aa9e3298878c6a5a667dbb00110c6b989f22149f6d079585c66'),
    ):
        assert sha256((ROOT/(P+path)).read_bytes()).hexdigest()==digest
