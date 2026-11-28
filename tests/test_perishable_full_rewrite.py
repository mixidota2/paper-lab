"""Accept only the reviewed prose bytes and retain the original toy evidence."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

import pytest
import yaml

from prose_preservation import before_perishable_full_rewrite, perishable_full_rewrite_hash, before_perishables_reader_assets

ROOT = Path(__file__).resolve().parents[1]
P = 'papers/discounted-perishables-forecast/'


def at_previous_prose(path):
    return before_perishables_reader_assets(ROOT, path, (ROOT/path).read_bytes())


def identity(b):
    return {'sha256': hashlib.sha256(b).hexdigest(),
            'blob': hashlib.sha1(f'blob {len(b)}\0'.encode() + b).hexdigest()}


def test_perishable_exact_prose_transitions():
    rows = json.loads((ROOT/'tests/perishable_full_rewrite_hashes.json').read_text())['files']
    assert rows.keys() == {P+n for n in ('README.md','evidence.md','experiment.md','interactive.html',
                                       'interactive.js','lab.yaml','mapping.md','method.md')}
    for path, row in rows.items():
        current = at_previous_prose(path)
        old = before_perishable_full_rewrite(ROOT, path, current)
        b, a = identity(old), identity(current)
        for alg in a:
            assert row['before_'+alg] == b[alg] and row['after_'+alg] == a[alg]
            assert perishable_full_rewrite_hash(ROOT, path, b[alg], alg) == a[alg]
            for invalid in (a[alg], '0'*len(a[alg])):
                with pytest.raises(AssertionError):
                    perishable_full_rewrite_hash(ROOT, path, invalid, alg)
        with pytest.raises(AssertionError):
            before_perishable_full_rewrite(ROOT, path, current+b'\n')


def test_perishable_overview_equations_and_demo_are_unchanged():
    current = at_previous_prose(P+'lab.yaml')
    prior = before_perishable_full_rewrite(ROOT, P+'lab.yaml', current)
    section = re.compile(rb'^  overview:.*?(?=^  problem:)', re.S | re.M)
    assert len(section.findall(current)) == 1
    assert section.findall(current) == section.findall(prior)
    before, after = map(yaml.safe_load, (prior, current))
    for name in ('question','summary','urls','authors','verification','title','topics'):
        assert before[name] == after[name]
    for n, o in zip(after['teaching_figures'], before['teaching_figures'], strict=True):
        assert n['id'] == o['id'] and n['kind'] == o['kind']
        assert [v['formula'] for v in n.get('steps',[])] == [v['formula'] for v in o.get('steps',[])]
    for file, blob in (('run.py','7ad7852defc37bf47f8809f81605553d2aa2b095'),
                       ('model.js','aaa609be8edfeaf99dc2faea45ca8df927fa694b'),
                       ('results.json','5d2da7636487a44a2fe09751e881d63fd0603a79')):
        assert identity(at_previous_prose(P+file))['blob'] == blob
    assert all(x in (ROOT/(P+'evidence.md')).read_text()
               for x in ('1,077','92.2%','0.41個','1,130','1,067','1,044','2602.04464v1'))


class Markup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.structure=[]
    def handle_starttag(self, tag, attrs):
        self.structure.append((tag, attrs))
    def handle_endtag(self, tag):
        self.structure.append((tag,))


def test_perishable_controls_links_and_logic_are_unchanged():
    page = P+'interactive.html'
    current = (ROOT/page).read_bytes()
    prior = before_perishable_full_rewrite(ROOT, page, current)
    b, a = Markup(), Markup()
    b.feed(prior.decode()); a.feed(current.decode())
    assert a.structure == b.structure
    script = P+'interactive.js'
    current = at_previous_prose(script)
    prior = before_perishable_full_rewrite(ROOT, script, current)
    strings = re.compile(rb"(?<=:)'[^'\n]+'")
    assert len(strings.findall(current)) == len(strings.findall(prior)) == 3
    assert strings.sub(b"''", current) == strings.sub(b"''", prior)
    links = re.compile(rb'\]\(([^)]*)\)|(?:src|href)="([^"]*)"')
    for name in ('README.md','evidence.md','experiment.md','mapping.md','method.md'):
        current=at_previous_prose(P+name)
        prior=before_perishable_full_rewrite(ROOT,P+name,current)
        assert links.findall(current) == links.findall(prior)
