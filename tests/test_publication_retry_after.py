"""Deterministic HTTP headers and clock; no remote requests or actual sleeps."""
import datetime as dt
from email.message import Message
import json
import urllib.error
from unittest.mock import patch

import pytest
from tools import compare_publication as m

START = dt.datetime(2026, 11, 9, 6, 0, 0, tzinfo=dt.timezone.utc)


def header(*values, name='Retry-After'):
    h = Message()
    for value in values:
        h[name] = value
    h['Set-Cookie'] = 'DO-NOT-RECORD'
    return h


def execute(tmp_path, headers, status=503, error_url=None, interrupt=False, advance=True):
    site = tmp_path / 'site'; site.mkdir()
    raw = b'<html></html>'
    (site / 'index.html').write_bytes(raw)
    manifest = tmp_path / 'manifest.json'
    digest = m.write_manifest(site, 'a' * 40, manifest)
    out = tmp_path / 'out'
    current = START
    calls, waits = [], []
    ledger = out / 'attempts' / (m.sha256(b'index.html') + '.json')

    def clock():
        return current

    def fetch(url, size, timeout):
        calls.append(current)
        if len(calls) == 1:
            raise urllib.error.HTTPError(error_url or url, status, 'fixture', headers, None)
        return raw, {'http_status': 200, 'final_url': url}

    def sleep(seconds):
        nonlocal current
        saved = json.loads(ledger.read_text())
        assert saved['attempts'][0]['http_status'] == status
        assert saved['attempts'][0]['retry_after']['value_count'] >= 1
        assert saved['attempts'][0]['wait_seconds'] == seconds
        waits.append(seconds)
        if interrupt:
            raise KeyboardInterrupt('fixture')
        if advance:
            current += dt.timedelta(seconds=seconds)

    with patch('socket.create_connection', side_effect=AssertionError('no network')):
        if interrupt:
            with pytest.raises(KeyboardInterrupt):
                m.check(site, manifest, digest, out, fetcher=fetch, sleeper=sleep, clock=clock, workers=1)
            report = json.loads(ledger.read_text())
            assert report['attempts'][0]['retry_decision'] == 'retry_transient_http'
            assert len(calls) == 1
            return None, report, calls, waits
        code = m.check(site, manifest, digest, out, fetcher=fetch, sleeper=sleep, clock=clock, workers=1)
    report = json.loads((out / 'result.json').read_text())
    assert report['expected_files'] == 1 and sum(report['counts'].values()) == 1
    assert report['expected_build_unchanged']
    assert 'DO-NOT-RECORD' not in (out / 'result.json').read_text()
    assert 'DO-NOT-RECORD' not in ledger.read_text()
    return code, report['files'][0], calls, waits


@pytest.mark.parametrize('value,wait,fmt', [
    ('0', 1, 'delta-seconds'), ('2', 2, 'delta-seconds'),
    ('5', 5, 'delta-seconds'),
    ('Mon, 09 Nov 2026 06:00:03 GMT', 3, 'IMF-fixdate'),
    ('Mon, 09 Nov 2026 06:00:05 GMT', 5, 'IMF-fixdate'),
    ('Mon, 09 Nov 2026 05:59:59 GMT', 1, 'IMF-fixdate'),
])
def test_valid_server_wait_is_never_shortened(tmp_path, value, wait, fmt):
    code, rec, calls, waits = execute(tmp_path, header(value, name='rEtRy-AfTeR'))
    assert code == 0 and waits == [wait] and calls == [START, START + dt.timedelta(seconds=wait)]
    first = rec['attempts'][0]
    assert first['retry_after']['values'][0]['value'] == value
    assert first['retry_after']['format'] == fmt
    assert dt.datetime.fromisoformat(first['not_before']) <= calls[1]
    assert first['wait_finished_at'] == calls[1].isoformat()
    assert first['wait_reason'] == 'server_and_backoff'


