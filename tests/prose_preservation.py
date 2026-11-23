"""Translate only exact old identities of the listed prose revisions."""
import json


def revised_hash(root, path, expected, algorithm='sha256'):
    revisions = json.loads((root / 'tests/prose_revision_hashes.json').read_text())['files']
    if path in revisions:
        row = revisions[path]
        assert expected == row['before_' + algorithm], path
        expected = row['after_' + algorithm]
    return yomiyasu_hash(root, path, expected, algorithm)


def yomiyasu_hash(root, path, expected, algorithm='sha256'):
    """Apply the separately recorded November revision to an exact prior hash."""
    revisions = json.loads((root / 'tests/yomiyasu_revision_hashes.json').read_text())['files']
    if path not in revisions:
        return issue21_hash(root, path, expected, algorithm)
    row = revisions[path]
    assert expected == row['before_' + algorithm], path
    return issue21_hash(root, path, row['after_' + algorithm], algorithm)


def before_yomiyasu_replenishment(root, path, content):
    """Reverse only the reviewed T3 explanation, retaining all historical guards."""
    target = 'papers/assortment-replenishment-hard-constraints/interactive.js'
    if path != target:
        return content
    import hashlib
    row = json.loads((root / 'tests/yomiyasu_revision_hashes.json').read_text())['files'][path]
    assert hashlib.sha256(content.encode()).hexdigest() == row['after_sha256']
    old = '需要の定義が違う利益は順位比較できません。'
    new = '需要の定義が違う場合、利益の順位は比較できません。'
    assert content.count(new) == 1
    restored = content.replace(new, old)
    assert hashlib.sha256(restored.encode()).hexdigest() == row['before_sha256']
    return restored


def issue21_hash(root, path, expected, algorithm='sha256'):
    """Permit only the separately recorded Issue 21 update from exact prior bytes."""
    revisions = json.loads((root / 'tests/issue21_revision_hashes.json').read_text())['files']
    if path in revisions:
        row = revisions[path]
        assert expected == row['before_' + algorithm], path
        expected = row['after_' + algorithm]
    return reading_prose_hash(root, path, expected, algorithm)


def reading_prose_hash(root, path, expected, algorithm='sha256'):
    """Permit the reviewed PR 61 text only from the exact preceding identity."""
    rows = json.loads((root / 'tests/reading_prose_revision_hashes.json').read_text())['files']
    if path in rows:
        row = rows[path]
        assert expected == row['before_' + algorithm], path
        expected = row['after_' + algorithm]
    return hasterad_registration_hash(root, path, expected, algorithm)


def hasterad_registration_hash(root, path, expected, algorithm='sha256'):
    """Accept the three exact README count corrections, not arbitrary changes."""
    row = json.loads((root / 'tests/hasterad_registration_hashes.json').read_text())['files'].get(path)
    if row is not None:
        assert expected == row['before_' + algorithm], path
        expected = row['after_' + algorithm]
    return reference_guess_markup_hash(root, path, expected, algorithm)


def reference_guess_markup_hash(root, path, expected, algorithm='sha256'):
    """Accept only the exact option markup repair, independently of prose review."""
    row = json.loads((root / 'tests/reference_guess_markup_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]
