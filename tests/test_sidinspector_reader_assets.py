"""The SIDInspector reader prose changes without modifying any test inputs or outputs."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

import pytest
import yaml

from prose_preservation import before_sidinspector_reader_assets, sidinspector_reader_assets_rows, sidinspector_reader_assets_hash

ROOT=Path(__file__).resolve().parents[1]
P='papers/sidinspector-mapping-diagnostics/'


def contents(name):
    path=P+name
    data=(ROOT/path).read_bytes()
    return before_sidinspector_reader_assets(ROOT,path,data),data


def test_sidinspector_reader_assets_require_exact_transition():
    names=('README.md','lab.yaml','mapping.md','method.md','results.json','run.py','plot.py','mapping-grid.svg')
    rows=sidinspector_reader_assets_rows(ROOT)
    assert rows.keys()=={P+n for n in names}
    for name in names:
        before,after=contents(name)
        path=P+name
        row=rows[path]
        for which,data in (('before',before),('after',after)):
            assert hashlib.sha256(data).hexdigest()==row[which+'_sha256']
            assert hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()==row[which+'_blob']
        for alg in ('sha256','blob'):
            assert sidinspector_reader_assets_hash(ROOT,path,row['before_'+alg],alg)==row['after_'+alg]
            if row['prior_spans']:
                with pytest.raises(AssertionError): sidinspector_reader_assets_hash(ROOT,path,'0'*len(row['before_'+alg]),alg)
        with pytest.raises(AssertionError): before_sidinspector_reader_assets(ROOT,path,after+b'\n')


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
    for name in ('plot.py','mapping-grid.svg','method.md'):
        assert len(set(contents(name)))==1

    script=tmp_path/'run.py'
    script.write_bytes(contents('run.py')[1])
    (tmp_path/'plot.py').write_bytes(contents('plot.py')[1])
    run1=subprocess.run([sys.executable,'-S',str(script)],capture_output=True,check=True)
    run2=subprocess.run([sys.executable,'-S',str(script)],capture_output=True,check=True)
    assert run1.stdout==run2.stdout==b''
    assert (tmp_path/'results.json').read_bytes()==contents('results.json')[1]
    assert (tmp_path/'mapping-grid.svg').read_bytes()==contents('mapping-grid.svg')[1]
    old,new=map(yaml.safe_load,contents('lab.yaml'))
    assert {k for k in old if old[k]!=new[k]}=={'sections'}
    assert {k for k in old['sections'] if old['sections'][k]!=new['sections'][k]}=={'overview'}
    overview=new['sections']['overview']
    assert all(x in overview for x in ('23,742商品','97.7%','0.154','0.447','公式GRIDの学習手順全体'))
    assert 'Lab' not in overview
    guide=contents('mapping.md')[1].decode().split('## 結果ファイルの読み方',1)[1]
    assert all(x in guide for x in ('D2_alias_item_rate','D3_L1_weighted','unique_unaligned','unique_aligned'))


def test_historical_chains_compose_without_replacing_sidscope_receipt():
    from prose_preservation import (
        reading_prose_hash,yomiyasu_hash,revised_hash,paper_overview_rewrite_hash,
        semantic_id_pair_full_rewrite_hash,sidscope_reader_assets_hash,
    )
    overview=json.loads((ROOT/'tests/paper_overview_hashes.json').read_text())
    ov=overview['files']|overview['mirrored']
    pair=json.loads((ROOT/'tests/semantic_id_pair_full_rewrite_hashes.json').read_text())['files']
    yom=json.loads((ROOT/'tests/yomiyasu_revision_hashes.json').read_text())['files']
    original=json.loads((ROOT/'tests/prose_revision_hashes.json').read_text())['files']
    current=sidinspector_reader_assets_rows(ROOT)
    for p, row in current.items():
        for alg in ('sha256','blob'):
            before='before_'+alg
            after='after_'+alg
            start=row[before]
            if p in pair:
                assert semantic_id_pair_full_rewrite_hash(ROOT,p,pair[p][before],alg)==row[before]
                start=pair[p][before]
            if p in ov:
                assert paper_overview_rewrite_hash(ROOT,p,ov[p][before],alg)==start
                start=ov[p][before]
            assert reading_prose_hash(ROOT,p,start,alg)==row[after]
            if p in yom:
                assert yomiyasu_hash(ROOT,p,yom[p][before],alg)==row[after]
            if p in original:
                assert revised_hash(ROOT,p,original[p][before],alg)==row[after]
            if row['prior_spans']:
                with pytest.raises(AssertionError):
                    reading_prose_hash(ROOT,p,'0'*len(start),alg)
    other=json.loads((ROOT/'tests/sidscope_reader_assets_hashes.json').read_text())['files']
    for p, row in other.items():
        for alg in ('sha256','blob'):
            expected=sidscope_reader_assets_hash(ROOT,p,row['before_'+alg],alg)
            assert expected==row['after_'+alg]==sidinspector_reader_assets_hash(ROOT,p,expected,alg)
