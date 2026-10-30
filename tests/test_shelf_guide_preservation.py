"""Negative controls for the exact, reversible shelf-guide revision exception."""
import json
from pathlib import Path
import subprocess
import pytest
from shelf_guide_preservation import GUIDE, BEFORE, AFTER, SYNTHESIS, PATCH_SHA, DCMP_PATCH_SHA, LAYOUT, LAYOUT_PATCH_SHA, reverse_exact, sha, verify_preserved_source

ROOT = Path(__file__).resolve().parents[1]
PATCH = (ROOT / 'tests/fixtures/shelf-guide-20261029.patch').read_bytes()
DCMP_PATCH = (ROOT / 'tests/fixtures/shelf-guide-dcmp-integration-20261030.patch').read_bytes()

LAYOUT_PATCH = (ROOT / 'tests/fixtures/shelf-guide-layout-integration-20261030.patch').read_bytes()

def prepare(tmp_path, data=None):
    target = tmp_path / GUIDE
    target.parent.mkdir(parents=True)
    target.write_bytes((ROOT / GUIDE).read_bytes() if data is None else data)
    return target


def test_reviewed_revision_and_previous_version_both_pass(tmp_path):
    target = prepare(tmp_path)
    assert sha(target.read_bytes()) == LAYOUT
    verify_preserved_source(tmp_path, GUIDE, BEFORE, patch_bytes=PATCH, dcmp_patch_bytes=DCMP_PATCH, layout_patch_bytes=LAYOUT_PATCH)
    target.write_bytes(reverse_exact(target.read_bytes(), LAYOUT_PATCH, LAYOUT_PATCH_SHA, AFTER))
    assert sha(target.read_bytes()) == AFTER
    verify_preserved_source(tmp_path, GUIDE, BEFORE, patch_bytes=PATCH, dcmp_patch_bytes=DCMP_PATCH, layout_patch_bytes=LAYOUT_PATCH)
    target.write_bytes(reverse_exact(target.read_bytes(), DCMP_PATCH, DCMP_PATCH_SHA, SYNTHESIS))
    verify_preserved_source(tmp_path, GUIDE, BEFORE, patch_bytes=PATCH)
    subprocess.run(['git', 'apply', '--reverse', '-'], input=PATCH, cwd=tmp_path, check=True)
    assert sha(target.read_bytes()) == BEFORE
    verify_preserved_source(tmp_path, GUIDE, BEFORE, patch_bytes=PATCH, dcmp_patch_bytes=DCMP_PATCH, layout_patch_bytes=LAYOUT_PATCH)


@pytest.mark.parametrize('old,new', [
    ('Kök・Fisher（2007）', 'Kök・Fisher（2008）'),  # pre-existing prose
    ('4.40%', '4.41%'),  # Cornell evidence must not change
    ('約25%の粗利増', '約26%の粗利増'),  # newly reviewed addition
])
def test_single_character_edits_are_rejected(tmp_path, old, new):
    data = (ROOT / GUIDE).read_text()
    assert old in data
    prepare(tmp_path, data.replace(old, new, 1).encode())
    with pytest.raises(AssertionError):
        verify_preserved_source(tmp_path, GUIDE, BEFORE, patch_bytes=PATCH, dcmp_patch_bytes=DCMP_PATCH, layout_patch_bytes=LAYOUT_PATCH)


def test_previous_paragraph_deletion_is_rejected(tmp_path):
    data = (ROOT / GUIDE).read_text()
    paragraph = next(p for p in data.split('\n\n') if p.startswith('Kök・Fisher（2007）'))
    prepare(tmp_path, data.replace(paragraph, '', 1).encode())
    with pytest.raises(AssertionError):
        verify_preserved_source(tmp_path, GUIDE, BEFORE, patch_bytes=PATCH, dcmp_patch_bytes=DCMP_PATCH, layout_patch_bytes=LAYOUT_PATCH)


def test_other_source_change_is_rejected(tmp_path):
    manifest = json.loads((ROOT / 'tests/main_107_catalog.json').read_text())
    path, expected = next((p,h) for p,h in manifest['source_hashes'].items() if p != GUIDE)
    target = tmp_path / path
    target.parent.mkdir(parents=True, exist_ok=True)
    original = (ROOT / path).read_bytes()
    target.write_bytes(original)
    verify_preserved_source(tmp_path, path, expected, patch_bytes=PATCH, dcmp_patch_bytes=DCMP_PATCH, layout_patch_bytes=LAYOUT_PATCH)
    target.write_bytes(original + b'\nchanged')
    with pytest.raises(AssertionError):
        verify_preserved_source(tmp_path, path, expected, patch_bytes=PATCH, dcmp_patch_bytes=DCMP_PATCH, layout_patch_bytes=LAYOUT_PATCH)


@pytest.mark.parametrize('patch', [PATCH + b'\n', PATCH.replace(b'guides/shelf-decisions.md', b'../outside.md')])
def test_patch_mutation_or_path_redirection_is_rejected(tmp_path, patch):
    prepare(tmp_path)
    assert sha(PATCH) == PATCH_SHA
    with pytest.raises(AssertionError):
        verify_preserved_source(tmp_path, GUIDE, BEFORE, patch_bytes=patch, dcmp_patch_bytes=DCMP_PATCH, layout_patch_bytes=LAYOUT_PATCH)


@pytest.mark.parametrize('patch', [DCMP_PATCH + b'\n', DCMP_PATCH.replace(b'guides/shelf-decisions.md', b'../outside.md')])
def test_dcmp_patch_mutation_or_path_redirection_is_rejected(tmp_path, patch):
    prepare(tmp_path)
    with pytest.raises(AssertionError):
        verify_preserved_source(tmp_path, GUIDE, BEFORE, patch_bytes=PATCH, dcmp_patch_bytes=patch, layout_patch_bytes=LAYOUT_PATCH)


@pytest.mark.parametrize('anchor', ['<span id="dcmp-evaluation"></span>', '<span id="preestimate-to-realization"></span>'])
def test_either_reviewed_addition_cannot_be_silently_deleted(tmp_path, anchor):
    data=(ROOT / GUIDE).read_text()
    assert anchor in data
    prepare(tmp_path, data.replace(anchor, '', 1).encode())
    with pytest.raises(AssertionError):
        verify_preserved_source(tmp_path, GUIDE, BEFORE, patch_bytes=PATCH, dcmp_patch_bytes=DCMP_PATCH, layout_patch_bytes=LAYOUT_PATCH)
