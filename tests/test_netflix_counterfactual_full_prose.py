import json
from pathlib import Path

import yaml

from prose_preservation import before_netflix_counterfactual_full_prose

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'papers/netflix-counterfactual-observability/'


def read_pair(name):
    path = PREFIX + name
    current = (ROOT / path).read_bytes()
    return before_netflix_counterfactual_full_prose(ROOT, path, current), current


def test_netflix_counterfactual_prose_holds_numeric_experiment_fixed():
    old, current = map(json.loads, read_pair('results.json'))
    assert current['experiments'][0]['n'] == 120000
    assert current['experiments'][0]['metrics']['incrementality'] == 0.04270420274730685
    for value in (old, current):
        del value['note']
        for e in value['experiments']:
            del e['name']
    assert old == current


def test_netflix_counterfactual_overview_is_paper_result():
    before, after = [yaml.safe_load(r)['sections'] for r in read_pair('lab.yaml')]
    assert before['overview'] == after['overview']
    assert '0.8212' in after['overview']
    lead = read_pair('README.md')[1].decode().split('\n\n')[1]
    assert all(phrase in lead for phrase in ('11件のA/Bテスト', '0.8212', '新しい推薦枠でも同じ精度になるとは限りません'))
    assert '人工' not in lead
    assert '120000' not in after['overview']
