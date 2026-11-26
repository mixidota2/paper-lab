"""The fixed-count theme keeps its scope and is generated with working links."""
from pathlib import Path
from collections import Counter
from paper_lab.build import build
from review_103 import Document

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'store-layout-fixed-counts'


def test_fixed_count_diagram_and_evidence_boundaries():
    text = (ROOT / 'guides' / f'{SLUG}.md').read_text()
    import re
    cells = re.findall(r'<td>([ABC])</td>', text)
    assert Counter(cells) == {'A': 5, 'B': 4, 'C': 3}
    assert Counter(re.findall(r'<text [^>]*>([ABC])</text>', text)) == Counter(cells)
    for label in 'ABC':
        positions = {i for i, value in enumerate(cells) if value == label}
        seen = {min(positions)}
        while True:
            expanded = seen | {q for p in seen for q in positions
                               if abs(p // 4 - q // 4) + abs(p % 4 - q % 4) == 1}
            if expanded == seen:
                break
            seen = expanded
        assert seen == positions
    for constraint in ('Σ_c x[c,p] = 1', 'Σ_p x[c,p] = n_c',
                       'Σ_(b∈B_c) y[c,b] = 1', 'Σ_(c,b:p∈b) y[c,b] = 1'):
        assert constraint in text
    for limit in ('実店舗での計算時間や売上効果を比べた結果ではない', '最適性ギャップは未確認',
                  '本文全体は未取得', '業界の採用率は分からない',
                  '店全体の増分粗利', '本数は変更せず'):
        assert limit in text


def test_generated_theme_and_reciprocal_links(tmp_path):
    site = tmp_path / 'site'
    assert len(build(root=ROOT, site_dir=site)) == 121
    target = site / 'guides' / f'{SLUG}.html'
    doc = Document(target.read_text())
    assert f'{SLUG}.html' in Document((site / 'guides/index.html').read_text()).links
    assert f'{SLUG}.html' in Document((site / 'guides/shelf-decisions.html').read_text()).links
    assert 'shelf-decisions.html#store-location' in doc.links
    assert '../papers/whole-foods-shelf.html' in doc.links
    assert '121件のLab ／ 3件のテーマガイド' in target.read_text()
    for text in (
        '棚を動かした日時と、売上を集計する日をそろえる',
        '水曜を、配置が変わった日として扱わない',
        '配置が分からなかった営業日として記録する',
        '事前の割付のまま主分析に含める',
        '本数を守る27,720通り',
        '実店舗での計算時間や売上効果を比べた結果ではない',
    ):
        assert text in target.read_text()