@pytest.mark.parametrize('values,reason', [
    (['6'], 'exceeds_wait_limit'),
    (['999999999999999999999999'], 'exceeds_wait_limit'),
    (['Mon, 09 Nov 2026 06:00:06 GMT'], 'exceeds_wait_limit'),
    (['1', '1'], 'duplicate'), (['1', '2'], 'duplicate'),
    (['1, 2'], 'invalid_or_unsupported'), ([''], 'invalid_or_unsupported'),
    (['-1'], 'invalid_or_unsupported'), (['1.5'], 'invalid_or_unsupported'),
    (['tomorrow'], 'invalid_or_unsupported'),
    (['Tue, 09 Nov 2026 06:00:03 GMT'], 'invalid_or_unsupported'),
    (['Monday, 09-Nov-26 06:00:03 GMT'], 'invalid_or_unsupported'),
    (['Mon, 09 Nov 2026 06:00:03 UTC'], 'invalid_or_unsupported'),
    (['x' * 129], 'invalid_or_too_long'),
])
def test_ambiguous_invalid_or_long_values_stop_and_remain_evidence(tmp_path, values, reason):
    code, rec, calls, waits = execute(tmp_path, header(*values))
    assert code == 3 and len(calls) == 1 and waits == []
    evidence = rec['attempts'][0]['retry_after']
    assert evidence['interpretation'] == reason
    assert evidence['value_count'] == len(values)
    assert evidence['values'][0]['value'] == values[0][:128]
    if len(values[0]) > 128:
        assert evidence['values'][0]['sha256'] == m.sha256(values[0].encode())
        assert evidence['values'][0]['truncated']


@pytest.mark.parametrize('status', [401, 403, 404, 429, 500])
def test_header_does_not_authorize_other_status(tmp_path, status):
    code, rec, calls, waits = execute(tmp_path, header('2'), status=status)
    assert code == 3 and len(calls) == 1 and waits == []
    assert rec['attempts'][0]['retry_after']['values'][0]['value'] == '2'


def test_unsafe_url_with_header_never_retries(tmp_path):
    code, rec, calls, waits = execute(tmp_path, header('2'), error_url='https://evil.invalid/')
    assert code == 3 and len(calls) == 1 and not waits
    assert rec['attempts'][0]['retry_decision'] == 'stop_unsafe_error_url'


def test_interrupted_wait_keeps_atomic_first_failure(tmp_path):
    execute(tmp_path, header('5'), interrupt=True)


def test_clock_not_reaching_deadline_stops_without_second_get(tmp_path):
    code, rec, calls, waits = execute(tmp_path, header('2'), advance=False)
    assert code == 3 and len(calls) == 1 and waits == [2]
    assert rec['attempts'][0]['retry_decision'] == 'stop_clock_before_deadline'


def test_capture_limits_and_case_insensitive_mapping():
    evidence = m.retry_after(header(*(['1'] * 12)), START)
    assert evidence['interpretation'] == 'duplicate'
    assert evidence['value_count'] == 12 and len(evidence['values']) == 8
    assert evidence['omitted_values'] == 4
    assert m.retry_after({'retry-after': '2'}, START)['minimum_delay_seconds'] == 2
    assert m.retry_after({'Retry-After': '2', 'retry-after': '3'}, START)['interpretation'] == 'duplicate'


def test_three_attempt_limit_with_server_headers_and_backoff(tmp_path):
    site = tmp_path / 'site'; site.mkdir()
    (site / 'index.html').write_bytes(b'<html></html>')
    manifest = tmp_path / 'manifest.json'
    digest = m.write_manifest(site, 'a' * 40, manifest)
    out = tmp_path / 'out'
    current = START
    calls, waits = [], []

    def fetch(url, size, timeout):
        calls.append(current)
        raise urllib.error.HTTPError(url, 504, 'fixture', header('0'), None)

    def sleep(seconds):
        nonlocal current
        waits.append(seconds)
        current += dt.timedelta(seconds=seconds)

    code = m.check(site, manifest, digest, out, fetcher=fetch, sleeper=sleep, clock=lambda: current)
    assert code == 3 and len(calls) == 3 and waits == [1, 2]
    record = json.loads((out / 'result.json').read_text())['files'][0]
    assert record['attempts'][-1]['retry_decision'] == 'stop_attempt_limit'
    assert all(a['retry_after']['values'][0]['value'] == '0' for a in record['attempts'])
