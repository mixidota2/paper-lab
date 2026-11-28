from pathlib import Path
import ast
import json
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import yaml
from overview_predicate_revisions import before_overview_predicate_revision
from prose_preservation import before_oxygenrec_full_prose

ROOT=Path(__file__).resolve().parents[1]
P='papers/oxygenrec-v2-idgr/'
def files(name):
    current=(ROOT/(P+name)).read_bytes()
    return current,before_oxygenrec_full_prose(ROOT,P+name,current)

def test_oxygenrec_primary_overview_and_reported_figures_preserved():
    new,old=map(yaml.safe_load,files('lab.yaml'))
    earlier = yaml.safe_load(before_overview_predicate_revision(ROOT, P+'lab.yaml', files('lab.yaml')[0]))
    assert earlier['sections']['overview']==old['sections']['overview']
    assert new['sections']['overview'] in (ROOT/P/'README.md').read_text()
    for key in ('source_review','verification','urls'):
        assert new[key]==old[key]
    assert [t['id'] for t in new['teaching_figures']]==[t['id'] for t in old['teaching_figures']]
    assert [s['formula'] for s in new['teaching_figures'][1]['steps']]==[s['formula'] for s in old['teaching_figures'][1]['steps']]
    for idx in (2,3):
        assert [r['cells'] for r in new['teaching_figures'][idx]['rows']]==[r['cells'] for r in old['teaching_figures'][idx]['rows']]
    evidence=new['sections']['evidence']
    assert all(v in evidence for v in ('一次資料','33.76%','33.89%','p=0.23','事前学習','追加学習'))
    assert '本文の§5では30億、付録G.2では7億' in new['sections']['what_we_did_not_verify']
    assert '教師あり学習の損失も加える' in new['sections']['implementation']

def test_oxygenrec_same_arithmetic_and_exact_download(tmp_path):
    def content(raw):
        data=json.loads(raw)
        data.pop('note')
        data['explorer'].pop('label')
        for r in data['explorer']['frames']:
            r.pop('note')
        return data
    current,old=files('results.json')
    assert content(current)==content(old)
    def code_structure(raw):
        tree=ast.parse(raw)
        tree.body=tree.body[1:]
        # Only presentation constants can change; the full numeric AST is compared.
        for node in ast.walk(tree):
            if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='names' for t in node.targets):
                assert len(node.value.elts)==3 and all(isinstance(e,ast.Constant) and isinstance(e.value,str) for e in node.value.elts)
                node.value=ast.Constant('display-names')
            if isinstance(node,ast.Dict):
                for i,k in enumerate(node.keys):
                    if isinstance(k,ast.Constant) and k.value in ('note','label'):
                        v=node.values[i]
                        if isinstance(v,ast.JoinedStr) and k.value=='label':
                            continue  # group/bar index label formats in the original are unchanged
                        node.values[i]=ast.Constant('display-description')
        return ast.dump(tree)
    assert code_structure(files('run.py')[0])==code_structure(files('run.py')[1])
    run=tmp_path/'run.py'
    shutil.copyfile(ROOT/P/'run.py',run)
    subprocess.run([sys.executable,str(run)],check=True)
    assert (tmp_path/'results.json').read_bytes()==current

def test_oxygenrec_teacher_figure_fits_and_describes_no_inference_future():
    data=ET.fromstring(files('figures/privilege.svg')[0])
    assert data.get('viewBox')=='0 0 440 470'
    ns='{http://www.w3.org/2000/svg}'
    assert '配信時には将来の行動を使わない' in data.find(ns+'desc').text
    for node in data.findall('.//'+ns+'text'):
        width=sum(1 if ord(c)>255 else .59 for c in node.text)*int(node.get('font-size'))
        assert int(node.get('x'))+width<440
