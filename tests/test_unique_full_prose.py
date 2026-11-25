import ast
import json
from pathlib import Path
import subprocess

import yaml

from prose_preservation import before_unique_full_prose


ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'papers/unique-baidu-unified-retrieval-ranking'
BASE = 'c23860ab5dd0ae0bb3f0bc74ee564071618b6e1a'


def test_scope_and_real_recommendation_boundary():
    before, after = {}, {}
    for name in ('README.md', 'lab.yaml', 'mapping.md', 'method.md', 'run.py', 'results.json'):
        rel = f'{PREFIX}/{name}'
        old = subprocess.check_output(['git', 'show', f'{BASE}:{rel}'], cwd=ROOT)
        new = (ROOT / rel).read_bytes()
        assert old != new and before_unique_full_prose(ROOT, rel, new) == old
        before[name], after[name] = old.decode(), new.decode()
    a, b = (yaml.safe_load(d['lab.yaml']) for d in (before, after))
    for key in a.keys() - {'question', 'summary', 'source_review', 'core_idea', 'sections', 'teaching_figures'}:
        assert a[key] == b[key]
    assert {k: v for k, v in a['source_review'].items() if k != 'scope'} == {
        k: v for k, v in b['source_review'].items() if k != 'scope'
    }
    assert a['sections'].keys() == b['sections'].keys()
    overview = b['sections']['overview']
    assert overview == after['README.md'].split('\n\n', 1)[1].split('\n\n##', 1)[0]
    assert '記事や動画' in overview and '商品' not in overview
    assert all(x in overview for x in ('1週間', '0.96%', '1.08%', '推薦画面全体の応答時間ではありません'))
    assert all(x in after['method.md'] for x in ('100個', '上位1万件', 'コードごとに上位30件', '後続処理'))
    assert all(x in b['sections']['evidence'] for x in ('0.1456', '利用継続率 +0.70%', '旧運用の候補取得方式'))
    assert [x['id'] for x in a['teaching_figures']] == [x['id'] for x in b['teaching_figures']]
    assert [x['formula'] for x in a['teaching_figures'][2]['steps']] == [
        x['formula'] for x in b['teaching_figures'][2]['steps']
    ]
    for name in ('assignments', 'attention', 'verification'):
        assert json.loads(before['results.json'])[name] == json.loads(after['results.json'])[name]
    def computation(text):
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, ast.keyword) and node.arg == 'note':
                node.value = ast.Constant(None)
        return ast.dump(tree)
    assert computation(before['run.py']) == computation(after['run.py'])
