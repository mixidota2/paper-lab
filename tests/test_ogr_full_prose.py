import ast
import json
from pathlib import Path
import re
import subprocess

import yaml

from prose_preservation import before_ogr_full_prose

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'papers/ogr-once-generated-ranked'
BASE = '8298ca2308eb382e1fb03a607a274f6fa24d41de'


def test_ogr_canonical_overview_source_and_computation():
    before, after = {}, {}
    for name in ('README.md', 'lab.yaml', 'mapping.md', 'method.md', 'run.py', 'results.json'):
        rel = f'{PREFIX}/{name}'
        old = subprocess.check_output(['git', 'show', f'{BASE}:{rel}'], cwd=ROOT)
        new = (ROOT / rel).read_bytes()
        assert old != new and before_ogr_full_prose(ROOT, rel, new) == old
        before[name], after[name] = old.decode(), new.decode()
    a, b = (yaml.safe_load(d['lab.yaml']) for d in (before, after))
    for key in a.keys() - {'question', 'summary', 'core_idea', 'sections', 'teaching_figures'}:
        assert a[key] == b[key]
    assert a['sections'].keys() == b['sections'].keys()
    assert a['sections']['overview'] == b['sections']['overview']
    assert b['sections']['overview'] == after['README.md'].split('\n\n', 1)[1].split('\n\n##', 1)[0]
    assert '標準偏差と10⁻⁶のうち大きい方' in after['method.md']
    assert '表示済みリストだけ' in after['method.md']
    assert all(x in b['sections']['evidence'] for x in ('2.43倍', '2.49倍', '20段と9段', '信頼区間'))
    assert [x['id'] for x in a['teaching_figures']] == [x['id'] for x in b['teaching_figures']]
    assert [x['formula'] for x in a['teaching_figures'][0]['steps']] == [
        x['formula'] for x in b['teaching_figures'][0]['steps']
    ]
    assert a['teaching_figures'][1]['bars'] == b['teaching_figures'][1]['bars']
    frames = lambda d: re.findall(r'<script type="application/json" data-frames>(.*?)</script>', d['sections']['executable_understanding'])
    assert len(frames(b)) == 2 and frames(a) == frames(b)

    def without_note(s):
        d = json.loads(s)
        d.pop('note')
        return d

    assert without_note(before['results.json']) == without_note(after['results.json'])

    def computation(text):
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.FunctionDef)) and ast.get_docstring(node):
                del node.body[0]
            if isinstance(node, ast.Dict):
                for i, key in enumerate(node.keys):
                    if isinstance(key, ast.Constant) and key.value == 'note':
                        node.values[i] = ast.Constant(None)
        return ast.dump(tree)

    assert computation(before['run.py']) == computation(after['run.py'])
