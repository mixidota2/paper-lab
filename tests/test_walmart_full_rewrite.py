"""Evidence, computation, accessible figures and previous exact-version guards."""
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
from xml.etree import ElementTree as ET

import pytest
import yaml

from prose_preservation import restored_before_paper_overview, walmart_full_rewrite_hash

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'papers/walmart-demand-transfer'
BASE = 'f7793bc88ab49a347b43e74a9ff45e77bb6fe5ad'
PROSE = ('lab.yaml', 'method.md', 'mapping.md', 'figures/restriction.svg',
         'figures/transfer.svg', 'results.json', 'run.py')


def old(path):
    return subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT)


def test_metadata_formula_annotations_and_figure_geometry():
    def links(raw):
        return Counter(re.findall(rb'https?://[^\s)\x27]+', raw))

    before, after = map(yaml.safe_load, (old(f'{SLUG}/lab.yaml'), (ROOT / SLUG / 'lab.yaml').read_bytes()))
    prose = {'question', 'summary', 'source_review', 'core_idea', 'sections', 'figures', 'teaching_figures'}
    assert {k: v for k, v in before.items() if k not in prose} == {k: v for k, v in after.items() if k not in prose}
    assert before['sections'].keys() == after['sections'].keys()
    assert {k: v for k, v in before['source_review'].items() if k != 'scope'} == {
        k: v for k, v in after['source_review'].items() if k != 'scope'}
    assert (before['sections']['method'], before['sections']['mapping']) == (
        after['sections']['method'], after['sections']['mapping'])
    for a, b in zip(before['figures'] + before['teaching_figures'], after['figures'] + after['teaching_figures'], strict=True):
        for key in set(a) - {'caption', 'title', 'rationale', 'rows'}:
            assert a[key] == b[key]
    for name in PROSE[:3]:
        path = f'{SLUG}/{name}'
        assert links(old(path)) == links((ROOT / path).read_bytes())
    m = (ROOT / SLUG / 'method.md').read_text()
    for formula in ('P(j|O)=exp(ηⱼ)/Σ_{k∈O}exp(η_k)', 'L(η)=ΣⱼKⱼηⱼ−Σₜmₜ log Σ_{i∈Sₜ}exp(ηᵢ)',
                    'ρ̂ᵢⱼ=exp(η̂ⱼ)/Σ_{k∈Sᵢ,k≠i}exp(η̂_k)', 'P(j)/P(k)=exp(ηⱼ−η_k)',
                    '(1−ℓᵢ)ρ̂ᵢⱼ', 'D̃ⱼ=D̂ⱼ+(1−ℓᵢ)ρ̂ᵢⱼD̂ᵢ'):
        assert f'`{formula}`' in m
    assert '60%の人が切り替えるという意味ではない' in m
    assert 'jとkそれぞれの選択確率は変わりうる' in m
    evidence = after['sections']['evidence']
    for row in ('| A | 0.28 | 0.21 | −0.07 |', '| B | 0.16 | 0.10 | −0.06 |', '| C | 0.02 | 0.03 | +0.01 |',
                '| D | 0.16 | 0.08 | −0.08 |', '| E | 0.18 | 0.07 | −0.11 |'):
        assert row in evidence
    assert '取引記録には客が実際に何から何へ切り替えたかが残らない' in evidence
    for n in PROSE[3:5]:
        p = ROOT / SLUG / n
        a, b = map(ET.fromstring, (old(f'{SLUG}/{n}'), p.read_bytes()))
        assert [(x.tag, x.attrib) for x in a.iter()] == [(x.tag, x.attrib) for x in b.iter()]


def test_only_named_annotations_change_not_the_toy():
    a, b = (json.loads(x) for x in (old(f'{SLUG}/results.json'), (ROOT / SLUG / 'results.json').read_bytes()))
    assert a['note'] != b['note'] and a['experiments'][0]['name'] != b['experiments'][0]['name']
    for r in (a, b):
        del r['note'], r['experiments'][0]['name']
    assert a == b
    a, b = map(ast.parse, (old(f'{SLUG}/run.py'), (ROOT / SLUG / 'run.py').read_bytes()))
    for tree in (a, b):
        redacted = 0
        for node in ast.walk(tree):
            if not isinstance(node, ast.Dict):
                continue
            for key, value in zip(node.keys, node.values, strict=True):
                if isinstance(key, ast.Constant) and key.value in ('note', 'name'):
                    assert isinstance(value, ast.Constant) and isinstance(value.value, str)
                    value.value = ''
                    redacted += 1
        assert redacted == 2
    assert ast.dump(a) == ast.dump(b)


@pytest.mark.parametrize('algorithm', ['sha256', 'blob'])
def test_accepts_only_recorded_identical_inputs(algorithm):
    manifest = json.loads((ROOT / 'tests/walmart_full_rewrite_hashes.json').read_bytes())
    assert manifest['base'] == BASE and set(manifest['files']) == {f'{SLUG}/{n}' for n in PROSE}
    def digest(x):
        if algorithm == 'sha256':
            return hashlib.sha256(x).hexdigest()
        return hashlib.sha1(f'blob {len(x)}\0'.encode()+x).hexdigest()
    for p in manifest['files']:
        a, b = old(p), restored_before_paper_overview(ROOT, p, (ROOT/p).read_bytes())
        assert walmart_full_rewrite_hash(ROOT, p, digest(a), algorithm) == digest(b)
        with pytest.raises(AssertionError):
            walmart_full_rewrite_hash(ROOT, p, digest(b+b'\n'), algorithm)
