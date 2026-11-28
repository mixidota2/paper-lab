"""Translate exactly reviewed pairs of overview sources and preserve older guards."""
import hashlib
import json

PREFIXES = (
    'papers/invevolve-whitebox-inventory-evolution/',
    'papers/pilot-experiment-lifecycle/',
    'papers/oxygenrec-v2-idgr/',
)


def row(root, path):
    if not path.startswith(PREFIXES) or path.rsplit('/', 1)[-1] not in ('lab.yaml', 'README.md'):
        return None
    return json.loads((root / 'tests/overview_predicate_revisions.json').read_text())[path]


def overview_predicate_hash(root, path, expected, algorithm='sha256'):
    exact = row(root, path)
    if exact is None:
        return expected
    assert expected == exact['before'][algorithm], path
    return exact['after'][algorithm]


def before_overview_predicate_revision(root, path, current):
    exact = row(root, path)
    if exact is None:
        return current
    assert hashlib.sha256(current).hexdigest() == exact['after']['sha256'], path
    edited = exact['new'].encode()
    assert current.count(edited) == 1, path
    previous = current.replace(edited, exact['old'].encode())
    assert hashlib.sha256(previous).hexdigest() == exact['before']['sha256'], path
    return previous
