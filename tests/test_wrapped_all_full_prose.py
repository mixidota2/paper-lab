"""Verify the study, evidence discrepancy, and toy calculations separately."""
from ast import parse, dump, FunctionDef, Expr, Constant
from pathlib import Path
import json
import subprocess
import sys

import pytest
import yaml

from prose_preservation import before_wrapped_all_full_prose

ROOT=Path(__file__).resolve().parents[1]
REL='papers/wrapped-produce-placement-controlled-trial/'


def pair(name):
    path=REL+name
    data=(ROOT/path).read_bytes()
    return before_wrapped_all_full_prose(ROOT,path,data),data


def test_names_scope_and_scientific_denominators():
    a,b=map(yaml.safe_load,pair('lab.yaml'))
    for key in ('id','doi','title','authors','urls','status','verification','related_threads'):
        assert a[key]==b[key]
    overview=b['sections']['overview']
    assert all(m in overview for m in ('36店舗','18店','主な指標','0.32標準偏差','3.3ポイント','−2.5〜9.2','無作為','配置だけの効果'))
    assert all(m not in overview for m in ('Lab','教材','操作図'))
    evidence=pair('evidence.md')[1].decode()
    assert all(m in evidence for m in ('要旨の0.11〜0.53','本文§3.2の上限表記は0.5','227人','248人','半年間に一度でも','女性で0.25標準偏差','子どもの差は0.06標準偏差','週0.20回高かった'))
    assert all(m in pair('mapping.md')[1].decode() for m in ('53,090 bytes','6362fec57b34ea85153a7a6bd2382a01abd4c176440a33e2d34df27894395451'))


def test_numeric_arrays_and_regeneration(tmp_path):
    a,b=map(json.loads,pair('results.json'))
    assert a['verification']==b['verification']
    assert len(a['synthetic'])==27 and a['synthetic']==b['synthetic']
    for key in ('household','store'):
        assert {k:a['reported'][key][k] for k in ('rows','domain')}=={k:b['reported'][key][k] for k in ('rows','domain')}
    # Descriptive docstrings may change, while the computational AST must not.
    def numerical(src):
        nodes=[n for n in parse(src).body if isinstance(n,FunctionDef) and n.name in ('line_fit','simulate')]
        for n in nodes:
            assert isinstance(n.body[0],Expr) and isinstance(n.body[0].value,Constant)
            n.body=n.body[1:]
        return [dump(n) for n in nodes]
    old,new=pair('run.py')
    assert len(numerical(old))==2 and numerical(old)==numerical(new)
    script=tmp_path/'run.py'; script.write_bytes(new)
    subprocess.run([sys.executable,str(script),'--test'],check=True)
    subprocess.run([sys.executable,str(script)],check=True)
    for name in ('results.json','evidence.md','experiment.md'):
        assert (tmp_path/name).read_bytes()==pair(name)[1]


def test_all_sources_exact_with_corruption_check():
    receipt=json.loads((ROOT/'tests/wrapped_all_full_prose_hashes.json').read_text())['files']
    names={'README.md','mapping.md','lab.yaml','method.md','results.json','run.py','evidence.md','experiment.md'}
    assert set(receipt)=={REL+n for n in names}
    for name in names:
        before,after=pair(name)
        assert before!=after
        with pytest.raises(AssertionError):
            before_wrapped_all_full_prose(ROOT,REL+name,after+b'\n')
