import ast
import json
from hashlib import sha256
from pathlib import Path

import pytest
import yaml

from paper_lab.batch28 import widget
from prose_preservation import before_eval_grain_full_prose

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'evaluation-choices-forecasting-leaderboard'
PAPER = ROOT / 'papers' / SLUG
RENDERER = 'paper_lab/batch28.py'


def test_eval_grain_exact_receipt_numbers_and_other_renderer_branches():
    files = json.loads((ROOT / 'tests/eval_grain_full_prose_hashes.json').read_text())['files']
    assert set(files) == {
        *(f'papers/{SLUG}/{n}' for n in ('README.md', 'lab.yaml', 'mapping.md', 'method.md', 'results.json', 'run.py')),
        RENDERER,
    }
    before = {}
    for p, row in files.items():
        cur = (ROOT / p).read_bytes()
        assert sha256(cur).hexdigest() == row['after']['sha256']
        before[p] = before_eval_grain_full_prose(ROOT, p, cur)
        assert sha256(before[p]).hexdigest() == row['before']['sha256']
        with pytest.raises(AssertionError):
            before_eval_grain_full_prose(ROOT, p, cur + b'\n')
    prior, current = (yaml.safe_load(blob) for blob in (before[f'papers/{SLUG}/lab.yaml'], (PAPER / 'lab.yaml').read_bytes()))
    assert current['sections']['overview'] == prior['sections']['overview']
    assert current['source_review'] == prior['source_review']
    assert prior['teaching_figures'][0]['rows'] == current['teaching_figures'][0]['rows']
    assert [x['formula'] for x in prior['teaching_figures'][1]['steps']] == [x['formula'] for x in current['teaching_figures'][1]['steps']]
    old, new = (json.loads(blob) for blob in (before[f'papers/{SLUG}/results.json'], (PAPER / 'results.json').read_bytes()))
    for obj in (old, new):
        del obj['note']
        for f in obj['frames']:
            del f['label']
    assert new == old

    old_namespace = {}
    exec(compile(before[RENDERER], RENDERER, 'exec'), old_namespace)
    kinds = {
        'reasoncast-agentic-demand-forecasting', 'scope-coupled-supply-chain-policies',
        'onetrans-v2-cascade-unification', 'harness-zero-distillation',
    }
    for slug in kinds:
        data = json.loads((ROOT / 'papers' / slug / 'results.json').read_text())
        assert 'lab28' in data
        assert old_namespace['widget'](data) == widget(data)

    path = f'papers/{SLUG}/run.py'
    class StripLabels(ast.NodeTransformer):
        def visit_Constant(self, node):
            if type(node.value) is str and (not node.value.isascii() or node.value.startswith('Standalone')):
                return ast.Constant('')
            return node
    assert ast.dump(StripLabels().visit(ast.parse(before[path]))) == ast.dump(
        StripLabels().visit(ast.parse((ROOT / path).read_bytes())))


def test_eval_grain_partitions_swap_winner_without_changing_residuals():
    d = json.loads((PAPER / 'results.json').read_text())
    assert d['actual'] == [100] * 4
    assert d['predictions'] == {'A': [140, 60, 140, 60], 'B': [110] * 4}
    assert [(f['scores'], f['winner']) for f in d['frames']] == [
        ({'A': 0, 'B': 10}, 'A'), ({'A': 0, 'B': 10}, 'A'),
        ({'A': 40, 'B': 10}, 'B'), ({'A': 40, 'B': 10}, 'B'),
    ]
    assert d['gap_closed_from_rounded_table6'] == pytest.approx(54.679802955665, abs=1e-9)


def test_eval_grain_comparisons_remain_distinct():
    src = yaml.safe_load((PAPER / 'lab.yaml').read_text())['sections']
    assert '全体では22起点の平均WAPE、買い手別では8起点の平均RMSSE' in src['evidence']
    assert '共通の19手法と8起点' in src['evidence']
    assert 'p=0.9099' in src['evidence']
    assert 'モデルがもともと出す分位点の比較ではありません' in src['evidence']
    assert '54.6%' in src['evidence']
    method = (PAPER / 'method.md').read_text()
    assert '約54.68%' in method and '分母にMAEを使っていた' in method
    assert '15通り' in src['results'] and '確率を表す数字ではありません' in src['results']
