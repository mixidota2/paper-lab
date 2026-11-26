import ast
import json
from pathlib import Path
import re
import subprocess

import yaml

from prose_preservation import before_intervention_full_prose

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'papers/intervention-paradox'
BASE = 'a4e6cd65739cf514a4da8d006ad79c53a72a25b4'


def test_intervention_keeps_overview_source_and_calculations():
    before, after = {}, {}
    for name in ('README.md', 'lab.yaml', 'mapping.md', 'method.md', 'run.py', 'results.json'):
        rel = f'{PREFIX}/{name}'
        old = subprocess.check_output(['git', 'show', f'{BASE}:{rel}'], cwd=ROOT)
        new = (ROOT / rel).read_bytes()
        assert old != new and before_intervention_full_prose(ROOT, rel, new) == old
        before[name], after[name] = old.decode(), new.decode()
    a, b = (yaml.safe_load(d['lab.yaml']) for d in (before, after))
    for key in a.keys() - {'question', 'summary', 'core_idea', 'sections', 'teaching_figures'}:
        assert a[key] == b[key]
    assert a['sections'].keys() == b['sections'].keys()
    assert a['sections']['overview'] == b['sections']['overview']
    assert before['README.md'].split('## 読み方')[0] == after['README.md'].split('## 同じ課題')[0]
    assert 'rとdがどちらも定義でき、合計が正' in after['method.md']
    assert 'τ=0.6とは別' in after['method.md']
    assert '6.7〜11.0ポイント増' in after['method.md']
    assert '論文の信頼区間ではない' in b['sections']['results']
    assert [x['id'] for x in a['teaching_figures']] == [x['id'] for x in b['teaching_figures']]
    assert [x['formula'] for x in a['teaching_figures'][0]['steps']] == [
        x['formula'] for x in b['teaching_figures'][0]['steps']
    ]
    payloads = lambda d: re.findall(r'<script.*?>.*?</script>', d['sections']['executable_understanding'])
    assert len(payloads(a)) == len(payloads(b)) == 1

    def without_note(s):
        d = json.loads(s)
        d.pop('note')
        for row in d['experiments']:
            row.pop('name')
        return d

    get_fixture = lambda d: payloads(d)[0].split('>',1)[1].rsplit('</script>',1)[0]
    assert without_note(get_fixture(a)) == without_note(get_fixture(b))
    assert without_note(before['results.json']) == without_note(after['results.json'])

    def computation(text):
        tree = ast.parse(text)
        if ast.get_docstring(tree):
            del tree.body[0]
        for node in ast.walk(tree):
            if isinstance(node, ast.Dict):
                for i, key in enumerate(node.keys):
                    if isinstance(key, ast.Constant) and key.value == 'note':
                        node.values[i] = ast.Constant(None)
                    if isinstance(key, ast.Constant) and key.value == 'name':
                        assert isinstance(node.values[i], ast.Constant)
                        node.values[i] = ast.Constant(None)
        return ast.dump(tree)

    assert computation(before['run.py']) == computation(after['run.py'])

def test_intervention_widget_changes_only_reader_text():
    rel = 'paper_lab/templates/interactives.js'
    old = subprocess.check_output(['git', 'show', f'{BASE}:{rel}'], cwd=ROOT).decode()
    from prose_preservation import before_gatesid_full_prose

    new = before_gatesid_full_prose(ROOT, rel, (ROOT / rel).read_bytes()).decode()
    start = "      const p = Number(root.querySelector('[data-failure]').value);"
    stop = "}\n  };\n  root.querySelectorAll('select,input')"
    def divide(text):
        prefix, rest = text.split(start)
        target, suffix = rest.split(stop, 1)
        return prefix, target.splitlines(), suffix
    p0, t0, s0 = divide(old)
    p1, t1, s1 = divide(new)
    assert (p0, s0) == (p1, s1)
    assert len(t0) == len(t1)
    assert [i for i, (a, b) in enumerate(zip(t0, t1)) if a != b] == [4, 5, 6]
    assert re.findall(r"\$\{(.*?)\}", t0[4]) == re.findall(r"\$\{(.*?)\}", t1[4])
    assert t0[5].split(" ? ")[0] == t1[5].split(" ? ")[0]
    assert t0[6].split("output.append")[0] == t1[6].split("output.append")[0]
