"""Track reviewed prose and preserve the exact forecast-critic executable results."""
from hashlib import sha1, sha256
import json
from pathlib import Path
import re

import pytest
import yaml

from prose_preservation import before_forecast_critic_all_full_prose, before_forecast_critic_full_rewrite, forecast_critic_full_rewrite_hash

ROOT = Path(__file__).resolve().parents[1]
P = 'papers/forecast-critic/'


def archived(path):
    return before_forecast_critic_all_full_prose(ROOT,path,(ROOT/path).read_bytes())

def identity(raw):
    return {'sha256':sha256(raw).hexdigest(),
            'blob':sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()}


def test_explicit_forecast_critic_prose_transitions():
    rows = json.loads((ROOT/'tests/forecast_critic_full_rewrite_hashes.json').read_text())['files']
    assert set(rows) == {P+n for n in ('lab.yaml','method.md','mapping.md')}
    for path,row in rows.items():
        updated=before_forecast_critic_all_full_prose(ROOT,path,(ROOT/path).read_bytes())
        previous=before_forecast_critic_full_rewrite(ROOT,path,updated)
        for alg in ('sha256','blob'):
            a,b=identity(previous)[alg],identity(updated)[alg]
            assert row['before_'+alg]==a and row['after_'+alg]==b
            assert forecast_critic_full_rewrite_hash(ROOT,path,a,alg)==b
            for mistaken in (b,'0'*len(b)):
                with pytest.raises(AssertionError):
                    forecast_critic_full_rewrite_hash(ROOT,path,mistaken,alg)
        with pytest.raises(AssertionError):
            before_forecast_critic_full_rewrite(ROOT,path,updated+b'\n')


def test_forecast_critic_exact_original_overview_figure_math_and_toy():
    path=P+'lab.yaml'
    after=archived(path)
    before=before_forecast_critic_full_rewrite(ROOT,path,after)
    rx=re.compile(rb'^  overview:.*?(?=^  problem:)',re.M|re.S)
    assert len(rx.findall(after))==1 and rx.findall(after)==rx.findall(before)
    old,new=map(yaml.safe_load,(before,after))
    for name in ('urls','source_review','title','authors','verification','interactives','related_threads'):
        assert old[name]==new[name]
    for a,b in zip(old['teaching_figures'],new['teaching_figures'],strict=True):
        for key in ('kind','id','source','after','locator'):
            assert a[key]==b[key]
        assert [v['formula'] for v in a.get('steps',[])]==[v['formula'] for v in b.get('steps',[])]
    evidence=new['sections']['evidence']
    for anchor in ('0.88','0.97','0.84','sCRPSの中央値','少なくとも10%','約2%から約40%','監視を導入すれば誤差が10%改善するという結果ではない'):
        assert anchor in evidence,anchor
    for name,blob in (('run.py','4a65d9e54459482771300c8d4ee50f016d850a0f'),
                      ('results.json','c71ecf9cf818991ebe57325655dc7dead219b0a6')):
        assert identity(archived(P+name))['blob']==blob
    r=re.compile(rb'\]\(([^)]*)\)')
    for name in ('lab.yaml','method.md','mapping.md'):
        path=P+name
        after=archived(path)
        before=before_forecast_critic_full_rewrite(ROOT,path,after)
        assert sorted(r.findall(before))==sorted(r.findall(after))
