"""Preserve the paper-only overview and the deliberately bounded PILOT toy."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml
from prose_preservation import pilot_full_prose_hash, before_pilot_full_prose

ROOT = Path(__file__).resolve().parents[1]
P = 'papers/pilot-experiment-lifecycle/'
NAMES = {'README.md','lab.yaml','mapping.md','method.md','results.json','run.py'}


def test_pilot_source_receipt_is_exact_and_reversible():
    entries = json.loads((ROOT/'tests/pilot_full_prose_hashes.json').read_text())['files']
    assert set(entries) == {P+n for n in NAMES}
    for p,row in entries.items():
        final=(ROOT/p).read_bytes()
        prior=before_pilot_full_prose(ROOT,p,final)
        for alg,digest in {
            'sha256': lambda b: hashlib.sha256(b).hexdigest(),
            'blob': lambda b: hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest(),
        }.items():
            assert digest(prior)==row['before'][alg]
            assert pilot_full_prose_hash(ROOT,p,digest(prior),alg)==digest(final)
            with pytest.raises(AssertionError):
                pilot_full_prose_hash(ROOT,p,digest(final),alg)
        with pytest.raises(AssertionError):
            before_pilot_full_prose(ROOT,p,final+b'\n')


def test_pilot_paper_data_and_toy_outcomes_are_separate_and_unchanged():
    p=P+'lab.yaml'
    b=(ROOT/p).read_bytes()
    a=yaml.safe_load(before_pilot_full_prose(ROOT,p,b))
    b=yaml.safe_load(b)
    for key in ('id','arxiv_id','authors','verification','urls','year','status','title','source_review'):
        assert a[key]==b[key]
    assert a['sections']['overview']==b['sections']['overview']
    p=P+'results.json'
    b=(ROOT/p).read_bytes()
    a,b=(json.loads(v) for v in (before_pilot_full_prose(ROOT,p,b),b))
    for key in ('verification','trace','memories','tree','checks'):
        assert a[key]==b[key]
    assert b['experiments'][1]['metrics']==a['experiments'][1]['metrics']
    assert set(b['experiments'][1]['metrics'])=={'ROAM','PILOT'}
    assert [x['率'] for x in b['experiments'][1]['metrics'].values()]==[53.33,93.33]


def test_pilot_transition_toy_does_not_authenticate_its_input_and_runs_alone(tmp_path):
    root=ROOT/P
    script=tmp_path/'run.py'
    script.write_bytes((root/'run.py').read_bytes())
    subprocess.run([sys.executable,'-S',str(script)],capture_output=True,text=True,check=True)
    assert (tmp_path/'results.json').read_bytes()==(root/'results.json').read_bytes()
    values={}
    exec(compile(script.read_bytes(),str(script),'exec'),values)
    t=values['transition']
    # The input called promote is already supplied by the toy; there is no certificate validator.
    assert t('observe','promote',healthy=True,approved=False,confirm=False)=='confirm'
    assert t('observe','promote',healthy=False,approved=True)=='paused'
    assert t('confirm','deliver',approved=True,confirm=False)=='confirm'
    assert t('confirm','deliver',approved=True,confirm=True)=='delivered'
    p=P+'run.py'
    b=script.read_bytes()
    a=before_pilot_full_prose(ROOT,p,b)
    class IgnoreText(ast.NodeTransformer):
        def visit_Constant(self, node):
            return ast.Constant('<text>') if isinstance(node.value,str) else node
    assert ast.dump(IgnoreText().visit(ast.parse(a)))==ast.dump(IgnoreText().visit(ast.parse(b)))
