"""The CORAL rewriting preserves the old identities and its source data."""
import hashlib
import json
from pathlib import Path

from paper_lab.models import load_all_labs
from prose_preservation import coral_full_rewrite_hash
import pytest

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'coral-meta-config-harness'


def test_coral_revision_rejects_unknown_or_already_updated_source():
    proof = json.loads((ROOT/'tests/coral_full_rewrite_hashes.json').read_text())
    assert proof['base'] == '5c97429443b48dd3d3e6568e4dd7087525bc8b63'
    assert {Path(p).name for p in proof['files']} == {'README.md','lab.yaml','mapping.md','method.md'}
    for path, row in proof['files'].items():
        content = (ROOT/path).read_bytes()
        actual = {'sha256': hashlib.sha256(content).hexdigest(),
                  'blob': hashlib.sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest()}
        for algo, digest in actual.items():
            before = row['before_'+algo]
            assert coral_full_rewrite_hash(ROOT, path, before, algo) == digest
            for unknown in ('0'*len(before), digest):
                with pytest.raises(AssertionError):
                    coral_full_rewrite_hash(ROOT, path, unknown, algo)
    assert coral_full_rewrite_hash(ROOT, f'papers/{SLUG}/run.py', 'other') == 'other'


def test_coral_keeps_paper_evidence_separate_from_lab_numbers():
    lab = next(p for p in load_all_labs(ROOT/'papers') if p.id == SLUG)
    evidence = lab.sections['evidence']
    experiment = lab.sections['executable_understanding']
    for number in ('0.13%', '0.15%', '0.16%', '0.77%', '0.23%', '44%', '14.4', '85.6'):
        assert number in evidence
    assert '費用が44%減った' in evidence and 'とは読めない' in evidence
    assert '有意差なしは効果が0%' in evidence
    assert '[4.667, 3.667, 1.667]' in experiment
    assert 'NOT TESTED' in lab.sections['what_we_did_not_verify']
