from pathlib import Path
from decimal import Decimal as D
import json, runpy, shutil, subprocess,sys
import yaml
from prose_preservation import before_snaplgr_full_prose

R=Path(__file__).resolve().parents[1]
P='papers/snaplgr-snapchat/'

def both(name):
    a=(R/(P+name)).read_bytes()
    return a,before_snaplgr_full_prose(R,P+name,a)

def test_snaplgr_author_overview_values_and_toy_are_preserved(tmp_path):
    a,b=map(yaml.safe_load,both('lab.yaml'))
    assert a['sections']['overview']==b['sections']['overview']
    assert a['sections']['overview'] in (R/(P+'README.md')).read_text()
    assert a['source_review']==b['source_review'] and a['verification']==b['verification']
    assert [x['value'] for x in a['teaching_figures'][0]['bars']]==[x['value'] for x in b['teaching_figures'][0]['bars']]
    assert [x['cells'][0] for x in a['teaching_figures'][1]['rows']]==[x['cells'][0] for x in b['teaching_figures'][1]['rows']]
    a,b=map(json.loads,both('results.json'))
    assert a.pop('note')!=b.pop('note')
    assert a['experiments'][0].pop('name')!=b['experiments'][0].pop('name')
    assert a==b
    p=tmp_path/'run.py'
    shutil.copyfile(R/(P+'run.py'),p)
    subprocess.run([sys.executable,str(p)],check=True,capture_output=True)
    assert (tmp_path/'results.json').read_bytes()==(R/(P+'results.json')).read_bytes()

def test_snaplgr_metric_and_batch_calendar_boundaries():
    e=yaml.safe_load((R/(P+'lab.yaml')).read_text())['sections']['evidence']
    assert all(v in e for v in ['2.765%','10.98%','6.486ポイント','0.13ポイント','約1.49倍','日次生成の処理量'])
    assert D('11.11')-D('4.624')==D('6.486')
    assert round(D('45.7')/D('30.7'),2)==D('1.49')
    method=(R/(P+'method.md')).read_text()
    assert all(v in method for v in ['SFTによる更新は1時間に1回','候補生成は日次','要求のたびに生成モデルを動かすわけではない'])
