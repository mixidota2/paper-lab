"""Console diagnostics cannot expose application exception data or change gates."""
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_103_evidence import RunEvidence, case_diagnostic, case_summary
from review_103_report import validation
import trace_review


def plan():
    source = Path(trace_review.__file__)
    return {'required_cases': ['trace-360'], 'semantic_groups': [['trace-verifier-brittleness', 360]],
            'source_hashes': {source.name: hashlib.sha256(source.read_bytes()).hexdigest()},
            'page_hashes': {'public': 'hash'}}


def test_approved_source_and_no_exception_data():
    try:
        trace_review.assert_trace_frame('SECRET https://private/?token=secret /home/private', {})
    except Exception as error:
        result = case_diagnostic(error, 'trace-360', plan())
    assert result == {'case': 'trace-360', 'type': 'KeyError',
                      'source': {'file': 'trace_review.py', 'line': 35, 'function': 'assert_trace_frame'}}
    assert 'SECRET' not in json.dumps(result)


def test_unknown_identifiers_and_stale_source():
    class PrivateSecretError(Exception):
        pass
    try:
        raise PrivateSecretError('secret URL environment DOM')
    except Exception as error:
        result = case_diagnostic(error, 'private/token=secret', plan())
    assert result == {'case': 'UNKNOWN', 'type': 'Exception', 'source': None}
    try:
        trace_review.assert_trace_frame('', {})
    except Exception as error:
        p = plan(); p['source_hashes']['trace_review.py'] = 'stale'
        assert case_diagnostic(error, 'trace-360', p)['source'] is None


def test_summary_bounds_and_unknown_planned_strings():
    p = plan(); p['required_cases'] = ['trace-'+str(i) for i in range(399)]
    p['semantic_groups'] = [['private?token=secret', 999999]] * 399
    report = {'cases': [{'name': n, 'status': 'FAIL', 'message': 'SECRET'} for n in p['required_cases']]}
    summary = case_summary(report, p)
    assert summary['failed_count'] == 399
    assert len(summary['failed']) == 12
    assert summary['missing_semantic_count'] == 399
    assert summary['missing_semantic'] == [['UNKNOWN', None]] * 12
    assert summary['truncated']
    assert len(json.dumps(summary)) < 8192
    assert 'secret' not in json.dumps(summary).lower()
    assert case_summary({}, p)['missing_case_count'] == 399


def test_finalize_preserves_failure_and_no_leak(tmp_path, capsys):
    p = plan(); evidence = RunEvidence(tmp_path, p)
    def fail():
        raise AssertionError('SECRET https://private/?token=x /home/private DOM')
    evidence.case('trace-360', fail)
    evidence.report['browser'] = 'EXECUTED'
    before = validation({**evidence.report, 'execution_completed': True}, p)
    result = evidence.finalize(True)
    assert result['automatic_status'] == 'FAIL'
    assert result['errors'] == before['errors']
    out = capsys.readouterr().err
    assert out.startswith('LAB_REVIEW_CASES ')
    assert 'SECRET' not in out and 'https://' not in out and '/home/' not in out
    summary = json.loads(out.removeprefix('LAB_REVIEW_CASES '))
    assert summary['failed_count'] == 1 and summary['missing_case_count'] == 0
    assert summary['missing_semantic_count'] == 1


def test_success_summary_does_not_add_acceptance(tmp_path, capsys):
    p = plan(); evidence = RunEvidence(tmp_path, p)
    evidence.case('trace-360', lambda: None)
    evidence.report['action_checks'] = [{'slug': 'trace-verifier-brittleness', 'width': 360, 'status': 'CONFIRMED: assertion'}]
    result = evidence.finalize(True)
    assert result['automatic_status'] == 'PASS'
    assert result['publication_decision'] == 'PENDING'
    assert json.loads(capsys.readouterr().err.removeprefix('LAB_REVIEW_CASES '))['failed_count'] == 0


def test_forged_saved_diagnostic_cannot_leak():
    p = plan()
    report = {'cases': [{'name': 'private?secret', 'status': 'FAIL',
                        'safe_case': {'case': 'secret', 'type': 'SecretException',
                                      'source': {'file': '/private/secret', 'line': 'secret',
                                                 'function': 'secret'}, 'extra': 'secret'}}]}
    result = case_summary(report, p)
    assert result['failed'] == [{'case': 'UNKNOWN', 'type': 'Exception', 'source': None}]
    assert 'secret' not in json.dumps(result).lower()


def test_closed_stderr_preserves_failed_report_and_return(tmp_path, monkeypatch):
    import io
    import review_103_evidence
    p = plan(); evidence = RunEvidence(tmp_path, p)
    def fail():
        raise AssertionError('not for console')
    evidence.case('trace-360', fail)
    closed = io.StringIO(); closed.close()
    monkeypatch.setattr(review_103_evidence.sys, 'stderr', closed)
    result = evidence.finalize(True)
    assert result['automatic_status'] == 'FAIL'
    assert result['status'] == 'FAIL'
    assert json.loads((tmp_path / 'report.json').read_text()) == result
    assert (tmp_path / 'index.html').is_file()
