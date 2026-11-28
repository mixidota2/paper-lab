"""Preserve the real-case evidence and render the method as Lab guidance."""
from hashlib import sha1, sha256
from pathlib import Path
import re

import pytest

from paper_lab.build import build
from shelf_prelaunch_revision import PATH, before_shelf_prelaunch_revision, receipt, shelf_prelaunch_hash

ROOT=Path(__file__).resolve().parents[1]


def test_exact_insertion_has_unchanged_evidence_and_known_identity():
    row=receipt(ROOT)
    actual=(ROOT/PATH).read_bytes()
    prior=before_shelf_prelaunch_revision(ROOT,PATH,actual)
    def identity(data):
        return {'sha256':sha256(data).hexdigest(),'blob':sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()}
    assert identity(actual)==row['after'] and identity(prior)==row['before']
    assert all(shelf_prelaunch_hash(ROOT,PATH,row['before'][alg],alg)==row['after'][alg] for alg in ('sha256','blob'))
    assert [l for l in actual.splitlines() if l.startswith(b'|')]==[l for l in prior.splitlines() if l.startswith(b'|')]
    with pytest.raises(AssertionError):
        before_shelf_prelaunch_revision(ROOT,PATH,actual+b'\n')
    with pytest.raises(AssertionError):
        before_shelf_prelaunch_revision(ROOT,PATH,prior)
    with pytest.raises(AssertionError):
        shelf_prelaunch_hash(ROOT,PATH,row['after']['sha256'],'sha256')


def test_rendered_method_separates_design_from_actual_evidence(tmp_path):
    build(root=ROOT,site_dir=tmp_path)
    html=(tmp_path/'guides/shelf-decisions.html').read_text()
    a=re.search(r'<span id="shelf-prelaunch-comparison-check"></span>(.*?)<span id="asda-pizza-facing-evaluation"></span>',html,re.S)
    assert a
    block=a[1]
    for text in ('その日より前のデータだけ','差を計算する前に','本番と同じ長さ','これだけで本番の効果','Labが提案','小売の調査ではありません'):
        assert text in block
    assert 'https://web.stanford.edu/~jhain/Paper/AJPS2015a.pdf' in block
