from pathlib import Path
import collections
from decimal import Decimal as D, ROUND_HALF_EVEN
import itertools, json, runpy
import shutil, subprocess, sys
from xml.etree import ElementTree as E
import yaml
from prose_preservation import before_tagr_full_prose

ROOT=Path(__file__).resolve().parents[1]
P='papers/tagr-live-sid/'
def both(name):
    latest=(ROOT/(P+name)).read_bytes()
    return latest,before_tagr_full_prose(ROOT,P+name,latest)

def test_tagr_retains_paper_overview_source_numeric_outputs_and_figures(tmp_path):
    a,b=map(yaml.safe_load,both('lab.yaml'))
    assert a['sections']['overview']==b['sections']['overview']
    assert a['source_review']==b['source_review'] and a['verification']==b['verification']
    assert [z['path'] for z in a['figures']]==[z['path'] for z in b['figures']]
    r,s=map(json.loads,both('results.json'))
    assert r.pop('kind')!=s.pop('kind') and r==s
    p=tmp_path/'run.py'
    shutil.copyfile(ROOT/(P+'run.py'),p)
    subprocess.run([sys.executable,str(p)],check=True)
    assert (tmp_path/'results.json').read_bytes()==(ROOT/(P+'results.json')).read_bytes()
    for n in ('clocks.svg','collision.svg'):
        ins=[E.fromstring(data) for data in both('figures/'+n)]
        first,second=ins
        assert first.attrib==second.attrib
        assert first.get('role')=='img'
        def numeric(svg):
            return [x.text for x in svg.iter() if x.tag.endswith('text') and x.text.startswith(('ID ','Cpr = 1','Cpr = 2','Cpr = 4'))]
        assert numeric(first)==numeric(second)
    assert '4件中1件' in a['sections']['results']
    assert '100 ms未満' in a['sections']['what_we_did_not_verify']

def test_tagr_same_population_metric_order_survives_two_decimal_rounding():
    root=yaml.safe_load((ROOT/(P+'lab.yaml')).read_text())
    e=root['sections']['evidence']
    for v in ['N≥U+M','1+0.39','1+Col','1.09と0.15','1.01と0.02','1.14と0.16','+3.8%','DLRM比+16.1%']:
        assert v in e
    q=lambda x:x.quantize(D('.01'),rounding=ROUND_HALF_EVEN)
    for counts in itertools.product(range(1,6),repeat=3):
        u=D(len(counts))
        n=D(sum(counts))
        m=D(sum(v>1 for v in counts))
        assert q(n/u) >= 1+q(m/u)
    for c,f in [('1.36','.39'),('1.09','.15'),('1.01','.02'),('1.14','.16')]:
        assert D(c)<1+D(f)
