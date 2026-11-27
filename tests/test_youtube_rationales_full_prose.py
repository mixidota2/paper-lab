import ast
import json
from pathlib import Path
import subprocess
import sys
import yaml
from prose_preservation import before_youtube_rationales_full_prose
ROOT=Path(__file__).resolve().parents[1]
PREFIX='papers/youtube-music-llm-rationales-discovery/'
def pair(n):
    p=PREFIX+n
    new=(ROOT/p).read_bytes()
    return before_youtube_rationales_full_prose(ROOT,p,new),new

def test_youtube_method_separates_artist_generation_and_existing_track_search():
    a,b=map(yaml.safe_load,pair('lab.yaml'))
    assert a['sections']['overview']==b['sections']['overview']
    assert pair('README.md')[1].count(b['sections']['overview'].encode())==1
    assert a['verification']==b['verification']
    assert [(f['id'],f['kind'],f['after'],f['source'],f['locator']) for f in a['teaching_figures']]==[(f['id'],f['kind'],f['after'],f['source'],f['locator']) for f in b['teaching_figures']]
    method=pair('method.md')[1].decode()
    assert '画面に出す曲や動画は、既存の候補検索でアーティストを指定して探します。' in method
    e=b['sections']['evidence']
    assert all(x in e for x in ('22.43%','8.07%','0.3%','64.8%','74.4%','ちょうど3点','信頼区間はなく'))

def test_youtube_toy_changes_no_ids_outcomes_or_choices(tmp_path):
    a,b=map(json.loads,pair('results.json'))
    assert a.pop('note')!=b.pop('note')
    assert a['full']['items'][0].pop('rationale')!=b['full']['items'][0].pop('rationale')
    assert a==b
    assert b['cold']['source']=='heuristic fallback'
    assert b['full']['items'][0]['id']==b['rationale_holdback']['items'][0]['id']=='b'
    assert b['rationale_holdback']['items'][0]['rationale'] is None
    def normalize(raw):
        tree=ast.parse(raw)
        assert isinstance(tree.body.pop(0),ast.Expr)
        allowed={'既存の好みとの接点（人工例）','もともとの好みに合う点を示す理由（架空の例）',
          '全artistと理由は人工fixture。Gemini、KG、A/Bを再現しない。',
          '名前、履歴、理由はすべて架空です。Gemini、実際の知識グラフ、論文の比較実験は再現していません。'}
        for n in ast.walk(tree):
            if isinstance(n,ast.Constant) and isinstance(n.value,str) and n.value in allowed: n.value=''
        return ast.dump(tree,include_attributes=False)
    run_before,run_after=pair('run.py')
    assert normalize(run_before)==normalize(run_after)
    (tmp_path/'run.py').write_bytes(run_after)
    subprocess.run([sys.executable,'-S','run.py'],cwd=tmp_path,check=True)
    assert (tmp_path/'results.json').read_bytes()==pair('results.json')[1]
