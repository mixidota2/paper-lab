import ast
import json
from pathlib import Path

import pytest
import yaml

from paper_lab.build import _metrics_table
from prose_preservation import before_uvr_full_prose


ROOT = Path(__file__).resolve().parents[1]
SLUG = 'uvr-wolt-trial-reorder'
PREFIX = f'papers/{SLUG}/'
LABELS = 'paper_lab/display_labels.py'


def unchanged_papers(raw):
    assign = next(node for node in ast.parse(raw).body
                  if isinstance(node, ast.Assign) and node.targets[0].id == 'LABELS')
    mapping = ast.literal_eval(assign.value)
    del mapping[SLUG]
    return mapping


def test_uvr_rendered_labels_keep_metrics_and_other_articles_unchanged():
    path = PREFIX + 'results.json'
    after = (ROOT / path).read_bytes()
    old = json.loads(before_uvr_full_prose(ROOT, path, after))
    cur = json.loads(after)
    for value in (old, cur):
        del value['note']
        del value['experiments'][0]['name']
    assert old == cur
    table = _metrics_table(cur['experiments'][0]['metrics'], SLUG)
    assert '<th>店への初回注文のMRR</th><th>同じ店への再注文のMRR</th>' in table
    assert '<td>0.73361</td><td>0.75899</td>' in table
    assert 'trial_MRR' not in table and 'reorder_MRR' not in table

    now = (ROOT / LABELS).read_bytes()
    before = before_uvr_full_prose(ROOT, LABELS, now)
    assert unchanged_papers(before) == unchanged_papers(now)
    with pytest.raises(AssertionError):
        before_uvr_full_prose(ROOT, LABELS, now + b'\n')


def test_uvr_overview_is_paper_summary_and_mirrored():
    path = PREFIX + 'lab.yaml'
    now = (ROOT / path).read_bytes()
    original = yaml.safe_load(before_uvr_full_prose(ROOT, path, now))
    overview = yaml.safe_load(now)['sections']['overview']
    readme = (ROOT / (PREFIX + 'README.md')).read_text()
    assert original['sections']['overview'] == overview
    assert overview in readme
    assert '合成' not in overview
