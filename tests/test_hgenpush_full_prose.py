import ast
import json
from math import exp, isclose
from pathlib import Path
import subprocess
import sys

import yaml

from prose_preservation import before_hgenpush_full_prose


ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'papers/hgenpush-kuaishou-heterogeneous-push-gr/'


def pair(name):
    path = PREFIX + name
    raw = (ROOT / path).read_bytes()
    return before_hgenpush_full_prose(ROOT, path, raw), raw


def test_hgenpush_paper_overview_keeps_the_original_summary():
    before, after = map(yaml.safe_load, pair('lab.yaml'))
    assert before['sections']['overview'] == after['sections']['overview']
    assert '0.181%' in after['sections']['overview']
    assert '統計的に有意ではありませんでした' in after['sections']['overview']
    before, after = pair('README.md')
    assert before.split(b'\n\n')[1:3] == after.split(b'\n\n')[1:3]


def test_hgenpush_replay_keeps_both_paths_and_the_same_probabilities(tmp_path):
    def norm(raw):
        m = ast.parse(raw)
        assert isinstance(m.body.pop(0), ast.Expr)
        for node in ast.walk(m):
            if isinstance(node, ast.keyword) and node.arg == 'note':
                node.value.value = ''
        return ast.dump(m, include_attributes=False)

    old, new = pair('run.py')
    assert norm(old) == norm(new)
    (tmp_path / 'run.py').write_bytes(new)
    subprocess.run([sys.executable, '-S', 'run.py'], cwd=tmp_path, check=True)
    before, after = pair('results.json')
    assert (tmp_path / 'results.json').read_bytes() == after
    before, after = map(json.loads, (before, after))
    del before['note'], after['note']
    assert before == after
    assert after['paths'] == {'video': ['v1'], 'author': ['v1', 'v2'], 'merged': ['v1', 'v2']}
    assert after['ranked'] == ['v2', 'v1']
    for name, first, second in [('prefix_a', 1.2, .3), ('prefix_b', .2, 1.3)]:
        p = 1 / (1 + exp(second - first))
        assert all(isclose(x, y, rel_tol=1e-14) for x, y in zip(after['conditional'][name], (p, 1 - p)))
