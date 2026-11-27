"""Preserve model behavior and distinguish the published paper editions."""
import ast
from pathlib import Path
import subprocess, sys, json
import pytest, yaml
from prose_preservation import before_retail_grain_all_full_prose

ROOT=Path(__file__).resolve().parents[1]
PREFIX='papers/retail-forecast-decision-grain/'
NAMES={'README.md','evidence.md','experiment.md','interactive.html','interactive.js','lab.yaml','mapping.md','method.md','model.js','run.py'}

def pair(n):
    p=PREFIX+n
    current=(ROOT/p).read_bytes()
    return before_retail_grain_all_full_prose(ROOT,p,current),current


def test_current_overview_follows_the_primary_source_not_the_demo():
    a,b=map(yaml.safe_load,pair('lab.yaml'))
    for k in ('id','arxiv_id','title','authors','urls','status','verification'):
        assert a[k]==b[k]
    p=b['sections']['overview']
    assert all(v in p for v in ('IyerとDabbeeru','4つの公開データ源','9つのうち7つ','8つのうち7つ','2モデル','27通りのうち22通り','8つのうち3つ','販売数'))
    assert all(v not in p for v in ('Lab','教材','操作図','500000000.05'))
    evidence=pair('evidence.md')[1].decode()
    assert all(v in evidence for v in ('| 4 | 3 | 1（M5） |','| 3 | 5 | 0 |','最大0.040','最大0.311','最大0.061','販売履歴のない新商品'))
    for old,new in zip(a['teaching_figures'],b['teaching_figures'],strict=True):
        assert old['source']==new['source'] and old['locator']==new['locator']
        assert [x['formula'] for x in old.get('steps',())]==[x['formula'] for x in new.get('steps',())]


def test_computation_and_regeneration_unchanged(tmp_path):
    def no_docstrings(v):
        tree=ast.parse(v)
        for node in ast.walk(tree):
            if isinstance(node,(ast.Module,ast.FunctionDef)) and ast.get_docstring(node) is not None:
                del node.body[0]
        return ast.dump(tree)
    a,b=pair('run.py')
    assert no_docstrings(a)==no_docstrings(b)
    stripped=lambda src:[line for line in src.splitlines() if not line.startswith(b'//')]
    assert stripped(pair('model.js')[0])==stripped(pair('model.js')[1])
    script=tmp_path/'run.py'
    script.write_bytes(b)
    subprocess.run([sys.executable,str(script)],cwd=tmp_path,check=True,capture_output=True)
    assert (tmp_path/'results.json').read_bytes()==(ROOT/PREFIX/'results.json').read_bytes()


def test_new_receipt_does_not_skip_any_reader_file():
    data=json.loads((ROOT/'tests/retail_grain_all_full_prose_hashes.json').read_text())['files']
    assert set(data)=={PREFIX+p for p in NAMES}
    for n in NAMES:
        old,new=pair(n)
        assert old!=new
        with pytest.raises(AssertionError):
            before_retail_grain_all_full_prose(ROOT,PREFIX+n,new+b'\n')
