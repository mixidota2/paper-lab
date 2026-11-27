"""Preserve paper boundaries, executable behavior, and the existing overview."""
import ast
from hashlib import sha1, sha256
import json
from pathlib import Path
import re

import pytest
import yaml

from prose_preservation import before_ono_reader_all_full_prose, before_ono_full_rewrite, ono_full_rewrite_hash

ROOT = Path(__file__).resolve().parents[1]
P = 'papers/ono-inventory-forecast-selection/'
W = 'paper_lab/ono_inventory.py'
NAMES = ('README.md', 'method.md', 'mapping.md', 'lab.yaml')


def identities(data):
    return {
        'blob': sha1(f'blob {len(data)}\0'.encode()+data).hexdigest(),
        'sha256': sha256(data).hexdigest(),
    }


def test_exact_ono_custody_rejects_unreviewed_source():
    ledger = json.loads((ROOT/'tests/ono_full_rewrite_hashes.json').read_text())['files']
    assert set(ledger) == {P+key for key in NAMES} | {W}
    for path, row in ledger.items():
        final = before_ono_reader_all_full_prose(ROOT, path, (ROOT/path).read_bytes())
        old = before_ono_full_rewrite(ROOT, path, final)
        for alg in ('blob', 'sha256'):
            before, after = identities(old)[alg], identities(final)[alg]
            assert before == row['before_'+alg] and after == row['after_'+alg]
            assert ono_full_rewrite_hash(ROOT, path, before, alg) == after
            with pytest.raises(AssertionError):
                ono_full_rewrite_hash(ROOT, path, after, alg)
        with pytest.raises(AssertionError):
            before_ono_full_rewrite(ROOT, path, final+b'\n')
        assert re.findall(rb'\]\(([^)]+)\)', final) == re.findall(rb'\]\(([^)]+)\)', old)
        assert re.findall(rb'```.*?\n(.*?)```', final, re.S) == re.findall(rb'```.*?\n(.*?)```', old, re.S)


def test_ono_keeps_metadata_geometry_and_toy_numbers():
    final = before_ono_reader_all_full_prose(ROOT, P+'lab.yaml', (ROOT/(P+'lab.yaml')).read_bytes())
    before = before_ono_full_rewrite(ROOT, P+'lab.yaml', final)
    old, new = map(yaml.safe_load, (before, final))
    assert old.keys() == new.keys()
    assert all(old[k] == new[k] for k in old if k not in ('core_idea','sections','teaching_figures'))
    assert old['sections'].keys() == new['sections'].keys()
    assert all(old['sections'][k] == new['sections'][k] for k in ('overview','method','mapping'))
    for a, b in zip(old['teaching_figures'], new['teaching_figures'], strict=True):
        assert a.keys() == b.keys()
        assert all(a[k] == b[k] for k in ('id','kind','after','source'))
        if 'steps' in a:
            assert [x['formula'] for x in a['steps']] == [x['formula'] for x in b['steps']]
    for name, expected in [
        ('results.json', 'e9dc8df6dd149a9bab2828782881cf8ccee9462070c60fb1b478342d051f5d08'),
        ('run.py', '3b58dbb7871aff538e80cf24a12d3acda0d9d260deb201eed1d038c3712c86e2'),
    ]:
        assert identities(before_ono_reader_all_full_prose(ROOT, P+name, (ROOT/(P+name)).read_bytes()))['sha256'] == expected
    widget = (ROOT/W).read_bytes()
    old_widget = before_ono_full_rewrite(ROOT, W, widget)
    class NoProse(ast.NodeTransformer):
        def visit_Constant(self, node):
            if isinstance(node.value, str):
                node.value = ''
            return node
    assert ast.dump(NoProse().visit(ast.parse(widget))) == ast.dump(NoProse().visit(ast.parse(old_widget)))
    evidence = new['sections']['evidence']
    assert all(term in evidence for term in ('一次資料','85,056','85,093','実店舗が支払った金額ではありません'))
    assert '欠品した発注サイクルの割合ではありません' in new['sections']['results']
