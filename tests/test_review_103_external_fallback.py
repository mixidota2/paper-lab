"""Offline controls for bounded, HTTP-only source reachability checks."""
import importlib.util
from pathlib import Path
import sys
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

import unittest
import tempfile

spec = importlib.util.spec_from_file_location('external_fallback_under_test', Path(__file__).with_name('review_103_external.py'))
external = importlib.util.module_from_spec(spec)
spec.loader.exec_module(external)
URL = 'https://example.test/paper.pdf'


def error(status):
    return HTTPError(URL, status, 'test response', {}, None)


def response(status=200):
    r = MagicMock()
    r.status, r.url = status, URL
    r.__enter__.return_value = r
    r.read.return_value = b'%PDF-test'
    return r


def check_method_failure_falls_back_to_small_same_url_get(head_status):
    r = response()
    with patch.object(external, 'urlopen', side_effect=[error(head_status), r]) as opener:
        result = external.check_url(URL)
    assert result['result'] == 'CONFIRMED HTTP reachability only'
    assert result['head_status'] == head_status
    assert result['fallback_method'] == result['method'] == 'GET'
    assert result['status'] == 200
    assert [c.args[0].get_method() for c in opener.call_args_list] == ['HEAD', 'GET']
    assert all(c.args[0].full_url == URL for c in opener.call_args_list)
    assert 0 < opener.call_args_list[1].kwargs['timeout'] <= 8
    r.read.assert_called_once_with(1024)
    r.__exit__.assert_called_once()


def test_get_404_stays_unconfirmed():
    with patch.object(external, 'urlopen', side_effect=[error(404), error(404)]) as opener:
        result = external.check_url(URL)
    assert opener.call_count == 2
    assert result['result'] == 'NOT CONFIRMED'
    assert result['status'] == result['head_status'] == 404
    assert result['fallback_method'] == 'GET'


def check_access_restrictions_and_other_errors_do_not_fall_back(status):
    with patch.object(external, 'urlopen', side_effect=error(status)) as opener:
        result = external.check_url(URL)
    opener.assert_called_once()
    assert result['result'] == 'NOT CONFIRMED'
    assert result['head_status'] == status
    assert 'fallback_method' not in result


def test_head_timeout_does_not_retry():
    with patch.object(external, 'urlopen', side_effect=TimeoutError('timed out')) as opener:
        result = external.check_url(URL)
    opener.assert_called_once()
    assert opener.call_args.kwargs['timeout'] == 8
    assert result['result'] == 'NOT CONFIRMED'


def test_get_timeout_uses_only_remaining_budget():
    with patch.object(external.time, 'monotonic', side_effect=[100, 106]), patch.object(external, 'urlopen', side_effect=[error(404), TimeoutError('timed out')]) as opener:
        result = external.check_url(URL)
    assert opener.call_args.kwargs['timeout'] == 2
    assert result['result'] == 'NOT CONFIRMED'


def test_no_get_after_url_budget_expires():
    with patch.object(external.time, 'monotonic', side_effect=[100, 108]), patch.object(external, 'urlopen', side_effect=error(404)) as opener:
        result = external.check_url(URL)
    opener.assert_called_once()
    assert result['result'] == 'NOT CONFIRMED'


def test_late_read_is_not_claimed_successful():
    r = response()
    with patch.object(external.time, 'monotonic', side_effect=[100, 101, 108]), patch.object(external, 'urlopen', side_effect=[error(404), r]):
        result = external.check_url(URL)
    assert result['result'] == 'NOT CONFIRMED'
    r.__exit__.assert_called_once()


def check_total_parent_budget_still_kills_stalled_worker(tmp_path):
    rows, summary = external.bounded_check([URL], tmp_path, budget_seconds=0.1,
        command=[sys.executable, '-c', 'import time; time.sleep(30)'])
    assert summary['timed_out']
    assert summary['elapsed_seconds'] < 3
    assert rows[0]['result'] == 'NOT CONFIRMED'


class FallbackTests(unittest.TestCase):
    def test_method_failures(self):
        for status in (404, 405, 501):
            with self.subTest(status=status):
                check_method_failure_falls_back_to_small_same_url_get(status)

    def test_restrictions(self):
        for status in (401, 403, 429, 500):
            with self.subTest(status=status):
                check_access_restrictions_and_other_errors_do_not_fall_back(status)

    def test_parent_budget(self):
        with tempfile.TemporaryDirectory() as directory:
            check_total_parent_budget_still_kills_stalled_worker(Path(directory))


for name, function in list(globals().items()):
    if name.startswith('test_') and callable(function):
        setattr(FallbackTests, name, lambda self, function=function: function())

del name, function

if __name__ == '__main__':
    unittest.main()
