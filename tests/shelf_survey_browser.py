"""Bounded survey/MathML evidence inside the existing protected browser runner.

No launch route, engine fallback or protection-policy change is defined here.
Geometry assertions are rendering checks, not proof of scientific correctness.
"""
import json
import math

SHELF = ('storewide-shelf-decomposition', 'assortment-replenishment-hard-constraints', 'shelf-placement-options')



def assert_math_term(term):
    """Check glyph position and computed type size as distinct measurements.

    Ink/layout height depends on the characters (e.g. α versus ip), so it
    cannot measure script scaling. CSS computed font-size measures type size;
    the recorded rectangles still check nonzero rendering and vertical position.
    """
    a, b = term['children']
    assert min(a['width'], a['height'], b['width'], b['height']) > 0, term
    if term['kind'] == 'mfrac':
        assert a['bottom'] <= b['y'], term
        return
    assert term['kind'] in ('msub', 'msup'), term
    sizes = (a['fontSize'], b['fontSize'])
    assert all(math.isfinite(size) and size > 0 for size in sizes), term
    assert b['fontSize'] < a['fontSize'], term
    if term['kind'] == 'msup':
        assert b['y'] < a['y'], term
    else:
        assert b['bottom'] > a['bottom'], term


def inspect_survey(page, base, out, width, snapshot):
    records = {'width': width, 'manual_visual_review': 'NOT TESTED',
               'scientific_content_validation': 'NOT TESTED by browser assertions',
               'tables': [], 'math': [], 'navigation': []}
    evidence_path = out / f'shelf-survey-{width}.json'
    def save():
        evidence_path.write_text(json.dumps(records, ensure_ascii=False, indent=2))
    def fit():
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), page.url
    try:
        assert page.goto(base + '/guides/shelf-decisions.html').ok
        page.wait_for_function('document.fonts.status === "loaded"')
        fit()
        diagrams = page.locator('.guide-body figure')
        assert diagrams.count() == 2
        assert page.locator('.survey-decisions > div').count() == 5  # assortment and facings share one box
        for i, diagram in enumerate(diagrams.all()):
            assert diagram.is_visible()
            snapshot(page, out, f'survey-{width}-diagram-{i}', diagram)
        tables = page.locator('.guide-body table')
        assert tables.count() >= 8
        for i, table in enumerate(tables.all()):
            table.scroll_into_view_if_needed()
            geometry = table.evaluate('e => ({width:e.clientWidth, scrollWidth:e.scrollWidth, overflow:getComputedStyle(e).overflowX})')
            assert geometry['width'] > 0
            assert geometry['overflow'] == 'auto'
            if geometry['scrollWidth'] > geometry['width'] + 1:
                table.evaluate('e => e.scrollLeft = e.scrollWidth')
                assert table.evaluate('e => e.scrollLeft > 0')
                if i == 0:
                    snapshot(page, out, f'survey-{width}-table-right', table)
                table.evaluate('e => e.scrollLeft = 0')
            records['tables'].append(geometry)
        if width == 360:
            assert any(t['scrollWidth'] > t['width'] + 1 for t in records['tables'])
        snapshot(page, out, f'survey-{width}-table-left', tables.first)
        for link in page.locator('.survey-toc a').all():
            href = link.get_attribute('href')
            link.click()
            assert page.url.endswith(href)
            target = page.locator(href)
            assert target.count() == 1
            assert target.evaluate('e => Math.abs(e.getBoundingClientRect().top) < innerHeight')
            records['navigation'].append(href)
        for slug in (*SHELF, 'whole-foods-shelf'):
            # Multiple citations point to the same Lab: choose the first deliberately.
            page.locator(f'.guide-body a[href="../papers/{slug}.html"]').first.click()
            page.wait_for_function('document.fonts.status === "loaded"')
            assert page.url.endswith(f'/papers/{slug}.html')
            fit()
            if slug in SHELF:
                expressions = page.locator('.math-expression math')
                assert expressions.count() == 2
                for i, expression in enumerate(expressions.all()):
                    expression.scroll_into_view_if_needed()
                    assert expression.is_visible()
                    data = expression.evaluate('''e => {
                      const rect = n => {const r=n.getBoundingClientRect(), s=getComputedStyle(n); return {x:r.x,y:r.y,width:r.width,height:r.height,bottom:r.bottom,fontSize:parseFloat(s.fontSize),mathDepth:s.getPropertyValue("math-depth"),text:n.textContent};};
                      return {namespace:e.namespaceURI, rect:rect(e),
                        terms:[...e.querySelectorAll('mfrac,msub,msup')].map(n=>({kind:n.localName, children:[...n.children].map(rect)}))};
                    }''')
                    assert data['namespace'] == 'http://www.w3.org/1998/Math/MathML'
                    assert data['rect']['height'] > 0 and data['rect']['width'] > 0
                    for term in data['terms']:
                        assert_math_term(term)
                    assert expression.locator('xpath=..').get_attribute('aria-label')
                    records['math'].append({'slug': slug, 'index': i, **data})
                    snapshot(page, out, f'survey-{width}-{slug}-math-{i}', expression.locator('xpath=ancestor::figure'))
            page.get_by_role('link', name='棚割りのテーマガイドへ', exact=True).click()
            assert page.url.endswith('/guides/shelf-decisions.html')
            records['navigation'].append(slug)
        kinds = {term['kind'] for item in records['math'] for term in item['terms']}
        assert {'mfrac', 'msup', 'msub'} <= kinds
        fit()
        records['status'] = 'AUTOMATED RENDERING CHECKS PASSED; manual/content review separate'
    finally:
        save()
