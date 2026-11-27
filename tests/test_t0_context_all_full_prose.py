"""Validate all reader sources and exact paper comparison boundaries."""
import ast
import json
from pathlib import Path
import re
import subprocess
import sys
import pytest
import yaml
from prose_preservation import before_t0_context_all_full_prose

ROOT=Path(__file__).resolve().parents[1]
P='papers/t0-tsfm-forecasting-with-context/'
NAMES={'README.md','lab.yaml','mapping.md','method.md','results.json','run.py'}

def pair(n):
    path=P+n
    current=(ROOT/path).read_bytes()
    return before_t0_context_all_full_prose(ROOT,path,current),current

def test_exact_prose_coverage_and_strict_prior_store():
    manifest=json.loads((ROOT/'tests/t0_context_all_full_prose_hashes.json').read_bytes())['files']
    assert set(manifest)=={P+n for n in NAMES}
    for n in NAMES:
        a,b=pair(n);assert a!=b
        with pytest.raises(AssertionError):
            before_t0_context_all_full_prose(ROOT,P+n,b+b'\n')

def test_primary_comparison_and_embedded_numerical_inputs():
    old,new=map(yaml.safe_load,pair('lab.yaml'))
    assert all(old[k]==new[k] for k in ('arxiv_id','title','authors','verification','urls'))
    o=new['sections']['overview']
    assert all(v in o for v in ('Meyerら','36.7%','43.0%','6.3ポイント','19課題','11課題','43%減りました'))
    assert not any(v in o for v in ('Lab','教材','<figure','9.95%'))
    for a,b in zip(old['teaching_figures'],new['teaching_figures'],strict=True):
        assert all(a[k]==b[k] for k in ('id','kind','locator','source','after'))
        assert [x['formula'] for x in a.get('steps',())]==[x['formula'] for x in b.get('steps',())]
    def widget(data):
        s=data['sections']['evidence'].split('<figure')[1]
        f=json.loads(re.search(r'<script[^>]+data-frames>(.*?)</script>',s).group(1))
        return re.findall(r'<option value="([01])"',s),[re.findall(r'<strong>([^<]+)</strong>',x) for x in f]
    assert widget(old)==widget(new)==(['0','1'],[['36.7','32.9'],['43.0','35.6']])

def test_numerical_reasoning_and_data_regeneration_unchanged(tmp_path):
    def strip(v):
        t=ast.parse(v);del t.body[0]
        for n in ast.walk(t):
            if isinstance(n,ast.keyword) and n.arg=='note':
                assert isinstance(n.value,ast.Constant)
                n.value.value=''
        return ast.dump(t)
    a,b=pair('run.py')
    assert strip(a)==strip(b)
    a,b=map(json.loads,pair('results.json'))
    assert a.pop('note')!=b.pop('note') and a==b
    p=tmp_path/'run.py';p.write_bytes(pair('run.py')[1])
    subprocess.run([sys.executable,str(p)],check=True)
    assert (tmp_path/'results.json').read_bytes()==pair('results.json')[1]
