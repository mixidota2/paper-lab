import ast
import json
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest
import yaml

from prose_preservation import before_harness_r1_full_prose

ROOT=Path(__file__).resolve().parents[1]
P='papers/harness-r1/'
N={'lab.yaml','mapping.md','method.md','results.json','run.py',*[f'figures/{n}.svg' for n in ('ablation','engineer-target','lifecycle')]}
def pair(k):
    p=P+k
    raw=(ROOT/p).read_bytes()
    return before_harness_r1_full_prose(ROOT,p,raw),raw
def test_harness_r1_paper_only_overview_with_equal_weight_and_separate_ablation():
    paths=json.loads((ROOT/'tests/harness_r1_full_prose_hashes.json').read_bytes())['files']
    assert set(paths)=={P+n for n in N}
    for n in N:
        a,b=pair(n)
        assert a!=b
        with pytest.raises(AssertionError):
            before_harness_r1_full_prose(ROOT,P+n,b+b'\n')
    prior,current=map(yaml.safe_load,pair('lab.yaml'))
    for k in ('id','urls','arxiv_id','authors','verification'):
        assert prior[k]==current[k]
    o=current['sections']['overview']
    assert o.count('\n\n')==1
    assert all(x in o for x in ('44.3%から53.6%', '9.3ポイント', '同じ重み', '全体の改善になるわけではありません'))
    assert all(x not in o for x in ('Lab','教材','run.py','<figure','<table'))
    text=current['sections']['evidence']
    assert all(x in text for x in ('46.4%','59.2%','64.2%','53.1%','44.2%','52.5%','52.2%','49.8%','49.2%','1,270課題','一次資料'))
def test_harness_r1_static_figure_geometry_and_numeric_replay(tmp_path):
    for k in N:
        if k.endswith('.svg'):
            def parse(b):
                t=ET.fromstring(b)
                return [(e.tag,e.attrib,len(e)) for e in t.iter()],[e.text for e in t.iter() if e.text and e.text.replace('.','').isdigit()]
            assert parse(pair(k)[0])==parse(pair(k)[1])
    for n,source in enumerate(pair('run.py')):
        target=tmp_path/f'example-{n}.py'
        target.write_bytes(source)
        subprocess.check_call([sys.executable,str(target)])
        assert (tmp_path/'results.json').read_bytes()==pair('results.json')[n]
    a,b=map(json.loads,pair('results.json'))
    a.pop('note');b.pop('note')
    a['experiments'][0].pop('name');b['experiments'][0].pop('name')
    assert a==b
    m=b['experiments'][0]['metrics']
    assert m['base']==.2 and m['full']==1 and [v for k,v in m.items() if k.startswith('without_')]==[.8]*4
