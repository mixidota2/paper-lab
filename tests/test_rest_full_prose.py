import json
import math
from pathlib import Path
import runpy
import yaml
from prose_preservation import before_rest_full_prose

ROOT=Path(__file__).resolve().parents[1]
SLUG='rest-sequence-ranking'
P=ROOT/'papers'/SLUG

def test_rest_reference_and_other_shared_runner_outputs(tmp_path):
    name='papers/_toy_common.py'
    now=(ROOT/name).read_bytes()
    p=tmp_path/'baseline.py'
    p.write_bytes(before_rest_full_prose(ROOT,name,now))
    b,a=map(runpy.run_path,(str(p),str(ROOT/name)))
    assert a['IDS']==b['IDS'] and len(a['IDS'])==11
    for key in a['IDS']:
        if key!=SLUG:
            assert a['compute'](key)==b['compute'](key),key
    data=json.loads((P/'results.json').read_text())
    expected=b['compute'](SLUG)
    assert a['compute'](SLUG)==data
    assert [(f['value'],[x['value'] for x in f['bars']]) for f in data['explorer']['frames']]==[(f['value'],[x['value'] for x in f['bars']]) for f in expected['explorer']['frames']]

def test_rest_primary_overview_formula_and_gradient_boundary():
    filename='papers/'+SLUG+'/lab.yaml'
    raw=(ROOT/filename).read_bytes()
    new,old=map(yaml.safe_load,(raw,before_rest_full_prose(ROOT,filename,raw)))
    assert new['sections']['overview']==old['sections']['overview']
    assert new['verification']==old['verification']
    assert [x['formula'] for x in new['teaching_figures'][1]['steps']]==[x['formula'] for x in old['teaching_figures'][1]['steps']]
    e=new['sections']['evidence']
    assert all(x in e for x in ['20%','5.8倍','系列処理部分','20分の1','p<0.01','50 ms'])
    y,seq,nonseq,g,w=1,.2,.9,-.1,.015
    main=2*(nonseq+g*seq-y)*g
    aux=2*w*(seq-y)
    assert math.isclose(main,.024) and math.isclose(aux,-.024)
    assert math.isclose(main+aux,0,abs_tol=1e-9)
