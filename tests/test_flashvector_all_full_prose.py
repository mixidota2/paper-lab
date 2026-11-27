"""Check FlashVector prose changes without confounding paper and toy results."""
from pathlib import Path
import ast
import json
import re
import subprocess
import sys
import pytest
import yaml
from prose_preservation import before_flashvector_all_full_prose

ROOT=Path(__file__).resolve().parents[1]
PREFIX='papers/flashvector-unity-serving-stack-agent/'


def pair(name):
    path=PREFIX+name
    raw=(ROOT/path).read_bytes()
    return before_flashvector_all_full_prose(ROOT,path,raw),raw


def test_flashvector_full_reader_scope_and_exact_inverse():
    receipt=json.loads((ROOT/'tests/flashvector_all_full_prose_hashes.json').read_bytes())['files']
    assert set(receipt)=={PREFIX+n for n in ('README.md','lab.yaml','mapping.md','method.md','results.json','run.py')}
    for path in receipt:
        a,b=pair(path.removeprefix(PREFIX))
        assert a!=b
        with pytest.raises(AssertionError):
            before_flashvector_all_full_prose(ROOT,path,b+b'\n')


def test_flashvector_overview_is_evidence_and_widget_uses_the_same_artificial_values():
    a,b=map(yaml.safe_load,pair('lab.yaml'))
    assert all(a[k]==b[k] for k in ('id','title','authors','arxiv_id','verification','urls'))
    overview=b['sections']['overview']
    assert all(v in overview for v in ('Wuら','2.00倍','30倍','1.10倍','広告のクリック率','実際の配信要求を再生'))
    assert not any(v in overview for v in ('Lab','<figure','教材','<table'))
    evidence=b['sections']['evidence']
    assert all(v in evidence for v in ('271 ms','250 ms','記載の誤りなのか','350倍','約1.6倍'))
    def widget(data):
        selector=data['sections']['executable_understanding']
        frames=json.loads(re.search(r'<script[^>]+data-frames>(.*?)</script>',selector,re.S)[1])
        return re.findall(r'<option value="([0-9])"',selector),[re.findall(r'<strong>([.0-9]+(?: ms)?)</strong>',f) for f in frames]
    assert widget(a)==widget(b)==(list('01234'),[['2','0.98','220 ms'],['1.3','1.2','270 ms'],['1.1','1.03','230 ms'],['1.4','1.3','200 ms'],['1.3','1.2','230 ms']])
    assert [x['value'] for x in a['teaching_figures'][2]['bars']]==[x['value'] for x in b['teaching_figures'][2]['bars']]


def test_flashvector_runner_outputs_and_order_unchanged_except_prose(tmp_path):
    a,b=map(json.loads,pair('results.json'))
    aliases={b.pop('note'):a.pop('note')}
    for prior,current in zip(a['candidates'],b['candidates'],strict=True):
        aliases[current.pop('name')]=prior.pop('name')
    assert a==b and len(aliases)==6
    class Normalize(ast.NodeTransformer):
        def visit_Constant(self,node):
            if isinstance(node.value,str) and node.value in aliases:
                node.value=aliases[node.value]
            return node
    def clean(v):
        data=ast.parse(v)
        assert getattr(data.body.pop(0).value,'value')
        return ast.dump(Normalize().visit(data))
    old,new=pair('run.py')
    assert clean(old)==clean(new)
    p=tmp_path/'run.py'
    p.write_bytes(new)
    subprocess.run([sys.executable,str(p)],check=True)
    assert (tmp_path/'results.json').read_bytes()==pair('results.json')[1]
