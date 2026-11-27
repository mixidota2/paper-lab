import ast
import json
from fractions import Fraction
from hashlib import sha256
from pathlib import Path

import pytest
import yaml

from prose_preservation import before_sim2real_all_full_prose, before_grace_full_prose, before_uvr_full_prose, before_hear_full_prose, before_autolr_full_prose, before_traffic_value_full_prose

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'traffic-forecast-to-decision-value'
PAPER = ROOT / 'papers' / SLUG
RENDERER = 'paper_lab/batch08.py'
LABELS = 'paper_lab/display_labels.py'


def test_traffic_value_source_receipt_and_fixed_numbers():
    files = json.loads((ROOT / 'tests/traffic_value_full_prose_hashes.json').read_text())['files']
    assert set(files) == {
        *(f'papers/{SLUG}/{n}' for n in ('README.md', 'lab.yaml', 'mapping.md', 'method.md', 'results.json', 'run.py')),
        RENDERER, LABELS,
    }
    before = {}
    for p, row in files.items():
        latest = before_sim2real_all_full_prose(ROOT, p, (ROOT / p).read_bytes())
        cur = before_autolr_full_prose(ROOT, p, before_hear_full_prose(ROOT, p, before_uvr_full_prose(ROOT, p, before_grace_full_prose(ROOT, p, latest))))
        assert sha256(cur).hexdigest() == row['after']['sha256']
        before[p] = before_traffic_value_full_prose(ROOT, p, cur)
        assert sha256(before[p]).hexdigest() == row['before']['sha256']
        with pytest.raises(AssertionError):
            before_traffic_value_full_prose(ROOT, p, cur + b'\n')
    prior, current = (yaml.safe_load(blob) for blob in (before[f'papers/{SLUG}/lab.yaml'], (PAPER / 'lab.yaml').read_bytes()))
    assert current['sections']['overview'] == prior['sections']['overview']
    assert current['source_review'] == prior['source_review']
    old, new = (json.loads(blob) for blob in (before[f'papers/{SLUG}/results.json'], (PAPER / 'results.json').read_bytes()))
    for obj in (old, new):
        del obj['note']
        obj['paper']['effects'] = [x[1:] for x in obj['paper']['effects']]
    assert new == old

    def remove_traffic_scope(blob):
        before, rest = blob.split(b"TRAFFIC = r'''", 1)
        return before, rest.split(b"HEAR = r'''",1)[1]
    latest = before_sim2real_all_full_prose(ROOT, RENDERER, (ROOT / RENDERER).read_bytes())
    assert remove_traffic_scope(before[RENDERER]) == remove_traffic_scope(before_hear_full_prose(ROOT, RENDERER, latest))

    def other_labels(blob):
        sets = ast.literal_eval(next(n.value for n in ast.parse(blob).body
                                    if isinstance(n, ast.Assign) and n.targets[0].id == 'LABELS'))
        del sets[SLUG]
        return sets
    current_labels = before_autolr_full_prose(ROOT, LABELS, before_uvr_full_prose(ROOT, LABELS, before_grace_full_prose(ROOT, LABELS, (ROOT / LABELS).read_bytes())))
    assert other_labels(before[LABELS]) == other_labels(current_labels)


def test_traffic_value_one_period_actions_and_loss_values():
    d = json.loads((PAPER / 'results.json').read_text())
    expected_loss = [(Fraction(203,75),)*3, (Fraction(203,75),0,0), (Fraction(437,75),)*3]
    expected_values = [[0,0,0],[0,100,100],[0,0,0]]
    for case, losses, reductions in zip(d['cases'].values(), expected_loss, expected_values, strict=True):
        assert [x['mae'] for x in case.values()] == [1624/600,382/600,0]
        assert [x['decision_loss'] for x in case.values()] == [float(x) for x in losses]
        assert [x['value_percent'] for x in case.values()] == pytest.approx(reductions, abs=2e-14)
    assert d['paper']['effective_actions'] == [1]*7 + [8,8]
    assert all(lo<0<hi for _,_,lo,hi in d['paper']['effects'])


def test_traffic_value_prose_separates_information_and_boundaries():
    src = yaml.safe_load((PAPER / 'lab.yaml').read_text())['sections']
    assert '負なら0' in (PAPER / 'method.md').read_text()
    method = (PAPER / 'method.md').read_text()
    assert '観測した列に含まれる' in method and '最大64通り' in method and '切り替え可能' in method
    assert '内部で計算した費用' in src['why_it_might_work']
    assert 'NO_GO' in src['why_it_might_work'] and '設定を固定' in src['why_it_might_work']
    assert all(s in src['evidence'] for s in ('15.06ポイント', '50,000', '観測した日数は7日'))
    assert '隣の候補まで4' in src['results'] and '100%下がるのは、この条件' in src['results']
