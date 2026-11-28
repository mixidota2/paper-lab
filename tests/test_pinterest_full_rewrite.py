import hashlib
import json
from pathlib import Path

import pytest
import yaml

from prose_preservation import before_pinterest_reader_full_prose, before_pinterest_full_rewrite, pinterest_full_rewrite_hash
ROOT=Path(__file__).resolve().parents[1]
P='papers/pinterest-causal-retrieval-shopping/'


def test_full_article_keeps_the_reviewed_overview_and_working_example():
    y=ROOT/(P+'lab.yaml')
    new=yaml.safe_load(before_pinterest_reader_full_prose(ROOT,P+y.name,y.read_bytes()))
    prior=yaml.safe_load(before_pinterest_full_rewrite(ROOT,P+y.name,before_pinterest_reader_full_prose(ROOT,P+y.name,y.read_bytes())))
    assert new['sections']['overview']==prior['sections']['overview']
    assert new['sections']['method']==prior['sections']['method']
    assert new['urls']==prior['urls'] and new['verification']==prior['verification']
    assert new['source_review']['pdf_version']==prior['source_review']['pdf_version']=='v2'
    assert new['source_review']['pdf_sha256']==prior['source_review']['pdf_sha256']
    assert [s['formula'] for s in new['teaching_figures'][1]['steps']]==[s['formula'] for s in prior['teaching_figures'][1]['steps']]
    readme=before_pinterest_reader_full_prose(ROOT,P+'README.md',(ROOT/(P+'README.md')).read_bytes()).decode()
    assert readme.count(new['sections']['overview'])==1
    for k,v in new['sections'].items():
        if k not in ('method','mapping','executable_understanding'):
            assert v in readme
    for x in ['約40%','最大85%','0.26%','1.10%','64.4%','64.6%','統計的に明確な差が出ていない']:
        assert x in new['sections']['evidence']
    assert '有限個のログで必ず真値に一致するという意味ではない' in (ROOT/(P+'method.md')).read_text()
    assert '均等割当のこの例で' in new['sections']['executable_understanding']


def test_only_exact_new_files_advance_the_guard():
    rows=json.loads((ROOT/'tests/pinterest_full_rewrite_hashes.json').read_text())['files']
    assert rows.keys()=={P+i for i in ('lab.yaml','README.md','method.md','mapping.md')}
    for p,row in rows.items():
        raw=before_pinterest_reader_full_prose(ROOT,p,(ROOT/p).read_bytes())
        for alg,current in [('sha256',hashlib.sha256(raw).hexdigest()),
                ('blob',hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest())]:
            assert current==row['after_'+alg]==pinterest_full_rewrite_hash(ROOT,p,row['before_'+alg],alg)
            with pytest.raises(AssertionError):
                pinterest_full_rewrite_hash(ROOT,p,'0'*len(current),alg)
        if p.endswith(('lab.yaml','README.md')):
            assert hashlib.sha256(before_pinterest_full_rewrite(ROOT,p,raw)).hexdigest()==row['before_sha256']
            with pytest.raises(AssertionError):
                before_pinterest_full_rewrite(ROOT,p,raw+b'\n')
