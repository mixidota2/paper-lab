from pathlib import Path
from prose_preservation import before_tagr_reader_assets
from xml.etree import ElementTree as ET
import ast
import json
import hashlib
import runpy

import pytest
import yaml

from prose_preservation import before_tagr_all_full_prose

ROOT = Path(__file__).resolve().parents[1]
P = 'papers/tagr-live-sid/'
ASSETS = {'lab.yaml', 'method.md', 'run.py', 'figures/clocks.svg', 'figures/collision.svg'}


def current(name):
    return before_tagr_reader_assets(ROOT,P+name,(ROOT/(P+name)).read_bytes())


def previous(name):
    return before_tagr_all_full_prose(ROOT, P+name, current(name))


def test_tagr_exact_edit_and_paper_only_overview():
    files = json.loads((ROOT/'tests/tagr_all_full_prose_hashes.json').read_bytes())['files']
    assert set(files) == {P+p for p in ASSETS}
    for n in ASSETS:
        assert previous(n) != current(n)
        with pytest.raises(AssertionError):
            before_tagr_all_full_prose(ROOT, P+n, current(n)+b'\n')
    old, new = (yaml.safe_load(b) for b in (previous('lab.yaml'), current('lab.yaml')))
    for k in 'id urls arxiv_id authors year verification'.split():
        assert old[k] == new[k]
    assert new['source_review']['pdf_version'] == 'v1'
    for title, code in (('overview', '16.1%'), ('evidence', '1.36'), ('executable_understanding', 'run.py')):
        assert code in new['sections'][title]
    o = new['sections']['overview']
    assert o.count('\n\n') == 1
    assert all(n in o for n in ('毎分', '4,000万人', '10%', '8.5%', '7.4%', '16.1%', 'DLRM', '後段', 'IDの更新だけを試した結果ではありません'))
    assert all(n not in o for n in ('Lab', '合成', 'run.py', '図', 'Cpr', 'Col'))
    assert all(x in new['sections']['evidence'] for x in ('1.36', '0.39', 'N≥U+M', '1.79', '1.68', '1.53', '第1階層'))
    assert '分母は記録の件数ではなく' in current('method.md').decode()


def test_tagr_svg_geometry_and_numeric_replay(tmp_path):
    for n in ('figures/clocks.svg', 'figures/collision.svg'):
        def shape(b):
            return [(e.tag, e.attrib, len(e)) for e in ET.fromstring(b).iter()]
        assert shape(previous(n)) == shape(current(n))
    a, b = map(ast.parse,(previous('run.py'),current('run.py')))
    assert isinstance(a.body.pop(0).value, ast.Constant)
    assert isinstance(b.body.pop(0).value, ast.Constant)
    assert ast.dump(a) == ast.dump(b)
    prior = tmp_path/'before.py'
    prior.write_bytes(previous('run.py'))
    q0 = runpy.run_path(str(prior))['experiment']()
    q1 = runpy.run_path(str(ROOT/(P+'run.py')))['experiment']()
    target = current('results.json')
    assert hashlib.sha256(target).hexdigest()=='dfded7ed370a53342c393e838d9fccbec40acce8b6b6f10f4df70ce4817c803e'
    assert q0 == q1 == json.loads(target)
    assert q1['spread']['refreshed']['cpr'] == 1
    assert q1['collapse_counterexample']['refreshed']['cpr'] == 4
    assert [q1['schedules'][k]['reward_updates'] for k in ('continuous','intermittent')] == [60,12]
