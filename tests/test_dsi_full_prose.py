import ast
import json
from pathlib import Path

import yaml

from prose_preservation import before_dsi_full_prose


ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'papers/beyond-scalar-dsi-watchtime/'


def read_pair(name):
    path = PREFIX + name
    current = (ROOT / path).read_bytes()
    return before_dsi_full_prose(ROOT, path, current), current


def test_dsi_prose_preserves_experiment_numbers_and_calculations():
    before, after = map(json.loads, read_pair('results.json'))
    for obj in (before, after):
        assert len(obj.pop('limitations')) == 3
    assert before == after
    assert after['expected_overplay_brier'] == {'best_shared_scalar_readout': 0.1875,
                                                'oracle_distribution_readout': 0.125}
    functions = {'state', 'summarize', 'expected_brier'}
    def core(raw):
        return {n.name: ast.dump(n) for n in ast.parse(raw).body
                if isinstance(n, ast.FunctionDef) and n.name in functions}
    earlier, current = map(core, read_pair('run.py'))
    assert earlier.keys() == functions and earlier == current


def test_dsi_paper_summary_is_unchanged_and_separate_from_toy():
    earlier, current = map(yaml.safe_load, read_pair('lab.yaml'))
    overview = current['sections']['overview']
    assert earlier['sections']['overview'] == overview
    assert overview in read_pair('README.md')[1].decode()
    assert '合成例' not in overview
    assert '0.1875' in current['sections']['results']
