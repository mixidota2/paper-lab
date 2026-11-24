from decimal import Decimal, ROUND_HALF_UP
from hashlib import sha1, sha256
import json
from pathlib import Path

import pytest

from prose_preservation import shelf_full_rewrite_hash, shelf_streicher_hash

ROOT = Path(__file__).resolve().parents[1]
GUIDE = 'guides/shelf-decisions.md'


def test_streicher_supplement_keeps_the_exact_guide_chain():
    original = json.loads((ROOT / 'tests/shelf_full_rewrite_hashes.json').read_text())['files'][GUIDE]
    extra = json.loads((ROOT / 'tests/shelf_streicher_hashes.json').read_text())['files'][GUIDE]
    raw = (ROOT / GUIDE).read_bytes()
    for algo, value in {
        'blob': sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest(),
        'sha256': sha256(raw).hexdigest(),
    }.items():
        prior = extra['before_' + algo]
        assert prior == original['after_' + algo]
        assert shelf_full_rewrite_hash(ROOT, GUIDE, original['before_' + algo], algo) == value
        assert shelf_streicher_hash(ROOT, GUIDE, prior, algo) == value
        assert shelf_streicher_hash(ROOT, 'guides/store-layout-fixed-counts.md', prior, algo) == prior
        with pytest.raises(AssertionError):
            shelf_streicher_hash(ROOT, GUIDE, ('0' if prior[0] != '0' else '1') + prior[1:], algo)
        with pytest.raises(AssertionError):
            shelf_streicher_hash(ROOT, GUIDE, value, algo)


def test_aisle_share_and_revenue_are_distinguished():
    guide = (ROOT / GUIDE).read_text()
    section = guide.split('<span id="streicher-aisle-evaluation"></span>', 1)[1].split('<span id="dcmp-evaluation"></span>', 1)[0]
    for fragment in ('スーパー1店', '陳列台5台', '各6週間', '11カテゴリ', '4.33%から4.83%', '0.50ポイント',
                     '比較店を置いておらず', '売上・粗利が増えたかは判断できません', '架空例',
                     '研究が行った比較ではありません'):
        assert fragment in section
    for total, share, expected in [('100000', '.0433', 4330), ('89000', '.0483', 4299)]:
        assert int((Decimal(total) * Decimal(share)).quantize(Decimal('1'), rounding=ROUND_HALF_UP)) == expected
    assert '4,330円から4,299円に下がります' in section
    assert guide.count('10.1371/journal.pone.0346492') == 2


def test_verbatim_restoration_and_patch_mutants():
    import gzip
    from shelf_guide_preservation import FULL_REWRITE, before_streicher
    raw = (ROOT / GUIDE).read_bytes()
    patch = gzip.decompress((ROOT / 'tests/fixtures/shelf-guide-streicher-20261124.patch.gz').read_bytes())
    assert sha256(before_streicher(raw)).hexdigest() == FULL_REWRITE
    assert before_streicher(raw + b'\n') == raw + b'\n'
    for mutant in (patch + b'\n', patch.replace(GUIDE.encode(), b'../outside.md')):
        with pytest.raises(AssertionError):
            before_streicher(raw, mutant)
