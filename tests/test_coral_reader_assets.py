"""The CORAL reader prose changes without modifying any test inputs or outputs."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

import pytest
import yaml

from prose_preservation import before_coral_reader_assets, coral_reader_assets_rows, coral_reader_assets_hash

ROOT=Path(__file__).resolve().parents[1]
P='papers/coral-meta-config-harness/'


def contents(name):
    path=P+name
    data=(ROOT/path).read_bytes()
    return before_coral_reader_assets(ROOT,path,data),data


def test_coral_reader_assets_require_exact_transition():
    names=('README.md','lab.yaml','mapping.md','method.md','results.json','run.py')
    rows=coral_reader_assets_rows(ROOT)
    assert rows.keys()=={P+n for n in names}
    for name in names:
        before,after=contents(name)
        path=P+name
        row=rows[path]
        for which,data in (('before',before),('after',after)):
            assert hashlib.sha256(data).hexdigest()==row[which+'_sha256']
            assert hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()==row[which+'_blob']
        for alg in ('sha256','blob'):
            assert coral_reader_assets_hash(ROOT,path,row['before_'+alg],alg)==row['after_'+alg]
            if row['prior_spans']:
                with pytest.raises(AssertionError): coral_reader_assets_hash(ROOT,path,'0'*len(row['before_'+alg]),alg)
        with pytest.raises(AssertionError): before_coral_reader_assets(ROOT,path,after+b'\n')


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
    run1=subprocess.run([sys.executable,str(script)],capture_output=True,check=True)
    run2=subprocess.run([sys.executable,str(script)],capture_output=True,check=True)
    assert run1.stdout==run2.stdout==(tmp_path/'results.json').read_bytes()==contents('results.json')[1]

    assert len(set(contents('mapping.md')))==len(set(contents('method.md')))==1
    old,new=map(yaml.safe_load,contents('lab.yaml'))
    assert {k for k in old if old[k]!=new[k]}=={'sections'}
    assert {k for k in old['sections'] if old['sections'][k]!=new['sections'][k]}=={'overview','evidence'}
    evidence=new['sections']['evidence']
    figures=lambda s: re.findall(r'<figure(?:[ >]).*?</figure>',s,re.S)
    assert len(figures(evidence))==2 and figures(evidence)==figures(old['sections']['evidence'])
    overview=new['sections']['overview']
    assert all(x in overview for x in ('人が運用を監督','0.15%','0.16%','視聴した人の数ではありません','44%','反応に差がないと証明したわけではありません'))
    assert 'Lab' not in overview
    assert contents('README.md')[1].decode().count(overview)==1
