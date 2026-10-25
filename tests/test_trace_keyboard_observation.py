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


class Control:
    def __init__(self, page, selector):
        self.page, self.selector = page, selector
    def focus(self):
        self.page.focus = self.selector
    def press(self, key):
        p = self.page; p.presses.append((self.selector, key))
        if self.selector == '#trace-normalize' and key == 'Enter' and p.mode != 'no-selection':
            p.value = '1'
            p.html = toy.frame(CASES[2 if p.mode == 'stale-output' else 3])
        if self.selector == '#trace-reset' and p.mode != 'no-reset':
            p.value = '0'; p.html = toy.frame(CASES[2])
    def input_value(self):
        return {'#trace-agent': '0', '#trace-alias': '1', '#trace-normalize': self.page.value}[self.selector]
    def inner_html(self):
        return self.page.html


class Page:
    viewport_size = {'width': 360}
    def __init__(self, mode):
        self.mode = mode; self.value = '0'; self.html = toy.frame(CASES[2])
        self.focus = None; self.presses = []; self.cleaned = False
    def locator(self, selector):
        return Control(self, selector)
    def evaluate(self, script):
        if script == review.KEYBOARD_CLEANUP:
            self.cleaned = True
        elif script == review.KEYBOARD_SNAPSHOT:
            return {'value': self.value, 'focus': {'#trace-normalize': 'normalize', '#trace-reset': 'reset'}.get(self.focus, 'other'),
                    'events': [], 'truncated': False}
        else:
            assert script == review.KEYBOARD_OBSERVER


@pytest.mark.parametrize('mode', ['no-selection', 'stale-output', 'no-reset'])
def test_original_gates_still_reject(mode, capsys):
    page = Page(mode)
    with pytest.raises(AssertionError):
        review.inspect_trace_keyboard(page, SOURCE / 'results.json', CASES)
    assert page.cleaned
    records = [json.loads(line.split(' ', 1)[1]) for line in capsys.readouterr().err.splitlines()]
    assert records[0]['value'] == '0'
    assert records[1]['focus'] == 'normalize'
    assert records[4]['stage'] == 'Enter'
    assert records[4]['value'] == ('0' if mode == 'no-selection' else '1')
    assert page.presses[:3] == [('#trace-normalize', k) for k in ('Space', 'ArrowDown', 'Enter')]


def test_mock_success_preserves_reset_and_records_stages(capsys):
    page = Page('success')
    review.inspect_trace_keyboard(page, SOURCE / 'results.json', CASES)
    assert page.cleaned and page.value == '0'
    assert page.presses[-1] == ('#trace-reset', 'Enter')
    records = [json.loads(line.split(' ', 1)[1]) for line in capsys.readouterr().err.splitlines()]
    assert [r['stage'] for r in records] == ['before-focus','focus','Space','ArrowDown','Enter','reset-focus','reset-Enter']
    assert records[-1]['value'] == '0'


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
    raw['events'] = [{'type': 'keydown', 'key': 'Space', 'target': 'normalize', 'value': '0', 'trusted': True}]
    assert review.keyboard_record(raw, 'Space', 360)['events'] == raw['events']


def test_closed_console_does_not_change_mock_gate(tmp_path, monkeypatch):
    import io
    closed = io.StringIO(); closed.close()
    monkeypatch.setattr(review.sys, 'stderr', closed)
    with pytest.raises(AssertionError):
        review.inspect_trace_keyboard(Page('no-selection'), SOURCE / 'results.json', CASES)
