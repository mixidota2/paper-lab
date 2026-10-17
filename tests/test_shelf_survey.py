"""Source-level regressions for the survey and native equation markup."""
from pathlib import Path
import xml.etree.ElementTree as ET

from paper_lab.models import load_all_labs
from paper_lab.build import markdown_to_html, paper_sections

ROOT = Path(__file__).resolve().parents[1]
SHELF = {'storewide-shelf-decomposition', 'assortment-replenishment-hard-constraints', 'shelf-placement-options'}


def test_shelf_equations_are_native_math_with_accessible_fallback():
    count = 0
    for lab in load_all_labs(ROOT / 'papers'):
        if lab.id not in SHELF:
            continue
        for figure in lab.teaching_figures:
            if figure['kind'] != 'equations':
                continue
            for step in figure['steps']:
                element = ET.fromstring(step['formula_mathml'])
                assert element.tag == '{http://www.w3.org/1998/Math/MathML}math'
                assert element.find('.//{http://www.w3.org/1998/Math/MathML}msub') is not None
                assert step['formula'].strip()  # retained readable aria-label/fallback
                count += 1
    assert count == 6


def test_shelf_sections_resolve_without_losing_the_experiment():
    for lab in load_all_labs(ROOT / 'papers'):
        if lab.id not in SHELF:
            continue
        sections = {s['key']: s['html'] for s in paper_sections(lab)}
        assert '<iframe' not in sections['method']
        assert '<iframe' in sections['executable_understanding']
        assert '実装と検証の補足' in sections['implementation']
        assert '<sub>' in sections['method']
        assert '実ブラウザー' in sections['what_we_verified']
        assert '<h2>' not in sections['method']  # common page owns the section heading


def test_survey_links_to_all_four_shared_labs_and_distinguishes_evidence():
    text = (ROOT / 'guides/shelf-decisions.md').read_text()
    for slug in SHELF | {'whole-foods-shelf'}:
        assert f'../papers/{slug}.html' in text
    for scope in ['品揃え', 'フェイス数', '棚内配置', '店内配置', '補充', '需要推定']:
        assert scope in text
    html = markdown_to_html(text)
    assert 'survey-decisions' in html
    assert 'Prisma Peremarket' in html
    assert '因果的改善・解法の独立検証' in html
    assert '7.5%' in html and '6.7%' in html and 'シミュレーション' in html


def test_protected_runner_requires_survey_checks_at_all_three_widths():
    import ast
    source = (ROOT / 'tests/review_103.py').read_text()
    tree = ast.parse(source)
    funcs = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    preflight = ast.unparse(funcs['preflight'])
    assert "f'shelf-survey-{w}' for w in (360, 768, 1440)" in preflight
    callback = funcs['survey_rendering']
    assert ast.unparse(callback.body[0]) == 'guard(browser)'
    assert 'inspect_survey(page, base, out, width, snapshot)' in ast.unparse(callback)
    helper = (ROOT / 'tests/shelf_survey_browser.py').read_text()
    assert 'chromium.launch' not in helper and 'connect_over_cdp' not in helper
    assert "'mfrac', 'msup', 'msub'" in helper
    assert "'manual_visual_review': 'NOT TESTED'" in helper
    assert '.first.click()' in helper  # citation tables repeat the canonical Lab links
