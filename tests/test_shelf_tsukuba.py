"""Keep the model comparison, field change, and sales evidence distinct."""
from hashlib import sha1
from pathlib import Path
from prose_preservation import historical_lab_public_guide

import pytest

from paper_lab.build import markdown_to_html
from prose_preservation import shelf_tsukuba_hash
from shelf_guide_preservation import BEFORE, GUIDE, STREICHER, before_tsukuba, sha, verify_preserved_source

ROOT = Path(__file__).resolve().parents[1]
RAW = historical_lab_public_guide(ROOT,GUIDE)
ANCHOR = 'tsukuba-sekisho-shelf-evaluation'
SOURCE = 'https://casebank.sk-tsukuba.university/case/10454'


def test_case_comparison_limits_and_link():
    text = RAW.decode()
    case = text.split(f'<span id="{ANCHOR}"></span>', 1)[1].split(
        '<span id="streicher-aisle-evaluation"></span>', 1)[0]
    for clue in ('14週分', '75.3%から32.9%', '最適化で作った配置の導入を見送り',
                 'コンビニ1店', '配置を変えなかった場合のモデル予測を12.2%上回りました',
                 '比較店の実績を基準にした数字ではありません', '集計範囲の詳細や粗利は確認できません',
                 '棚替えが売上をどれだけ変えたかは分かりません'):
        assert clue in case
    html = markdown_to_html(text)
    assert html.count(f'id="{ANCHOR}"') == html.count(f'href="#{ANCHOR}"') == 1
    assert html.count(f'href="{SOURCE}"') == 2


@pytest.mark.parametrize('kind', ['sha256', 'blob'])
def test_revision_keeps_both_hash_chains(kind):
    def digest(data):
        if kind == 'sha256':
            return sha(data)
        return sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()
    past = before_tsukuba(RAW)
    assert sha(past) == STREICHER
    assert before_tsukuba(past) == past
    assert shelf_tsukuba_hash(ROOT, GUIDE, digest(past), kind) == digest(RAW)
    assert shelf_tsukuba_hash(ROOT, 'guides/store-layout-fixed-counts.md', digest(past), kind) == digest(past)
    with pytest.raises(AssertionError):
        shelf_tsukuba_hash(ROOT, GUIDE, digest(RAW), kind)


@pytest.mark.parametrize('before,after', [('12.2%', '13.2%'), ('モデル予測', '対照店の売上'),
                                         ('0.50ポイント', '0.51ポイント')])
def test_changed_evidence_is_not_accepted(tmp_path, before, after):
    target = tmp_path / GUIDE
    target.parent.mkdir()
    assert before.encode() in RAW
    mutant = RAW.replace(before.encode(), after.encode(), 1)
    target.write_bytes(mutant)
    assert before_tsukuba(mutant) == mutant
    with pytest.raises(AssertionError):
        verify_preserved_source(tmp_path, GUIDE, BEFORE)
