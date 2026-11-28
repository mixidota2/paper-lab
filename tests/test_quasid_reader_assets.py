"""Keep the model arithmetic and controls identical when changing prose."""
import ast
import hashlib
import json
from pathlib import Path

import pytest
import yaml

from prose_preservation import (before_quasid_reader_assets, quasid_reader_assets_hash,
                                quasid_reader_assets_rows)

ROOT = Path(__file__).resolve().parents[1]
P = 'papers/quasid-collision-qualified-sid/'

def contents(name):
    path = P+name
    now = (ROOT/path).read_bytes()
    return before_quasid_reader_assets(ROOT,path,now),now


def test_quasid_rendered_and_source_assets_are_exact():
    rows = quasid_reader_assets_rows(ROOT)
    names = ('README.md','lab.yaml','mapping.md','method.md','figures/geometry.svg',
             'figures/online.svg','run.py','results.json')
    assert rows.keys() == {P+name for name in names}
    for name in names:
        path=P+name
        row=rows[path]
        prior,now=contents(name)
        for data, stage in ((prior, 'before'),(now, 'after')):
            assert hashlib.sha256(data).hexdigest()==row[stage+'_sha256']
            assert hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()==row[stage+'_blob']
        for algorithm in ('sha256','blob'):
            assert quasid_reader_assets_hash(ROOT,path,row['before_'+algorithm],algorithm)==row['after_'+algorithm]
            if row['prior_spans']:
                with pytest.raises(AssertionError):
                    quasid_reader_assets_hash(ROOT,path,'0'*len(row['before_'+algorithm]),algorithm)
        with pytest.raises(AssertionError):
            before_quasid_reader_assets(ROOT,path,now+b'\n')
    record=json.loads((ROOT/'tests/quasid_reader_assets_hashes.json').read_text())
    render=[line for line in (ROOT/'paper_lab/display_labels.py').read_text().splitlines(keepends=True)
            if "'quasid-collision-qualified-sid':" in line]
    assert len(render)==1 and hashlib.sha256(render[0].encode()).hexdigest()==record['renderer_entry_sha256']


def test_quasid_numeric_and_geometric_invariants():
    def logic(source):
        parsed=ast.parse(source)
        assert ast.get_docstring(parsed)
        del parsed.body[0]
        for node in ast.walk(parsed):
            if not isinstance(node,ast.Dict):
                continue
            for key,value in zip(node.keys,node.values):
                if not isinstance(key,ast.Constant) or key.value not in {'note','label','metric','name'}:
                    continue
                if isinstance(value,ast.JoinedStr):
                    assert key.value=='note'
                    for part in value.values:
                        if isinstance(part,ast.Constant):
                            part.value='<label text>'
                else:
                    assert isinstance(value,ast.Constant) and isinstance(value.value,str)
                    value.value='<label text>'
        return ast.dump(parsed)

    assert len(set(map(logic,contents('run.py'))))==1
    previous,new=map(json.loads,contents('results.json'))
    assert new['explorer']['label']=='二つの表現ベクトルの角度'
    for data in (previous,new):
        data.pop('note')
        data['experiments'][0].pop('name')
        explorer=data['explorer']
        explorer.pop('label'); explorer.pop('metric')
        frames=explorer['frames']
        assert len(frames)==19
        for frame in frames:
            frame.pop('note')
            for bar in frame['bars']: bar.pop('label')
    assert previous==new
    for name in ('README.md','mapping.md','method.md','figures/geometry.svg','figures/online.svg'):
        assert len(set(contents(name)))==1
    original,new=map(yaml.safe_load,contents('lab.yaml'))
    before=original['sections']; after=new['sections']
    assert {key for key in after if after[key]!=before[key]}=={'overview','evidence'}
    assert {key for key in new if new[key]!=original[key]}=={'sections'}
    assert all(x in after['overview'] for x in ('正例','TIGER','NDCG@5','0.55%','2.38%'))
    assert 'Lab' not in after['overview']
    assert all(x in after['evidence'] for x in ('0.0193','0.0181','0.0170','本番でCVPMやHaMRだけを外した結果を示しておらず'))
