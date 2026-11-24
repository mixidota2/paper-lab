"""Exercise evidence gating and protection order without a browser."""
from copy import deepcopy
from types import SimpleNamespace

import pytest

import research_pair_review as m
from review_103_evidence import ProtectionStop


def test_required_cases_need_unique_protected_attestation():
    pairs = [[m.DCDN, 360], [m.ONO, 360], [m.DCDN, 1440], [m.ONO, 1440]]
    assert pairs == m.expected_research_groups()
    m.assert_research_plan({'signed_layout_research_groups': pairs})
    with pytest.raises(AssertionError):
        m.assert_research_plan({})
    with pytest.raises(AssertionError):
        m.assert_research_plan({'signed_layout_research_groups': pairs[:-1]})
    report = [dict(slug=s, width=w, protection=['before-navigation', 'after-navigation', 'after-actions'])
              for s, w in pairs]
    m.assert_research_record(report)
    for broken in ([], report[:-1], report + report[:1], report[:1] + report[:1] + report[2:]):
        with pytest.raises(AssertionError):
            m.assert_research_record(broken)
    broken = deepcopy(report)
    broken[0]['protection'].pop()
    with pytest.raises(AssertionError):
        m.assert_research_record(broken)


@pytest.mark.parametrize('stop, expected', [
    (0, ['guard']), (1, ['guard', 'goto', 'guard']),
    (2, ['guard', 'goto', 'guard', 'settled', 'heading', 'width', 'actions', 'overflow', 'guard']),
    (None, ['guard', 'goto', 'guard', 'settled', 'heading', 'width', 'actions', 'overflow', 'guard']),
])
def test_protection_blocks_interaction_or_result_on_failure(monkeypatch, stop, expected):
    ops = []
    browser = object()

    def guard(candidate):
        assert candidate is browser
        n = ops.count('guard')
        ops.append('guard')
        if n == stop:
            raise ProtectionStop('unprotected synthetic test')

    def go(url):
        assert url == f'http://127.0.0.1:1234/papers/{m.DCDN}.html'
        ops.append('goto')
        return SimpleNamespace(ok=True)

    def evaluate(js):
        if js == 'innerWidth':
            ops.append('width')
            return 360
        assert js == 'document.documentElement.scrollWidth<=innerWidth'
        ops.append('overflow')
        return True

    monkeypatch.setattr(m, 'dcdn_checks', lambda _: ops.append('actions'))
    def invoke():
        return m.protected_research(SimpleNamespace(goto=go, evaluate=evaluate), browser,
                                    'http://127.0.0.1:1234', m.DCDN, 360, guard,
                                    lambda _: ops.append('settled'), lambda _: ops.append('heading'))

    if stop is None:
        assert invoke() == {'slug': m.DCDN, 'width': 360,
                            'protection': ['before-navigation', 'after-navigation', 'after-actions']}
    else:
        with pytest.raises(ProtectionStop):
            invoke()
    assert ops == expected
