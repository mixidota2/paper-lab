import ast
from collections import Counter
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import yaml

ROOT=Path(__file__).resolve().parents[1]
REL=Path('papers/storewide-shelf-decomposition')
BASE='f7793bc88ab49a347b43e74a9ff45e77bb6fe5ad'

def old(name):
    return subprocess.check_output(['git','show',f'{BASE}:{REL / name}'],cwd=ROOT)
def current(name):
    return (ROOT/REL/name).read_bytes()

def test_scope_facts_and_machine_artifacts_unchanged():
    a,b=(yaml.safe_load(raw('lab.yaml')) for raw in (old,current))
    assert b['status']=='draft'
    for key in ('id','doi','arxiv_id','submitted','year','title','authors','topics','urls','verdict','status','related_threads','figures','interactives','verification'):
        assert a[key]==b[key]
    for value in ('18条件','16条件','0.10〜0.29秒','候補を求める時間は含まない','利益は報告していない'):
        assert value in b['sections']['evidence']
    for section in ('method','executable_understanding','implementation','mapping','what_we_verified'):
        assert a['sections'][section]==b['sections'][section]
    for x,y in zip(a['teaching_figures'],b['teaching_figures'],strict=True):
        assert all(x[k]==y[k] for k in ('kind','id','after','locator','source'))
        for m,n in zip(x.get('steps',[]),y.get('steps',[]),strict=True):
            assert all(m[k]==n[k] for k in ('formula','formula_mathml'))
    assert old('model.js')==current('model.js')
    p,q=(json.loads(raw('results.json')) for raw in (old,current))
    assert p.pop('note')!=q.pop('note')
    assert p==q
    def parse(raw):
        t=ast.parse(raw('run.py'))
        notes=[n for n in ast.walk(t) if isinstance(n,ast.keyword) and n.arg=='note']
        assert len(notes)==1 and isinstance(notes[0].value,ast.Constant)
        notes[0].value.value=''
        return ast.dump(t)
    assert parse(old)==parse(current)

def test_existing_links_and_html_operational_structure_unchanged():
    for f in ('README.md','method.md','experiment.md','implementation.md','mapping.md','validation.md','lab.yaml'):
        anchors=lambda raw:Counter(re.findall(rb'https?://[^\s\)>,\x27"]+',raw(f)))
        assert anchors(old)==anchors(current),f
    class Structure(HTMLParser):
        def __init__(self,body):
            super().__init__()
            self.nodes=[]
            self.feed(body.decode())
        def handle_starttag(self,tag,attrs):
            self.nodes.append((tag,tuple((k,v) for k,v in attrs if k not in ('title','aria-label'))))
        def handle_endtag(self,tag):
            self.nodes.append(('/'+tag,()))
    html=lambda raw:Structure(raw('interactive.html')).nodes
    assert html(old)==html(current)
    for literal in ('id="summary"','noscript','150.780593'):
        assert literal.encode() in current('interactive.html')
    for literal in ('実行不能','optimal_face_count','selected_detail_widths','data-cap','shelf-synthetic-results.json'):
        assert literal.encode() in current('interactive.js')

def test_exact_rewrite_manifest_matches_public_base_input():
    from prose_preservation import storewide_full_rewrite_hash
    manifest=json.loads((ROOT/'tests/storewide_full_rewrite_hashes.json').read_text())['files']
    assert len(manifest)==11
    for path, rec in manifest.items():
        f=Path(path).name
        for alg,h in [('sha256',lambda x:hashlib.sha256(x).hexdigest()),('blob',lambda x:hashlib.sha1(b'blob '+str(len(x)).encode()+bytes([0])+x).hexdigest())]:
            assert h(old(f))==rec['before_'+alg]
            assert h(current(f))==rec['after_'+alg]
            assert storewide_full_rewrite_hash(ROOT,path,h(old(f)),alg)==h(current(f))
