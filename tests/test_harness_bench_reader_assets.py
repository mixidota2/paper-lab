"""The Harness-Bench reader prose changes without modifying any test inputs or outputs."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from prose_preservation import before_harness_bench_reader_assets, harness_bench_reader_assets_rows, harness_bench_reader_assets_hash

ROOT=Path(__file__).resolve().parents[1]
P='papers/harness-bench/'


def contents(name):
    path=P+name
    data=(ROOT/path).read_bytes()
    return before_harness_bench_reader_assets(ROOT,path,data),data


def test_harness_bench_reader_assets_require_exact_transition():
    names=('lab.yaml','method.md','results.json','run.py','figures/failures.svg','figures/gap.svg','figures/unit.svg')
    rows=harness_bench_reader_assets_rows(ROOT)
    assert rows.keys()=={P+n for n in names}
    for name in names:
        before,after=contents(name)
        path=P+name
        row=rows[path]
        for which,data in (('before',before),('after',after)):
            assert hashlib.sha256(data).hexdigest()==row[which+'_sha256']
            assert hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()==row[which+'_blob']
        for alg in ('sha256','blob'):
            assert harness_bench_reader_assets_hash(ROOT,path,row['before_'+alg],alg)==row['after_'+alg]
            if row['prior_spans']:
                with pytest.raises(AssertionError): harness_bench_reader_assets_hash(ROOT,path,'0'*len(row['before_'+alg]),alg)
        with pytest.raises(AssertionError): before_harness_bench_reader_assets(ROOT,path,after+b'\n')


def test_harness_bench_invariants(tmp_path):
    from xml.etree import ElementTree as ET
    for name in ('method.md','run.py','results.json','figures/failures.svg','figures/unit.svg'):
        assert len(set(contents(name)))==1
    before,after=[ET.fromstring(x) for x in contents('figures/gap.svg')]
    assert [(e.tag,e.attrib) for e in before.iter()]==[(e.tag,e.attrib) for e in after.iter()]
    assert [e.text for e in after.iter() if e.tag.endswith('}text')]==[
        'ハーネスの違いと完了度（実測値ではありません）','ハーネス','完了度']
    package=tmp_path/'papers'
    script=package/'harness-bench'/'run.py'
    script.parent.mkdir(parents=True)
    script.write_bytes(contents('run.py')[1])
    (package/'_toy_common.py').write_bytes((ROOT/'papers/_toy_common.py').read_bytes())
    for _ in range(2):
        subprocess.run([sys.executable,'-I','-S',str(script)],capture_output=True,check=True)
        assert script.with_name('results.json').read_bytes()==contents('results.json')[1]
    old,new=map(yaml.safe_load,contents('lab.yaml'))
    assert {k for k in old if old[k]!=new[k]}=={'sections'}
    assert {k for k in old['sections'] if old['sections'][k]!=new['sections'][k]}=={'overview','mapping'}
    overview=new['sections']['overview']
    for clue in ('106課題と8モデル','76.2点','52.4点','23.8ポイント','同じ外部の言語モデル','一つの機能だけの効果でもありません','標準のGPT-5.4構成'):
        assert clue in overview
    assert 'Lab' not in overview and '教材' not in overview
    assert 'explorer.frames' in new['sections']['mapping']


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
        harness_icegr_full_rewrite_hash,
    )
    overview=json.loads((ROOT/'tests/paper_overview_hashes.json').read_text())
    ov=overview['files']|overview['mirrored']
    first=json.loads((ROOT/'tests/harness_icegr_full_rewrite_hashes.json').read_text())['files']
    yom=json.loads((ROOT/'tests/yomiyasu_revision_hashes.json').read_text())['files']
    orig=json.loads((ROOT/'tests/prose_revision_hashes.json').read_text())['files']
    for p,end in harness_bench_reader_assets_rows(ROOT).items():
        for alg in ('sha256','blob'):
            before='before_'+alg
            after='after_'+alg
            start=end[before]
            if p in first:
                assert harness_icegr_full_rewrite_hash(ROOT,p,first[p][before],alg)==start
                start=first[p][before]
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
