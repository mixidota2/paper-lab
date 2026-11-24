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
        if row.get('after_reference_guess_markup'):
            # Historical source guards still start at the exact pre-repair
            # bytes. New prose checks can start at the already repaired hash.
            if expected != row['before_' + algorithm]:
                expected = reference_guess_markup_hash(root, path, expected, algorithm)
            assert expected == row['before_' + algorithm], path
            return row['after_' + algorithm]
        assert expected == row['before_' + algorithm], path
        expected = row['after_' + algorithm]
    expected = replenishment_guide_rewrite_hash(root, path, expected, algorithm)
    expected = replenishment_cards_rewrite_hash(root, path, expected, algorithm)
    expected = replenishment_cards_followup_hash(root, path, expected, algorithm)
    expected = store_layout_full_rewrite_hash(root, path, expected, algorithm)
    result = hasterad_registration_hash(root, path, expected, algorithm)
    return coral_full_rewrite_hash(root, path, result, algorithm)


def replenishment_guide_rewrite_hash(root, path, expected, algorithm='sha256'):
    """Apply the complete guide rewrite only to the exact preceding guide."""
    row = json.loads((root / 'tests/replenishment_guide_rewrite_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def replenishment_cards_rewrite_hash(root, path, expected, algorithm='sha256'):
    """Apply the seven evidence-card rewrites only from the exact prior bytes."""
    row = json.loads((root / 'tests/replenishment_cards_rewrite_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def replenishment_cards_followup_hash(root, path, expected, algorithm='sha256'):
    """Explain five terms only from the frozen rewrite bytes."""
    row = json.loads((root / 'tests/replenishment_cards_followup_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


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


def coral_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    """Recognize four exact source and authored CORAL identities; reject any other input."""
    row = json.loads((root / 'tests/coral_full_rewrite_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return coral_role_clarification_hash(root, path, row['after_' + algorithm], algorithm)


def coral_role_clarification_hash(root, path, expected, algorithm='sha256'):
    """Recognize only the exact published-to-clarified CORAL source transition."""
    row = json.loads((root / 'tests/coral_role_clarification_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def store_layout_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    """Permit only the separately recorded full fixed-count layout guide rewrite."""
    row = json.loads((root / 'tests/store_layout_full_rewrite_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]
