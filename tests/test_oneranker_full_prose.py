from pathlib import Path
import ast
import json
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import yaml
from prose_preservation import before_oneranker_full_prose
ROOT=Path(__file__).resolve().parents[1]
P='papers/oneranker-ads/'
def src(name):
    c=(ROOT/(P+name)).read_bytes()
    return c,before_oneranker_full_prose(ROOT,P+name,c)

def test_oneranker_pins_versions_and_distinguishes_test_stages():
    current,old=map(yaml.safe_load,src('lab.yaml'))
    for k in ('source_review','verification','urls'):
        assert current[k]==old[k]
    assert current['sections']['overview']==old['sections']['overview']
    evidence=current['sections']['evidence']
    assert all(x in evidence for x in ('同じ節に信頼区間は示されていない','30候補を共通で使う','第4版は表に合わせて説明を直した','第2段の状態を渡し、分布を近づける損失は外す | 0.6173','第2段の状態を第3段へ渡さず、分布を近づける損失だけを追加 | 0.6161','5%を従来方式へ戻す'))
    method=(ROOT/P/'method.md').read_text()
    assert all(x in method for x in ('全カタログから上位500件','同じ30候補','既存の精密ランキングは、この後に別の処理として残る'))

def test_oneranker_numbers_and_numeric_program_unchanged(tmp_path):
    def clean(raw):
        s=json.loads(raw)
        for f in ('counterexample','not_tested'):s.pop(f)
        return s
    current,old=src('results.json')
    assert clean(current)==clean(old)
    def logic(raw):
        module=ast.parse(raw)
        module.body=module.body[1:]
        for n in ast.walk(module):
            if isinstance(n,ast.Dict):
                for i,k in enumerate(n.keys):
                    if isinstance(k,ast.Constant) and k.value in ('counterexample','not_tested'):
                        n.values[i]=ast.Constant('display-only')
            elif isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='dumps':
                n.keywords=[k for k in n.keywords if k.arg!='ensure_ascii']
        return ast.dump(module)
    assert logic(src('run.py')[0])==logic(src('run.py')[1])
    run=tmp_path/'run.py'
    shutil.copyfile(ROOT/P/'run.py',run)
    proc=subprocess.run([sys.executable,str(run)],capture_output=True,check=True)
    assert proc.stdout==(tmp_path/'results.json').read_bytes()==current

def test_oneranker_mask_and_figure_geometry_unchanged():
    n='{http://www.w3.org/2000/svg}'
    for f in ('figures/mask.svg','figures/stack.svg'):
        current,old=map(ET.fromstring,src(f))
        assert current.get('viewBox')==old.get('viewBox')
        for shape in ('rect','path'):
            assert [v.attrib for v in current.iter(n+shape)]==[v.attrib for v in old.iter(n+shape)]
        assert current.find(n+'desc') is not None
        for t in current.iter(n+'text'):
            width=sum(1 if ord(ch)>255 else .59 for ch in t.text)*int(t.get('font-size'))
            assert int(t.get('x'))+width<440
