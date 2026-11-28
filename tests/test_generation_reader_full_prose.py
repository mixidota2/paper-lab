import ast
import hashlib
import json
import re
from pathlib import Path
import subprocess
import sys
from xml.etree import ElementTree as ET

import pytest
import yaml

from prose_preservation import before_generation_reader_full_prose, generation_reader_full_prose_hash

R=Path(__file__).resolve().parents[1]
P='papers/case-against-generation-retrieval/'


def test_generation_review_preserves_runtime_and_vector_geometry(tmp_path):
    rows=json.loads((R/'tests/generation_reader_full_prose_hashes.json').read_text())['files']
    assert len(rows)==8
    def geometry(raw):
        return [(e.tag,e.attrib) for e in ET.fromstring(raw).iter()]
    for p in rows:
        b=(R/p).read_bytes()
        a=before_generation_reader_full_prose(R,p,b)
        assert (a==b)==(p==P+'results.json')
        assert generation_reader_full_prose_hash(R,p,hashlib.sha256(a).hexdigest())==hashlib.sha256(b).hexdigest()
        with pytest.raises(AssertionError):
            before_generation_reader_full_prose(R,p,b+b'\n')
        if p.endswith('.svg'):
            assert geometry(a)==geometry(b)
        if p.endswith('run.py'):
            x,y=map(ast.parse,(a,b))
            assert ast.dump(ast.Module(body=x.body[1:],type_ignores=[]))==ast.dump(ast.Module(body=y.body[1:],type_ignores=[]))
    t=tmp_path/'case-against-generation-retrieval'
    t.mkdir()
    (t/'run.py').write_bytes((R/(P+'run.py')).read_bytes())
    (tmp_path/'_toy_common.py').write_bytes((R/'papers/_toy_common.py').read_bytes())
    subprocess.run([sys.executable,t/'run.py'],check=True,capture_output=True)
    assert (t/'results.json').read_bytes()==(R/(P+'results.json')).read_bytes()


def test_generation_article_distinguishes_recall_and_downstream_ranking():
    sec=yaml.safe_load((R/(P+'lab.yaml')).read_bytes())['sections']
    assert all(s in sec['overview'] for s in ('Recall@10','4.3〜35.3%','0.0471から0.0380','同じモデル規模','保存しておいた利用者ベクトル'))
    assert 'Lab' not in sec['overview']
    assert all(s in sec['evidence'] for s in ('0.0791 → 0.0825','0.0412 → 0.0542','0.0797 → 0.1078','0.5%','Qwen3-8B','Qwen3-0.6B'))
    assert '定期的に計算し直し' in (R/(P+'method.md')).read_text()
