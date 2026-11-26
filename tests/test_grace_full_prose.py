import ast
import json
from pathlib import Path

import pytest
import yaml

from paper_lab.build import _metrics_table
from prose_preservation import before_grace_full_prose

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'grace-meta-ads-gtm-serving'
PREFIX = f'papers/{SLUG}/'
LABELS = 'paper_lab/display_labels.py'


def labels_without_grace(raw):
    node = next(n for n in ast.parse(raw).body
                if isinstance(n, ast.Assign) and n.targets[0].id == 'LABELS')
    labels = ast.literal_eval(node.value)
    labels.pop(SLUG, None)
    return labels


def test_grace_display_names_do_not_change_measured_values_or_other_labs():
    path = PREFIX + 'results.json'
    now = (ROOT / path).read_bytes()
    previous = before_grace_full_prose(ROOT, path, now)
    current, old = map(json.loads, (now, previous))
    for obj in (current, old):
        del obj['note'], obj['experiments'][0]['name']
    assert current == old
    metrics = current['experiments'][0]['metrics']
    assert metrics['eligible_ads_after_exact'] == {'CD_only': 0, 'GTM': 1}
    assert metrics['mixed_prefix_false_positive'] == {'observed': True}
    table = _metrics_table(metrics, SLUG)
    assert '最終照合を通った広告数' in table
    assert '<td>0</td><td>1</td>' in table
    assert '枝は残ったが配信できる広告はなかった' in table
    assert 'mixed_prefix_false_positive' not in table

    current_src = (ROOT / LABELS).read_bytes()
    previous_src = before_grace_full_prose(ROOT, LABELS, current_src)
    assert labels_without_grace(current_src) == labels_without_grace(previous_src)
    with pytest.raises(AssertionError):
        before_grace_full_prose(ROOT, LABELS, current_src + b'\n')


def test_grace_overview_separates_the_two_paper_evaluations():
    doc = yaml.safe_load((ROOT / (PREFIX + 'lab.yaml')).read_text())
    overview = doc['sections']['overview']
    assert all(phrase in overview for phrase in (
        '23.55%から40.42%', '利用者の位置には人工データ', '197.7ミリ秒から17.8ミリ秒', '53.6ミリ秒',
    ))
    assert 'Lab' not in overview and '合成例' not in overview
