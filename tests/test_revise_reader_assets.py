"""The REVISE reader prose changes without modifying any test inputs or outputs."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from prose_preservation import before_revise_reader_assets, revise_reader_assets_rows, revise_reader_assets_hash

ROOT=Path(__file__).resolve().parents[1]
P='papers/revise-recovery/'


def contents(name):
    path=P+name
    data=(ROOT/path).read_bytes()
    return before_revise_reader_assets(ROOT,path,data),data


def test_revise_reader_assets_require_exact_transition():
    names=('lab.yaml','method.md','results.json','run.py','figures/impact.svg','figures/certificate.svg')
    rows=revise_reader_assets_rows(ROOT)
    assert rows.keys()=={P+n for n in names}
    for name in names:
        before,after=contents(name)
        path=P+name
        row=rows[path]
        for which,data in (('before',before),('after',after)):
            assert hashlib.sha256(data).hexdigest()==row[which+'_sha256']
            assert hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()==row[which+'_blob']
        for alg in ('sha256','blob'):
            assert revise_reader_assets_hash(ROOT,path,row['before_'+alg],alg)==row['after_'+alg]
            if row['prior_spans']:
                with pytest.raises(AssertionError): revise_reader_assets_hash(ROOT,path,'0'*len(row['before_'+alg]),alg)
        with pytest.raises(AssertionError): before_revise_reader_assets(ROOT,path,after+b'\n')


def test_revise_invariants(tmp_path):
    def logic(text):
        tree=ast.parse(text)
        assert ast.get_docstring(tree)
        del tree.body[0]
        for node in ast.walk(tree):
            if isinstance(node,ast.Dict):
                for key,value in zip(node.keys,node.values):
                    if isinstance(key,ast.Constant) and key.value in {'note','name'}:
                        assert isinstance(value,ast.Constant) and isinstance(value.value,str)
                        value.value='<reader text>'
        return ast.dump(tree)
    assert len(set(map(logic,contents('run.py'))))==1
    old,new=map(json.loads,contents('results.json'))
    for data in (old,new):
        data.pop('note')
        for exp in data['experiments']: exp.pop('name')
    assert old==new
    for name in ('method.md','figures/impact.svg','figures/certificate.svg'):
        assert len(set(contents(name)))==1
    script=tmp_path/'run.py'
    script.write_bytes(contents('run.py')[1])
    for _ in range(2):
        subprocess.run([sys.executable,'-I','-S',str(script)],capture_output=True,check=True)
        assert (tmp_path/'results.json').read_bytes()==contents('results.json')[1]
    old,new=map(yaml.safe_load,contents('lab.yaml'))
    assert {k for k in old if old[k]!=new[k]}=={'sections'}
    assert {k for k in old['sections'] if old['sections'][k]!=new['sections'][k]}=={'overview','evidence'}
    overview=new['sections']['overview']
    for clue in ('分岐条件','完了済みなら結果を再利用','15,939回','同じ依存関係の情報','43.6%','5.9%','分散環境での障害復旧'):
        assert clue in overview
    assert 'Lab' not in overview and '教材' not in overview
    assert all(x in new['sections']['evidence'] for x in ('0.207ミリ秒','0.0026ミリ秒','800回'))


def test_legacy_registration_sources_compose():
    from prose_preservation import revised_hash
    for filename,key in [('main_105_catalog.json','source_hashes'),('main_107_catalog.json','source_hashes'),('trial_trace_baseline.json','sources')]:
        data=json.loads((ROOT/'tests'/filename).read_text())[key]
        for path,prior in data.items():
            if path.startswith(P):
                assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==revised_hash(ROOT,path,prior)


def test_exact_overview_and_earlier_full_rewrite_compose_with_new_stage():
    from prose_preservation import (
        reading_prose_hash,revised_hash,yomiyasu_hash,arxiv_versioned_overview_hash,
        revise_full_rewrite_hash,
    )
    overview=json.loads((ROOT/'tests/arxiv_versioned_overview_hashes.json').read_text())
    ov=overview['files']
    first=json.loads((ROOT/'tests/revise_full_rewrite_hashes.json').read_text())['files']
    yom=json.loads((ROOT/'tests/yomiyasu_revision_hashes.json').read_text())['files']
    orig=json.loads((ROOT/'tests/prose_revision_hashes.json').read_text())['files']
    for p,end in revise_reader_assets_rows(ROOT).items():
        for alg in ('sha256','blob'):
            before='before_'+alg
            after='after_'+alg
            start=end[before]
            if p in first:
                assert revise_full_rewrite_hash(ROOT,p,first[p][before],alg)==start
                start=first[p][before]
            if p in ov:
                assert arxiv_versioned_overview_hash(ROOT,p,ov[p][before],alg)==start
                start=ov[p][before]
            assert reading_prose_hash(ROOT,p,start,alg)==end[after]
            if p in yom:
                assert yomiyasu_hash(ROOT,p,yom[p][before],alg)==end[after]
            if p in orig:
                assert revised_hash(ROOT,p,orig[p][before],alg)==end[after]
            if end['prior_spans']:
                with pytest.raises(AssertionError):
                    reading_prose_hash(ROOT,p,'0'*len(start),alg)
