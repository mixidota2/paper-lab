"""Bounded failure logging must preserve stopped status and omit raw secrets."""
import json
import subprocess

import pytest

from review_103_evidence import RunEvidence, console_diagnostic


VERIFY = ['/usr/bin/codesign', '--verify', '--deep', '--strict', '--verbose=2',
          '/Applications/Google Chrome.app']


def test_codesign_stop_logs_same_safe_fields_as_artifact(tmp_path, capsys):
    secret = 'TOKEN_DO_NOT_LOG'
    error = subprocess.CalledProcessError(1, VERIFY, stderr=(
        'a sealed resource is missing or invalid\nfile modified: /private/'+secret+
        '\nhttps://example.invalid/?signature='+secret))
    evidence = RunEvidence(tmp_path, {})
    interruption = {**evidence.diagnostic(error), 'kind': 'interruption', 'phase': 'startup'}
    result = evidence.finalize(False, interruption)
    logged = capsys.readouterr().err
    summary = json.loads(logged.removeprefix('LAB_REVIEW_STOP '))
    assert summary == json.loads((tmp_path/'stopped.json').read_text())['console']
    assert summary == result['interruption']['console']
    assert summary['type'] == 'CalledProcessError' and summary['returncode'] == 1
    assert summary['message'] == str(error)
    assert summary['recognized_stderr_reasons'] == [
        'a sealed resource is missing or invalid', 'file modified']
    assert secret not in logged and 'https://' not in logged and '/private/' not in logged
    assert result['status'] == 'STOPPED' and result['automatic_status'] == 'FAIL'
    assert result['browser'] == 'NOT STARTED' and result['mandatory_recorded'] == 0


@pytest.mark.parametrize('error', [
    RuntimeError('credential=DO_NOT_LOG https://host/?sig=DO_NOT_LOG'),
    subprocess.CalledProcessError(1, VERIFY+['DO_NOT_LOG']),
    subprocess.TimeoutExpired(['other-command','DO_NOT_LOG'],30),
])
def test_unrecognized_details_are_not_emitted(error):
    summary = console_diagnostic(error)
    assert summary['message'] == 'Failure details retained in report.json'
    assert 'DO_NOT_LOG' not in json.dumps(summary)


def test_known_command_timeout_is_identifiable():
    error = subprocess.TimeoutExpired(VERIFY,30,stderr='DO_NOT_LOG')
    summary = console_diagnostic(error)
    assert summary['type'] == 'TimeoutExpired' and summary['message'] == str(error)
    assert 'DO_NOT_LOG' not in json.dumps(summary)


def test_log_stream_failure_does_not_change_stopped_outcome(tmp_path, monkeypatch):
    import review_103_evidence
    class BrokenStream:
        def write(self, text):
            raise OSError('injected closed log stream')
    monkeypatch.setattr(review_103_evidence.sys, 'stderr', BrokenStream())
    evidence = RunEvidence(tmp_path, {})
    result = evidence.finalize(False, evidence.diagnostic(RuntimeError('failure')))
    assert result['status'] == 'STOPPED' and result['automatic_status'] == 'FAIL'
    assert (tmp_path/'stopped.json').is_file() and (tmp_path/'report.json').is_file()
