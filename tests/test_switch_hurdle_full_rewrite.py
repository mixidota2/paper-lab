"""The reader-facing rewrite retains the recorded experiment and paper evidence."""
from pathlib import Path
import hashlib
import json
import re

import pytest
import yaml

from prose_preservation import before_switch_hurdle_full_rewrite, switch_hurdle_full_rewrite_hash

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'papers/switch-hurdle-intermittent-demand/'


def identity(b):
    return {'sha256':hashlib.sha256(b).hexdigest(),
            'blob':hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()}


def test_switch_hurdle_exact_prose_transition():
    rows = json.loads((ROOT/'tests/switch_hurdle_full_rewrite_hashes.json').read_text())['files']
    assert set(rows) == {PREFIX+n for n in ('README.md','mapping.md','method.md','lab.yaml')}
    for path, row in rows.items():
        new = (ROOT/path).read_bytes()
        old = before_switch_hurdle_full_rewrite(ROOT, path, new)
        for algorithm, prior_hash in identity(old).items():
            new_hash = identity(new)[algorithm]
            assert prior_hash == row['before_'+algorithm] and new_hash == row['after_'+algorithm]
            assert switch_hurdle_full_rewrite_hash(ROOT,path,prior_hash,algorithm) == new_hash
            for invalid in (new_hash, '0'*len(new_hash)):
                with pytest.raises(AssertionError):
                    switch_hurdle_full_rewrite_hash(ROOT,path,invalid,algorithm)
        with pytest.raises(AssertionError):
            before_switch_hurdle_full_rewrite(ROOT,path,new+b'\n')


def test_switch_hurdle_keeps_overview_links_and_experiment():
    path = PREFIX+'lab.yaml'
    recent = (ROOT/path).read_bytes()
    prior = before_switch_hurdle_full_rewrite(ROOT,path,recent)
    overview = re.compile(rb'^  overview:.*?(?=^  problem:)',re.S|re.M)
    assert len(overview.findall(prior)) == 1
    assert overview.findall(recent) == overview.findall(prior)
    before, after = map(yaml.safe_load,(prior,recent))
    for k in ('authors','urls','source_review','verification','status','title'):
        assert before[k] == after[k]
    for a,b in zip(before['teaching_figures'],after['teaching_figures'],strict=True):
        for k in ('id','kind','locator','after','source','bars','maximum'):
            assert a.get(k) == b.get(k)
        assert [x['formula'] for x in a.get('steps',[])] == [x['formula'] for x in b.get('steps',[])]
        assert [x.get('cells') for x in a.get('rows',[])] == [x.get('cells') for x in b.get('rows',[])]
    for n in ('0.6307','0.6403','0.6932','0.7895','2.4744','2.4562','0.8992','0.8983',
              '53.99%','55.60%','0.5865','0.5803','67.5%','90.8%','94.0%'):
        assert n in after['sections']['evidence']
    links = re.compile(rb'\]\(([^)]*)\)')
    for n in ('README.md','mapping.md','method.md','lab.yaml'):
        p = PREFIX+n
        newer = (ROOT/p).read_bytes()
        prior = before_switch_hurdle_full_rewrite(ROOT,p,newer)
        assert sorted(links.findall(newer)) == sorted(links.findall(prior))
    for n,expected in (('run.py','aa77166336d9ca084e113ad3d975102f7f83a65b'),
                       ('results.json','1801386f29907d4ca02973ba8dd9131319ee02b9')):
        assert identity((ROOT/(PREFIX+n)).read_bytes())['blob'] == expected
