from decimal import Decimal as D
from itertools import chain
from pathlib import Path
from random import Random
import json, math, shutil, subprocess, sys
from xml.etree import ElementTree as E
import yaml
from prose_preservation import before_gr4ad_full_prose

ROOT=Path(__file__).resolve().parents[1]
P='papers/gr4ad-ads-generative/'
def both(name):
    now=(ROOT/(P+name)).read_bytes()
    return now,before_gr4ad_full_prose(ROOT,P+name,now)

def test_gr4ad_overview_data_and_figure_values_are_unchanged(tmp_path):
    a,b=map(yaml.safe_load,both('lab.yaml'))
    assert a['sections']['overview']==b['sections']['overview']
    assert a['sections']['overview'] in (ROOT/(P+'README.md')).read_text()
    assert a['source_review']==b['source_review'] and a['verification']==b['verification']
    assert [x['path'] for x in a['figures']]==[x['path'] for x in b['figures']]
    for n in [f['path'] for f in a['figures']]:
        n1,n0=map(E.fromstring,both(n))
        assert n1.attrib==n0.attrib and n1.attrib['role']=='img'
    a,b=map(json.loads,both('results.json'))
    for k in ('note','definition'):
        assert a.pop(k)!=b.pop(k)
    assert a['experiments'][0].pop('name')!=b['experiments'][0].pop('name')
    assert a==b
    run=tmp_path/'run.py'
    shutil.copyfile(ROOT/(P+'run.py'),run)
    subprocess.run([sys.executable,str(run)],check=True)
    assert (tmp_path/'results.json').read_bytes()==(ROOT/(P+'results.json')).read_bytes()

def test_gr4ad_local_precut_and_different_prefix_width_are_not_equivalent():
    s=(ROOT/(P+'method.md')).read_text()
    assert all(x in s for x in ['対数比の**絶対値**','同点時の順序','同じ生成段の幅kを変えない','候補数nで取り得る最大の差n−1'])
    sort=lambda v:sorted(v,key=lambda t:(-t[0],t[1],t[2]))
    r=Random(260222732)
    for _ in range(500):
        k=r.randrange(1,10)
        rows=[[(r.randrange(-3,4),i,j) for j in range(r.randrange(1,25))]
              for i in range(r.randrange(1,18))]
        assert sort(chain.from_iterable(rows))[:k]==sort(chain.from_iterable(sort(row)[:k] for row in rows))[:k]
    prefixes=[('A',-.51),('B',-.92)]
    continuations={'A':[('a1',-.69),('a2',-.70)],'B':[('b1',-.01),('b2',-4.61)]}
    top=lambda w:max((score+suffix,k+'/'+j) for k,score in prefixes[:w] for j,suffix in continuations[k])[1]
    assert top(1)=='A/a1' and top(2)=='B/b1'
    assert D('1.07') < 1 + D('0.1826')
    signed=[math.log(.8/.2),math.log(.2/.8)]
    assert math.isclose(sum(signed)/2,0.) and sum(map(abs,signed))/2>1.
