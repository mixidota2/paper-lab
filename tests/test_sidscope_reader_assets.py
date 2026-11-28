"""The SIDScope reader prose changes without modifying any test inputs or outputs."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

import pytest
import yaml

from prose_preservation import before_sidscope_reader_assets, sidscope_reader_assets_rows, sidscope_reader_assets_hash

ROOT=Path(__file__).resolve().parents[1]
P='papers/sidscope-diagnostics/'


def contents(name):
    path=P+name
    data=(ROOT/path).read_bytes()
    return before_sidscope_reader_assets(ROOT,path,data),data


def test_sidscope_reader_assets_require_exact_transition():
    names=('README.md','lab.yaml','mapping.md','method.md','results.json','run.py','official-check.json','NOTICE.txt')
    rows=sidscope_reader_assets_rows(ROOT)
    assert rows.keys()=={P+n for n in names}
    for name in names:
        before,after=contents(name)
        path=P+name
        row=rows[path]
        for which,data in (('before',before),('after',after)):
            assert hashlib.sha256(data).hexdigest()==row[which+'_sha256']
            assert hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()==row[which+'_blob']
        for alg in ('sha256','blob'):
            assert sidscope_reader_assets_hash(ROOT,path,row['before_'+alg],alg)==row['after_'+alg]
            if row['prior_spans']:
                with pytest.raises(AssertionError): sidscope_reader_assets_hash(ROOT,path,'0'*len(row['before_'+alg]),alg)
        with pytest.raises(AssertionError): before_sidscope_reader_assets(ROOT,path,after+b'\n')


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
    for name in ('official-check.json','NOTICE.txt','method.md'):
        assert len(set(contents(name)))==1

    script=tmp_path/'run.py'
    script.write_bytes(contents('run.py')[1])
    run1=subprocess.run([sys.executable,'-I','-S',str(script)],capture_output=True,check=True)
    run2=subprocess.run([sys.executable,'-I','-S',str(script)],capture_output=True,check=True)
    assert run1.stdout==run2.stdout==(tmp_path/'results.json').read_bytes()==contents('results.json')[1]
    assert '公式の実装ではない' in subprocess.run([sys.executable,str(script),'--help'],text=True,capture_output=True,check=True).stdout

    old,new=map(yaml.safe_load,contents('lab.yaml'))
    assert {k for k in old if old[k]!=new[k]}=={'sections'}
    assert {k for k in old['sections'] if old['sections'][k]!=new['sections'][k]}=={'overview'}
    overview=new['sections']['overview']
    assert all(x in overview for x in ('同じ先頭の符号','NDCG@20','0.976','0.900','0.083','6.4%','3.4%'))
    assert 'Lab' not in overview
    assert contents('README.md')[1].decode().count(overview)==1
    guide=contents('mapping.md')[1].decode().split('## 配布ファイルの読み方',1)[1]
    assert all(x in guide for x in ('official_preflight_status','official_quickstart_mapping','target_path_survives','unique_item_hit'))


def test_historical_reader_chain_has_exact_order():
    from prose_preservation import (
        reading_prose_hash,revised_hash,yomiyasu_hash,paper_overview_rewrite_hash,
        semantic_id_pair_full_rewrite_hash,before_semantic_id_pair_full_rewrite,
    )
    overview=json.loads((ROOT/'tests/paper_overview_hashes.json').read_text())
    ov=overview['files']|overview['mirrored']
    sem=json.loads((ROOT/'tests/semantic_id_pair_full_rewrite_hashes.json').read_text())['files']
    yom=json.loads((ROOT/'tests/yomiyasu_revision_hashes.json').read_text())['files']
    orig=json.loads((ROOT/'tests/prose_revision_hashes.json').read_text())['files']
    for name in ('README.md','lab.yaml','mapping.md','run.py','results.json'):
        p=P+name
        previous,present=contents(name)
        end=sidscope_reader_assets_rows(ROOT)[p]
        for alg in ('sha256','blob'):
            before='before_'+alg
            after='after_'+alg
            if p in sem:
                assert semantic_id_pair_full_rewrite_hash(ROOT,p,sem[p][before],alg)==end[before]
                if p in ov:
                    assert paper_overview_rewrite_hash(ROOT,p,ov[p][before],alg)==sem[p][before]
                assert yomiyasu_hash(ROOT,p,yom[p][before],alg)==end[after]
                oldest=before_semantic_id_pair_full_rewrite(ROOT,p,previous)
                assert oldest!=previous
                start=(ov[p] if p in ov else sem[p])[before]
            elif p in orig:
                assert orig[p][after]==end[before]
                assert revised_hash(ROOT,p,orig[p][before],alg)==end[after]
                start=end[before]
            else:
                start=end[before]
            assert reading_prose_hash(ROOT,p,start,alg)==end[after]
            with pytest.raises(AssertionError):
                reading_prose_hash(ROOT,p,'0'*len(start),alg)
