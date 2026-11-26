"""Keep Auto-RecSys paper evidence and its synthetic scheduling example distinct."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

import pytest
import yaml
from prose_preservation import autorecsys_full_prose_hash, before_autorecsys_full_prose

ROOT = Path(__file__).resolve().parents[1]
P = 'papers/auto-recsys-harness/'
FIG = {'figures/boundary.svg','figures/loops.svg','figures/reliability.svg'}
FILES = {'README.md','lab.yaml','mapping.md','method.md','run.py','results.json'} | FIG


def test_autorecsys_exact_reversible_receipts():
    entries = json.loads((ROOT/'tests/autorecsys_full_prose_hashes.json').read_text())['files']
    assert set(entries)=={P+x for x in FILES}
    for f,r in entries.items():
        after=(ROOT/f).read_bytes()
        before=before_autorecsys_full_prose(ROOT,f,after)
        for alg,dig in {
            'sha256': lambda b: hashlib.sha256(b).hexdigest(),
            'blob': lambda b: hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest(),
        }.items():
            assert dig(before)==r['before'][alg]
            assert autorecsys_full_prose_hash(ROOT,f,dig(before),alg)==dig(after)
            with pytest.raises(AssertionError):
                autorecsys_full_prose_hash(ROOT,f,dig(after),alg)
        with pytest.raises(AssertionError):
            before_autorecsys_full_prose(ROOT,f,after+b'\n')


def test_autorecsys_preserves_paper_summary_svg_geometry_and_all_toy_values():
    def pair(name, parse):
        path=P+name
        final=(ROOT/path).read_bytes()
        return parse(before_autorecsys_full_prose(ROOT,path,final)),parse(final)
    x,y=pair('lab.yaml',yaml.safe_load)
    assert x['sections']['overview']==y['sections']['overview']
    for k in ('id','arxiv_id','authors','urls','title','verification'):
        assert x[k]==y[k]
    assert [z['path'] for z in x['figures']]==[z['path'] for z in y['figures']]
    for n in FIG:
        a,b=pair(n,ET.fromstring)
        signature=lambda node:[(e.tag,sorted(e.attrib.items()),e.text if e.tag.endswith('}style') else None) for e in node.iter()]
        assert signature(a)==signature(b)
    a,b=pair('results.json',json.loads)
    assert a['assumptions']==b['assumptions']
    assert a['runs']==b['runs']
    assert sum(len(x['trace']) for x in b['runs'].values())==124
    assert [x['metrics'] for x in a['experiments']]==[x['metrics'] for x in b['experiments']]


def test_autorecsys_no_external_jobs_required_for_exact_json(tmp_path):
    script=tmp_path/'run.py'
    script.write_bytes((ROOT/P/'run.py').read_bytes())
    subprocess.run([sys.executable,'-S',str(script)],capture_output=True,text=True,check=True)
    assert (tmp_path/'results.json').read_bytes()==(ROOT/P/'results.json').read_bytes()
