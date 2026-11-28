"""Changing the explanation keeps its destinations, units, and reviewed history."""
from collections import Counter
from pathlib import Path
from prose_preservation import historical_lab_public_guide
import hashlib
import json
import re
import subprocess

import pytest
from prose_preservation import shelf_full_rewrite_hash
from shelf_guide_preservation import before_full_rewrite, before_streicher, GUIDE

ROOT = Path(__file__).resolve().parents[1]
BASE = 'df58ceae17143d38d03499090c8bbd449a0c738d'


def test_all_source_links_anchors_and_numeric_occurrences_survive():
    current = historical_lab_public_guide(ROOT,GUIDE)
    previous = subprocess.check_output(['git', 'show', f'{BASE}:{GUIDE}'], cwd=ROOT)
    assert before_full_rewrite(current) == previous
    a, b = previous.decode(), before_streicher(current).decode()
    for regex in (r'href="([^"]+)"|\]\(([^)]+)\)', r'\bid="([^"]+)"',
                  r'[+−]?\d+(?:[.,]\d+)*(?:%)?'):
        assert Counter(re.findall(regex, a)) == Counter(re.findall(regex, b)), regex
    assert a.count('<figure ') == b.count('<figure ') == 2
    assert a.count('| --- |') == b.count('| --- |')
    old_paragraphs = {p for p in a.split('\n\n') if p and not p.startswith('<span')}
    assert not old_paragraphs.intersection(b.split('\n\n'))


@pytest.mark.parametrize('algo', ['sha256', 'blob'])
def test_manifest_requires_exact_prior_and_current_identities(algo):
    record = json.loads((ROOT / 'tests/shelf_full_rewrite_hashes.json').read_text())
    assert record['files'].keys() == {GUIDE}
    old = subprocess.check_output(['git', 'show', f'{BASE}:{GUIDE}'], cwd=ROOT)
    new = historical_lab_public_guide(ROOT,GUIDE)
    def digest(raw):
        if algo == 'sha256':
            return hashlib.sha256(raw).hexdigest()
        return hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()
    assert shelf_full_rewrite_hash(ROOT, GUIDE, digest(old), algo) == digest(new)
    assert digest(new + b'\n') != digest(new)
    with pytest.raises(AssertionError):
        shelf_full_rewrite_hash(ROOT, GUIDE, digest(new), algo)
