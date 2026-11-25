"""Keep source links and the worked example intact across the complete guide rewrite."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess

import pytest
from prose_preservation import before_weather_cutoff, replenishment_guide_rewrite_hash

ROOT = Path(__file__).resolve().parents[1]
GUIDE = 'guides/forecast-to-replenishment.md'
BASE = '5c97429443b48dd3d3e6568e4dd7087525bc8b63'


def original():
    return subprocess.check_output(['git', 'show', f'{BASE}:{GUIDE}'], cwd=ROOT)


def test_rewrite_keeps_exact_material_and_a_single_insertion_point():
    before, after = original().decode(), before_weather_cutoff(ROOT, GUIDE, (ROOT / GUIDE).read_bytes()).decode()
    links = re.compile(r'\]\(([^)]+)\)')
    code = re.compile(r'```python\n(.*?)```', re.S)
    assert Counter(links.findall(after)) == Counter(links.findall(before))
    assert code.findall(after) == code.findall(before)
    assert after.count('<!-- EVIDENCE_CARDS -->') == 1


def test_rewrite_identities_advance_once_and_reject_unknown_bytes():
    manifest = json.loads((ROOT / 'tests/replenishment_guide_rewrite_hashes.json').read_text())
    assert manifest['base'] == BASE and set(manifest['files']) == {GUIDE}
    before, after = original(), before_weather_cutoff(ROOT, GUIDE, (ROOT / GUIDE).read_bytes())

    def digest(raw, algo):
        return (hashlib.sha256(raw).hexdigest() if algo == 'sha256'
                else hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest())

    for algo in ('sha256', 'blob'):
        assert replenishment_guide_rewrite_hash(ROOT, GUIDE, digest(before, algo), algo) == digest(after, algo)
        with pytest.raises(AssertionError):
            replenishment_guide_rewrite_hash(ROOT, GUIDE, digest(after + b'\n', algo), algo)
