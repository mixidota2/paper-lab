"""Body revisions retain the separately reviewed paper overviews and toy data."""
import hashlib
import json
from pathlib import Path

import pytest
import yaml

from prose_preservation import before_forecast_pair_full_rewrite, forecast_pair_full_rewrite_hash

ROOT = Path(__file__).resolve().parents[1]
T0 = 'papers/t0-tsfm-forecasting-with-context/'
RC = 'papers/reasoncast-agentic-demand-forecasting/'


def identity(data):
    return {'sha256': hashlib.sha256(data).hexdigest(),
            'blob': hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()}


def test_each_exact_prose_transition_replays_prior_bytes():
    receipt = ROOT / 'tests/forecast_pair_full_rewrite_hashes.json'
    rows = json.loads(receipt.read_text())['files']
    assert rows.keys() == {slug+n for slug in (RC, T0) for n in ('lab.yaml','README.md','method.md','mapping.md')}
    for p, row in rows.items():
        raw = (ROOT / p).read_bytes()
        initial = before_forecast_pair_full_rewrite(ROOT, p, raw)
        a,b = identity(initial),identity(raw)
        for k in a:
            assert a[k] == row['before_'+k] and b[k] == row['after_'+k]
            assert forecast_pair_full_rewrite_hash(ROOT,p,a[k],k) == b[k]
            for invalid in (b[k], '0' * len(b[k])):
                with pytest.raises(AssertionError):
                    forecast_pair_full_rewrite_hash(ROOT,p,invalid,k)
        with pytest.raises(AssertionError):
            before_forecast_pair_full_rewrite(ROOT,p,raw+b'\n')


def test_both_overviews_and_computations_are_unchanged():
    for slug in (T0, RC):
        p = slug + 'lab.yaml'
        new = (ROOT / p).read_bytes()
        old = before_forecast_pair_full_rewrite(ROOT,p,new)
        n,o = map(yaml.safe_load,(new,old))
        assert n['sections']['overview']==o['sections']['overview']
        for a,b in zip(n['teaching_figures'],o['teaching_figures'],strict=True):
            assert a['id']==b['id'] and a['kind']==b['kind'] and a['after']==b['after']
            assert [t['formula'] for t in a.get('steps',())]==[t['formula'] for t in b.get('steps',())]
            assert [t['value'] for t in a.get('bars',())]==[t['value'] for t in b.get('bars',())]
        values=('36.7','43.0','6.3','+2.2','+10.9','42.2','46.7') if slug==T0 else (
            '33.10%','32.63%','7.91%','9.59%','13区間','15区間')
        assert all(t in n['sections']['evidence'] for t in values)
    values=json.loads((ROOT / (RC+'results.json')).read_text())['reference']['output']['rows']
    assert [round(t['wmape'],6) for t in values]==[50.0,0.0,29.289322]
