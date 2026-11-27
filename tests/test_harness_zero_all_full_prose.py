from pathlib import Path
import ast,json,subprocess,sys
import pytest
import yaml
from prose_preservation import before_harness_zero_all_full_prose

ROOT=Path(__file__).resolve().parents[1]
P='papers/harness-zero-distillation/'


def pair(n):
    raw=(ROOT/(P+n)).read_bytes()
    return before_harness_zero_all_full_prose(ROOT,P+n,raw),raw


def test_harness_zero_exact_source_and_author_measurements():
    receipt=json.loads((ROOT/'tests/harness_zero_all_full_prose_hashes.json').read_bytes())['files']
    assert set(receipt)=={P+n for n in ('README.md','lab.yaml','mapping.md','method.md','results.json','run.py')}
    for name in receipt:
        a,b=pair(name.removeprefix(P))
        assert a!=b
        with pytest.raises(AssertionError):
            before_harness_zero_all_full_prose(ROOT,name,b+b'\n')
    a,b=map(yaml.safe_load,pair('lab.yaml'))
    assert all(a[k]==b[k] for k in ('authors','arxiv_id','verification','urls'))
    ov=b['sections']['overview']
    assert all(x in ov for x in ('Yeら','23.3%','44.3%','41.7%','30.0%','38.0%','全課題を合算した成功率ではありません'))
    assert all(x not in ov for x in ('Lab','教材','<table','<figure'))
    for x,y in zip(a['teaching_figures'],b['teaching_figures'],strict=True):
        assert [v['value'] for v in x.get('bars',[])]==[v['value'] for v in y.get('bars',[])]
        assert [v['cells'] for v in x.get('rows',[]) if 'cells' in v]==[v['cells'] for v in y.get('rows',[]) if 'cells' in v]
    assert '点検役の視点で書いた推論が入り込む場合は、その部分を損失に入れません' in pair('method.md')[1].decode()


def test_harness_zero_selection_inputs_and_replay_exact(tmp_path):
    a,b=map(json.loads,pair('results.json'))
    names={b.pop('note'):a.pop('note')}
    for x,y in zip(a['frames'],b['frames'],strict=True):
        names[y.pop('label')]=x.pop('label')
    assert a==b and len(names)==4
    class Normalize(ast.NodeTransformer):
        def visit_Constant(self,n):
            if isinstance(n.value,str) and n.value in names:n.value=names[n.value]
            return n
    def tree(s):
        t=ast.parse(s)
        assert isinstance(t.body.pop(0).value,ast.Constant)
        return ast.dump(Normalize().visit(t))
    a,b=pair('run.py')
    assert tree(a)==tree(b)
    target=tmp_path/'run.py';target.write_bytes(b)
    subprocess.run([sys.executable,str(target)],check=True,capture_output=True)
    assert (tmp_path/'results.json').read_bytes()==pair('results.json')[1]
