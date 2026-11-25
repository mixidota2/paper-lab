import ast
import json
from pathlib import Path
import re
import subprocess

import pytest
import yaml

from prose_preservation import before_flashtrie_full_prose, flashtrie_full_prose_hash

ROOT = Path(__file__).resolve().parents[1]
P = ROOT/'papers/flashtrie-gpu-beam'
BASE = 'fbfed78f5fe9433d05a933777bb4b415bee59833'


def test_whole_flashtrie_rewrite_keeps_overview_facts_and_code():
    before, after = {}, {}
    for n in ('README.md', 'lab.yaml', 'mapping.md', 'method.md', 'run.py', 'results.json'):
        rel = f'papers/flashtrie-gpu-beam/{n}'
        old = subprocess.check_output(['git', 'show', f'{BASE}:{rel}'], cwd=ROOT)
        new = (P/n).read_bytes()
        assert new != old and before_flashtrie_full_prose(ROOT, rel, new) == old
        before[n], after[n] = old.decode(), new.decode()
    def overview(s):
        return re.search(r'^  overview:.*?(?=^  \w)', s, re.M|re.S)[0]
    assert overview(before['lab.yaml']) == overview(after['lab.yaml'])
    a,b = (yaml.safe_load(x['lab.yaml']) for x in (before,after))
    for k in a.keys()-{'question','summary','source_review','core_idea','sections','teaching_figures'}:
        assert a[k] == b[k]
    assert a['source_review'].keys() == b['source_review'].keys()
    assert all(b['source_review'][k] == v for k,v in a['source_review'].items() if k != 'scope')
    def grid(y):
        return json.loads(re.search(r'data-values>(.*?)</script>',y['sections']['evidence'],re.S)[1])
    assert grid(a)==grid(b)
    for key in ('beams','depth_only','exhaustive_best','checks'):
        assert json.loads(before['results.json'])[key] == json.loads(after['results.json'])[key]
    def logic(t):
        return [ast.dump(node) for node in ast.parse(t).body[1:] if not (isinstance(node,ast.FunctionDef) and node.name=='compute')]
    assert logic(before['run.py']) == logic(after['run.py'])
    assert 'Impression Yield' in b['sections']['evidence']


@pytest.mark.parametrize('algorithm', ['sha256', 'blob'])
def test_history_guard_rejects_unknown_prior_and_current_bytes(algorithm):
    rows = json.loads((ROOT/'tests/flashtrie_full_prose_hashes.json').read_text())['files']
    for rel,row in rows.items():
        assert flashtrie_full_prose_hash(ROOT,rel,row['before'][algorithm],algorithm) == row['after'][algorithm]
        with pytest.raises(AssertionError):
            flashtrie_full_prose_hash(ROOT,rel,row['after'][algorithm],algorithm)
        with pytest.raises(AssertionError):
            before_flashtrie_full_prose(ROOT,rel,(ROOT/rel).read_bytes()+b'\n')
