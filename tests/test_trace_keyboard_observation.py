"""Mock gate/diagnostic tests only; no native macOS keyboard evidence."""
import importlib.util
import json
from pathlib import Path
import pytest
import trace_review as review

SOURCE = Path(__file__).resolve().parents[1] / 'papers/trace-verifier-brittleness'
spec = importlib.util.spec_from_file_location('trace_keyboard_toy', SOURCE / 'run.py')
toy = importlib.util.module_from_spec(spec); spec.loader.exec_module(toy)
CASES = json.loads((SOURCE / 'results.json').read_text())['synthetic']


def event(kind, key, value, target='normalize', trusted=True):
    return dict(type=kind, key=key, value=value, target=target, trusted=trusted)


class Control:
    def __init__(self, page, selector):
        self.page, self.selector = page, selector
    def focus(self):
        if self.page.mode != 'wrong-focus':
            self.page.focus = self.selector
    def press(self, key):
        p = self.page; p.presses.append((self.selector, key))
        assert self.selector == '#trace-reset' and key == 'Enter'
        p.events = [event(k, 'Enter', p.value, 'reset') for k in ('keydown','keypress','keyup')]
        if p.mode != 'no-reset':
            p.value = '0'; p.html = toy.frame(CASES[2])
    def input_value(self):
        return {'#trace-agent': '0', '#trace-alias': '1', '#trace-normalize': self.page.value}[self.selector]
    def inner_html(self):
        return self.page.html
    def locator(self, selector):
        assert selector == 'div[style*="width:"]'
        return self
    def nth(self, index):
        self.index = index
        return self
    def evaluate(self, script):
        assert 'getBoundingClientRect' in script
        return 0 if self.page.mode == 'bad-geometry' else CASES[3][['original_score','raw_score','rescored'][self.index]]


class Session:
    def __init__(self, page):
        self.page = page; self.calls = []; self.detached = False
    def send(self, method, args):
        p = self.page; self.calls.append((method, args))
        if p.mode == 'send-error':
            raise RuntimeError('mock transport failure')
        if args['type'] == 'keyDown':
            p.events = [event(k, '別', '0') for k in ('keydown','keypress')]
            if p.mode != 'no-selection':
                p.value = '1'
                p.html = toy.frame(CASES[2 if p.mode == 'stale-output' else 3])
            if p.mode != 'no-change':
                p.events += [event(k, 'OTHER', '1') for k in ('input','change')]
        else:
            p.events = [event('keyup', '別', p.value)]
        if p.mode == 'no-delivery':
            p.events = []
        if p.mode == 'untrusted':
            for e in p.events: e['trusted'] = False
    def detach(self):
        self.detached = True


class Page:
    viewport_size = {'width': 360}
    def __init__(self, mode):
        self.mode = mode; self.value = '0'; self.html = toy.frame(CASES[2])
        self.focus = None; self.presses = []; self.cleaned = False
        self.events = []; self.context = self; self.session = None
    def new_cdp_session(self, page):
        assert page is self
        self.session = Session(self)
        return self.session
    def locator(self, selector):
        return Control(self, selector)
    def evaluate(self, script):
        if script == review.KEYBOARD_CLEANUP:
            self.cleaned = True
        elif script == review.KEYBOARD_SNAPSHOT:
            events, self.events = self.events, []
            return {'value': self.value, 'open': self.mode == 'open-popup',
                    'focus': {'#trace-normalize': 'normalize', '#trace-reset': 'reset'}.get(self.focus, 'other'),
                    'events': events, 'truncated': False}
        elif script == 'document.documentElement.scrollWidth<=innerWidth':
            return True
        else:
            assert script == review.KEYBOARD_OBSERVER


@pytest.mark.parametrize('mode', ['wrong-focus','open-popup','no-delivery','untrusted',
                                 'no-change','no-selection','stale-output','bad-geometry','no-reset'])
def test_gates_reject_mock_failures(mode):
    page = Page(mode)
    with pytest.raises(AssertionError):
        review.inspect_trace_keyboard(page, SOURCE / 'results.json', CASES)
    assert page.cleaned
    if page.session:
        assert page.session.detached
    else:
        assert mode in ('wrong-focus','open-popup')


def test_mock_success_exact_protocol_and_reset(capsys):
    page = Page('success')
    review.inspect_trace_keyboard(page, SOURCE / 'results.json', CASES)
    assert page.cleaned and page.value == '0' and page.session.detached
    assert page.session.calls == [
        ('Input.dispatchKeyEvent', {'type':'keyDown','key':'別','text':'別','unmodifiedText':'別','modifiers':0}),
        ('Input.dispatchKeyEvent', {'type':'keyUp','key':'別','modifiers':0})]
    assert page.presses == [('#trace-reset', 'Enter')]
    records = [json.loads(line.split(' ', 1)[1]) for line in capsys.readouterr().err.splitlines()]
    assert [r['stage'] for r in records] == ['before-focus','focus','Unicode-keyDown','Unicode-keyUp','reset-focus','reset-Enter']
    assert records[-1]['value'] == '0'


def test_session_detached_on_send_failure():
    page = Page('send-error')
    with pytest.raises(RuntimeError):
        review.inspect_trace_keyboard(page, SOURCE / 'results.json', CASES)
    assert page.session.detached and page.cleaned


def test_allowlisted_bounded_records_do_not_promote_untrusted_events():
    raw = {'value': 'private-token', 'focus': 'https://private',
           'events': [{'type': 'secret', 'key': 'private', 'target': '/home/private',
                       'value': 'secret', 'trusted': 'true', 'extra': 'secret'}] * 99}
    result = review.keyboard_record(raw, 'private', 999999)
    assert result['width'] is None and result['stage'] == 'UNKNOWN'
    assert result['truncated'] and len(result['events']) == 8
    assert all(e['trusted'] is False for e in result['events'])
    assert 'private' not in json.dumps(result) and 'secret' not in json.dumps(result)
    assert len(json.dumps(result)) < 2048
    raw['events'] = [{'type': 'keydown', 'key': '別', 'target': 'normalize', 'value': '0', 'trusted': True}]
    assert review.keyboard_record(raw, 'Unicode-keyDown', 360)['events'] == raw['events']


def test_closed_console_does_not_change_mock_gate(tmp_path, monkeypatch):
    import io
    closed = io.StringIO(); closed.close()
    monkeypatch.setattr(review.sys, 'stderr', closed)
    with pytest.raises(AssertionError):
        review.inspect_trace_keyboard(Page('no-selection'), SOURCE / 'results.json', CASES)
