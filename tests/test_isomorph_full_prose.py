import ast
import json
from fractions import Fraction
from hashlib import sha256
from pathlib import Path

import yaml

from prose_preservation import before_isomorph_full_prose

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'isomorph-supply-chain-digital-twin'
PAPER = ROOT / 'papers' / SLUG


def test_isomorph_exact_before_after_and_unchanged_paper_facts():
    manifest = json.loads((ROOT / 'tests/isomorph_full_prose_hashes.json').read_text())['files']
    assert set(manifest) == {
        *(f'papers/{SLUG}/{n}' for n in ('README.md', 'lab.yaml', 'mapping.md', 'method.md', 'results.json', 'run.py')),
        'paper_lab/isomorph30.py',
    }
    before = {}
    for p, row in manifest.items():
        final = (ROOT / p).read_bytes()
        assert sha256(final).hexdigest() == row['after']['sha256']
        before[p] = before_isomorph_full_prose(ROOT, p, final)
        assert sha256(before[p]).hexdigest() == row['before']['sha256']
    prior, current = (yaml.safe_load(blob) for blob in (before[f'papers/{SLUG}/lab.yaml'], (PAPER / 'lab.yaml').read_bytes()))
    assert prior['sections']['overview'] == current['sections']['overview']
    assert prior['source_review'] == current['source_review']
    assert [(f['source'], f['rows']) for f in prior['teaching_figures']] == [(f['source'], f['rows']) for f in current['teaching_figures']]
    previous = json.loads(before[f'papers/{SLUG}/results.json'])
    updated = json.loads((PAPER / 'results.json').read_text())
    for old, new in zip(previous['frames'], updated['frames'], strict=True):
        assert {k: v for k, v in old.items() if k != 'label'} == {k: v for k, v in new.items() if k != 'label'}
    for path in (f'papers/{SLUG}/run.py', 'paper_lab/isomorph30.py'):
        class StripCopy(ast.NodeTransformer):
            def visit_Constant(self, node):
                if type(node.value) is str:
                    return ast.Constant('')
                return node
        copies = [StripCopy().visit(ast.parse(z)) for z in (before[path], (ROOT / path).read_bytes())]
        assert ast.dump(copies[0]) == ast.dump(copies[1])


def test_isomorph_same_day_fill_is_not_eventual_fill():
    frames = json.loads((PAPER / 'results.json').read_text())['frames']
    for frame, cap, new, final, max_backlog, stock in zip(
        frames, (8, 12, 20), (73, 812, 812), (679, 816, 816), (137, 1, 2), (0, 3, 18), strict=True
    ):
        rows = frame['rows']
        demands = tuple(r['demand'] for r in rows)
        assert frame['capacity'] == cap and demands == (8, 8, 8, 8, 14, 14, 8) * 12
        assert sum(Fraction(r['fill']).limit_denominator(14) * r['demand'] for r in rows) == new
        assert sum(demands) - rows[-1]['backlog'] == final
        assert max(r['backlog'] for r in rows) == max_backlog
        assert rows[-1]['stock'] == stock


def test_isomorph_paper_metrics_and_local_scope():
    src = yaml.safe_load((PAPER / 'lab.yaml').read_text())
    evidence = src['sections']['evidence']
    assert '過去区間の季節ナイーブ法の誤差' in evidence
    assert '同じテスト期間で季節ナイーブ法に負けたという意味ではありません' in evidence
    assert all(n in evidence for n in ('0.828', '2.228', '1.473', '0.721', '29件', '24件', '36窓'))
    assert '輸送中の数量と手元在庫を引きます' in (PAPER / 'method.md').read_text()
    assert '輸送路の空き容量' in (PAPER / 'method.md').read_text()
    assert '8.95%' in src['sections']['results'] and '83.21%' in src['sections']['results']
