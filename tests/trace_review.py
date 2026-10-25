"""TRACE assertions for offline output checks and the existing protected runner.
No browser launch, server, permission or security configuration lives here.
"""
from html.parser import HTMLParser
from itertools import product
import json
import re, sys


class Frame(HTMLParser):
    def __init__(self, html):
        super().__init__(); self.text=[]; self.codes=[]; self.steps=[]; self.bars=[]
        self.code=None; self.step=None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag=='code': self.code=''
        if tag=='li': self.step=''
        if tag=='div' and 'width:' in attrs.get('style',''):
            self.bars.append(float(re.search(r'width:([\d.]+)%',attrs['style'])[1]))

    def handle_data(self, text):
        self.text.append(text)
        if self.code is not None: self.code+=text
        if self.step is not None: self.step+=text

    def handle_endtag(self, tag):
        if tag=='code': self.codes.append(self.code); self.code=None
        if tag=='li': self.steps.append(self.step); self.step=None


def assert_trace_frame(html, case):
    frame=Frame(html); text=''.join(frame.text)
    records=[case['base'],case['changed']]
    assert frame.steps==[f"{s['tool']}({s['argument']}) → 在庫{s['observation']}" for r in records for s in r['trace']]
    assert [c for c in frame.codes if re.fullmatch('[0-9a-f]{64}',c)]==[
        records[0]['canonical_hash'],records[1]['canonical_hash'],records[0]['state_hash'],records[1]['state_hash']]
    for key,label in [('original_score','元の実行の点数'),('raw_score','比較側・修正前の点数'),('rescored','比較側・現在の採点方式')]:
        assert f'{label} {case[key]:.2f}' in text
    assert frame.bars==[case[key]*100 for key in ['original_score','raw_score','rescored']]
    assert f"修正前 {case['raw_gap']:.2f} → 現在 {case['gap_after']:.2f}" in text
    assert f"比較側の在庫：{case['changed']['state']['stock']}（正解5）" in text
    assert '正規の操作列：'+('同じ' if case['behavior_same'] else '違う') in text
    assert '最終状態：'+('同じ' if case['state_same'] else '違う') in text
    assert '実行のやり直しはない' in text


def assert_trace_initial(page, source):
    data=json.loads(source.read_text())
    assert [page.locator('#trace-'+key).input_value() for key in ['agent','alias','normalize']]==['0','1','0']
    assert_trace_frame(page.locator('#trace-output').inner_html(),data['synthetic'][2])



KEYBOARD_OBSERVER = r"""() => {
    const ids = ['trace-normalize', 'trace-reset'];
    const state = {events: [], truncated: false, listeners: []};
    const value = () => {
        const v = document.getElementById(ids[0]).value;
        return ['0', '1'].includes(v) ? v : 'UNKNOWN';
    };
    for (const id of ids) {
        const element = document.getElementById(id);
        for (const type of ['keydown', 'keypress', 'keyup', 'input', 'change']) {
            const listener = event => {
                if (state.events.length >= 8) { state.truncated = true; return; }
                const keys = {' ': 'Space', ArrowDown: 'ArrowDown', Enter: 'Enter', '別': '別'};
                state.events.push({type, key: keys[event.key] || 'OTHER',
                    trusted: event.isTrusted === true,
                    target: id === ids[0] ? 'normalize' : 'reset', value: value()});
            };
            element.addEventListener(type, listener);
            state.listeners.push([element, type, listener]);
        }
    }
    window.__traceKeyboardObservation = state;
}"""
KEYBOARD_SNAPSHOT = r"""() => {
    const state = window.__traceKeyboardObservation;
    const select = document.getElementById('trace-normalize');
    const reset = document.getElementById('trace-reset');
    const result = {value: select.value, open: select.matches(':open'),
        focus: document.activeElement === select ? 'normalize' :
               document.activeElement === reset ? 'reset' : 'other',
        events: state.events, truncated: state.truncated};
    state.events = []; state.truncated = false;
    return result;
}"""
KEYBOARD_CLEANUP = r"""() => {
    const state = window.__traceKeyboardObservation;
    for (const [element, type, listener] of state.listeners)
        element.removeEventListener(type, listener);
    delete window.__traceKeyboardObservation;
}"""


