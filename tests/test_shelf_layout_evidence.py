"""Private layout-evidence candidate: scope, units and exact preservation."""
from pathlib import Path
import re
import pytest
from paper_lab.build import markdown_to_html
from shelf_guide_preservation import (GUIDE, BEFORE, AFTER, LAYOUT_PATCH_SHA,
                                      reverse_exact, verify_preserved_source)
ROOT = Path(__file__).resolve().parents[1]
PATCH = (ROOT / 'tests/fixtures/shelf-guide-layout-integration-20261030.patch').read_bytes()
TEXT = (ROOT / GUIDE).read_text()
SECTION = TEXT.split('<span id="iceland-layout-evaluation"></span>')[1].split('<span id="dcmp-evaluation"></span>')[0]


def test_evidence_units_uncertainty_scope_and_sources():
    for term in ('介入3店', '対照3店', '無作為割付ではなく', '固定した棚総数',
                 '位置だけの因果効果', '導入前後の週次の推移',
                 '+2.42 SD（95%信頼区間 0.22〜4.62）',
                 '+0.21 SD（95%信頼区間 −1.79〜2.21）',
                 '逆正規変換', '標準化尺度', '金額（£）や増加率（%）ではありません',
                 '元の売上金額は公開されていません', '信頼区間は広く0をまたぎ',
                 '証明していません', '粗利・利益、設備費や従業員の教育費',
                 '採算やROIは分かりません', '初期解析で結果変数の分布',
                 '登録履歴は独立確認していません', '不正や全分析が事後的だったという指摘ではなく',
                 'パイロット', '独立した追試2件とは数えません',
                 '効果量の差からレジ撤去の追加効果も求められません',
                 'https://journals.plos.org/plosmedicine/article?id=10.1371/journal.pmed.1003729',
                 'https://journals.plos.org/plosmedicine/article?id=10.1371/journal.pmed.1004575'):
        assert term in SECTION, term
    assert 'https://doi.org/10.1371/journal.pmed.1003729' in TEXT
    assert '最新研究としてではなく' in TEXT


def test_exact_prior_bytes_and_all_existing_anchors_preserved():
    previous = reverse_exact(TEXT.encode(), PATCH, LAYOUT_PATCH_SHA, AFTER).decode()
    old_anchors = re.findall(r'id="([^"]+)"', previous)
    new_anchors = re.findall(r'id="([^"]+)"', TEXT)
    assert [a for a in new_anchors if a != 'iceland-layout-evaluation'] == old_anchors
    assert new_anchors.count('iceland-layout-evaluation') == 1
    # This candidate is additions only: all prior lines stay in the same order.
    import difflib
    assert not any(line.startswith('- ') for line in difflib.ndiff(previous.splitlines(), TEXT.splitlines()))
    html = markdown_to_html(TEXT)
    assert 'id="iceland-layout-evaluation"' in html
    assert 'href="#iceland-layout-evaluation"' in html


@pytest.mark.parametrize('old,new', [('+0.21 SD', '+0.22 SD'),
    ('−1.79〜2.21', '0.01〜2.21'), ('逆正規変換', ''),
    ('<span id="iceland-layout-evaluation"></span>', ''),
    ('独立した追試2件とは数えません', '独立した追試2件です')])
def test_new_evidence_mutation_rejected(tmp_path, old, new):
    p=tmp_path/GUIDE; p.parent.mkdir(); p.write_text(TEXT.replace(old,new,1))
    with pytest.raises(AssertionError):
        verify_preserved_source(tmp_path,GUIDE,BEFORE,layout_patch_bytes=PATCH)


@pytest.mark.parametrize('patch', [PATCH+b'\n', PATCH.replace(b'guides/shelf-decisions.md', b'../outside.md')])
def test_new_patch_mutation_and_redirection_rejected(tmp_path, patch):
    p=tmp_path/GUIDE; p.parent.mkdir(); p.write_text(TEXT)
    with pytest.raises(AssertionError):
        verify_preserved_source(tmp_path,GUIDE,BEFORE,layout_patch_bytes=patch)
