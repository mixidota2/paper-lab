"""Protect source, experiment, attribution, and paper-summary boundaries."""
import ast
import json
from pathlib import Path
import re
import runpy

import yaml

from prose_preservation import before_tmall_full_prose

ROOT = Path(__file__).resolve().parents[1]
REL = 'papers/cq-sid-eg-grpo-tmall/'
P = ROOT / REL


def before(name):
    return before_tmall_full_prose(ROOT, REL + name, (P / name).read_bytes())


def test_quantization_and_preserved_artificial_experiment():
    current = yaml.safe_load((P / 'lab.yaml').read_bytes())
    original = yaml.safe_load(before('lab.yaml'))
    assert current['verification'] == original['verification']
    for key in ('id', 'arxiv_id', 'title', 'authors', 'year', 'topics', 'verification', 'status', 'verdict'):
        assert current[key] == original[key]
    for old, now in zip(original['teaching_figures'], current['teaching_figures'], strict=True):
        assert all(old[k] == now[k] for k in ('id', 'kind', 'after', 'locator'))
        assert [s['formula'] for s in old.get('steps', [])] == [s['formula'] for s in now.get('steps', [])]

    raw = json.loads((P / 'results.json').read_text())
    assert raw == runpy.run_path(str(P/'run.py'))['compute']()
    embedded = current['sections']['executable_understanding'].split('<script type="application/json" data-probe-data>')[1].split('</script>')[0]
    assert raw == json.loads(embedded)
    prev = json.loads(before('results.json'))
    for label in ('note',):
        assert raw[label] != prev[label]
        del raw[label], prev[label]
    for label in ('name', 'dataset'):
        assert raw['experiments'][0][label] != prev['experiments'][0][label]
        del raw['experiments'][0][label], prev['experiments'][0][label]
    assert raw == prev

    def normalized(code):
        node = ast.parse(code)
        assert isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value.value, str)
        node.body.pop(0)
        edited = []
        for x in ast.walk(node):
            if isinstance(x, ast.Dict):
                for k, v in zip(x.keys, x.values, strict=True):
                    if isinstance(k, ast.Constant) and k.value in {'note', 'name', 'dataset'}:
                        assert isinstance(v, ast.Constant) and isinstance(v.value, str)
                        v.value = ''
                        edited.append(k.value)
        assert sorted(edited) == ['dataset', 'name', 'note']
        return ast.dump(node)
    assert normalized(before('run.py')) == normalized((P / 'run.py').read_text())


def test_v2_paper_summary_and_overlap_inclusive_attribution():
    d = yaml.safe_load((P / 'lab.yaml').read_bytes())
    assert d['urls']['pdf'] == 'https://arxiv.org/pdf/2605.14434v2'
    assert d['source_review']['version'] == '2605.14434v2'
    assert d['source_review']['url'] == 'https://arxiv.org/html/2605.14434v2'
    s = d['sections']
    overview = s['overview']
    assert len(overview.split('\n\n')) == 2
    assert all(x in overview for x in ('既存の順位付け', '42.75%', '44.22%', '2週間', '1.15%', '0.40%', '72.63%', '重複'))
    assert all(x not in overview for x in ('人工', 'Lab', '<figure', '<table', 'run.py'))
    e = s['evidence']
    assert all(x in e for x in ('51.99%', '61.81%', '17.95%', '8 GPU', '40ms', 'A/Bテスト', '構成比'))
    assert '購入：生成経路にも帰属 72.63% / 生成経路への帰属なし 27.37%' in e
    assert '淡い色は「他の経路の取り分」ではありません' in e
    assert '27.370000000000005' not in e
    assert re.findall(r'width:([\d.]+)%', e) == ['50.25','49.75','58.96','41.04','72.63','27.37']
    assert '配信中に検索の正解を渡す仕組みではありません' in (P/'method.md').read_text()
    assert '100の上限' in (P/'method.md').read_text()
    assert '複数経路への重複帰属' in (P/'mapping.md').read_text()
