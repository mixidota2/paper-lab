import json
import subprocess
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import pytest
import yaml
from prose_preservation import before_swe_serve_full_prose
ROOT=Path(__file__).resolve().parents[1]
P='papers/swe-serve-inference-serving-agents/'
N={'README.md', 'lab.yaml', 'mapping.md', 'method.md', 'results.json', 'run.py'}
def pair(n):
    raw=(ROOT/(P+n)).read_bytes()
    return before_swe_serve_full_prose(ROOT,P+n,raw),raw
def test_swe_serve_paper_summary_with_numerators_and_current_source():
    indexes=json.loads((ROOT/'tests/swe_serve_full_prose_hashes.json').read_bytes())['files']
    assert set(indexes)=={P+n for n in N}
    for n in N:
        old,now=pair(n)
        assert old != now
        with pytest.raises(AssertionError):
            before_swe_serve_full_prose(ROOT,P+n,now+b'\n')
    old,now=map(yaml.safe_load,pair('lab.yaml'))
    for k in ('id','urls','arxiv_id','authors','verification'):
        assert old[k]==now[k]
    section=now['sections']['overview']
    assert section.count('\n\n')==1
    assert (ROOT/(P+'README.md')).read_text().count(section)==1
    assert all(x in section for x in ('53課題','19課題','627件','288件','435件','147件','45.9%','69.4%','同じ変更のまま'))
    assert not any(x in section for x in ('Lab','教材','図','|','<table'))
    assert sum((288,147,178,14))==627
    rate=lambda n:(Decimal(n)*100/627).quantize(Decimal('0.1'),rounding=ROUND_HALF_UP)
    assert tuple(map(str,map(rate,(288,435,147))))==('45.9','69.4','23.4')
def test_swe_serve_synthetic_inputs_and_output_numbers_stay_fixed(tmp_path):
    old, now=map(json.loads,pair('results.json'))
    for i,raw in enumerate(pair('run.py')):
        p=tmp_path/f'script-{i}.py'
        p.write_bytes(raw)
        out=subprocess.check_output([sys.executable,str(p)])
        expected=(old, now)[i]
        assert json.loads(out)==expected['variants']
        assert json.loads((tmp_path/'results.json').read_bytes())==expected
    assert old['variants']==now['variants']
    assert old['verification']==now['verification']
    for a,b in zip(old['explorer']['frames'],now['explorer']['frames'],strict=True):
        assert a['value']==b['value']
        assert [x['value'] for x in a['bars']]==[x['value'] for x in b['bars']]
        assert a['note']!=b['note']
    assert [x['bars'][0]['value'] for x in now['explorer']['frames']]==[3,2,1]
