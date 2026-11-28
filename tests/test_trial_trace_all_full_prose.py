"""Verify the new prose and keep the deterministic numbers and markup unchanged."""
from pathlib import Path
from html.parser import HTMLParser
import json,subprocess,sys,yaml
from prose_preservation import before_trial_trace_all_full_prose
ROOT=Path(__file__).resolve().parents[1]
P='papers/trial-by-trace-evidence-boundaries/'
def versions(n):
    path=P+n
    b=(ROOT/path).read_bytes()
    return before_trial_trace_all_full_prose(ROOT,path,b),b

class Tags(HTMLParser):
    def __init__(self,s):super().__init__();self.shape=[];self.feed(s)
    def handle_starttag(self,t,a):self.shape.append((t,[(k,v) for k,v in a if k!='aria-label']))
    def handle_endtag(self,t):self.shape.append((t,None))

def test_same_calculation_and_controls(tmp_path):
    old,new=map(json.loads,versions('results.json'))
    assert old['note']!=new['note']
    assert old['cases']==new['cases'] and len(old['cases'])==64
    for name in ('run.py','model.js','ui.js','test.cjs'):
        (tmp_path/name).write_bytes(versions(name)[1])
    subprocess.run([sys.executable,str(tmp_path/'run.py')],check=True,capture_output=True)
    assert (tmp_path/'results.json').read_bytes()==versions('results.json')[1]
    a,b=[x.decode() for x in versions('index.html')]
    assert Tags(a).shape==Tags(b).shape
    assert a.split('<style>')[1].split('</style>')[0]==b.split('<style>')[1].split('</style>')[0]

def test_paper_overview_preserves_denominators_and_uncertainty():
    a,b=map(yaml.safe_load,versions('lab.yaml'))
    for k in ('id','arxiv_id','urls','verification','status','interactives','figures'):
        assert a[k]==b[k]
    assert [r['formula'] for r in a['teaching_figures'][1]['steps']]==[r['formula'] for r in b['teaching_figures'][1]['steps']]
    s=b['sections']['overview']
    assert len(s.split('\n\n'))==2
    for n in ('4種類','9種類','95課題','3,420回','1,351回','286回','1,065回','31.1%','証拠が見つからない'):
        assert n in s
    assert not any(t in s for t in ('Lab','教材','64条件','<figure','チェック欄'))
    assert 1351-286==1065 and round(1065/3420*100,1)==31.1
