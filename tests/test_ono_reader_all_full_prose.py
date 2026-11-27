from pathlib import Path
import ast
import json
import subprocess
import sys

import pytest
import yaml

from prose_preservation import before_ono_reader_all_full_prose

ROOT=Path(__file__).resolve().parents[1]
P='papers/ono-inventory-forecast-selection/'


def pair(name):
    final=(ROOT/(P+name)).read_bytes()
    return before_ono_reader_all_full_prose(ROOT,P+name,final),final


def test_exact_prose_and_paper_summary():
    receipt=json.loads((ROOT/'tests/ono_reader_all_full_prose_hashes.json').read_bytes())['files']
    assert set(receipt)=={P+k for k in ('README.md','lab.yaml','results.json','run.py')}
    for n in receipt:
        a,b=pair(n.removeprefix(P))
        assert a!=b
        with pytest.raises(AssertionError):
            before_ono_reader_all_full_prose(ROOT,n,b+b'\n')
    a,b=map(yaml.safe_load,pair('lab.yaml'))
    old=a['sections'].pop('overview')
    new=b['sections'].pop('overview')
    assert a==b and old!=new
    assert all(v in new for v in ('Onoら','LightGBM','M5公開売上','85,056','85,093','約0.04%','欠品費用は増えました','実店舗の発注を変えて測った結果ではありません'))
    assert all(v not in new for v in ('架空の例','Lab','画面','<table','<figure'))


def test_data_and_code_keep_numerical_cases(tmp_path):
    a,b=map(json.loads,pair('results.json'))
    aliases={}
    for old,new in zip(a['toy_service'],b['toy_service'],strict=True):
        aliases[new.pop('label')]=old.pop('label')
    assert a==b and len(aliases)==2
    class Normalize(ast.NodeTransformer):
        def visit_Constant(self,n):
            if isinstance(n.value,str) and n.value in aliases:
                n.value=aliases[n.value]
            return n
    def clean(s):
        t=ast.parse(s)
        assert isinstance(t.body.pop(0).value,ast.Constant)
        return ast.dump(Normalize().visit(t))
    old,new=pair('run.py')
    assert clean(old)==clean(new)
    p=tmp_path/'run.py'
    p.write_bytes(new)
    subprocess.run([sys.executable,str(p)],check=True)
    assert (tmp_path/'results.json').read_bytes()==pair('results.json')[1]
