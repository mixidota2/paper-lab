"""AgentX's revised copy preserves the paper-only overview and toy calculations."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml
from prose_preservation import before_overview_figure_relocations, agentx_full_prose_hash, before_agentx_full_prose

ROOT = Path(__file__).resolve().parents[1]
P = 'papers/agentx-kuaishou/'
NAMES = {'README.md', 'lab.yaml', 'mapping.md', 'method.md', 'results.json', 'run.py'}


def test_agentx_source_receipts_reject_wrong_input_and_restore_exact_source():
    entries = json.loads((ROOT/'tests/agentx_full_prose_hashes.json').read_text())['files']
    assert set(entries) == {P+n for n in NAMES}
    for p,row in entries.items():
        final = before_overview_figure_relocations(ROOT, p, (ROOT/p).read_bytes())
        prior = before_agentx_full_prose(ROOT,p,final)
        for alg, digest in {
            'sha256': lambda b: hashlib.sha256(b).hexdigest(),
            'blob': lambda b: hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest(),
        }.items():
            assert digest(prior)==row['before'][alg]
            assert agentx_full_prose_hash(ROOT,p,digest(prior),alg)==digest(final)
            with pytest.raises(AssertionError):
                agentx_full_prose_hash(ROOT,p,digest(final),alg)
        with pytest.raises(AssertionError):
            before_agentx_full_prose(ROOT,p,final+b'\n')


def test_agentx_preserves_exact_overview_and_reported_data():
    p=P+'lab.yaml'
    final=before_overview_figure_relocations(ROOT, p, (ROOT/p).read_bytes())
    a=yaml.safe_load(before_agentx_full_prose(ROOT,p,final))
    b=yaml.safe_load(final)
    for key in ('id','arxiv_id','authors','verification','urls','year','status','title'):
        assert a[key]==b[key]
    assert a['sections']['overview']==b['sections']['overview']
    p=P+'results.json'
    final=(ROOT/p).read_bytes()
    a,b=(json.loads(x) for x in (before_agentx_full_prose(ROOT,p,final),final))
    trace=lambda ds:[tuple(v[k] for k in ('verdict','effect','ci_low','guardrail','window_days')) for v in ds.values()]
    assert trace(a['decisions'])==trace(b['decisions'])
    assert [*a['replay'].values()]==[*b['replay'].values()]
    assert a['checks']==b['checks']


def test_agentx_distributed_run_emits_same_saved_values(tmp_path):
    original = ROOT/P
    script = tmp_path/'run.py'
    script.write_bytes((original/'run.py').read_bytes())
    result = subprocess.run([sys.executable,'-S',str(script)], capture_output=True, text=True, check=True)
    assert (tmp_path/'results.json').read_bytes()==(original/'results.json').read_bytes()
    d=json.loads(result.stdout)
    assert [x['verdict'] for x in d['decisions'].values()]==['KEEP','DISCARD','EXTEND','EXTEND','EXTEND']
    assert [x['accepted'] for x in d['replay'].values()]==[True,False,False]
