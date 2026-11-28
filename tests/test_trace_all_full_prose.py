"""Keep exact numeric results, visual markup and the scientific scope."""
import json,re,yaml
from pathlib import Path
from html.parser import HTMLParser
from prose_preservation import before_trace_all_full_prose
ROOT=Path(__file__).resolve().parents[1]
P='papers/trace-verifier-brittleness/'
class Tags(HTMLParser):
    def __init__(self,s):super().__init__();self.e=[];self.feed(s)
    def handle_starttag(self,t,a):self.e.append((t,a))
    def handle_endtag(self,t):self.e.append((t,None))
def versions(n):
    p=P+n
    b=(ROOT/p).read_bytes()
    return before_trace_all_full_prose(ROOT,p,b),b

def test_numeric_and_widget_contracts():
    a,b=map(json.loads,versions('results.json'))
    assert a.pop('note')!=b.pop('note') and a==b
    assert len(b['synthetic'])==12
    a,b=[s.decode() for s in versions('experiment.md')]
    assert Tags(a).e==Tags(b).e
    assert a.split('<style>',1)[1].split('</style>',1)[0]==b.split('<style>',1)[1].split('</style>',1)[0]
    x,y=[re.search(r'const frames=(\[.*?\]);(.*?)</script>',s,re.S) for s in (a,b)]
    assert x and y and x[2]==y[2]
    m,n=[json.loads(p[1]) for p in (x,y)]
    assert len(m)==len(n)==12
    assert all(Tags(p).e==Tags(q).e for p,q in zip(m,n,strict=True))

def test_overview_reports_only_the_paper():
    a,b=map(yaml.safe_load,versions('lab.yaml'))
    for k in ('id','arxiv_id','urls','verification','status','figures','interactives'):
        assert a[k]==b[k]
    assert [r['cells'] for r in a['teaching_figures'][1]['rows']]==[r['cells'] for r in b['teaching_figures'][1]['rows']]
    s=b['sections']['overview']
    assert len(s.split('\n\n'))==2
    for w in ('25件','0.250','15〜36%','公開ベンチマーク','同じ記録を採点'):assert w in s
    assert not any(w in s for w in ('Lab','教材','在庫','<figure'))
    s=(ROOT/(P+'evidence.md')).read_text()
    for w in ('88課題','158課題','57%','95%と38%','7/8','6/8'):assert w in s
