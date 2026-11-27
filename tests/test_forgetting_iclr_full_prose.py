"""Verify content scope, identical numeric examples and the historical receipt."""
import json
from pathlib import Path

import pytest
import yaml

from prose_preservation import before_forgetting_iclr_full_prose


ROOT = Path(__file__).resolve().parents[1]
REL = 'papers/agent-reasoning-forgetting-externalized-state/'


def before(path):
    return before_forgetting_iclr_full_prose(ROOT, path, (ROOT / path).read_bytes())


def test_author_scope_and_paper_only_overview():
    p = ROOT / REL
    now = yaml.safe_load((p / 'lab.yaml').read_bytes())
    old = yaml.safe_load(before(REL + 'lab.yaml'))
    for key in ('id', 'arxiv_id', 'title', 'authors', 'urls', 'verification', 'status'):
        assert now[key] == old[key]
    overview = now['sections']['overview']
    assert len(overview.split('\n\n')) == 3
    assert all(x in overview for x in ('260 課題', '0.699', '0.718', '80課題', '0.7376', '0.7178', '67.31%', '36.15%'))
    assert all(x not in overview for x in ('Lab', '作例', '<table', '<figure', '6 回'))
    assert '削除の因果効果や、課題の失敗率ではない' in now['sections']['evidence']
    assert '削除は要求列の開始前だけに行う' in now['sections']['executable_understanding']
    assert overview in (p / 'README.md').read_text()


def test_every_rewritten_source_and_same_local_and_author_numbers():
    paths = {REL + f for f in ('README.md', 'lab.yaml', 'method.md', 'mapping.md', 'run.py', 'results.json')}
    paths.add('paper_lab/forgetting05.py')
    rows = json.loads((ROOT / 'tests/forgetting_iclr_full_prose_hashes.json').read_text())['files']
    assert set(rows) == paths
    for path in paths:
        current = (ROOT / path).read_bytes()
        assert current != before(path)
        with pytest.raises(AssertionError):
            before_forgetting_iclr_full_prose(ROOT, path, current + b'\n')
    a, b = (json.loads(src) for src in ((ROOT / REL / 'results.json').read_bytes(), before(REL + 'results.json')))
    for val in (a, b):
        del val['note'], val['experiments'][0]['name']
        for row in val['paper']['risk']:
            del row['group']
    assert a == b
    assert [c['rederivations'] for c in a['cases'].values()] == [0, 4, 0, 4]
