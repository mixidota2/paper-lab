"""Keep the toy results and release status independent of the editorial changes."""
from pathlib import Path
import json
import yaml
from prose_preservation import before_reusegr_full_prose

ROOT=Path(__file__).resolve().parents[1]
REL='papers/query-prefix-reuse/'
P=ROOT/REL
def before(name):
    return before_reusegr_full_prose(ROOT,REL+name,(P/name).read_bytes())

def test_reusegr_receipt_and_source_boundary():
    a=yaml.safe_load((P/'lab.yaml').read_bytes())
    b=yaml.safe_load(before('lab.yaml'))
    for k in ('verification','topics','title','authors','status','arxiv_id','submitted','urls'):
        assert a[k]==b[k]
    assert a['status']=='draft'
    sec=a['sections']
    overview=sec['overview']
    assert len(overview.split('\n\n'))==3
    assert all(x in overview for x in ('44,225件','85.82%','71.45 ms','1.05%','0.93%','注文数'))
    assert all(x not in overview for x in ('人工','Lab','<figure','<table'))
    e=sec['evidence']
    assert all(x in e for x in ('286,046','82.38%','83.40%','利用者は各群で約1,280万人','0.2104','一次資料'))
    assert all(x in sec['results'] for x in ('0.18ms','67.01ms','3.84ms','0.42ms','約2.44時間','P95'))

def test_reusegr_unchanged_results_except_explanatory_labels():
    a=json.loads((P/'results.json').read_bytes())
    b=json.loads(before('results.json'))
    x,y=(m.pop('not_tested') for m in (a,b))
    assert len(x)==len(y)==7 and x!=y
    assert a==b
