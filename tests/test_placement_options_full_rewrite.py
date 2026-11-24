"""Preserve the shelf-placement study's inputs, model, scope, DOM and exact history."""
import ast
from collections import Counter
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess

import pytest
import yaml

from prose_preservation import placement_options_full_rewrite_hash

ROOT = Path(__file__).resolve().parents[1]
BASE = 'f7793bc88ab49a347b43e74a9ff45e77bb6fe5ad'
DIR = 'papers/shelf-placement-options'
NAMES = ('README.md','experiment.md','implementation.md','interactive.html','interactive.js',
         'lab.yaml','mapping.md','method.md','results.json','run.py','validation.md')


def inputs(name):
    old = subprocess.check_output(['git','show',f'{BASE}:{DIR}/{name}'],cwd=ROOT)
    return old,(ROOT/DIR/name).read_bytes()


def markup(raw):
    class Structure(HTMLParser):
        def __init__(self):
            super().__init__()
            self.nodes = []
            self.numbers = []

        def handle_starttag(self, name, attrs):
            self.nodes.append((name, [(k,v) for k,v in attrs if k not in {'aria-label','title'}]))

        def handle_endtag(self, name):
            self.nodes.append(('/'+name, []))

        def handle_data(self, segment):
            if re.fullmatch(r'[\d.×]+', segment.strip()):
                self.numbers.append(segment.strip())
    parser = Structure()
    parser.feed(raw.decode())
    return parser.nodes,parser.numbers


def test_models_dom_metadata_and_links_are_unchanged():
    a,b = map(ast.parse,inputs('run.py'))
    for node in (a,b):
        note = [v for v in ast.walk(node) if isinstance(v,ast.keyword) and v.arg=='note']
        assert len(note)==1
        note[0].value = ast.Constant(value=None)
    assert ast.dump(a) == ast.dump(b)
    a,b = map(json.loads,inputs('results.json'))
    assert a.pop('note') != b.pop('note')
    assert a == b
    a,b = inputs('model.js')
    assert a == b
    a,b = map(markup,inputs('interactive.html'))
    assert a == b
    a,b = map(yaml.safe_load,inputs('lab.yaml'))
    for data in (a,b):
        assert data['status'] == 'draft'
        assert data['verification']['performance'] == 'NOT TESTED'
    prose = {'question','summary','sections','core_idea','teaching_figures','source_review'}
    assert {k:v for k,v in a.items() if k not in prose} == {k:v for k,v in b.items() if k not in prose}
    assert a['sections'].keys() == b['sections'].keys()
    assert a['source_review']['checked'] == b['source_review']['checked']
    assert a['source_review']['url'] == b['source_review']['url']
    assert [(s['formula'],s['formula_mathml']) for s in a['teaching_figures'][0]['steps']] == [
        (s['formula'],s['formula_mathml']) for s in b['teaching_figures'][0]['steps']
    ]
    assert all(phrase in b['sections']['evidence'] for phrase in ('237商品','平均4.0%','平均0.6%','比較相手','測った結果ではない'))
    for n in NAMES:
        values = [Counter(re.findall(rb'https?://[^\s)\x27"<>]+',raw)) for raw in inputs(n)]
        assert values[0] == values[1], n


@pytest.mark.parametrize('algorithm',['sha256','blob'])
def test_exact_rewrite_identities(algorithm):
    rows = json.loads((ROOT/'tests/placement_options_full_rewrite_hashes.json').read_text())['files']
    assert set(rows) == {f'{DIR}/{n}' for n in NAMES}
    def digest(raw):
        if algorithm=='sha256':
            return hashlib.sha256(raw).hexdigest()
        return hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()
    for n in NAMES:
        path = f'{DIR}/{n}'
        a,b = inputs(n)
        assert placement_options_full_rewrite_hash(ROOT,path,digest(a),algorithm)==digest(b)
        with pytest.raises(AssertionError):
            placement_options_full_rewrite_hash(ROOT,path,digest(b+b'\n'),algorithm)
