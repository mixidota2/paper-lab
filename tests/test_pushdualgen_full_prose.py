from pathlib import Path
import ast
import json
import shutil
import subprocess
import sys
import yaml
from prose_preservation import before_pushdualgen_full_prose

ROOT=Path(__file__).resolve().parents[1]
P='papers/pushdualgen-kuaishou/'
def data(n):
    current=(ROOT/(P+n)).read_bytes()
    return current,before_pushdualgen_full_prose(ROOT,P+n,current)

def test_pushdualgen_paper_summary_boundary_and_values():
    new,old=map(yaml.safe_load,data('lab.yaml'))
    assert new['sections']['overview']==old['sections']['overview']
    assert new['sections']['overview'] in (ROOT/P/'README.md').read_text()
    assert new['source_review']==old['source_review']
    assert new['verification']==old['verification']
    assert [s['formula'] for s in new['teaching_figures'][0]['steps']]==[s['formula'] for s in old['teaching_figures'][0]['steps']]
    assert [s['value'] for s in new['teaching_figures'][1]['bars']]==[s['value'] for s in old['teaching_figures'][1]['bars']]
    assert '原論文の§6は、文面からコードを生成する逆方向の使い方' in new['sections']['what_we_did_not_verify']
    assert '本番で文面の生成だけを省いたときの効果は報告していない' in new['sections']['evidence']
    assert '同じ手順でコードを先に確定した場合' in new['teaching_figures'][0]['steps'][0]['explanation']

def test_pushdualgen_arithmetic_unchanged_and_download_reruns(tmp_path):
    def normalize(raw):
        model=json.loads(raw)
        model.pop('note')
        model['experiments'][0].pop('name')
        return model
    result,old_result=data('results.json')
    assert normalize(result)==normalize(old_result)
    traces=json.loads(result)['decode_trace']
    for h,e in traces.items():
        assert e['copy_on']['sid']==e['copy_off']['sid']
        assert e['copy_off']['steps']==1
        assert e['copy_on']['steps']==1+len(e['copy_on']['copy'])
    def grammar(raw):
        tree=ast.parse(raw)
        tree.body=tree.body[1:]
        for node in ast.walk(tree):
            if isinstance(node,ast.Dict):
                for i,k in enumerate(node.keys):
                    if isinstance(k,ast.Constant) and k.value in ('name','note'):
                        assert isinstance(node.values[i],ast.Constant)
                        node.values[i]=ast.Constant('display')
        return ast.dump(tree)
    a,b=data('run.py')
    assert grammar(a)==grammar(b)
    run=tmp_path/'run.py'
    shutil.copyfile(ROOT/P/'run.py',run)
    subprocess.run([sys.executable,str(run)],check=True,capture_output=True)
    assert (tmp_path/'results.json').read_bytes()==result