def keyboard_record(raw, stage, width):
    """Finite console fields; never log labels, DOM or arbitrary event strings."""
    def enum(value, allowed):
        return value if isinstance(value, str) and value in allowed else 'UNKNOWN'
    events = raw.get('events', [])
    return {'width': width if type(width) is int and width in (360,390,768,1440) else None,
            'stage': enum(stage, ('before-focus','focus','Unicode-keyDown','Unicode-keyUp','reset-focus','reset-Enter')),
            'focus': enum(raw.get('focus'), ('normalize','reset','other')),
            'value': enum(raw.get('value'), ('0','1')),
            'open': raw.get('open') if type(raw.get('open')) is bool else None,
            'events': [{'type': enum(e.get('type'), ('keydown','keypress','keyup','input','change')),
                        'key': enum(e.get('key'), ('Space','ArrowDown','Enter','別','OTHER')),
                        'trusted': e.get('trusted') is True,
                        'target': enum(e.get('target'), ('normalize','reset')),
                        'value': enum(e.get('value'), ('0','1'))}
                       for e in events[:8] if isinstance(e, dict)],
            'truncated': raw.get('truncated') is True or len(events) > 8}


def observe_keyboard(page, stage):
    record = keyboard_record(page.evaluate(KEYBOARD_SNAPSHOT), stage, page.viewport_size['width'])
    try:
        print('LAB_TRACE_KEYBOARD '+json.dumps(record), file=sys.stderr, flush=True)
    except (OSError, ValueError):
        pass
    return record


def assert_key_delivery(records, key, target):
    assert all(not r['truncated'] for r in records)
    events = [e for r in records for e in r['events']]
    keys = [e for e in events if e['type'] in ('keydown','keypress','keyup')]
    assert [(e['type'], e['key'], e['trusted'], e['target']) for e in keys] == [
        (kind, key, True, target) for kind in ('keydown','keypress','keyup')]
    assert all(e['trusted'] and e['target'] == target for e in events)
    return events


def inspect_trace_keyboard(page, source, cases):
    # Browser-generated trusted Unicode typeahead; not physical Japanese/IME
    # input or native-popup navigation. Only attach to this already guarded page.
    assert_trace_initial(page, source)
    page.evaluate(KEYBOARD_OBSERVER)
    try:
        observe_keyboard(page, 'before-focus')
        control = page.locator('#trace-normalize')
        control.focus()
        focused = observe_keyboard(page, 'focus')
        assert focused['focus'] == 'normalize' and focused['value'] == '0'
        assert focused['open'] is False
        session = page.context.new_cdp_session(page)
        try:
            session.send('Input.dispatchKeyEvent', {'type': 'keyDown', 'key': '別',
                         'text': '別', 'unmodifiedText': '別', 'modifiers': 0})
            down = observe_keyboard(page, 'Unicode-keyDown')
            session.send('Input.dispatchKeyEvent', {'type': 'keyUp', 'key': '別', 'modifiers': 0})
            up = observe_keyboard(page, 'Unicode-keyUp')
        finally:
            session.detach()
        events = assert_key_delivery([down, up], '別', 'normalize')
        assert [(e['type'], e['value']) for e in events
                if e['type'] in ('input','change')] == [('input','1'), ('change','1')]
        assert up['focus'] == 'normalize' and up['open'] is False
        assert control.input_value() == '1'
        output = page.locator('#trace-output')
        assert_trace_frame(output.inner_html(), cases[3])
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        bars = output.locator('div[style*="width:"]')
        for i, key in enumerate(['original_score','raw_score','rescored']):
            ratio = bars.nth(i).evaluate('(e)=>e.getBoundingClientRect().width/e.parentElement.getBoundingClientRect().width')
            assert abs(ratio-cases[3][key]) < .001
        reset = page.locator('#trace-reset')
        reset.focus()
        assert observe_keyboard(page, 'reset-focus')['focus'] == 'reset'
        reset.press('Enter')
        assert_key_delivery([observe_keyboard(page, 'reset-Enter')], 'Enter', 'reset')
        assert_trace_initial(page, source)
    finally:
        page.evaluate(KEYBOARD_CLEANUP)

def inspect_trace(page, source):
    data=json.loads(source.read_text()); cases=data['synthetic']
    assert len(cases)==12
    assert_trace_initial(page,source)
    assert '2610.11678' in page.locator('body').inner_text()
    assert '2026-08-02T05:41:14Z' in page.locator('body').inner_text()
    for a,b,n in product(range(3),range(2),range(2)):
        for key,value in zip(['agent','alias','normalize'],[a,b,n],strict=True):
            page.locator('#trace-'+key).select_option(str(value))
        output=page.locator('#trace-output')
        assert_trace_frame(output.inner_html(),cases[a*4+b*2+n])
        output.locator('summary').click()
        assert output.locator('details').evaluate('(e)=>e.open')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        bars=output.locator('div[style*="width:"]')
        for i,key in enumerate(['original_score','raw_score','rescored']):
            ratio=bars.nth(i).evaluate('(e)=>e.getBoundingClientRect().width/e.parentElement.getBoundingClientRect().width')
            assert abs(ratio-cases[a*4+b*2+n][key])<.001
    page.locator('#trace-reset').click()
    assert_trace_initial(page,source)
    inspect_trace_keyboard(page, source, cases)
    assert page.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)')
