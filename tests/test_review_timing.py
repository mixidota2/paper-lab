"""Timing diagnostics must retain failure and capture semantics."""
import json
import pytest
import review_103_capture as c
from review_103_evidence import RunEvidence, ProtectionStop


def test_phase_accumulates_and_preserves_error(monkeypatch):
    ticks=iter([1.,3.,4.,7.]);monkeypatch.setattr(c.time,'monotonic',lambda:next(ticks))
    timing={}
    with c.timed_phase(timing,'readiness'):pass
    error=RuntimeError('original')
    with pytest.raises(RuntimeError) as caught:
        with c.timed_phase(timing,'readiness'):raise error
    assert caught.value is error
    assert timing=={'readiness':{'count':2,'elapsed_s':5.}}


@pytest.mark.parametrize('failure',[False,True])
def test_capture_timing_return_and_error(tmp_path,monkeypatch,failure):
    error=ValueError('original');result={'tiles':[]}
    def capture(*args):
        if failure:raise error
        return result
    monkeypatch.setattr(c,'_capture',capture)
    if failure:
        with pytest.raises(ValueError) as caught:c.capture(None,tmp_path)
        assert caught.value is error
    else:assert c.capture(None,tmp_path) is result
    receipt=json.loads((tmp_path/'capture-timing.json').read_text())
    assert receipt['elapsed_s']>=0 and receipt['phases']=={}


def test_timing_write_failure_does_not_replace_original(tmp_path,monkeypatch):
    error=RuntimeError('original')
    def fail(*args):raise error
    monkeypatch.setattr(c,'_capture',fail)
    with pytest.raises(RuntimeError) as caught:c.capture(None,tmp_path/'absent')
    assert caught.value is error


@pytest.mark.parametrize('outcome',['PASS','FAIL','STOP'])
def test_current_case_persisted_before_execution_and_timed_after(tmp_path,outcome):
    evidence=RunEvidence(tmp_path,{'required_cases':['case']})
    def run():
        saved=json.loads((tmp_path/'report.json').read_text())
        assert saved['current_case_timing']['case']=='case'
        assert not saved['cases']
        if outcome=='FAIL':raise AssertionError('failure')
        if outcome=='STOP':raise ProtectionStop('stop')
    if outcome=='STOP':
        with pytest.raises(ProtectionStop):evidence.case('case',run)
    else:evidence.case('case',run)
    saved=json.loads((tmp_path/'report.json').read_text())
    assert saved['current_case_timing'] is None
    assert saved['case_timings']['case']['elapsed_s']>=0
    assert saved['cases']==[] if outcome=='STOP' else saved['cases'][0]['status']==outcome


def test_unplanned_id_not_copied_into_timing(tmp_path):
    evidence=RunEvidence(tmp_path,{'required_cases':['case']})
    evidence.case('untrusted',lambda:None)
    assert evidence.report.get('case_timings',{})=={}
