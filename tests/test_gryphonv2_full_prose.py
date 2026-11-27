from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import json, shutil, subprocess, sys
from xml.etree import ElementTree as E
import yaml
from prose_preservation import before_gryphonv2_full_prose

ROOT=Path(__file__).resolve().parents[1]
P='papers/gryphon-v2-cascade/'

def raw(n):
    a=(ROOT/(P+n)).read_bytes()
    return a,before_gryphonv2_full_prose(ROOT,P+n,a)

def test_gryphonv2_preserves_author_overview_figure_values_and_toy(tmp_path):
    a,b=map(yaml.safe_load,raw('lab.yaml'))
    assert a['sections']['overview']==b['sections']['overview']
    assert a['source_review']==b['source_review'] and a['verification']==b['verification']
    assert [x['path'] for x in a['figures']]==[x['path'] for x in b['figures']]
    for n in [x['path'] for x in a['figures']]:
        a1,b1=map(E.fromstring,raw(n))
        assert a1.attrib==b1.attrib and a1.get('role')=='img'
    a,b=map(json.loads,raw('results.json'))
    assert a.pop('note')!=b.pop('note')
    assert a['experiments'][0].pop('name')!=b['experiments'][0].pop('name')
    assert a['controls'].pop('loss')!=b['controls'].pop('loss')
    assert a==b
    run=tmp_path/'run.py'
    shutil.copyfile(ROOT/(P+'run.py'),run)
    subprocess.run([sys.executable,str(run)],check=True)
    assert (tmp_path/'results.json').read_bytes()==(ROOT/(P+'results.json')).read_bytes()

def test_gryphonv2_source_means_and_cap_are_different_boundaries():
    rollout,impressions=set(range(10)),{0,10}
    w=Counter()
    for xs in rollout,impressions:
        for x in xs:
            w[x]+=F(1,len(xs))
    assert len(rollout|impressions)==11 and F(len(rollout),11)>F(9,10)
    assert w[0]==F(3,5) and w[1]==F(1,10) and w[10]==F(1,2) and sum(w.values())==2
    groups=[('high',3),('middle',3),('low',3)]
    while sum(v for _,v in groups)>8:
        groups.pop()
    assert groups==[('high',3),('middle',3)]
    m=(ROOT/(P+'method.md')).read_text()
    assert '1/10＋1/2' in m and '常に1,200曲が残るわけではない' in m
    e=yaml.safe_load((ROOT/(P+'lab.yaml')).read_text())['sections']['evidence']
    assert all(x in e for x in ('約4倍','重い教師をつないで','応答時間は同程度','8%ずつ'))
