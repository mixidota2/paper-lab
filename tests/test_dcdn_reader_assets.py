"""The DCDN reader prose changes without modifying any test inputs or outputs."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from prose_preservation import before_dcdn_reader_assets, dcdn_reader_assets_rows, dcdn_reader_assets_hash

ROOT=Path(__file__).resolve().parents[1]
P='papers/deep-cross-division/'


def contents(name):
    path=P+name
    data=(ROOT/path).read_bytes()
    return before_dcdn_reader_assets(ROOT,path,data),data


def test_dcdn_reader_assets_require_exact_transition():
    names=('README.md','evidence.md','experiment.md','interactive.html','interactive.js','lab.yaml','mapping.md','method.md','results.json','run.py','test.cjs','widget.html')
    rows=dcdn_reader_assets_rows(ROOT)
    assert rows.keys()=={P+n for n in names}
    for name in names:
        before,after=contents(name)
        path=P+name
        row=rows[path]
        for which,data in (('before',before),('after',after)):
            assert hashlib.sha256(data).hexdigest()==row[which+'_sha256']
            assert hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()==row[which+'_blob']
        for alg in ('sha256','blob'):
            assert dcdn_reader_assets_hash(ROOT,path,row['before_'+alg],alg)==row['after_'+alg]
            if row['prior_spans']:
                with pytest.raises(AssertionError): dcdn_reader_assets_hash(ROOT,path,'0'*len(row['before_'+alg]),alg)
        with pytest.raises(AssertionError): before_dcdn_reader_assets(ROOT,path,after+b'\n')


def test_dcdn_invariants(tmp_path):
    for name in ('README.md','evidence.md','experiment.md','interactive.html','interactive.js','method.md','results.json','run.py','test.cjs','widget.html'):
        assert len(set(contents(name)))==1
    script=tmp_path/'run.py'
    script.write_bytes(contents('run.py')[1])
    for _ in range(2):
        subprocess.run([sys.executable,'-I','-S',str(script)],capture_output=True,check=True)
        assert (tmp_path/'results.json').read_bytes()==contents('results.json')[1]
    old,new=map(yaml.safe_load,contents('lab.yaml'))
    assert {k for k in old if old[k]!=new[k]}=={'sections'}
    assert {k for k in old['sections'] if old['sections'][k]!=new['sections'][k]}=={'overview'}
    overview=new['sections']['overview']
    for clue in ('両方のモデルに渡す','どちらにも渡さない','4つの評価対象','14日間','40.1%','3.25%','16.26%','0.33%','モデルと入力を同時に変えた効果'):
        assert clue in overview
    assert 'Lab' not in overview and '教材' not in overview
    old,new=(text.decode() for text in contents('mapping.md'))
    assert new.split('\n## 配布ファイルの読み方',1)[0]==old
    assert all(key in new for key in ('toy.fits','table5.rows','5152','0.5152','実ブラウザー'))


def test_exact_overview_and_earlier_full_rewrite_compose_with_new_stage():
    from prose_preservation import (
        reading_prose_hash,revised_hash,yomiyasu_hash,paper_overview_rewrite_hash,
        dcdn_full_prose_hash,
    )
    overview=json.loads((ROOT/'tests/paper_overview_hashes.json').read_text())
    ov=overview['files']|overview['mirrored']
    first=json.loads((ROOT/'tests/dcdn_full_prose_hashes.json').read_text())['files']
    reading=json.loads((ROOT/'tests/reading_prose_revision_hashes.json').read_text())['files']
    yom=json.loads((ROOT/'tests/yomiyasu_revision_hashes.json').read_text())['files']
    orig=json.loads((ROOT/'tests/prose_revision_hashes.json').read_text())['files']
    for p,end in dcdn_reader_assets_rows(ROOT).items():
        for alg in ('sha256','blob'):
            before='before_'+alg
            after='after_'+alg
            start=end[before]
            if p in first:
                assert dcdn_full_prose_hash(ROOT,p,first[p][before],alg)==start
                start=first[p][before]
            if p in ov:
                assert paper_overview_rewrite_hash(ROOT,p,ov[p][before],alg)==start
                start=ov[p][before]
            if p in reading:
                assert reading[p][after]==start
                start=reading[p][before]
            assert reading_prose_hash(ROOT,p,start,alg)==end[after]
            if p in yom:
                assert yomiyasu_hash(ROOT,p,yom[p][before],alg)==end[after]
            if p in orig:
                assert revised_hash(ROOT,p,orig[p][before],alg)==end[after]
            if end['prior_spans']:
                with pytest.raises(AssertionError):
                    reading_prose_hash(ROOT,p,'0'*len(start),alg)
