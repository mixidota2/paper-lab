"""Keep the paper-only summary, numeric results and neighboring widgets independent."""
import ast
import json
from pathlib import Path
import re
import subprocess
import sys

import pytest
import yaml
from prose_preservation import before_sim2real_all_full_prose

ROOT = Path(__file__).resolve().parents[1]
P = 'papers/sim2real-policy-conditioned-inbound-forecast/'
RENDERER = 'paper_lab/batch08.py'
FILES = {P + x for x in ('README.md', 'lab.yaml', 'mapping.md', 'method.md', 'results.json', 'run.py')} | {RENDERER}


def pair(p):
    now = (ROOT / p).read_bytes()
    return before_sim2real_all_full_prose(ROOT, p, now), now


def test_every_reader_source_and_original_is_authenticated():
    proof = json.loads((ROOT / 'tests/sim2real_all_full_prose_hashes.json').read_text())['files']
    assert set(proof) == FILES
    for p in FILES:
        old, new = pair(p)
        assert old != new
        with pytest.raises(AssertionError):
            before_sim2real_all_full_prose(ROOT, p, new + b'\n')


def test_abstract_is_about_paper_and_holds_evidence_boundaries():
    old,new = map(yaml.safe_load, pair(P + 'lab.yaml'))
    for k in ('id','arxiv_id','authors','urls','verification','status'):
        assert new[k] == old[k]
    ov = new['sections']['overview']
    assert all(x in ov for x in ('Wangら','同じ構造','新ルール導入後の入荷実績',
                                 '1.2〜3.1ポイント','12.5〜18.7ポイント','9.4%から6.9%',
                                 '一つのシミュレーター','欠品'))
    assert all(x not in ov for x in ('Lab','人工実験','操作図','28.054'))
    assert ov in (ROOT / (P + 'README.md')).read_text()
    assert '差に対する区間ではありません' in new['sections']['evidence']
    assert '著者らが実際の導入事例で得た、補正前の改善は再現できませんでした' in new['sections']['results']
    for a,b in zip(old['teaching_figures'], new['teaching_figures'], strict=True):
        for k in ('id','kind','locator','source'):
            assert a[k]==b[k]
        assert [v['formula'] for v in a.get('steps',())]==[v['formula'] for v in b.get('steps',())]


def normalized_results(value):
    value.pop('note')
    value['experiments'][0].pop('name')
    return value


def test_only_prose_changed_and_current_runner_matches_previous(tmp_path):
    def computation(code):
        t=ast.parse(code); del t.body[0]
        for node in ast.walk(t):
            if isinstance(node,ast.Dict):
                for k,v in zip(node.keys,node.values,strict=True):
                    if isinstance(k,ast.Constant) and k.value in ('note','name'):
                        assert isinstance(v,ast.Constant)
                        v.value=''
        return ast.dump(t)
    a,b=pair(P+'run.py')
    assert computation(a)==computation(b)
    assert len({json.dumps(normalized_results(json.loads(v))) for v in pair(P+'results.json')})==1
    generated=[]
    for source in (a,b):
        script=tmp_path/'run.py'
        script.write_bytes(source)
        subprocess.run([sys.executable,str(script)],check=True)
        generated.append(normalized_results(json.loads((tmp_path/'results.json').read_bytes())))
    assert generated[0]==generated[1]


def test_only_sim2real_widget_changed_and_event_hooks_stayed():
    a,b=pair(RENDERER)
    def dissect(v):
        first,after=v.split(b"SIM = r'''",1)
        own,last=after.split(b"HARNESS = r'''",1)
        return (first,last),own
    oa,owna=dissect(a)
    ob,ownb=dissect(b)
    assert oa==ob
    def selectors(v):
        return sorted(re.findall(rb'data-[a-z-]+',v))
    assert selectors(owna)==selectors(ownb)
    assert b'data-cost' in ownb and b'data-study' in ownb and b'data-week' in ownb
