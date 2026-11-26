from pathlib import Path
import csv
import hashlib

import pytest
import yaml

from source_overview_corrections import (
    HASTERAD,
    ORPR_ARCHIVE,
    _receipt,
    before_hasterad_overview_correction,
    source_overview_correction_hash,
)

ROOT = Path(__file__).resolve().parents[1]


def test_only_reviewed_overview_changed():
    raw = (ROOT / HASTERAD).read_bytes()
    before = before_hasterad_overview_correction(ROOT, HASTERAD, raw)
    old, new = map(yaml.safe_load, (before, raw))
    overview = new['sections'].pop('overview')
    assert '棚の費用が高く' in old['sections'].pop('overview')
    assert new == old
    for phrase in ('週次販売、価格、販促', '商品1品当たりの固定費', '最適案を平均10.9%下回りました', '人工データ'):
        assert phrase in overview
    assert 'Lab' not in overview and '棚の費用が高く' not in overview
    with pytest.raises(AssertionError):
        before_hasterad_overview_correction(ROOT, HASTERAD, raw + b'\n')


@pytest.mark.parametrize('path', [HASTERAD, ORPR_ARCHIVE])
@pytest.mark.parametrize('algorithm', ['sha256', 'blob'])
def test_exact_receipt_rejects_other_bytes(path, algorithm):
    row = _receipt(ROOT)['files'][path]
    body = (ROOT / path).read_bytes()
    actual = (hashlib.sha256(body).hexdigest() if algorithm == 'sha256'
              else hashlib.sha1(f'blob {len(body)}\0'.encode() + body).hexdigest())
    assert source_overview_correction_hash(ROOT, path, row['before'][algorithm], algorithm) == actual
    for other in (actual, '0' * len(actual)):
        with pytest.raises(AssertionError):
            source_overview_correction_hash(ROOT, path, other, algorithm)


def test_archive_keeps_historical_entry_and_links_the_current_article():
    with (ROOT / 'research-data/papers.csv').open(newline='') as stream:
        rows = [row for row in csv.reader(stream) if row[1] == '2512.19001']
    assert len(rows) == 1
    assert all(term in ' '.join(rows[0]) for term in ('A/B+DiD', '+0.47pp'))
    annotation = next(line for line in (ROOT / ORPR_ARCHIVE).read_text().splitlines() if line.startswith('- ORPR'))
    assert 'Y+0.47%' in annotation and '無作為に割り付けたという意味ではありません' in annotation
    assert 'https://mixidota2.github.io/paper-lab/papers/orpr-or-guided-pretrain-reinforce-inventory.html' in annotation
