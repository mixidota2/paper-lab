import ast
import json
from pathlib import Path
import subprocess
import sys
import yaml
from prose_preservation import before_spotify_causal_full_prose
ROOT=Path(__file__).resolve().parents[1]
PREFIX='papers/spotify-incremental-recommendation-causal/'
def pair(name):
    p=PREFIX+name
    new=(ROOT/p).read_bytes()
    return before_spotify_causal_full_prose(ROOT,p,new),new

def test_overview_and_figure_layout_stay_separate_and_intact():
    old,new=map(yaml.safe_load,pair('lab.yaml'))
    assert old['sections']['overview']==new['sections']['overview']
    assert pair('README.md')[1].count(new['sections']['overview'].encode())==1
    assert old['verification']==new['verification']
    for a,b in zip(old['teaching_figures'],new['teaching_figures'],strict=True):
        for k in ('kind','id','source','locator','after'): assert a[k]==b[k]
    assert [e['formula'] for e in old['teaching_figures'][1]['steps']]==[e['formula'] for e in new['teaching_figures'][1]['steps']]
    assert all(t in new['sections']['evidence'] for t in ('同じモデルと学習データ','95%信頼区間','約93%','個々の表示'))

def test_only_visible_copy_changes_and_11_options_keep_the_same_results(tmp_path):
    a,b=map(json.loads,pair('results.json'))
    for p in (a,b):
        e=p['explorer']
        del e['label'],e['metric']
        for f in e['frames']:
            del f['note']
            for bar in f['bars']: del bar['label']
    assert a==b
    assert [f['value'] for f in b['explorer']['frames']]==[x/10 for x in range(11)]
    assert b['baseline']['impressions']==3 and b['proposed']['impressions']==2
    assert b['baseline']['expected_incremental_streams']==.82
    assert b['proposed']['expected_incremental_streams']==.8
    def invariant(raw):
        p=ast.parse(raw)
        assert isinstance(p.body.pop(0),ast.Expr)
        out=[x for x in p.body if isinstance(x,ast.Assign) and isinstance(x.targets[0],ast.Name) and x.targets[0].id=='out']
        assert len(out)==1 and isinstance(out[0].value,ast.Dict)
        i=[k.value for k in out[0].value.keys].index('explorer')
        out[0].value.values[i]=ast.Constant(None)
        return ast.dump(p)
    before,after=pair('run.py')
    assert invariant(before)==invariant(after)
    (tmp_path/'run.py').write_bytes(after)
    subprocess.run([sys.executable,'-S','run.py'],cwd=tmp_path,check=True)
    assert (tmp_path/'results.json').read_bytes()==pair('results.json')[1]
