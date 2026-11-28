"""The ICEGR reader prose changes without modifying any test inputs or outputs."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

import pytest
import yaml

from prose_preservation import before_icegr_reader_assets, icegr_reader_assets_rows, icegr_reader_assets_hash

ROOT=Path(__file__).resolve().parents[1]
P='papers/icegr-baidu-intent-generative-retrieval/'


def contents(name):
    path=P+name
    data=(ROOT/path).read_bytes()
    return before_icegr_reader_assets(ROOT,path,data),data


def test_icegr_reader_assets_require_exact_transition():
    names=('README.md','lab.yaml','mapping.md','method.md','results.json','run.py','plot.py','margin-curve.svg')
    rows=icegr_reader_assets_rows(ROOT)
    assert rows.keys()=={P+n for n in names}
    for name in names:
        before,after=contents(name)
        path=P+name
        row=rows[path]
        for which,data in (('before',before),('after',after)):
            assert hashlib.sha256(data).hexdigest()==row[which+'_sha256']
            assert hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()==row[which+'_blob']
        for alg in ('sha256','blob'):
            assert icegr_reader_assets_hash(ROOT,path,row['before_'+alg],alg)==row['after_'+alg]
            if row['prior_spans']:
                with pytest.raises(AssertionError): icegr_reader_assets_hash(ROOT,path,'0'*len(row['before_'+alg]),alg)
        with pytest.raises(AssertionError): before_icegr_reader_assets(ROOT,path,after+b'\n')


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

    script=tmp_path/'run.py'
    script.write_bytes(contents('run.py')[1])
    (tmp_path/'plot.py').write_bytes(contents('plot.py')[1])
    run1=subprocess.run([sys.executable,str(script)],capture_output=True,check=True)
    run2=subprocess.run([sys.executable,str(script)],capture_output=True,check=True)
    assert run1.stdout==run2.stdout==b''
    assert (tmp_path/'results.json').read_bytes()==contents('results.json')[1]
    assert len(set(contents('margin-curve.svg') + ((tmp_path/'margin-curve.svg').read_bytes(),)))==1
    for name in ('mapping.md','method.md','plot.py'):
        assert len(set(contents(name)))==1
    old,new=map(yaml.safe_load,contents('lab.yaml'))
    assert {k for k in old if old[k]!=new[k]}=={'summary','sections'}
    assert {k for k in old['sections'] if old['sections'][k]!=new['sections'][k]}=={'overview','evidence'}
    assert re.findall(r'(?m)^\|.*$',new['sections']['evidence'])==re.findall(r'(?m)^\|.*$',old['sections']['evidence'])
    overview=new['sections']['overview']
    assert all(x in overview for x in ('20%を対象','支払いの有無','商品表示1回あたり','一定数','15.96%'))
    assert 'Lab' not in overview
    assert contents('README.md')[1].decode().count(overview)==1


@pytest.mark.parametrize('name',('README.md','lab.yaml','run.py','results.json'))
def test_icegr_forward_chain_accepts_the_precise_historical_predecessor(name):
    from prose_preservation import (
        reading_prose_hash, paper_overview_rewrite_hash, harness_icegr_full_rewrite_hash,
    )
    path=P+name
    previous,present=contents(name)
    current=icegr_reader_assets_rows(ROOT)[path]
    overview=json.loads((ROOT/'tests/paper_overview_hashes.json').read_text())
    overview_row=(overview['files']|overview['mirrored']).get(path)
    rewritten=json.loads((ROOT/'tests/harness_icegr_full_rewrite_hashes.json').read_text())['files'].get(path)
    assert (overview_row is not None)==(rewritten is not None)==(name in {'README.md','lab.yaml'})
    fingerprints={
        'sha256': hashlib.sha256(present).hexdigest(),
        'blob': hashlib.sha1(f'blob {len(present)}\0'.encode()+present).hexdigest(),
    }
    for alg,expected in fingerprints.items():
        key='before_'+alg
        if overview_row:
            assert paper_overview_rewrite_hash(ROOT,path,overview_row[key],alg)==rewritten[key]
            assert harness_icegr_full_rewrite_hash(ROOT,path,rewritten[key],alg)==current[key]
        start=(overview_row or current)[key]
        assert reading_prose_hash(ROOT,path,start,alg)==expected
        with pytest.raises(AssertionError):
            reading_prose_hash(ROOT,path,'0'*len(start),alg)
