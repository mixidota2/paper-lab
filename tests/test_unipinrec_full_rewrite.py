"""Preserve UniPinRec's scientific boundaries and all executable artifacts."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import re
import subprocess

import pytest
import yaml

from prose_preservation import restored_before_paper_overview, unipinrec_full_rewrite_hash

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'papers/unipinrec'
BASE = 'c7f80bbc75e73c99f3caf4dad7b9c12cc5059d17'
PROSE = ('README.md', 'method.md', 'lab.yaml')


def old(path):
    return subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT)


def test_metadata_matrix_equation_urls_and_behavior_unchanged():
    path = f'{SLUG}/lab.yaml'
    original, written = map(yaml.safe_load, (old(path), (ROOT / path).read_bytes()))
    reader_fields = {'summary','question','core_idea','sections','interactives','source_review','teaching_figures'}
    assert {k:v for k,v in original.items() if k not in reader_fields} == {
        k:v for k,v in written.items() if k not in reader_fields
    }
    assert original['sections'].keys() == written['sections'].keys()
    assert original['sections']['method'] == written['sections']['method']
    scope = {'checked','url'}
    assert {k: original['source_review'][k] for k in scope} == {k: written['source_review'][k] for k in scope}
    assert [i['kind'] for i in original['interactives']] == [i['kind'] for i in written['interactives']]
    a, b = original['teaching_figures'], written['teaching_figures']
    keys = ('kind','id','after','source','locator')
    assert [[m[k] for k in keys] for m in a] == [[m[k] for k in keys] for m in b]
    assert a[0]['rows'] == b[0]['rows'] and a[0]['columns'] == b[0]['columns']
    assert a[2]['steps'][0]['formula'] == b[2]['steps'][0]['formula']
    for name in PROSE:
        path = f'{SLUG}/{name}'
        links = lambda raw: Counter(re.findall(rb'https?://[^\s)\x27]+', raw))
        assert links(old(path)) == links((ROOT / path).read_bytes())
    for path in (f'{SLUG}/run.py', f'{SLUG}/results.json', 'papers/_toy_common.py'):
        assert old(path) == (ROOT / path).read_bytes()
    reported = written['sections']['evidence']
    assert all(x in reported for x in ('表3','11.1%','63.6%','キャッシュ共有だけの寄与ではない','§5'))
    toy = written['sections']['executable_understanding']
    assert all(x in toy for x in ('80リクエスト','候補数を固定','実際のattention演算数や応答時間を測る実験ではない'))


@pytest.mark.parametrize('algorithm', ['sha256','blob'])
def test_exact_three_inputs_and_outputs_only(algorithm):
    manifest = json.loads((ROOT / 'tests/unipinrec_full_rewrite_hashes.json').read_text())
    assert manifest['base'] == BASE
    assert set(manifest['files']) == {f'{SLUG}/{name}' for name in PROSE}
    def digest(raw):
        if algorithm == 'sha256':
            return hashlib.sha256(raw).hexdigest()
        return hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()
    for path in manifest['files']:
        after = restored_before_paper_overview(ROOT, path, (ROOT / path).read_bytes())
        assert unipinrec_full_rewrite_hash(ROOT,path,digest(old(path)),algorithm) == digest(after)
        with pytest.raises(AssertionError):
            unipinrec_full_rewrite_hash(ROOT,path,digest(after+b'\n'),algorithm)
