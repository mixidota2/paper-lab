"""Tie reader copy to the unchanged synthetic, regenerated values."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import pytest
import yaml

from prose_preservation import before_series_reader_assets, series_reader_assets_rows, series_reader_assets_hash

ROOT=Path(__file__).resolve().parents[1]
P='papers/series-wise-validation/'

def pair(name):
    path=P+name
    current=(ROOT/path).read_bytes()
    return before_series_reader_assets(ROOT,path,current),current

def test_exact_reader_transitions_preserve_all_topic_assets():
    files={'README.md','evidence.md','experiment.md','interactive.html','interactive.js','lab.yaml',
           'mapping.md','method.md','model.js','results.json','run.py','table3.json'}
    rows=series_reader_assets_rows(ROOT)
    assert rows.keys()=={P+n for n in files}
    edited=set()
    for n in files:
        before,after=pair(n)
        p=P+n
        row=rows[p]
        assert bool(row['prior_spans'])==(before!=after)
        if before!=after:
            edited.add(n)
        for label,b in (('before',before),('after',after)):
            assert hashlib.sha256(b).hexdigest()==row[label+'_sha256']
            assert hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()==row[label+'_blob']
        for alg in ('sha256','blob'):
            assert series_reader_assets_hash(ROOT,p,row['before_'+alg],alg)==row['after_'+alg]
        with pytest.raises(AssertionError):
            before_series_reader_assets(ROOT,p,after+b'\n')
    assert edited=={'lab.yaml','README.md','mapping.md','evidence.md'}

def test_historical_reverse_and_forward_receipts_keep_exact_order():
    from prose_preservation import (
        before_series_full_prose, series_full_prose_hash, reading_prose_hash,
        paper_overview_rewrite_hash, yomiyasu_hash,
    )
    full=json.loads((ROOT/'tests/series_full_prose_hashes.json').read_text())['files']
    overview=json.loads((ROOT/'tests/paper_overview_hashes.json').read_text())['files']
    earlier=json.loads((ROOT/'tests/yomiyasu_revision_hashes.json').read_text())['files']
    preliminary=json.loads((ROOT/'tests/reading_prose_revision_hashes.json').read_text())['files']
    assert full.keys()==set(series_reader_assets_rows(ROOT))-{P+'results.json'}
    for path,row in full.items():
        filename=path[len(P):]
        previous,current=pair(filename)
        oldest=before_series_full_prose(ROOT,path,previous)
        for algorithm,identity in (
            ('sha256',lambda b: hashlib.sha256(b).hexdigest()),
            ('blob',lambda b: hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()),
        ):
            assert identity(oldest)==row['before'][algorithm]
            assert identity(previous)==row['after'][algorithm]
            assert series_full_prose_hash(ROOT,path,row['before'][algorithm],algorithm)==row['after'][algorithm]
            # Start ahead of both full passes, using the historical overview and global rewrite where present.
            if path in overview:
                start=overview[path]['before_'+algorithm]
                assert paper_overview_rewrite_hash(ROOT,path,start,algorithm)==row['before'][algorithm]
                assert preliminary[path]['after_'+algorithm]==start
                start=preliminary[path]['before_'+algorithm]
            else:
                start=row['before'][algorithm]
            assert reading_prose_hash(ROOT,path,start,algorithm)==identity(current)
            if path in earlier:
                assert yomiyasu_hash(ROOT,path,earlier[path]['before_'+algorithm],algorithm)==identity(current)
            with pytest.raises(AssertionError):
                reading_prose_hash(ROOT,path,'0'*len(start),algorithm)
        with pytest.raises(AssertionError):
            before_series_full_prose(ROOT,path,previous+b'\n')

def test_guide_matches_unchanged_results_and_current_article(tmp_path):
    a,b=map(yaml.safe_load,pair('lab.yaml'))
    assert {k for k in a if a[k]!=b[k]}=={'summary','sections'}
    a,b=a['sections'],b['sections']
    assert {k for k in a if a[k]!=b[k]}=={'overview'}
    assert all(v in b['overview'] for v in ('約3割の系列','全系列で','その時点までの観測値','0.857','0.883','0.859','0.849','最も近い値'))
    assert 'Lab' not in b['overview']
    guide=pair('mapping.md')[1].decode().split('## 結果ファイルの読み方',1)[1]
    out=json.loads(pair('results.json')[1])
    assert all(f'`{k}`' in guide for k in out)
    assert len(out['toy']['records'])==50
    assert sum(len(r['errors']) for r in out['toy']['records'])==200
    for method,row in out['table3_checks'].items():
        assert row['dataset_count']==11
        assert out['without_weather'][method]['dataset_count']==10
    outpath=tmp_path/'results.json'
    subprocess.run([sys.executable,str(ROOT/P/'run.py'),'--out',str(outpath)],check=True,capture_output=True)
    assert outpath.read_bytes()==pair('results.json')[0]==pair('results.json')[1]
