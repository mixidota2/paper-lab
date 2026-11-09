"""Offline retry contracts: never turn denied access or mismatches into success."""
import json
from pathlib import Path
import urllib.error
from unittest.mock import patch

import pytest
import yaml
from tools import compare_publication as subject


def run_case(tmp_path, events):
    site = tmp_path / 'site'
    site.mkdir()
    (site / 'index.html').write_bytes(b'<html></html>')
    (site / '.nojekyll').write_bytes(b'')
    manifest = tmp_path / 'manifest.json'
    digest = subject.write_manifest(site, 'a' * 40, manifest)
    out = tmp_path / 'evidence'
    calls, waits = [], []
    pending = iter(events)

    def fetch(url, size, timeout):
        if url.endswith('.nojekyll'):
            return b'', {'http_status': 200, 'final_url': url}
        calls.append(url)
        event = next(pending)
        if isinstance(event, tuple):
            code, headers, error_url = event
            raise urllib.error.HTTPError(error_url or url, code, 'fixture', headers, None)
        if isinstance(event, Exception):
            raise event
        if event == 'unsafe':
            return b'<html></html>', {'http_status': 200, 'final_url': 'https://evil.invalid/x'}
        return event, {'http_status': 200, 'final_url': url}

    def sleep(seconds):
        # Early errors must already be durable when waiting starts.
        ledger = json.loads((out / 'attempts' / (subject.sha256(b'index.html') + '.json')).read_text())
        assert ledger['attempts'][-1]['wait_seconds'] == seconds
        assert ledger['attempts'][0]['http_status'] in (502, 503, 504)
        waits.append(seconds)

    with patch('socket.create_connection', side_effect=AssertionError('network forbidden')):
        code = subject.check(site, manifest, digest, out, fetcher=fetch, sleeper=sleep, workers=1)
    report = json.loads((out / 'result.json').read_text())
    assert report['expected_files'] == 2
    assert sum(report['counts'].values()) == 2
    assert report['expected_build_unchanged']
    assert report['links']['issues'] == []
    assert (out / 'received/.nojekyll').read_bytes() == b''
    record = next(x for x in report['files'] if x['path'] == 'index.html')
    assert len(record['attempts']) == len(calls)
    for attempt in record['attempts']:
        assert attempt['started_at'] <= attempt['finished_at']
        assert 'retry_decision' in attempt
    return code, report, record, waits


@pytest.mark.parametrize('status', [502, 503, 504])
def test_transient_recovery_keeps_first_failure(tmp_path, status):
    code, report, record, waits = run_case(tmp_path, [(status, {}, None), b'<html></html>'])
    assert code == 0 and report['counts'] == {'match': 2, 'mismatch': 0, 'fetch_failed': 0}
    assert waits == [1]
    assert [a['status'] for a in record['attempts']] == ['fetch_failed', 'match']
    assert record['attempts'][0]['http_status'] == status
    assert 'error' not in record


def test_persistent_503_stops_at_three(tmp_path):
    code, report, record, waits = run_case(tmp_path, [(503, {}, None)] * 3)
    assert code == 3 and report['counts']['fetch_failed'] == 1
    assert len(record['attempts']) == 3 and waits == [1, 2]


@pytest.mark.parametrize('event', [
    (401, {}, None), (403, {}, None), (404, {}, None), (429, {}, None),
    (500, {}, None), (503, {'Retry-After': '1'}, None),
    (503, {'Retry-After': 'invalid'}, None),
    (503, {}, 'https://evil.invalid/x'), 'unsafe',
    b'<html>wrong!', TimeoutError('fixture'), ValueError('security violation'),
    RuntimeError('fixture'),
])
@pytest.mark.parametrize('preceded_by_transient', [False, True])
def test_terminal_outcomes_never_retry(tmp_path, event, preceded_by_transient):
    events = ([(502, {}, None)] if preceded_by_transient else []) + [event]
    code, report, record, waits = run_case(tmp_path, events)
    assert code == 3
    assert len(record['attempts']) == len(events)
    assert waits == ([1] if preceded_by_transient else [])
    expected = 'mismatch' if isinstance(event, bytes) else 'fetch_failed'
    assert record['status'] == expected and report['counts'][expected] == 1


def test_evidence_upload_preserves_hidden_files_with_narrow_paths():
    workflow = yaml.safe_load((Path(__file__).parents[1] / '.github/workflows/pages.yml').read_text())
    job = workflow['jobs']['verify-publication']
    uploads = [s for s in job['steps'] if s.get('uses') == 'actions/upload-artifact@v4']
    assert len(uploads) == 1
    step = uploads[0]
    assert step['if'] == 'always()'
    assert step['with']['include-hidden-files'] is True
    assert step['with']['path'].split() == ['publication-evidence/', 'publication-diagnostics/']
    assert step['with']['if-no-files-found'] == 'error'
    assert job['permissions'] == {'contents': 'read'}
