import ast
import json
import re
from hashlib import sha256
from pathlib import Path
from statistics import mean

import pytest
import yaml

from prose_preservation import before_exaone_full_prose

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'exaone-demand-routed-tsfm'
PAPER = ROOT / 'papers' / SLUG


def test_exaone_exact_before_after_and_unchanged_source_numbers():
    files = json.loads((ROOT / 'tests/exaone_full_prose_hashes.json').read_text())['files']
    assert set(files) == {
        *(f'papers/{SLUG}/{n}' for n in ('README.md', 'lab.yaml', 'mapping.md', 'method.md', 'results.json', 'run.py')),
        'paper_lab/exaone05.py',
    }
    before = {}
    for p, row in files.items():
        new = (ROOT / p).read_bytes()
        assert sha256(new).hexdigest() == row['after']['sha256']
        before[p] = before_exaone_full_prose(ROOT, p, new)
        assert sha256(before[p]).hexdigest() == row['before']['sha256']
    prior, current = (yaml.safe_load(blob) for blob in (before[f'papers/{SLUG}/lab.yaml'], (PAPER / 'lab.yaml').read_bytes()))
    assert current['sections']['overview'] == prior['sections']['overview']
    assert current['source_review'] == prior['source_review']
    new, old = (json.loads(blob) for blob in ((PAPER / 'results.json').read_bytes(), before[f'papers/{SLUG}/results.json']))
    assert new.pop('scope') != old.pop('scope')
    assert new == old
    path = f'papers/{SLUG}/run.py'

    class StripCommentsAndScope(ast.NodeTransformer):
        def visit_Constant(self, node):
            if type(node.value) is str and (not node.value.isascii() or
                node.value.startswith(('Small mechanism', '4種類'))):
                return ast.Constant('')
            return node

    assert ast.dump(StripCommentsAndScope().visit(ast.parse(before[path]))) == ast.dump(
        StripCommentsAndScope().visit(ast.parse((ROOT / path).read_bytes())))
    old_widget, new_widget = before['paper_lab/exaone05.py'].decode(), (ROOT / 'paper_lab/exaone05.py').read_text()
    startup = r'const controls=.*?</script>'
    assert re.search(startup, new_widget, re.S)[0] == re.search(startup, old_widget, re.S)[0]
    for script in (old_widget, new_widget):
        assert 'p.reduce((s,v)=>s+v*v,0)' in script
        assert 'if(inv<8&&due<0)due=t+3;' in script


def test_exaone_does_not_conflate_teacher_route_or_scope():
    src = yaml.safe_load((PAPER / 'lab.yaml').read_text())
    evidence = src['sections']['evidence']
    assert '同じ将来期間で季節ナイーブ法より悪かったという意味ではありません' in evidence
    assert '表9に掲載した7モデルの中で22件中10件' in evidence
    assert '836組' in evidence and '358,008系列' in evidence
    assert '10.70' in evidence and '10.63' in evidence
    method = (PAPER / 'method.md').read_text()
    assert '予測時に使うのはπやπ̃ではなく' in method
    assert '投影）ごとに' in method and '全トークンに同じ配分' in method
    assert '予測誤差と、qを学習用の教師比率π̃に近づける補助損失' in method
    assert '欠品中の潜在需要を復元することは、原論文でも将来の課題' in src['sections']['what_we_did_not_verify']


def test_exaone_numeric_toy_runs_and_reported_tables_have_distinct_results():
    data = json.loads((PAPER / 'results.json').read_text())
    seeds = data['seed_results']
    assert [r['seed'] for r in seeds if r['mase_routed'] < r['mase_global']] == [19]
    assert mean(r['mase_global'] for r in seeds) == pytest.approx(.8583738656, abs=1e-10)
    assert mean(r['mase_routed'] for r in seeds) == pytest.approx(.8589736107, abs=1e-10)
    assert [r['class'] for r in data['class_results'] if r['routed'] < r['global']] == ['Smooth']
    assert len(data['reported_datasets']) == 22
    assert data['reported_aggregate'][0] == ['EXAONE Demand', 1.0667]
