import ast
import hashlib
import json
import re
from pathlib import Path

import pytest
import yaml

from prose_preservation import before_zalando_reader_full_prose, zalando_reader_full_prose_hash

R=Path(__file__).resolve().parents[1]
P='papers/zalando-sales-event-pricing-forecast-optimize/'
C='paper_lab/zalando05.py'


def strip_docstrings(raw):
    t=ast.parse(raw)
    for n in ast.walk(t):
        if isinstance(n,(ast.Module,ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) and ast.get_docstring(n) is not None:
            del n.body[0]
    return ast.dump(t)


def test_zalando_whole_asset_lineage_keeps_results_and_renderer_contracts():
    book=json.loads((R/'tests/zalando_reader_full_prose_hashes.json').read_text())
    assert book['files'].keys()=={C,*(P+n for n in ('README.md','lab.yaml','mapping.md','method.md','results.json','run.py'))}
    def paths(path):
        new=(R/path).read_bytes()
        prior=before_zalando_reader_full_prose(R,path,new)
        return prior,new
    for path in book['files']:
        prior,new=paths(path)
        assert (prior==new)==(path==P+'results.json')
        assert zalando_reader_full_prose_hash(R,path,hashlib.sha256(prior).hexdigest())==hashlib.sha256(new).hexdigest()
        with pytest.raises(AssertionError):
            before_zalando_reader_full_prose(R,path,new+b'\n')
    old,new=paths(P+'run.py')
    assert strip_docstrings(old)==strip_docstrings(new)
    data=json.loads((R/(P+'results.json')).read_bytes())
    assert len(data['frames'])==21 and len(data['experiment'])==6
    out=[]
    for raw in paths(C):
        ctx={}
        exec(compile(raw,C,'exec'),ctx)
        out.append(ctx['widget'](data))
    a,b=out
    assert a!=b
    for pattern in (r'<script(?: [^>]*)?>(.*?)</script>',r'<(?:input|select|circle|rect|polyline|path)[^>]*>',r'<td>([\d,%.−+]+)</td>'):
        assert re.findall(pattern,a,re.S)==re.findall(pattern,b,re.S)


def test_overview_and_evidence_distinguish_field_test_and_simulation():
    text=yaml.safe_load((R/(P+'lab.yaml')).read_bytes())['sections']
    assert all(s in text['overview'] for s in ('23件','12市場','0.79〜11.03%','売上が対照と同等だったとまでは言えない'))
    assert 'Lab' not in text['overview'] and '人工データ' not in text['overview']
    assert all(s in text['evidence'] for s in ('商品をグループ単位','市場や時期の違い','115.02%','93.07%','94.21%','91.57%'))
    assert '人工データの真の需要で評価' in text['evidence']
    assert text['overview'].strip() in (R/(P+'README.md')).read_text()
