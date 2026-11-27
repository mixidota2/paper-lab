from __future__ import annotations

import ast
import json
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

import yaml

from prose_preservation import before_unirec_full_prose

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'unirec-chain-of-attribute'
PREFIX = f'papers/{SLUG}/'


def test_unirec_paper_summary_keeps_lab_analysis_in_method():
    path = PREFIX + 'lab.yaml'
    raw = (ROOT / path).read_bytes()
    old = yaml.safe_load(before_unirec_full_prose(ROOT, path, raw))
    new = yaml.safe_load(raw)
    overview = new['sections']['overview']
    before_overview, removed = old['sections']['overview'].split('論文は、生成モデル', 1)
    assert '商品ごとに違えば' in removed
    assert overview == before_overview
    assert new['sections']['overview'] in (ROOT / PREFIX / 'README.md').read_text()
    assert new['sections']['method'] == old['sections']['method']
    assert new['verification'] == old['verification']
    assert new['source_review'] == old['source_review']
    assert '分母' not in overview
    method = (ROOT / PREFIX / 'method.md').read_text()
    assert all(v in method for v in ('【Labの検討】', 'Aが9/13、Bが4/13', '一致するとは限らない'))
    assert '不確かさがどれだけ減る' in method


def test_unirec_retains_numeric_artifacts(tmp_path):
    paths = ('run.py', 'results.json')
    curr = {n: (ROOT / PREFIX / n).read_bytes() for n in paths}
    prior = {n: before_unirec_full_prose(ROOT, PREFIX + n, curr[n]) for n in paths}
    get_numeric = lambda raw: {k: v for k, v in json.loads(raw).items() if k != 'note'}
    assert get_numeric(curr['results.json']) == get_numeric(prior['results.json'])
    # Runtime code, not serialized fixture labels, defines the outcome.
    def strip_doc_and_note(raw):
        root = ast.parse(raw)
        root.body = root.body[1:]
        for node in ast.walk(root):
            if isinstance(node, ast.Dict):
                for k, v in zip(node.keys, node.values):
                    if isinstance(k, ast.Constant) and k.value == 'note':
                        assert isinstance(v, ast.Constant)
                        v.value = ''
        return ast.dump(root)
    assert strip_doc_and_note(curr['run.py']) == strip_doc_and_note(prior['run.py'])
    run = tmp_path / 'run.py'
    shutil.copyfile(ROOT / PREFIX / 'run.py', run)
    proc = subprocess.run([sys.executable, str(run)], capture_output=True, check=True)
    assert proc.stdout == curr['results.json'] == (tmp_path / 'results.json').read_bytes()


class Figures(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scopes = []
        self.meters = []

    def handle_starttag(self, tag, attr):
        a = dict(attr)
        if tag == 'figure':
            self.scopes.append(a.get('class', ''))
        if tag == 'meter':
            self.meters.append(float(a['value']))


def test_unirec_figure_values_preserved():
    def figures(lab, method):
        p = Figures()
        p.feed(lab['sections']['evidence'])
        figure, = re.findall(r'<figure .*?</figure>', method, flags=re.S)
        p.feed(figure)
        return p.scopes, p.meters, [s['formula'] for s in lab['teaching_figures'][0]['steps']]
    lab = (ROOT / PREFIX / 'lab.yaml').read_bytes()
    method = (ROOT / PREFIX / 'method.md').read_bytes()
    curr = figures(yaml.safe_load(lab), method.decode())
    orig = figures(
        yaml.safe_load(before_unirec_full_prose(ROOT, PREFIX + 'lab.yaml', lab)),
        before_unirec_full_prose(ROOT, PREFIX + 'method.md', method).decode(),
    )
    assert curr == orig
    assert curr[0] == ['teaching batch17'] * 3
    assert curr[1] == [33.24, 87.9, 89.62]
