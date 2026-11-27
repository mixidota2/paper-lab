from pathlib import Path
import ast,json,re,subprocess,sys
import pytest
import yaml
from prose_preservation import before_sgc_all_full_prose

ROOT=Path(__file__).resolve().parents[1]
P='papers/sgc-state-grounded-conditioning/'


def pair(n):
    raw=(ROOT/(P+n)).read_bytes()
    return before_sgc_all_full_prose(ROOT,P+n,raw),raw


def test_exact_sgc_reader_sources_and_paper_measurements():
    receipt=json.loads((ROOT/'tests/sgc_all_full_prose_hashes.json').read_bytes())['files']
    assert set(receipt)=={P+n for n in ('README.md','lab.yaml','mapping.md','method.md','results.json','run.py')}
    for p in receipt:
        a,b=pair(p.removeprefix(P))
        assert a!=b
        with pytest.raises(AssertionError):
            before_sgc_all_full_prose(ROOT,p,b+b'\n')
    a,b=map(yaml.safe_load,pair('lab.yaml'))
    assert all(a[k]==b[k] for k in ('arxiv_id','title','authors','urls','verification'))
    overview=b['sections']['overview']
    assert all(v in overview for v in ('Liuら','200セッション','1,000回答','96.7%','83.5%','26.5%','1.5秒','6.1秒','勝率'))
    assert not any(v in overview for v in ('Lab','<figure','教材','<table'))
    assert '見送りを挟む再提案は数えません' in b['sections']['results']
    assert '見送りを挟む再提案は数えません' in pair('README.md')[1].decode()
    for x,y in zip(a['teaching_figures'],b['teaching_figures'],strict=True):
        assert [z['formula'] for z in x.get('steps',[])]==[z['formula'] for z in y.get('steps',[])]
        assert [z['value'] for z in x.get('bars',[])]==[z['value'] for z in y.get('bars',[])]
    def frames(v):
        raw=v['sections']['executable_understanding']
        ar=json.loads(re.search(r'<script[^>]+data-frames>(.*?)</script>',raw,re.S)[1])
        return re.findall(r'<option value="([0-9])"',raw),[(re.findall(r'([0-9]+): ([A-C]|見送り)',r),re.findall(r'([0-9]+) 回',r)) for r in ar]
    assert frames(a)==frames(b)
    assert [x[1] for x in frames(b)[1]]==[['12','11','0'],['0','11','0'],['0','0','2']]


def test_sgc_runner_is_numerically_and_structurally_identical(tmp_path):
    a,b=map(json.loads,pair('results.json'))
    names={b.pop('note'):a.pop('note')}
    for x,y in zip(a['experiments'],b['experiments'],strict=True):
        names[y.pop('name')]=x.pop('name')
    assert a==b and len(names)==2
    class Normalize(ast.NodeTransformer):
        def visit_Constant(self,n):
            if isinstance(n.value,str) and n.value in names:n.value=names[n.value]
            return n
    def tree(s):
        t=ast.parse(s)
        for group in [t.body,*[n.body for n in t.body if isinstance(n,ast.FunctionDef)]]:
            top=group[0]
            if isinstance(top,ast.Expr) and isinstance(top.value,ast.Constant) and isinstance(top.value.value,str):
                group.pop(0)
        return ast.dump(Normalize().visit(t))
    a,b=pair('run.py')
    assert tree(a)==tree(b)
    p=tmp_path/'run.py';p.write_bytes(b)
    subprocess.run([sys.executable,str(p)],check=True,capture_output=True)
    assert (tmp_path/'results.json').read_bytes()==pair('results.json')[1]
