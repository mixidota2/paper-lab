import hashlib
import json
from pathlib import Path

import pytest

from paper_lab.build import markdown_to_html
from prose_preservation import shelf_asda_hash
from shelf_guide_preservation import GUIDE, before_asda

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'https://www.nesta.org.uk/report/nesta-and-asda-retail-innovation-partnership/'
ANCHOR = 'asda-pizza-facing-evaluation'


def test_case_and_readme_distinguish_field_trial_from_synthetic_example():
    receipt = json.loads((ROOT/'tests/shelf_asda_hashes.json').read_text())['files']
    g = (ROOT/GUIDE).read_bytes()
    html = markdown_to_html(g.decode())
    assert html.count(f'id="{ANCHOR}"') == html.count(f'href="#{ANCHOR}"') == 1
    assert html.count(f'href="{SOURCE}"') == 2
    case = g.decode().split(f'id="{ANCHOR}"',1)[1].split('<span id=',1)[0]
    for phrase in ('実施店20店','約2ポイント','比較店でも通常の棚替え',
                   '比較店での変化幅を示していません','統計的に明確な差は出ませんでした',
                   '売上額の推定差は−0.5%','実施店と比較店の実際の面数を同じ日に記録',
                   '売場全体の棚本数を固定してカテゴリを移す試験でもありません'):
        assert phrase in case
    r = receipt['README.md']
    readme = (ROOT/'README.md').read_text()
    assert readme.count(r['new']) == 1 and r['old'] not in readme
    assert '棚を5・4・3本に分けた図は模式図です。別の合成例では' in r['new']
    assert '27,720通り' in r['new'] and '16通り' in r['new']
    current = readme.encode()
    forward = json.loads((ROOT/'tests/root_readme_catalog_120_hashes.json').read_text())
    assert hashlib.sha256(current).hexdigest() == forward['after']['sha256']
    assert readme.count('120件のLab') == 3
    readme = readme.replace('120件のLab','119件のLab')
    assert hashlib.sha256(readme.encode()).hexdigest() == forward['before']['sha256']
    old_readme = readme.replace(r['new'],r['old'],1).encode()
    old_guide = before_asda(g)
    assert old_guide != g and before_asda(g+b'\n') == g+b'\n'
    for p,old,new in ((GUIDE,old_guide,g),('README.md',old_readme,readme.encode())):
        row = receipt[p]
        for alg,h in (('sha256',lambda x: hashlib.sha256(x).hexdigest()),
                      ('blob',lambda x: hashlib.sha1(f'blob {len(x)}\0'.encode()+x).hexdigest())):
            assert h(old) == row['before_'+alg]
            assert h(new) == row['after_'+alg] == shelf_asda_hash(ROOT,p,h(old),alg)
            with pytest.raises(AssertionError):
                shelf_asda_hash(ROOT,p,h(old+b'\n'),alg)
