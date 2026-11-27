from pathlib import Path
import ast,json,subprocess,sys
import pytest
from prose_preservation import before_genpage_reader_full_prose

ROOT=Path(__file__).resolve().parents[1]
P='papers/genpage-netflix-homepage/'


def pair(n):
    path=P+n
    current=(ROOT/path).read_bytes()
    with pytest.raises(AssertionError):
        before_genpage_reader_full_prose(ROOT,path,current+b'\n')
    return before_genpage_reader_full_prose(ROOT,path,current),current


def test_genpage_retains_exact_story_layout_and_numerical_output(tmp_path):
    rows=json.loads((ROOT/'tests/genpage_reader_full_prose_hashes.json').read_bytes())['files']
    assert set(rows)=={P+'run.py',P+'results.json'}
    a,b=map(json.loads,pair('results.json'))
    aliases={b.pop('note'):a.pop('note'),b['experiments'][0].pop('name'):a['experiments'][0].pop('name')}
    assert len(aliases)==2 and a==b
    assert [r['forward_calls'] for r in b['cases'].values()]==[8,8,6,4]
    assert [r['candidate_violations'] for r in b['cases'].values()]==[6,0,0,0]
    class Normalize(ast.NodeTransformer):
        def visit_Constant(self,node):
            if isinstance(node.value,str):node.value=aliases.get(node.value,node.value)
            return node
    def clean(raw):
        t=ast.parse(raw)
        assert isinstance(t.body.pop(0).value,ast.Constant)
        return ast.dump(Normalize().visit(t))
    a,b=pair('run.py')
    assert clean(a)==clean(b)
    p=tmp_path/'run.py'
    p.write_bytes(b)
    subprocess.run([sys.executable,str(p)],check=True,capture_output=True)
    assert p.with_name('results.json').read_bytes()==pair('results.json')[1]
