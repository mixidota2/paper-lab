"""Preserve both the paper's comparison scope and the toy computation."""
from pathlib import Path
import ast
import importlib.util
import json
import subprocess
import sys

import pytest
import yaml
from prose_preservation import before_or_transformer_all_full_prose

ROOT=Path(__file__).resolve().parents[1]
P='papers/or-transformer-joint-replenishment/'
W='paper_lab/batch29.py'
FILES={P+n for n in ('README.md','lab.yaml','mapping.md','method.md','results.json','run.py')} | {W}

def pair(path):
    raw=(ROOT/path).read_bytes()
    return before_or_transformer_all_full_prose(ROOT,path,raw),raw

def test_exact_prior_for_all_reader_content():
    rows=json.loads((ROOT/'tests/or_transformer_all_full_prose_hashes.json').read_bytes())['files']
    assert set(rows)==FILES
    for path in FILES:
        old,new=pair(path)
        assert old!=new
        with pytest.raises(AssertionError):
            before_or_transformer_all_full_prose(ROOT,path,new+b'\n')

def test_paper_headline_compares_like_with_like():
    old,new=map(yaml.safe_load,pair(P+'lab.yaml'))
    for k in ('id','arxiv_id','authors','urls','verification','status'):
        assert old[k]==new[k]
    s=new['sections'];ov=s['overview']
    assert all(x in ov for x in ('Liuら','1,024商品','50回','PPOより約75%','128回','実店舗では検証していません'))
    assert not any(x in ov for x in ('Lab','Gurobi','0.0432','教材'))
    assert all(x in s['evidence'] for x in ('6,400回','発注量0','8回','19.1%','48時間49分','内訳は確認できていません'))
    for a,b in zip(old['teaching_figures'],new['teaching_figures'],strict=True):
        for k in ('id','after','locator','columns','values','bars'):
            assert a.get(k)==b.get(k)
        assert [x['formula'] for x in a.get('steps',())]==[x['formula'] for x in b.get('steps',())]

def test_runner_and_labels_keep_toy_results(tmp_path):
    def computation(raw):
        t=ast.parse(raw);del t.body[0]
        for n in ast.walk(t):
            if isinstance(n,ast.keyword) and n.arg=='note':
                assert isinstance(n.value,ast.Constant)
                n.value.value=''
        return ast.dump(t)
    a,b=pair(P+'run.py')
    assert computation(a)==computation(b)
    x,y=map(json.loads,pair(P+'results.json'))
    assert x.pop('note')!=y.pop('note') and x==y
    assert [f['pathwise'] for f in y['frames']]==[-8,-3,2]
    p=tmp_path/'run.py';p.write_bytes(b)
    subprocess.run([sys.executable,str(p)],check=True)
    assert (tmp_path/'results.json').read_bytes()==pair(P+'results.json')[1]

def test_only_the_target_widget_output_changed(tmp_path):
    import paper_lab.batch29 as new
    a,b=pair(W)
    prior=tmp_path/'prior.py';prior.write_bytes(a)
    spec=importlib.util.spec_from_file_location('paper_lab.prior_batch29_for_test',prior)
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    for slug in ('sabreagent-design-time-inventory','switch-hurdle-intermittent-demand'):
        data=json.loads((ROOT/'papers'/slug/'results.json').read_bytes())
        assert old.widget(data)==new.widget(data)
    data=json.loads((ROOT/(P+'results.json')).read_bytes())
    first,now=old.widget(data),new.widget(data)
    assert first!=now
    assert '確率を決める値（logit）' in now and '学習した発注量ではありません' in now
    assert now.count('data-frames')==first.count('data-frames')==1
    assert now.count('data-output')==first.count('data-output')==1
