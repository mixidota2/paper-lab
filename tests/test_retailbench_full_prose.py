"""Keep RetailBench paper results, local accounting, and prior prose distinct."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from prose_preservation import before_retailbench_full_prose, retailbench_full_prose_hash

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'retailbench-long-horizon-store-agents'
P = 'papers/' + SLUG + '/'


def test_retailbench_source_receipt_rejects_unknown_bytes_and_prior_hash():
    rows = json.loads((ROOT/'tests/retailbench_full_prose_hashes.json').read_text())['files']
    assert set(rows) == {'paper_lab/retailbench30.py'} | {
        P + name for name in ('README.md', 'lab.yaml', 'method.md', 'mapping.md',
                              'interactive.html', 'interactive.js', 'model.js',
                              'run.py', 'results.json')
    }
    for path, row in rows.items():
        data = (ROOT/path).read_bytes()
        old = before_retailbench_full_prose(ROOT, path, data)
        for algorithm, f in {
            'sha256': lambda v: hashlib.sha256(v).hexdigest(),
            'blob': lambda v: hashlib.sha1(b'blob ' + str(len(v)).encode() + b'\0' + v).hexdigest(),
        }.items():
            assert f(old) == row['before'][algorithm]
            assert retailbench_full_prose_hash(ROOT,path,f(old),algorithm) == f(data)
            with pytest.raises(AssertionError):
                retailbench_full_prose_hash(ROOT,path,f(data),algorithm)
        with pytest.raises(AssertionError):
            before_retailbench_full_prose(ROOT, path, data + b'\n')


def test_retailbench_preserves_overview_and_saved_scientific_values():
    path = P + 'lab.yaml'
    raw = (ROOT/path).read_bytes()
    before = yaml.safe_load(before_retailbench_full_prose(ROOT, path, raw))
    after = yaml.safe_load(raw)
    assert after['sections']['overview'] == before['sections']['overview']
    for key in ('arxiv_id','source_review','urls','verification','id','title','authors','status'):
        assert before[key] == after[key]
    for was, now in zip(before['teaching_figures'], after['teaching_figures'], strict=True):
        for key in ('id','source','locator','kind'):
            assert was[key] == now[key]
        assert [bar['value'] for bar in was.get('bars',[])] == [bar['value'] for bar in now.get('bars',[])]
    path = P + 'results.json'
    raw = (ROOT/path).read_bytes()
    before, after = (json.loads(v) for v in (before_retailbench_full_prose(ROOT,path,raw), raw))
    assert after.pop('limitations') != before.pop('limitations')
    assert before == after


def test_retailbench_distributed_run_reproduces_saved_bytes(tmp_path):
    original = ROOT/P
    program = tmp_path/'run.py'
    program.write_bytes((original/'run.py').read_bytes())
    proc = subprocess.run([sys.executable,'-S',str(program)], capture_output=True, text=True, check=True)
    assert '240 daily accounting checks' in proc.stdout
    assert (tmp_path/'results.json').read_bytes() == (original/'results.json').read_bytes()
