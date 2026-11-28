"""The STATIC reader prose changes without modifying any test inputs or outputs."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

import pytest
import yaml

from prose_preservation import before_static_reader_assets, static_reader_assets_rows, static_reader_assets_hash

ROOT=Path(__file__).resolve().parents[1]
P='papers/static-constrained-gr/'


def contents(name):
    path=P+name
    data=(ROOT/path).read_bytes()
    return before_static_reader_assets(ROOT,path,data),data


def test_static_reader_assets_require_exact_transition():
    names=('README.md','lab.yaml','mapping.md','method.md','results.json','run.py')
    rows=static_reader_assets_rows(ROOT)
    assert rows.keys()=={P+n for n in names}
    for name in names:
        before,after=contents(name)
        path=P+name
        row=rows[path]
        for which,data in (('before',before),('after',after)):
            assert hashlib.sha256(data).hexdigest()==row[which+'_sha256']
            assert hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()==row[which+'_blob']
        for alg in ('sha256','blob'):
            assert static_reader_assets_hash(ROOT,path,row['before_'+alg],alg)==row['after_'+alg]
            if row['prior_spans']:
                with pytest.raises(AssertionError): static_reader_assets_hash(ROOT,path,'0'*len(row['before_'+alg]),alg)
        with pytest.raises(AssertionError): before_static_reader_assets(ROOT,path,after+b'\n')


def test_coral_runtime_numeric_results_and_figures_remain_intact(tmp_path):
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
    previous,present=map(json.loads,contents('results.json'))
    for data in (previous,present):
        data.pop('note')
        for experiment in data['experiments']: experiment.pop('name')
    assert previous==present
    for name in ('method.md',):
        assert len(set(contents(name)))==1

    script=tmp_path/'run.py'
    script.write_bytes(contents('run.py')[1])
    run1=subprocess.run([sys.executable,'-I','-S',str(script)],capture_output=True,check=True)
    run2=subprocess.run([sys.executable,'-I','-S',str(script)],capture_output=True,check=True)
    assert run1.stdout==run2.stdout==(tmp_path/'results.json').read_bytes()==contents('results.json')[1]
    old,new=map(yaml.safe_load,contents('lab.yaml'))
    assert {k for k in old if old[k]!=new[k]}=={'sections'}
    assert {k for k in old['sections'] if old['sections'][k]!=new['sections'][k]}=={'overview','evidence'}
    for clue in ('0.033ミリ秒','0.25%','視聴回数が5.1%','候補をすべて7日以内に絞ったわけではありません','実験期間ではありません'):
        assert clue in new['sections']['overview']
    assert 'Lab' not in new['sections']['overview']
    from re import findall
    figures=lambda s: findall(r'<figure(?:[ >]).*?</figure>',s)
    assert figures(old['sections']['evidence'])==figures(new['sections']['evidence'])
    guide=contents('mapping.md')[1].decode().split('## 結果ファイルの読み方',1)[1]
    assert all(f'`{k}`' in guide for k in ('csr','indptr','tokens','next_state','post_filter','constrained','experiments','checks'))


def test_exact_overview_and_earlier_full_rewrite_compose_with_new_stage():
    from prose_preservation import (
        reading_prose_hash,revised_hash,yomiyasu_hash,paper_overview_rewrite_hash,
        static_constrained_full_rewrite_hash,
    )
    overview=json.loads((ROOT/'tests/paper_overview_hashes.json').read_text())
    ov=overview['files']|overview['mirrored']
    first=json.loads((ROOT/'tests/static_constrained_full_rewrite_hashes.json').read_text())['files']
    yom=json.loads((ROOT/'tests/yomiyasu_revision_hashes.json').read_text())['files']
    orig=json.loads((ROOT/'tests/prose_revision_hashes.json').read_text())['files']
    for p,end in static_reader_assets_rows(ROOT).items():
        for alg in ('sha256','blob'):
            before='before_'+alg
            after='after_'+alg
            start=end[before]
            if p in first:
                assert static_constrained_full_rewrite_hash(ROOT,p,first[p][before],alg)==start
                start=first[p][before]
            if p in ov:
                assert paper_overview_rewrite_hash(ROOT,p,ov[p][before],alg)==start
                start=ov[p][before]
            assert reading_prose_hash(ROOT,p,start,alg)==end[after]
            if p in yom:
                assert yomiyasu_hash(ROOT,p,yom[p][before],alg)==end[after]
            if p in orig:
                assert revised_hash(ROOT,p,orig[p][before],alg)==end[after]
            if end['prior_spans']:
                with pytest.raises(AssertionError):
                    reading_prose_hash(ROOT,p,'0'*len(start),alg)
