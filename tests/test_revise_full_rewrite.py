from pathlib import Path
import re
from xml.etree import ElementTree as ET

import pytest
import yaml

from prose_preservation import before_revise_full_rewrite, revise_full_rewrite_hash, revise_rewrite_receipt
from test_arxiv_versioned_overviews import blob, sha

ROOT = Path(__file__).resolve().parents[1]
BASE = 'papers/revise-recovery/'
DOCS = {'lab.yaml','method.md','figures/impact.svg','figures/certificate.svg'}


def test_rewrite_receipt_does_not_allow_unreviewed_bytes():
    rows = revise_rewrite_receipt(ROOT)
    assert set(rows) == {BASE + file for file in DOCS}
    for path, row in rows.items():
        current = (ROOT/path).read_bytes()
        for algorithm, hash_ in (('sha256', sha), ('blob', blob)):
            assert hash_(current) == row['after_' + algorithm]
            assert revise_full_rewrite_hash(ROOT, path, row['before_' + algorithm], algorithm) == hash_(current)
            with pytest.raises(AssertionError):
                revise_full_rewrite_hash(ROOT, path, hash_(current+b'\n'), algorithm)
        if path.endswith(('lab.yaml','method.md')):
            before = before_revise_full_rewrite(ROOT, path, current)
            assert sha(before) == row['before_sha256']
            assert blob(before) == row['before_blob']
            with pytest.raises(AssertionError):
                before_revise_full_rewrite(ROOT, path, current+b'\n')
    assert revise_full_rewrite_hash(ROOT,BASE+'run.py','unchanged') == 'unchanged'


def test_summary_source_and_formula_preservation():
    lab_path = BASE + 'lab.yaml'
    method_path = BASE + 'method.md'
    raw = (ROOT/lab_path).read_bytes()
    old = yaml.safe_load(before_revise_full_rewrite(ROOT, lab_path, raw))
    new = yaml.safe_load(raw)
    assert {k:v for k,v in new.items() if k not in ('question','summary','source_review','core_idea','sections','figures')} == {
        k:v for k,v in old.items() if k not in ('question','summary','source_review','core_idea','sections','figures')}
    assert new['source_review'] == {**old['source_review'],'scope':new['source_review']['scope']}
    assert new['sections']['overview'] == old['sections']['overview']
    assert new['sections']['method'] == old['sections']['method']
    new_m = (ROOT/method_path).read_bytes()
    old_m = before_revise_full_rewrite(ROOT, method_path, new_m)
    assert re.findall(rb'```text\n(.*?)```',new_m,re.S) == re.findall(rb'```text\n(.*?)```',old_m,re.S)
    for new_f, old_f in zip(new['figures'], old['figures'], strict=True):
        assert new_f == {**old_f, 'title':new_f['title'], 'caption':new_f['caption']}
        svg = ET.parse(ROOT/BASE/new_f['path']).getroot()
        assert svg.get('aria-labelledby') == 'title desc'
        for suffix, expected in (('title',new_f['title']),('desc',new_f['caption'])):
            assert svg.find(f'{{http://www.w3.org/2000/svg}}{suffix}').text == expected


def test_reported_experiments_remain_distinct_from_the_toy():
    article = yaml.safe_load((ROOT/BASE/'lab.yaml').read_text())['sections']
    evidence = article['evidence']
    assert all(x in evidence for x in ('15,939回','0件','15,000回','300回','10.0 | 80.0 | 719 ms','7.8 | 62.4 | 711 ms',
                  '4.4 | 35.2 | 669 ms','6.00回、5.19回、3.56回','全方式が平均6.00回','発生率を推定する標本ではない'))
    assert all(x in article['results'] for x in ('6処理すべて','A、C、Fの3処理','出力も、最新の入力で最初から計算した結果と一致','換算していない'))
    assert '著者の実験は再実行していない' in article['what_we_did_not_verify']
