"""The only live overview correction and the exact archived VN2 article."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from prose_preservation import before_forecast_critic_all_full_prose, before_apollopfn_full_prose, before_vn2_full_prose, vn2_full_prose_hash

ROOT = Path(__file__).resolve().parents[1]
BASE = '374a5d35ed43fba71ec5d24b5d0e042f879606f5'
PREFIX = 'papers/vn2-stockout-catboost'


def historical(path):
    return subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT)


def test_vn2_restores_exact_archived_bytes_and_isolates_the_overview():
    for path in ('lab.yaml', 'method.md', 'run.py', 'results.json'):
        rel = f'{PREFIX}/{path}'
        new = (ROOT / rel).read_bytes()
        assert new != historical(rel)
        assert before_vn2_full_prose(ROOT, rel, new) == historical(rel)
        with pytest.raises(AssertionError):
            before_vn2_full_prose(ROOT, rel, new + b'\n')
        row = json.loads((ROOT / 'tests/vn2_full_prose_hashes.json').read_text())['files'][rel]
        for algo in ('sha256', 'blob'):
            assert vn2_full_prose_hash(ROOT, rel, row['before'][algo], algo) == row['after'][algo]
            with pytest.raises(AssertionError):
                vn2_full_prose_hash(ROOT, rel, row['after'][algo], algo)
    helper = 'papers/_toy_common.py'
    assert before_apollopfn_full_prose(ROOT, helper, before_forecast_critic_all_full_prose(ROOT,helper,(ROOT / helper).read_bytes())) == historical(helper)
    old, new = map(yaml.safe_load, (historical(f'{PREFIX}/lab.yaml'), (ROOT / PREFIX / 'lab.yaml').read_bytes()))
    prose = {'summary', 'question', 'core_idea', 'sections', 'interactives', 'source_review', 'teaching_figures'}
    assert {k: v for k, v in old.items() if k not in prose} == {k: v for k, v in new.items() if k not in prose}
    assert old['sections'].keys() == new['sections'].keys()
    assert old['sections']['method'] == new['sections']['method']
    assert {k:v for k,v in old['source_review'].items() if k != 'scope'} == {k:v for k,v in new['source_review'].items() if k != 'scope'}
    assert [i['kind'] for i in old['interactives']] == [i['kind'] for i in new['interactives']]
    for a, b in zip(old['teaching_figures'], new['teaching_figures'], strict=True):
        assert all(a[k] == b[k] for k in ('id', 'kind', 'after', 'source', 'locator'))
        assert [s['formula'] for s in a.get('steps', ())] == [s['formula'] for s in b.get('steps', ())]
    overview = new['sections']['overview']
    assert '計3つ学習' in overview and '1週先、2週先、3週先' in overview
    assert '4.334ユーロから3.763ユーロへ13.2%' in overview and '実店舗で測った結果ではありません' in overview


def test_vn2_regenerated_results_preserve_every_value():
    p = ROOT / PREFIX
    spec = importlib.util.spec_from_file_location('vn2_public_download', p / 'run.py')
    entry = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    original_path = sys.path[:]
    try:
        spec.loader.exec_module(entry)
    finally:
        sys.path[:] = original_path
    old = json.loads(historical(f'{PREFIX}/results.json'))
    new = json.loads((p / 'results.json').read_bytes())
    assert entry.compute() == new
    assert old['verification'] == new['verification']
    a, b = (o['explorer'] for o in (old, new))
    assert a['default'] == b['default'] and a['unit'] == b['unit'] and len(b['frames']) == 14
    assert list(old['experiments'][0]['metrics'].values()) == list(new['experiments'][0]['metrics'].values())
    for prior, actual in zip(a['frames'], b['frames'], strict=True):
        assert prior['value'] == actual['value']
        assert [q['value'] for q in prior['bars']] == [q['value'] for q in actual['bars']]
        assert [q['values'] for q in prior['lines']] == [q['values'] for q in actual['lines']]
    assert b['frames'][0]['bars'][-1]['value'] is None
    assert b['frames'][10]['bars'][-1]['value'] == 19.3333
