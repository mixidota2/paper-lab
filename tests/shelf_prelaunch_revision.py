"""Reverse one reviewed paragraph without losing earlier strict guide checks."""
import hashlib
import json

PATH = 'guides/shelf-decisions.md'


def receipt(root):
    return json.loads((root/'tests/shelf_prelaunch_revision.json').read_text())


def shelf_prelaunch_hash(root,path,expected,algorithm):
    if path != PATH:
        return expected
    row = receipt(root)
    assert expected == row['before'][algorithm],path
    return row['after'][algorithm]


def before_shelf_prelaunch_revision(root,path,current):
    if path != PATH:
        return current
    row = receipt(root)
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'],path
    inserted = row['insert'].encode()
    assert current.count(inserted) == 1,path
    prior = current.replace(inserted,b'')
    assert hashlib.sha256(prior).hexdigest() == row['before']['sha256'],path
    return prior
