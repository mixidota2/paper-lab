"""Source scope, exact figures and fixed rules of the synthetic shelf problem."""
from pathlib import Path
import ast
import json
import re
import subprocess
import sys

import pytest
import yaml
from prose_preservation import before_assortment_all_full_prose

ROOT = Path(__file__).resolve().parents[1]
P = 'papers/assortment-replenishment-hard-constraints/'
NAMES={'README.md','experiment.md','implementation.md','interactive.html','interactive.js',
       'lab.yaml','mapping.md','method.md','model.js','results.json','run.py','validation.md'}

def pair(n):
    path=P+n
    raw=(ROOT/path).read_bytes()
    return before_assortment_all_full_prose(ROOT,path,raw),raw

def test_exact_archive_coverage():
    all_paths=json.loads((ROOT/'tests/assortment_all_full_prose_hashes.json').read_text())['files']
    assert set(all_paths)=={P+n for n in NAMES}
    for n in NAMES:
        old,new=pair(n)
        assert old!=new
        with pytest.raises(AssertionError):
            before_assortment_all_full_prose(ROOT,P+n,new+b'\n')

def test_abstract_is_paper_only_and_uses_the_field_study_boundary():
    a,b=map(yaml.safe_load,pair('lab.yaml'))
    for k in ('title','doi','authors','year','submitted','verification','urls'):
        assert a[k]==b[k]
    ov=b['sections']['overview']
    for k in ('HübnerとKuhn','飲料データ','最大14%','あと','棚を変更しておらず'):
        assert k in ov or (k=='あと' and '決めてから調整' in ov), k
    assert not any(k in ov for k in ('Lab','架空','1.4個','教材','操作'))
    assert ov in (ROOT/(P+'README.md')).read_text()
    assert all(k in b['sections']['evidence'] for k in ('1〜8%', '67〜87%', '作業費'))
    for x,y in zip(a['teaching_figures'],b['teaching_figures'],strict=True):
        assert all(x[k]==y[k] for k in ('kind','after','id','source','locator'))
        for p,q in zip(x.get('steps',()),y.get('steps',()),strict=True):
            assert p['formula']==q['formula'] and p['formula_mathml']==q['formula_mathml']

def test_rebuild_exact_result_without_changing_any_value(tmp_path):
    def computation(v):
        t=ast.parse(v)
        assert isinstance(t.body[0],ast.Expr)
        del t.body[0]
        for n in ast.walk(t):
            if isinstance(n,ast.keyword) and n.arg=='note':
                assert isinstance(n.value,ast.Constant)
                n.value.value=''
        return ast.dump(t)
    a,b=pair('run.py')
    assert computation(a)==computation(b)
    a,b=map(json.loads,pair('results.json'))
    assert a.pop('note')!=b.pop('note') and a==b
    script=tmp_path/'run.py';script.write_bytes(pair('run.py')[1])
    subprocess.run([sys.executable,str(script)],check=True)
    assert (tmp_path/'results.json').read_bytes()==pair('results.json')[1]

def test_controls_and_saved_model_implementation_do_not_change():
    a,b=pair('model.js')
    assert b.replace(b.splitlines(keepends=True)[1],b'',1)==a
    for n,r in [('interactive.html',rb'(?:id|value|src)="[^"]+"'),
                ('interactive.js',rb"\$\('[a-zA-Z-]+'\)|addEventListener\('[a-z]+'")]:
        a,b=pair(n)
        assert re.findall(r,a)==re.findall(r,b)
