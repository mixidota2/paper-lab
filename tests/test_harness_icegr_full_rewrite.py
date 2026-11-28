"""Check the exact transitions and keep evidence separate for two body reviews."""
import hashlib
import json
from pathlib import Path
from prose_preservation import before_icegr_reader_assets
from prose_preservation import before_harness_bench_reader_assets

import pytest
import yaml

from prose_preservation import before_harness_icegr_full_rewrite, harness_icegr_full_rewrite_hash

ROOT = Path(__file__).resolve().parents[1]
H = 'papers/harness-bench/'
I = 'papers/icegr-baidu-intent-generative-retrieval/'


def identity(data):
    return {'sha256': hashlib.sha256(data).hexdigest(),
            'blob': hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()}


def test_full_rewrite_replays_earlier_source_bytes_only():
    rows = json.loads((ROOT / 'tests/harness_icegr_full_rewrite_hashes.json').read_text())['files']
    assert rows.keys() == {H + 'lab.yaml', H + 'method.md'} | {
        I + name for name in ('lab.yaml','README.md','mapping.md','method.md','plot.py','margin-curve.svg')}
    for p, row in rows.items():
        raw = before_harness_bench_reader_assets(ROOT,p,before_icegr_reader_assets(ROOT,p,(ROOT / p).read_bytes()))
        prior = before_harness_icegr_full_rewrite(ROOT, p, raw)
        old, new = identity(prior), identity(raw)
        for key in old:
            assert old[key] == row['before_' + key] and new[key] == row['after_' + key]
            assert harness_icegr_full_rewrite_hash(ROOT,p,old[key],key) == new[key]
            for disallowed in (new[key], '0' * len(new[key])):
                with pytest.raises(AssertionError):
                    harness_icegr_full_rewrite_hash(ROOT,p,disallowed,key)
        with pytest.raises(AssertionError):
            before_harness_icegr_full_rewrite(ROOT,p,raw+b'\n')


def test_article_evidence_keeps_version_figures_and_toys_separate():
    for slug in (H, I):
        lab = slug + 'lab.yaml'
        raw = (ROOT / lab).read_bytes()
        current = yaml.safe_load(raw)
        historical = before_harness_bench_reader_assets(ROOT,lab,before_icegr_reader_assets(ROOT,lab,raw))
        prior = yaml.safe_load(before_harness_icegr_full_rewrite(ROOT,lab,historical))
        assert yaml.safe_load(historical)['sections']['overview'] == prior['sections']['overview']
        assert current['source_review']['version'] == 'v1'
        for a,b in zip(current['teaching_figures'],prior['teaching_figures'],strict=True):
            assert a['id']==b['id'] and a['after']==b['after'] and a['kind']==b['kind']
            assert [r['formula'] for r in a.get('steps',[])]==[r['formula'] for r in b.get('steps',[])]
            assert a.get('bars')==b.get('bars')
        if slug==H:
            assert all(s in current['sections']['evidence'] for s in ('106課題','5,088回','76.2点','52.4点','80.4点は参考値'))
            assert all(s in current['sections']['results'] for s in ('24件','36件','48件','12件は不合格'))
        else:
            e=current['sections']['evidence']
            assert all(s in e for s in ('ProdGR（対照）','0.4247','0.5169','20%を対象に2週間','注文数 | +15.96%','取引総額（GMV） | +7.53%'))
            assert '0.486' in current['sections']['results']
    for f, blob in {
        H+'run.py': '9cea0ae52a3418a89f92496b50f68dcd529709ee',
        H+'results.json': '63308ef63ec6f50ec577a6a5bdc06fc0ced9af25',
        I+'run.py': '78b2aad9c08c3487d03f56ed6e7583f678c678d6',
        I+'results.json': '380f49f1dbb557291cf0c48f9378699bca2612a1',
    }.items():
        assert identity(before_icegr_reader_assets(ROOT,f,(ROOT / f).read_bytes()))['blob'] == blob
