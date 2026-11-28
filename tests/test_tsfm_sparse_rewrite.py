"""Keep the reviewed text confined to exact source and destination identities."""

import hashlib
import json
from pathlib import Path

import pytest

from prose_preservation import before_sparse_inspection_full_prose, before_sparse_reader_all_full_prose, restored_before_paper_overview, tsfm_sparse_rewrite_hash


ROOT = Path(__file__).resolve().parents[1]
BASE = 'f7793bc88ab49a347b43e74a9ff45e77bb6fe5ad'
SCOPE = 'papers/tsfm-sparse-event-ranking/'


def identity(content, algorithm):
    if algorithm == 'sha256':
        return hashlib.sha256(content).hexdigest()
    return hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()


@pytest.mark.parametrize('name', ('README.md', 'lab.yaml', 'mapping.md', 'method.md'))
@pytest.mark.parametrize('algorithm', ('sha256', 'blob'))
def test_sparse_rewrite_keeps_exact_reviewed_bytes(name, algorithm):
    proof = json.loads((ROOT / 'tests/tsfm_sparse_rewrite_hashes.json').read_text())
    assert proof['base'] == BASE
    assert set(proof['files']) == {SCOPE + f for f in ('README.md', 'lab.yaml', 'mapping.md', 'method.md')}
    path = SCOPE + name
    historic = 'yomiyasu_revision_hashes.json' if name in ('README.md', 'lab.yaml') else 'reading_prose_revision_hashes.json'
    previous = json.loads((ROOT / 'tests' / historic).read_text())['files'][path]['after_' + algorithm]
    assert proof['files'][path]['before_' + algorithm] == previous
    content = restored_before_paper_overview(ROOT, path, before_sparse_reader_all_full_prose(ROOT, path, before_sparse_inspection_full_prose(ROOT, path, (ROOT / path).read_bytes())))
    after = tsfm_sparse_rewrite_hash(ROOT, path, previous, algorithm)
    assert after == identity(content, algorithm)
    assert after != identity(content + b'\n', algorithm)
    wrong = ('0' if previous[0] != '0' else '1') + previous[1:]
    with pytest.raises(AssertionError):
        tsfm_sparse_rewrite_hash(ROOT, path, wrong, algorithm)
    with pytest.raises(AssertionError):
        tsfm_sparse_rewrite_hash(ROOT, path, after, algorithm)
    for other in ('README.md', SCOPE + 'run.py', SCOPE + 'results.json'):
        assert tsfm_sparse_rewrite_hash(ROOT, other, previous, algorithm) == previous
