"""Semantic checks shared by offline JS tests and the protected browser gate."""
from html.parser import HTMLParser
from itertools import product
import json
import math
import re


class Frame(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.tags = []
        self.text = []
        self.cells = []
        self.cell = None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
        if tag == 'td':
            self.cell = ''

    def handle_data(self, data):
        self.text.append(data)
        if self.cell is not None:
            self.cell += data

    def handle_endtag(self, tag):
        if tag == 'td':
            self.cells.append(self.cell)
            self.cell = None


def assert_reported(html, data, outcome, time):
    frame = Frame(html)
    spec = data['reported'][outcome]
    label, value, low, high = spec['rows'][time]
    text = ''.join(frame.text)
    assert spec['label'] in text
    assert f'{label}：{value:+g} {spec["unit"]}' in text
    assert f'95% CI [{low:g}, {high:g}]' in text
    assert spec['locator'] in text
    assert ('区間は0をまたぐ' if low <= 0 <= high else '区間は0より上') in text
    def x(v):
        return 35 + 490*(v-spec['domain'][0])/(spec['domain'][1]-spec['domain'][0])
    circles = [a for t, a in frame.tags if t == 'circle']
    assert len(circles) == 1
    assert math.isclose(float(circles[0]['cx']), x(value), abs_tol=1e-7)
    paths = [a['d'] for t, a in frame.tags if t == 'path']
    assert len(paths) == 1
    coordinates = list(map(float, re.findall(r'-?\d+(?:\.\d+)?(?:e[+-]?\d+)?', paths[0])))
    expected = [x(low), 48, 72, x(low), 60, x(high), x(high), 48, 72]
    assert len(coordinates) == len(expected)
    assert all(math.isclose(a,b,abs_tol=1e-7) for a,b in zip(coordinates,expected))


def assert_synthetic(html, data, c, s, m):
    frame = Frame(html)
    scenario = data['synthetic'][c*9+s*3+m]
    assert scenario['control_change'] == [-.04,0,.04][c]
    assert scenario['shock'] == [0,.4,.8][s]
    assert scenario['mismatch'] == [-.02,0,.02][m]
    text = ''.join(frame.text)
    assert f"共通の傾き変化 {scenario['control_change']:+.2f}／週" in text
    assert f"改装ショック {scenario['shock']:.1f}" in text
    assert f"介入店だけの傾き変化 {scenario['mismatch']:+.2f}／週" in text
    assert '論文のSDとは比較できない' in text
    expected = [f'{e[k]:+.3f}' for e in scenario['effects'] for k in ['without_control','controlled','true_placement_and_range']]
    assert frame.cells == expected
    lines = [a for t,a in frame.tags if t == 'polyline']
    assert len(lines) == 4
    for line, key in zip(lines, ['control','intervention','counterfactual','fitted'], strict=True):
        points = [tuple(map(float,p.split(','))) for p in line['points'].split()]
        assert len(points) == len(scenario['rows']) == 39
        for (x,y), row in zip(points,scenario['rows'],strict=True):
            assert math.isclose(x,45+(row['week']+12)/38*500,abs_tol=.0051)
            assert math.isclose(y,250-(row[key]+.5)/4*210,abs_tol=.0051)


def assert_wrapped_initial(page, source):
    data = json.loads(source.read_text())
    assert page.locator('#wrapped-outcome').input_value() == 'household'
    assert page.locator('#wrapped-time').input_value() == '2'
    assert_reported(page.locator('#wrapped-ci').inner_html(),data,'household',2)
    assert_synthetic(page.locator('#wrapped-simulation').inner_html(),data,1,0,1)


def inspect_wrapped(page, source):
    data = json.loads(source.read_text())
    assert_wrapped_initial(page, source)
    for outcome, time in product(['household','store'],range(3)):
        page.locator('#wrapped-outcome').select_option(outcome)
        page.locator('#wrapped-time').select_option(str(time))
        assert_reported(page.locator('#wrapped-ci').inner_html(),data,outcome,time)
    controls = [page.locator('#wrapped-'+key) for key in ['control','shock','mismatch']]
    for c,s,m in product(range(3),repeat=3):
        for control,value in zip(controls,[c,s,m],strict=True):
            control.select_option(str(value))
        assert_synthetic(page.locator('#wrapped-simulation').inner_html(),data,c,s,m)
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    inspect_wrapped_keyboard(page, data, controls)


def inspect_wrapped_keyboard(page, data, controls):
    # Native closed selects on macOS do not use Home to select the first item.
    # ASCII '0'/'+' uniquely prefix the middle/last options and are supported
    # by Playwright's US keyboard map. U+2212 is not a supported press() key.
    # Keep both the exact selected value and the resulting semantic/geometry gate.
    assert [x.input_value() for x in controls] == ['2','2','2']
    for key, value in [('0',1), ('+',2)]:
        # Blur/refocus resets the native type-ahead prefix between keystrokes.
        controls[1].focus()
        controls[0].focus()
        assert controls[0].evaluate('(element) => element === document.activeElement')
        controls[0].evaluate('''element => {
            element.__wrappedKeyEvents = [];
            for (const type of ['keydown', 'keypress', 'keyup'])
                element.addEventListener(type, event => element.__wrappedKeyEvents.push(
                    {type: event.type, key: event.key, trusted: event.isTrusted}), {once: true});
        }''')
        controls[0].press(key)
        events = controls[0].evaluate('(element) => element.__wrappedKeyEvents')
        assert events == [{'type': kind, 'key': key, 'trusted': True}
                          for kind in ['keydown','keypress','keyup']]
        assert [x.input_value() for x in controls] == [str(value),'2','2']
        assert_synthetic(page.locator('#wrapped-simulation').inner_html(),data,value,2,2)
    reset = page.locator('#wrapped-reset')
    reset.focus()
    reset.press('Enter')
    assert [x.input_value() for x in controls] == ['1','0','1']
    assert_synthetic(page.locator('#wrapped-simulation').inner_html(),data,1,0,1)
