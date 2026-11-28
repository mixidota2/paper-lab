from pathlib import Path
import hashlib
import json
import subprocess
import sys

import pytest
import yaml

from prose_preservation import before_pinterest_reader_full_prose, pinterest_reader_full_prose_hash

R=Path(__file__).resolve().parents[1]
P='papers/pinterest-causal-retrieval-shopping/'


def test_pinterest_exact_editorial_transition_leaves_numerical_output(tmp_path):
    rows=json.loads((R/'tests/pinterest_reader_full_prose_hashes.json').read_text())['files']
    assert rows.keys()=={P+n for n in ('README.md','lab.yaml','mapping.md','method.md','results.json','run.py')}
    old=None
    for p in rows:
        post=(R/p).read_bytes()
        prior=before_pinterest_reader_full_prose(R,p,post)
        assert (prior==post)==(p==P+'method.md')
        assert pinterest_reader_full_prose_hash(R,p,hashlib.sha256(prior).hexdigest())==hashlib.sha256(post).hexdigest()
        with pytest.raises(AssertionError):
            before_pinterest_reader_full_prose(R,p,post+b'\n')
        if p==P+'results.json':
            old=json.loads(prior)
    tmp=tmp_path/'run.py'
    tmp.write_bytes((R/(P+'run.py')).read_bytes())
    subprocess.run([sys.executable,tmp],check=True,capture_output=True)
    out=(tmp_path/'results.json').read_bytes()
    assert out==(R/(P+'results.json')).read_bytes()
    final=json.loads(out)
    assert old is not None
    for q in (old,final):
        z=q['explorer']
        z.pop('label')
        z.pop('metric')
        assert len(z['frames'])==7 and len(q['dr'])==3
        for f in z['frames']:
            f.pop('note')
            for b in f['bars']:
                b.pop('label')
    assert old==final


def test_pinterest_article_keeps_the_two_controls_and_outcomes_separate():
    sec=yaml.safe_load((R/(P+'lab.yaml')).read_bytes())['sections']
    assert all(s in sec['overview'] for s in ('無作為','しきい値','約40%','1.10%','85%減らしたのは別の群'))
    assert '0.43%' not in sec['overview'] and 'Lab' not in sec['overview']
    assert all(s in sec['evidence'] for s in ('64.4%','64.6%','1.10%','0.43%','件数（Volume）','分母が何かは載っていない','統計的に明確な差が出ていない'))
    assert (R/(P+'README.md')).read_text().count(sec['overview'])==1
