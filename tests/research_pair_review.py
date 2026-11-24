"""Paper-specific checks for pages served by the existing protected review."""
DCDN = 'deep-cross-division'
ONO = 'ono-inventory-forecast-selection'
RESEARCH_WIDTHS = (360, 1440)
RESEARCH_SLUGS = (DCDN, ONO)
RESEARCH_ATTESTATION = ['before-navigation', 'after-navigation', 'after-actions']
DCDN_CONTROLS = {'dcdn-' + k for k in ('n', 'd', 'mask', 'task', 'view')}


def expected_research_groups():
    return [[slug, width] for width in RESEARCH_WIDTHS for slug in RESEARCH_SLUGS]


def assert_research_plan(plan):
    assert plan.get('signed_layout_research_groups') == expected_research_groups(), (
        'Missing or unexpected signed layout research plan'
    )


def assert_research_record(rows):
    pairs = [[row.get('slug'), row.get('width')] for row in rows]
    assert pairs == expected_research_groups(), 'Missing, duplicated, or unexpected protected research case'
    assert all(row.get('protection') == RESEARCH_ATTESTATION for row in rows), 'Research protection not confirmed'


def static_contract(dcdn, ono):
    starts_disabled = {attrs.get('id') for tag, attrs in dcdn.tags
                       if tag in ('input', 'select') and 'disabled' in attrs}
    assert DCDN_CONTROLS <= starts_disabled
    assert {'dcdn-' + k for k in ('raw', 'rho', 'term', 'view-note')} <= dcdn.ids
    assert 'ono-lab' in ono.ids
    disclosures = [(attrs.get('name'), 'open' in attrs) for tag, attrs in ono.tags if tag == 'details']
    for group, count in [('ono-penalty', 4), ('ono-service', 2)]:
        assert [opened for name, opened in disclosures if name == group] == [True] + [False] * (count - 1)


def dcdn_checks(page):
    def text(name):
        return page.locator('#dcdn-' + name).inner_text()
    def arithmetic():
        return tuple(text(n) for n in ('product', 'raw', 'rho', 'term'))
    for control in sorted(DCDN_CONTROLS):
        assert page.locator('#' + control).is_enabled(), control
    assert arithmetic() == ('0.025', '1000', '100', '500')
    denominator = page.locator('#dcdn-d')
    denominator.fill('-0.005')
    assert arithmetic() == ('-0.025', '-1000', '-100', '-500')
    denominator.fill('0')
    assert arithmetic() == ('0', '未定義（0 で割れません）', '0', '0')
    denominator.fill('0.005')
    page.locator('#dcdn-mask').uncheck()
    assert arithmetic() == ('0.025', '1000', '0', '0')
    view = page.locator('#dcdn-view')
    view.select_option('full')
    assert tuple(text(k) for k in ('control', 'treatment', 'delta')) == ('0.5589', '0.5681', '+0.0092')
    assert tuple(text(k) for k in ('control-label', 'treatment-label')) == ('DCNv2（比率あり）', 'DCDN（比率あり）')
    assert '入力をそろえたオフライン比較' in text('view-note')
    view.select_option('deployed')
    assert tuple(text(k) for k in ('control', 'treatment', 'delta')) == ('0.5589', '0.5629', '+0.0040')
    assert tuple(text(k) for k in ('control-label', 'treatment-label')) == ('DCNv2（比率あり）', 'DCDN（比率なし）')
    assert 'A/B テストの結果ではありません' in text('view-note')


def ono_checks(page):
    penalty = page.locator('#ono-lab details[name="ono-penalty"]')
    service = page.locator('#ono-lab details[name="ono-service"]')
    assert penalty.count() == 4 and service.count() == 2
    def activate(group, index, key):
        summary = group.nth(index).locator('summary')
        summary.focus()
        summary.press(key)
        assert group.evaluate_all('(nodes) => nodes.filter(node => node.open).length') == 1
        assert group.nth(index).get_attribute('open') is not None
    assert '1.74%' in penalty.first.locator('p:visible').inner_text()
    activate(penalty, 3, 'Enter')
    assert '0.54%' in penalty.last.locator('p:visible').inner_text()
    assert penalty.first.locator('p:visible').count() == 0
    activate(penalty, 0, 'Space')
    assert '1.74%' in penalty.first.locator('p:visible').inner_text()
    assert service.first.locator('p:visible strong').all_inner_texts() == ['90%', '96%']
    activate(service, 1, 'Enter')
    assert service.last.locator('p:visible strong').all_inner_texts() == ['60%', '96%']
    assert service.first.locator('p:visible').count() == 0


def protected_research(page, browser, base, slug, width, guard, settled, heading):
    assert slug in RESEARCH_SLUGS and width in RESEARCH_WIDTHS
    guard(browser)
    assert page.goto(f'{base}/papers/{slug}.html').ok
    guard(browser)
    settled(page)
    heading(page)
    assert page.evaluate('innerWidth') == width
    (dcdn_checks if slug == DCDN else ono_checks)(page)
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    guard(browser)
    return {'slug': slug, 'width': width, 'protection': RESEARCH_ATTESTATION.copy()}
