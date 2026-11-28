"""Pin the whole-document rewrite without changing prior reviewed identities."""

import hashlib
import json
from pathlib import Path
from prose_preservation import historical_lab_public_guide

import pytest

from prose_preservation import root_readme_rewrite_hash


ROOT = Path(__file__).resolve().parents[1]
PATH = 'README.md'
PREVIOUS = {
    'sha256': '1e0d442833bc0538b695991a4523c2fe1b8fad9ca097bbe8e4e884e761397627',
    'blob': 'c0869926f8c2c73ff95e903d29e0c9a48e405b8f',
}


def identity(content, algorithm):
    if algorithm == 'sha256':
        return hashlib.sha256(content).hexdigest()
    return hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()


@pytest.mark.parametrize('algorithm', ('sha256', 'blob'))
def test_root_readme_identity_rejects_one_digit_or_unrelated_path(algorithm):
    proof = json.loads((ROOT / 'tests/root_readme_rewrite_hashes.json').read_text())
    assert proof['base'] == 'f7793bc88ab49a347b43e74a9ff45e77bb6fe5ad'
    assert set(proof['files']) == {PATH}
    before = PREVIOUS[algorithm]
    assert proof['files'][PATH]['before_' + algorithm] == before
    content = historical_lab_public_guide(ROOT,PATH)
    after = root_readme_rewrite_hash(ROOT, PATH, before, algorithm)
    assert after == identity(content, algorithm)
    assert after != identity(content + b'\n', algorithm)
    wrong = ('0' if before[0] != '0' else '1') + before[1:]
    with pytest.raises(AssertionError):
        root_readme_rewrite_hash(ROOT, PATH, wrong, algorithm)
    with pytest.raises(AssertionError):
        root_readme_rewrite_hash(ROOT, PATH, after, algorithm)
    assert root_readme_rewrite_hash(ROOT, 'research-data/README.md', before, algorithm) == before
