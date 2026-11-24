"""Keep the exact approved prose revision and the study denominators."""
import hashlib
import itertools
import json
from pathlib import Path

import pytest
import yaml

from prose_preservation import accuracy_full_rewrite_hash, restored_before_paper_overview

ROOT = Path(__file__).resolve().parents[1]
NAME = 'accuracy-not-service-intermittent-demand'
FILES = json.loads((ROOT / 'tests/accuracy_full_rewrite_hashes.json').read_text())['files']


@pytest.mark.parametrize('path, algorithm', tuple(itertools.product(FILES, ('blob', 'sha256'))))
def test_accuracy_source_guards_match_exact_reviewed_bytes(path, algorithm):
    row = FILES[path]
    expected = accuracy_full_rewrite_hash(ROOT, path, row['before_' + algorithm], algorithm)
    b = restored_before_paper_overview(ROOT, path, (ROOT / path).read_bytes())
    actual = (hashlib.sha1(f'blob {len(b)}\0'.encode() + b).hexdigest()
              if algorithm == 'blob' else hashlib.sha256(b).hexdigest())
    assert expected == actual == row['after_' + algorithm]
    for rejected in (row['after_' + algorithm], '0' * len(actual)):
        with pytest.raises(AssertionError):
            accuracy_full_rewrite_hash(ROOT, path, rejected, algorithm)
    assert accuracy_full_rewrite_hash(ROOT, 'outside/' + path, expected, algorithm) == expected


def test_accuracy_distinguishes_benchmark_counts_and_actual_service():
    data = yaml.safe_load((ROOT / 'papers' / NAME / 'lab.yaml').read_text())
    p = data['sections']['problem']
    e = data['sections']['evidence']
    assert all(s in p for s in ('4,021品目','3,828品目','20,330件','4,558品目'))
    assert '補充規則の目標90%' in e and '| 77.5% | 92.0% |' in e
    assert '| 54% | 63% |' in e and '80%以上で完納率80%以上' in e
    assert '−0.555264' in data['sections']['results'] and 'NOT OBSERVED' in data['sections']['results']
