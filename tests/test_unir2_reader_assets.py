"""The source edits change no computation, experiment outputs or figure markup."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from prose_preservation import before_unir2_reader_assets, unir2_reader_assets_rows, unir2_reader_assets_hash

ROOT=Path(__file__).resolve().parents[1]
P='papers/unir2-sequence-unify/'


def contents(name):
    path=P+name
    data=(ROOT/path).read_bytes()
    return before_unir2_reader_assets(ROOT,path,data),data


def test_reader_asset_guard_applies_only_exact_identities():
    names=('README.md','lab.yaml','mapping.md','method.md','results.json','run.py',
           'figures/isolation.svg','figures/mask.svg','figures/sequence.svg','figures/serving.svg')
    rows=unir2_reader_assets_rows(ROOT)
    assert rows.keys()=={P+n for n in names}
    for name in names:
        before,after=contents(name)
        path=P+name
        row=rows[path]
        for which,data in (('before',before),('after',after)):
            assert hashlib.sha256(data).hexdigest()==row[which+'_sha256']
            assert hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()==row[which+'_blob']
        for alg in ('sha256','blob'):
            assert unir2_reader_assets_hash(ROOT,path,row['before_'+alg],alg)==row['after_'+alg]
            if row['prior_spans']:
                with pytest.raises(AssertionError): unir2_reader_assets_hash(ROOT,path,'0'*len(row['before_'+alg]),alg)
        with pytest.raises(AssertionError): before_unir2_reader_assets(ROOT,path,after+b'\n')


def test_unir2_only_reader_text_changes_and_results_regenerate(tmp_path):
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
        data['experiments'][0].pop('name')
    assert previous==present
    script=tmp_path/'run.py'
    script.write_bytes(contents('run.py')[1])
    subprocess.run([sys.executable,str(script)],check=True)
    assert (tmp_path/'results.json').read_bytes()==contents('results.json')[1]
    for name in ('mapping.md','figures/isolation.svg','figures/mask.svg',
                 'figures/sequence.svg','figures/serving.svg'):
        assert len(set(contents(name)))==1
    previous,present=map(yaml.safe_load,contents('lab.yaml'))
    before=previous.pop('sections')
    after=present.pop('sections')
    assert previous==present
    assert {name for name in after if before[name]!=after[name]}=={'overview','evidence'}
    overview=after['overview']
    assert all(x in overview for x in ('OneLive','1.177%','2.569%','二つの処理を同時に置き換えた',
                                       'クリック、長時間視聴、ギフト','生成途中の計算を再利用'))
    assert 'Lab' not in overview
    readme=contents('README.md')[1].decode()
    assert all(readme.count(after[k])==1 for k in ('overview','evidence'))
    assert '表2も過去の記録を使った評価' in after['evidence']
    method=contents('method.md')[1].decode()
    assert '候補が決まる前に採点まで同時に済ませるわけではない' in method
