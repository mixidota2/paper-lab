"""Preserve exact past guide versions and reject unreviewed current changes."""
from hashlib import sha1,sha256
import json
from pathlib import Path

import pytest
from prose_preservation import (
    LAB_PUBLIC_GUIDES, before_lab_public_guide, lab_public_guide_hash, reading_prose_hash,
)
from shelf_guide_preservation import BEFORE,GUIDE,verify_preserved_source

ROOT=Path(__file__).resolve().parents[1]

def identities(data):
    return {'sha256':sha256(data).hexdigest(),'blob':sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()}

def manifest(filename):
    return json.loads((ROOT/'tests'/filename).read_text())

@pytest.mark.parametrize('path',sorted(LAB_PUBLIC_GUIDES))
def test_exact_after_and_reverse_preserve_historical_bytes(path):
    rows=manifest('lab_public_guides_hashes.json')
    assert rows.keys()==LAB_PUBLIC_GUIDES
    current=(ROOT/path).read_bytes()
    previous=before_lab_public_guide(ROOT,path,current)
    assert identities(current)==rows[path]['after']
    assert identities(previous)==rows[path]['before']
    for algorithm in ('sha256','blob'):
        assert lab_public_guide_hash(ROOT,path,rows[path]['before'][algorithm],algorithm)==rows[path]['after'][algorithm]
        for bad in (rows[path]['after'][algorithm],'0'*len(rows[path]['before'][algorithm])):
            with pytest.raises(AssertionError):
                lab_public_guide_hash(ROOT,path,bad,algorithm)
    with pytest.raises(AssertionError):
        before_lab_public_guide(ROOT,path,current+b'\n')
    with pytest.raises(AssertionError):
        before_lab_public_guide(ROOT,path,previous)

def test_live_shelf_revision_still_passes_exact_legacy_verifier():
    verify_preserved_source(ROOT,GUIDE,BEFORE)

@pytest.mark.parametrize(('file','path'),(
    ('reading_prose_revision_hashes.json','README.md'),
    ('shelf_full_rewrite_hashes.json','guides/shelf-decisions.md'),
    ('reading_prose_revision_hashes.json','guides/store-layout-fixed-counts.md'),
    ('reading_prose_revision_hashes.json','guides/forecast-to-replenishment.md'),
))
def test_outer_forward_transform_runs_after_historical_layers(file,path):
    row=manifest(file)['files'][path]
    for alg,digest in identities((ROOT/path).read_bytes()).items():
        assert reading_prose_hash(ROOT,path,row['before_'+alg],alg)==digest
        with pytest.raises(AssertionError):
            reading_prose_hash(ROOT,path,'0'*len(digest),alg)

def test_varg_intro_explains_local_conversion_order_not_global_ranking():
    text=(ROOT/'README.md').read_text()
    line=next(line for line in text.splitlines() if line.startswith('[VARG]'))
    assert all(part in line for part in (
        '初回に商品IDを作るとき','先頭2つの符号が同じ商品どうし','購入につながる見込みの推定値',
        '3つ目の符号','全商品を一列に並べた順位ではありません','専用の枠','既存の最終順位付け',
    ))
