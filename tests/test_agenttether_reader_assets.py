"""The AgentTether reader prose changes without modifying any test inputs or outputs."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from prose_preservation import before_agenttether_reader_assets, agenttether_reader_assets_rows, agenttether_reader_assets_hash

ROOT=Path(__file__).resolve().parents[1]
P='papers/agenttether-repair/'


def contents(name):
    path=P+name
    data=(ROOT/path).read_bytes()
    return before_agenttether_reader_assets(ROOT,path,data),data


def test_agenttether_reader_assets_require_exact_transition():
    names=('lab.yaml','method.md','results.json','run.py','figures/ctg.svg','figures/guards.svg')
    rows=agenttether_reader_assets_rows(ROOT)
    assert rows.keys()=={P+n for n in names}
    for name in names:
        before,after=contents(name)
        path=P+name
        row=rows[path]
        for which,data in (('before',before),('after',after)):
            assert hashlib.sha256(data).hexdigest()==row[which+'_sha256']
            assert hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()==row[which+'_blob']
        for alg in ('sha256','blob'):
            assert agenttether_reader_assets_hash(ROOT,path,row['before_'+alg],alg)==row['after_'+alg]
            if row['prior_spans']:
                with pytest.raises(AssertionError): agenttether_reader_assets_hash(ROOT,path,'0'*len(row['before_'+alg]),alg)
        with pytest.raises(AssertionError): before_agenttether_reader_assets(ROOT,path,after+b'\n')


def test_agenttether_invariants(tmp_path):
    for name in ('method.md','run.py','results.json','figures/ctg.svg','figures/guards.svg'):
        assert len(set(contents(name)))==1
    script=tmp_path/'run.py'
    script.write_bytes(contents('run.py')[1])
    for _ in range(2):
        subprocess.run([sys.executable,'-I','-S',str(script)],capture_output=True,check=True)
        assert (tmp_path/'results.json').read_bytes()==contents('results.json')[1]
    old,new=map(yaml.safe_load,contents('lab.yaml'))
    assert {k for k in old if old[k]!=new[k]}=={'sections'}
    assert {k for k in old['sections'] if old['sections'][k]!=new['sections'][k]}=={'overview','evidence','mapping'}
    overview=new['sections']['overview']
    for clue in ('最初に失敗した83件','最大3回','39件','49件','13件','失敗した課題も3件','全課題に対する成功率ではありません'):
        assert clue in overview
    assert 'Lab' not in overview and '教材' not in overview
    for clue in ('17.88分','20.88分','介入を何回に抑えれば成功しやすいかを試した結果ではありません'):
        assert clue in new['sections']['evidence']
    for clue in ('localization','adherence_proxy','guards'):
        assert clue in new['sections']['mapping']


def test_legacy_registration_sources_compose():
    from prose_preservation import revised_hash
    for filename,key in [('main_105_catalog.json','source_hashes'),('main_107_catalog.json','source_hashes'),('trial_trace_baseline.json','sources')]:
        data=json.loads((ROOT/'tests'/filename).read_text())[key]
        for path,prior in data.items():
            if path.startswith(P):
                assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==revised_hash(ROOT,path,prior)


def test_exact_overview_and_earlier_full_rewrite_compose_with_new_stage():
    from prose_preservation import (
        reading_prose_hash,revised_hash,yomiyasu_hash,paper_overview_rewrite_hash,
        agenttether_full_prose_hash,
    )
    overview=json.loads((ROOT/'tests/paper_overview_hashes.json').read_text())
    ov=overview['files']|overview['mirrored']
    first=json.loads((ROOT/'tests/agenttether_full_prose_hashes.json').read_text())['files']
    yom=json.loads((ROOT/'tests/yomiyasu_revision_hashes.json').read_text())['files']
    orig=json.loads((ROOT/'tests/prose_revision_hashes.json').read_text())['files']
    for p,end in agenttether_reader_assets_rows(ROOT).items():
        for alg in ('sha256','blob'):
            before='before_'+alg
            after='after_'+alg
            start=end[before]
            if p in first:
                assert agenttether_full_prose_hash(ROOT,p,first[p]['before'][alg],alg)==start
                start=first[p]['before'][alg]
            if p in ov:
                assert paper_overview_rewrite_hash(ROOT,p,ov[p][before],alg)==start
                start=ov[p][before]
            assert reading_prose_hash(ROOT,p,start,alg)==end[after]
            if p in yom:
                assert yomiyasu_hash(ROOT,p,yom[p][before],alg)==end[after]
            if p in orig:
                assert revised_hash(ROOT,p,orig[p][before],alg)==end[after]
            if end['prior_spans']:
                with pytest.raises(AssertionError):
                    reading_prose_hash(ROOT,p,'0'*len(start),alg)
