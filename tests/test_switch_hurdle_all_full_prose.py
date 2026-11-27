"""Preserve exact historical wording, not just stable numerical results."""
from pathlib import Path
import ast, subprocess, sys, json
import yaml
import pytest
from prose_preservation import before_switch_hurdle_all_full_prose

ROOT=Path(__file__).resolve().parents[1]
P='papers/switch-hurdle-intermittent-demand/'
NAMES={'README.md','lab.yaml','mapping.md','method.md','results.json','run.py'}

def pair(n):
    p=P+n
    now=(ROOT/p).read_bytes()
    return before_switch_hurdle_all_full_prose(ROOT,p,now),now


def test_author_identity_headline_and_different_metrics():
    old,new=map(yaml.safe_load,pair('lab.yaml'))
    for k in ('arxiv_id','title','authors','urls','verification','status'):
        assert new[k]==old[k]
    for k in ('version','pdf_sha256','url'):
        assert new['source_review'][k]==old['source_review'][k]
    ov=new['sections']['overview']
    assert all(v in ov for v in ('MușatとCăbuz','過去56日','次の28日','WRMSSE','0.6307','0.6403','53.99%','55.60%','MASEはTFTの方が小さい','在庫費用'))
    assert all(v not in ov for v in ('Lab','教材','操作図','2.6667'))
    assert '各割合の分母はその数量区分の入力数' in new['sections']['evidence']
    for a,b in zip(old['teaching_figures'],new['teaching_figures'],strict=True):
        for k in ('source','locator','bars','maximum'):
            assert a.get(k)==b.get(k)
        assert [x['formula'] for x in a.get('steps',())]==[x['formula'] for x in b.get('steps',())]
        assert [x.get('cells') for x in a.get('rows',())]==[x.get('cells') for x in b.get('rows',())]


def test_regeneration_and_exact_distributions(tmp_path):
    old,new=map(json.loads,pair('results.json'))
    assert old.pop('note')!=new.pop('note') and old==new
    assert len(new['frames'])==4
    assert len({f['positive_mean'] for f in new['frames'][:3]})==1
    assert len({f['mean'] for f in new['frames'][:3]})==3
    def computation(v):
        t=ast.parse(v);del t.body[0]
        for n in ast.walk(t):
            if isinstance(n,ast.keyword) and n.arg=='note':
                n.value.value=''
        return ast.dump(t)
    a,b=pair('run.py')
    assert computation(a)==computation(b)
    script=tmp_path/'run.py'
    script.write_bytes(b)
    subprocess.run([sys.executable,str(script)],check=True)
    assert (tmp_path/'results.json').read_bytes()==pair('results.json')[1]


def test_exact_prior_for_every_reader_source():
    x=json.loads((ROOT/'tests/switch_hurdle_all_full_prose_hashes.json').read_text())['files']
    assert set(x)=={P+n for n in NAMES}
    for n in NAMES:
        old,now=pair(n)
        assert old!=now
        with pytest.raises(AssertionError):
            before_switch_hurdle_all_full_prose(ROOT,P+n,now+b'\n')
