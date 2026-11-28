import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest
import yaml

from prose_preservation import (
    before_bridging_reader_full_prose,
    bridging_reader_full_prose_hash,
)

ROOT = Path(__file__).resolve().parents[1]
P = 'papers/bridging-forecast-accuracy-inventory-kpis/'


def test_exact_reader_release_and_preserved_historical_bytes(tmp_path):
    rows = json.loads((ROOT/'tests/bridging_reader_full_prose_hashes.json').read_text())['files']
    assert set(rows) == {P+n for n in ('README.md','lab.yaml','mapping.md','method.md','results.json','run.py')}
    for path, row in rows.items():
        final = (ROOT / path).read_bytes()
        original = before_bridging_reader_full_prose(ROOT,path,final)
        assert final != original
        from hashlib import sha256
        assert bridging_reader_full_prose_hash(ROOT,path,sha256(original).hexdigest()) == sha256(final).hexdigest()
        with pytest.raises(AssertionError):
            before_bridging_reader_full_prose(ROOT,path,final+b'\n')
        with pytest.raises(AssertionError):
            bridging_reader_full_prose_hash(ROOT,path,'0'*64)
    original_results = json.loads(before_bridging_reader_full_prose(ROOT,P+'results.json',(ROOT/(P+'results.json')).read_bytes()))
    new = json.loads((ROOT/(P+'results.json')).read_bytes())
    assert {k for k in new if new[k]!=original_results[k]}=={'reported_source','boundary'}
    assert len(new['reported'])==7 and sum(len(f['rows']) for f in new['frames'])==8
    for f in new['frames']:
        a,b=f['rows']
        assert a['cost']-b['cost'] == (a['lost']-b['lost'])*f['penalty']-(b['holding']-a['holding'])
        assert a['lost']-b['lost']==147 and b['holding']-a['holding']==945
    script=shutil.copy(ROOT/(P+'run.py'),tmp_path)
    subprocess.run([sys.executable,script],check=True,capture_output=True)
    assert (tmp_path/'results.json').read_bytes()==(ROOT/(P+'results.json')).read_bytes()


def test_article_separates_author_findings_and_lab_cost_threshold():
    view=yaml.safe_load((ROOT/(P+'lab.yaml')).read_bytes())['sections']
    overview=view['overview']
    assert len(overview.split('\n\n'))==2
    assert all(x in overview for x in ('48条件','0.43','0.52','確かめていません'))
    assert '6.43' not in overview and 'Lab' not in overview
    assert all(x in view['evidence'] for x in ('0.95','−0.16','−0.06','まとめると','平均すると'))
    assert 'この人工需要と補充ルールに限った値' in view['results']
    readme=(ROOT/(P+'README.md')).read_text()
    assert all(view[k].strip() in readme for k in ('overview','results'))
    for name in ('method.md','mapping.md'):
        assert (ROOT/(P+name)).read_text().strip() in readme
