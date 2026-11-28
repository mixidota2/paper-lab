import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from prose_preservation import before_sid_ope_reader_full_prose, sid_ope_reader_full_prose_hash

R=Path(__file__).resolve().parents[1]
P='papers/sid-ope-hierarchy/'


def test_sid_ope_reader_assets_and_conditional_polyframes(tmp_path):
    rows=json.loads((R/'tests/sid_ope_reader_full_prose_hashes.json').read_text())['files']
    changed={'lab.yaml','mapping.md','run.py','results.json'}
    old_data=None
    for path in rows:
        b=(R/path).read_bytes()
        a=before_sid_ope_reader_full_prose(R,path,b)
        assert (a!=b)==(path.removeprefix(P) in changed)
        assert sid_ope_reader_full_prose_hash(R,path,hashlib.sha256(a).hexdigest())==hashlib.sha256(b).hexdigest()
        with pytest.raises(AssertionError):
            before_sid_ope_reader_full_prose(R,path,b+b'\n')
        if path==P+'results.json':
            old_data=json.loads(a)
    src=tmp_path/'run.py'
    src.write_bytes((R/(P+'run.py')).read_bytes())
    subprocess.run([sys.executable,src],check=True)
    out=(tmp_path/'results.json').read_bytes()
    assert out==(R/(P+'results.json')).read_bytes()
    final=json.loads(out)
    assert old_data is not None
    for q in (old_data,final):
        q.pop('note')
        q['explorer'].pop('label')
        assert len(q['explorer']['frames'])==4
        for f in q['explorer']['frames']:
            f.pop('note')
    assert old_data==final


def test_sid_ope_paper_score_does_not_promise_best_policy():
    sec=yaml.safe_load((R/(P+'lab.yaml')).read_bytes())['sections']
    assert all(s in sec['overview'] for s in ('KuaiRand','SNIPS','0.155','0.087','同じ数のグループ','見落とします'))
    assert 'Kendall' not in sec['overview'] and 'Lab' not in sec['overview']
    assert all(s in sec['evidence'] for s in ('16種類の方策','0.08','0.13','0.15','0.18','区間で区別できず','同じグループ内で商品を替えるだけ'))
