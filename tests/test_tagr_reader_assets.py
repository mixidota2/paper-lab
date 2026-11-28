"""Check the article rewrite without weakening frozen TAGR source identities."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from prose_preservation import (
    before_tagr_reader_assets,tagr_reader_assets_rows,tagr_reader_assets_hash,
    before_tagr_all_full_prose,tagr_all_full_prose_hash,arxiv_versioned_overview_hash,
    revised_hash,yomiyasu_hash,
)

ROOT=Path(__file__).resolve().parents[1]
P='papers/tagr-live-sid/'

def ident(data):
    return {'sha256':hashlib.sha256(data).hexdigest(),'blob':hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()}

def rows(file):
    return json.loads((ROOT/'tests'/file).read_text())['files']

def test_tagr_reader_assets_only_change_one_exact_yaml_source():
    receipts=tagr_reader_assets_rows(ROOT)
    assert receipts.keys()=={P+n for n in ('lab.yaml','method.md','run.py','results.json','figures/clocks.svg','figures/collision.svg')}
    earlier=rows('tagr_all_full_prose_hashes.json')
    arxiv=rows('arxiv_versioned_overview_hashes.json')
    revision=rows('prose_revision_hashes.json')
    yomi=rows('yomiyasu_revision_hashes.json')
    for p,row in receipts.items():
        final=(ROOT/p).read_bytes()
        old=before_tagr_reader_assets(ROOT,p,final)
        assert bool(row['prior_spans'])==(old!=final)==(p==P+'lab.yaml')
        for alg,digest in ident(final).items():
            before,after='before_'+alg,'after_'+alg
            assert digest==row[after] and ident(old)[alg]==row[before]
            assert tagr_reader_assets_hash(ROOT,p,row[before],alg)==row[after]
            if p in earlier:
                last=earlier[p]
                assert last['after'][alg]==row[before]
                assert tagr_all_full_prose_hash(ROOT,p,last['before'][alg],alg)==row[before]
                assert ident(before_tagr_all_full_prose(ROOT,p,old))[alg]==last['before'][alg]
            if p in arxiv:
                assert arxiv_versioned_overview_hash(ROOT,p,arxiv[p][before],alg)==earlier[p]['before'][alg]
            if p in revision:
                assert revised_hash(ROOT,p,revision[p][before],alg)==digest
            if p in yomi:
                assert yomiyasu_hash(ROOT,p,yomi[p][before],alg)==digest
            if row['prior_spans']:
                with pytest.raises(AssertionError):
                    tagr_reader_assets_hash(ROOT,p,'0'*len(digest),alg)
        with pytest.raises(AssertionError):
            before_tagr_reader_assets(ROOT,p,final+b'\n')

def test_article_guidance_and_downloaded_results_agree(tmp_path):
    path=P+'lab.yaml'
    new=(ROOT/path).read_bytes()
    a,b=map(yaml.safe_load,(before_tagr_reader_assets(ROOT,path,new),new))
    assert {k for k in a if a[k]!=b[k]}=={'sections'}
    a,b=a['sections'],b['sections']
    assert {k for k in a if a[k]!=b[k]}=={'overview','evidence','mapping'}
    for clue in ('毎分','4,000万人超','10%を対象','広告を表示した後','購入率ではなく','商品の流通総額ではありません',
                 '同じ','16.1%','IDの更新だけを試した結果ではありません'):
        assert clue in b['overview'], clue
    assert not any(s in b['overview'] for s in ('Lab','合成','run.py','図','Cpr','Col'))
    for clue in ('固定ID','既定のLSID','表1のDLRM'):
        assert clue in b['evidence']
    keys=['spread','collapse_counterexample','static','refreshed','cpr','col','assignment_stability',
          'semantic_mse','schedules','reward_updates','loss_trace']
    for key in keys:
        assert f'`{key}`' in b['mapping']
    script=tmp_path/'run.py'
    script.write_bytes((ROOT/P/'run.py').read_bytes())
    run1=subprocess.run([sys.executable,'-I','-S',str(script)],capture_output=True,check=True)
    run2=subprocess.run([sys.executable,'-I','-S',str(script)],capture_output=True,check=True)
    assert run1.stdout==run2.stdout==(tmp_path/'results.json').read_bytes()==(ROOT/P/'results.json').read_bytes()
