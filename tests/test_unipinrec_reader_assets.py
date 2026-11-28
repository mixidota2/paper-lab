"""Check exact reader-copy revisions and reuse of the unmodified reference computation."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
from xml.etree import ElementTree

import pytest
import yaml

from prose_preservation import before_unipinrec_reader_assets, unipinrec_reader_assets_rows, unipinrec_reader_assets_hash

ROOT=Path(__file__).resolve().parents[1]
P='papers/unipinrec/'


def contents(name):
    path=P+name
    data=(ROOT/path).read_bytes()
    return before_unipinrec_reader_assets(ROOT,path,data),data


def test_unipinrec_reader_asset_guards_bind_exact_bytes():
    names=('README.md','lab.yaml','method.md','results.json','run.py',
           'figures/cascade.svg','figures/kv-cache.svg','figures/mam.svg')
    rows=unipinrec_reader_assets_rows(ROOT)
    assert rows.keys()=={P+n for n in names}
    for name in names:
        before,after=contents(name)
        path=P+name
        row=rows[path]
        for which,data in (('before',before),('after',after)):
            assert hashlib.sha256(data).hexdigest()==row[which+'_sha256']
            assert hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()==row[which+'_blob']
        for alg in ('sha256','blob'):
            assert unipinrec_reader_assets_hash(ROOT,path,row['before_'+alg],alg)==row['after_'+alg]
            if row['prior_spans']:
                with pytest.raises(AssertionError): unipinrec_reader_assets_hash(ROOT,path,'0'*len(row['before_'+alg]),alg)
        with pytest.raises(AssertionError): before_unipinrec_reader_assets(ROOT,path,after+b'\n')


def test_common_toy_controls_svg_geometry_and_values_unchanged(tmp_path):
    before,after=map(json.loads,contents('results.json'))
    spec=importlib.util.spec_from_file_location('reference',ROOT/'papers/_toy_common.py')
    common=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(common)
    assert before==common.compute('unipinrec')
    assert after['explorer']['default']==2
    assert [f['value'] for f in after['explorer']['frames']]==list(range(0,129,8))
    for prior,now in zip(before['explorer']['frames'],after['explorer']['frames'],strict=True):
        assert re.findall(r'\d+\.\d+%',prior.pop('note'))==re.findall(r'\d+\.\d+%',now.pop('note'))
        assert prior==now
    for data in (before,after):
        data.pop('note')
        data['experiments'][0].pop('name')
        data['experiments'][0].pop('dataset')
    assert before==after

    folder=tmp_path/'unipinrec'
    folder.mkdir()
    (tmp_path/'_toy_common.py').write_bytes((ROOT/'papers/_toy_common.py').read_bytes())
    script=folder/'run.py'
    script.write_bytes(contents('run.py')[1])
    result=subprocess.run([sys.executable,str(script)],capture_output=True,text=True,check=True)
    assert '17条件' in result.stdout
    assert (folder/'results.json').read_bytes()==contents('results.json')[1]

    for name in ('figures/cascade.svg','figures/kv-cache.svg','figures/mam.svg'):
        b,c=contents(name)
        assert b!=c
        def structure(data):
            root=ElementTree.fromstring(data)
            return [(n.tag,n.attrib,n.text if n.tag.rsplit('}',1)[-1] not in {'text','title','desc'} else None)
                    for n in root.iter()]
        assert structure(b)==structure(c)
    old,new=map(yaml.safe_load,contents('lab.yaml'))
    assert {k for k in old if old[k]!=new[k]}=={'sections'}
    assert {k for k in old['sections'] if old['sections'][k]!=new['sections'][k]}=={'overview','evidence'}
    assert 'Lab' not in new['sections']['overview']
    for literal in ('後段の精密な順位付けは変えていません','0.95%','0.91%','11.1%','63.6%'):
        assert literal in new['sections']['overview']
    assert all(term in new['sections']['evidence'] for term in ('約2倍','約3倍','TransAct V2','利用者単位で集計した'))
