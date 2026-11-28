"""A portfolio shift is measured in store sales, not inferred as position-only lift."""
import hashlib
import json
from pathlib import Path
from prose_preservation import historical_lab_public_guide

import pytest

from paper_lab.build import markdown_to_html
from prose_preservation import shelf_hermans_hash
from shelf_guide_preservation import GUIDE, before_asda, before_hermans

ROOT = Path(__file__).resolve().parents[1]
ANCHOR = 'german-store-category-effects'
DOI = 'https://doi.org/10.1016/j.jretai.2026.03.005'


def test_hermans_source_scope_limit_and_comparison():
    raw = (ROOT / GUIDE).read_bytes()
    html = markdown_to_html(raw.decode())
    assert html.count(f'id="{ANCHOR}"') == html.count(f'href="#{ANCHOR}"') == 1
    assert html.count(f'href="{DOI}"') == 2
    case = raw.decode().split(f'id="{ANCHOR}"', 1)[1].split('\n## ', 1)[0]
    for phrase in ('未改装店', '改装前54週', '再開後71週', '工事中の39週',
                   '会員カードを使った取引', '売上額の対数', '120カテゴリの売上が18%増え',
                   '65カテゴリは4%', '47カテゴリは6%減った', '無作為に選んでおらず',
                   '棚位置だけの効果や粗利はこの比較から分かりません'):
        assert phrase in case


def test_case_guard_accepts_only_scoped_review():
    current = before_asda(historical_lab_public_guide(ROOT,GUIDE))
    unreviewed = current.replace('47カテゴリは6%'.encode(), '47カテゴリは7%'.encode())
    assert unreviewed != current and before_hermans(unreviewed) == unreviewed
    old = before_hermans(current)
    receipt = json.loads((ROOT / 'tests/shelf_hermans_hashes.json').read_text())
    a, b = (hashlib.sha256(x).hexdigest() for x in (old, current))
    assert a == receipt['before_sha256'] and b == receipt['after_sha256']
    asda = json.loads((ROOT / 'tests/shelf_asda_hashes.json').read_text())['files'][GUIDE]
    assert b == asda['before_sha256']
    assert shelf_hermans_hash(ROOT, GUIDE, a) == asda['after_sha256']
    with pytest.raises(AssertionError):
        shelf_hermans_hash(ROOT, GUIDE, hashlib.sha256(unreviewed).hexdigest())
