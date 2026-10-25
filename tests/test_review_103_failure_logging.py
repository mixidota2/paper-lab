"""Bounded failure logging must preserve stopped status and omit raw secrets."""
import json
import subprocess

import pytest

from review_103_evidence import (RunEvidence, console_diagnostic, bounded_stderr,
                                 STDERR_INPUT_LIMIT, STDERR_TEXT_LIMIT)


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
    assert secret not in logged and '?signature=' not in logged and '/private/' not in logged
    assert summary['stderr']['present'] is True and summary['stderr']['truncated'] is False
    assert summary['stderr']['byte_length'] == len(error.stderr.encode('utf-8'))
    assert result['status'] == 'STOPPED' and result['automatic_status'] == 'FAIL'
    assert result['browser'] == 'NOT STARTED' and result['mandatory_recorded'] == 0


@pytest.mark.parametrize('error', [
    RuntimeError('credential=DO_NOT_LOG https://host/?sig=DO_NOT_LOG'),
    subprocess.CalledProcessError(1, VERIFY+['DO_NOT_LOG']),
    subprocess.TimeoutExpired(['other-command','DO_NOT_LOG'],30),
])
def test_unrecognized_details_are_not_emitted(error):
    summary = console_diagnostic(error)
    assert summary['message'] == 'Exception type only; message and stderr omitted from console'
    assert 'stderr' not in summary
    assert 'DO_NOT_LOG' not in json.dumps(summary)


def test_known_command_timeout_is_identifiable():
    error = subprocess.TimeoutExpired(VERIFY,30,stderr='token=DO_NOT_LOG')
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


@pytest.mark.parametrize('raw,present,size,text', [
    (None, False, None, None), ('', True, 0, ''), (b'', True, 0, ''),
    ('Previously unrecognized integrity reason', True, 40,
     'Previously unrecognized integrity reason'),
])
def test_absent_empty_and_unmatched_stderr_are_distinct(raw, present, size, text):
    summary = console_diagnostic(subprocess.CalledProcessError(1, VERIFY, stderr=raw))
    assert summary['stderr'] == {
        'present': present, 'byte_length': size, 'truncated': False, 'text': text}
    assert summary['recognized_stderr_reasons'] == []


def test_multiline_bytes_preserve_ordinary_codesign_paths_and_reason():
    raw = ('/Applications/Google Chrome.app: unexpected integrity diagnostic\n'
           'In subcomponent: /Applications/Google Chrome.app/Contents/Frameworks/test\n'
           '理由: 署名対象が一致しない\n').encode('utf-8')
    result = bounded_stderr(raw)
    assert result['text'] == raw.decode() and result['byte_length'] == len(raw)
    assert result['truncated'] is False
    assert bounded_stderr(raw.decode()) == result


@pytest.mark.parametrize('raw', [b'x'*(STDERR_INPUT_LIMIT+1), '界'*(STDERR_INPUT_LIMIT+1),
                               'y'*(STDERR_TEXT_LIMIT+1)])
def test_input_and_output_caps(raw):
    result = bounded_stderr(raw)
    size = len(raw if isinstance(raw, bytes) else raw.encode('utf-8'))
    assert result['byte_length'] == size and result['truncated'] is True
    assert len(result['text'].encode('utf-8')) <= STDERR_TEXT_LIMIT


@pytest.mark.parametrize('raw,secrets', [
    ('token=ABCSECRET api_key: "KEY SECRET" password=PASSSECRET',
     ['ABCSECRET','KEY SECRET','PASSSECRET']),
    ('Authorization: Bearer BEARERSECRET\nBearer "QUOTED SECRET"',
     ['BEARERSECRET','QUOTED SECRET']),
    ('https://alice:PWSECRET@host/path?sig=QUERYSECRET#FRAGMENTSECRET',
     ['alice','PWSECRET','QUERYSECRET','FRAGMENTSECRET']),
    ('https://host/path#ONLYFRAGMENT', ['ONLYFRAGMENT']),
    ('/Users/Alice Smith/Library/file\n/home/bob/.cache/file\nC:\\Users\\Carol Doe\\file\n~dave/file',
     ['Alice Smith','bob','Carol Doe','dave']),
    ('\x1b[31mtok\u200ben=ANSI_SECRET\x1b[0m\n'
     '\x1b]8;;https://host/?sig=OSC_SECRET\x07link\x1b]8;;\x07\r\x00',
     ['ANSI_SECRET','OSC_SECRET']),
    ('prefix\n"access_token": "JSON SECRET", X-Amz-Signature=SIGSECRET',
     ['JSON SECRET','SIGSECRET']),
])
def test_redaction_and_terminal_control_removal(raw, secrets):
    text = bounded_stderr(raw)['text']
    assert all(secret not in text for secret in secrets)
    assert '\x1b' not in text and '\x00' not in text and '\r' not in text and '\u200b' not in text


def test_redaction_precedes_output_truncation():
    raw = 'x'*(STDERR_TEXT_LIMIT-20)+' token='+'SECRET'*2000
    result = bounded_stderr(raw)
    assert result['truncated'] is True and 'SECRET' not in result['text']


@pytest.mark.parametrize('prefix', ['password="', "token='", 'Bearer "'])
def test_unterminated_secret_quotes_at_input_cap(prefix):
    raw = prefix+'FIRST SECRET '+('MORE SECRET '*STDERR_INPUT_LIMIT)
    result = bounded_stderr(raw)
    assert result['truncated'] is True
    assert 'SECRET' not in result['text']


def test_unknown_command_never_processes_stderr(monkeypatch):
    import review_103_evidence
    def forbidden(raw):
        raise AssertionError('unrecognized stderr must not be inspected')
    monkeypatch.setattr(review_103_evidence, 'bounded_stderr', forbidden)
    error = subprocess.CalledProcessError(1, VERIFY+['--extra'], stderr='DO_NOT_LOG')
    assert 'stderr' not in console_diagnostic(error)


@pytest.mark.parametrize('raw', [
    'Authorization: Basic dXNlcjpwYXNzd29yZA==',
    'authorization: bAsIc\t  dXNlcjpwYXNzd29yZA==',
    'Authorization: Basic "dXNlcjpwYXNzd29yZA=="',
    "Authorization: Basic 'dXNlcjpwYXNzd29yZA=='",
    '"Authorization": "Basic dXNlcjpwYXNzd29yZA=="',
    'Proxy-Authorization: BASIC\n dXNlcjpwYXNzd29yZA==',
])
def test_basic_authorization_payload_is_fully_redacted(raw):
    summary = console_diagnostic(subprocess.CalledProcessError(1, VERIFY, stderr=raw))
    assert 'dXNlcjpwYXNzd29yZA==' not in json.dumps(summary)
    assert '[REDACTED]' in summary['stderr']['text']
