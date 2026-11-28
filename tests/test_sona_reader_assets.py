"""Preserve calculations, asset structure and evidence scope with the new prose."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

import pytest
import yaml

from prose_preservation import before_sona_reader_assets, sona_reader_assets_rows, sona_reader_assets_hash

ROOT=Path(__file__).resolve().parents[1]
P='papers/sona-yandex-music/'


def contents(name):
    path=P+name
    data=(ROOT/path).read_bytes()
    return before_sona_reader_assets(ROOT,path,data),data


def test_sona_reader_assets_only_accept_exact_identities():
    names=('README.md','lab.yaml','mapping.md','method.md','results.json','run.py')
    rows=sona_reader_assets_rows(ROOT)
    assert rows.keys()=={P+n for n in names}
    for name in names:
        before,after=contents(name)
        path=P+name
        row=rows[path]
        for which,data in (('before',before),('after',after)):
            assert hashlib.sha256(data).hexdigest()==row[which+'_sha256']
            assert hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()==row[which+'_blob']
        for alg in ('sha256','blob'):
            assert sona_reader_assets_hash(ROOT,path,row['before_'+alg],alg)==row['after_'+alg]
            if row['prior_spans']:
                with pytest.raises(AssertionError): sona_reader_assets_hash(ROOT,path,'0'*len(row['before_'+alg]),alg)
        with pytest.raises(AssertionError): before_sona_reader_assets(ROOT,path,after+b'\n')


def test_sona_calculations_and_rendered_figures_do_not_change(tmp_path):
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
        data['attention_pair_counts'].pop('note')
    assert previous==present
    script=tmp_path/'run.py'
    script.write_bytes(contents('run.py')[1])
    result=subprocess.run([sys.executable,str(script)],capture_output=True,check=True)
    assert result.stdout==(tmp_path/'results.json').read_bytes()==contents('results.json')[1]

    assert len(set(contents('mapping.md')))==len(set(contents('method.md')))==1
    old,new=map(yaml.safe_load,contents('lab.yaml'))
    assert {k for k in old if old[k]!=new[k]}=={'summary','sections'}
    assert {k for k in old['sections'] if old['sections'][k]!=new['sections'][k]}=={'overview','evidence'}
    evidence=new['sections']['evidence']
    figures=lambda s: re.findall(r'<figure(?:[ >]).*?</figure>',s,re.S)
    assert len(figures(evidence))==1 and figures(evidence)==figures(old['sections']['evidence'])
    overview=new['sections']['overview']
    assert all(x in overview for x in ('各群15%','Active Users','4.53%','6.30%','教師を動かしません','最終構成をまとめて試した'))
    assert 'Lab' not in overview
    assert all(x in evidence for x in ('含める条件の記載はない','上位の曲が同じ順番に並ぶ必要はない','0.2983',
                                       '0.5654','0.8663','0.8615','分母を1,000にする'))
    readme=contents('README.md')[1].decode()
    assert readme.count(overview)==1
    for fragment in evidence.split('\n\n'):
        if not fragment.startswith('<figure'):
            assert re.sub(r'\[([^]]+)\]\(gryphon-v2-cascade\.html\)',r'\1',fragment) in readme
