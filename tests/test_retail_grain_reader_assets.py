"""Tie reader copy to the unchanged synthetic, regenerated values."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import pytest
import yaml

from prose_preservation import before_retail_grain_reader_assets, retail_grain_reader_assets_rows, retail_grain_reader_assets_hash

ROOT=Path(__file__).resolve().parents[1]
P='papers/retail-forecast-decision-grain/'

def pair(name):
    path=P+name
    current=(ROOT/path).read_bytes()
    return before_retail_grain_reader_assets(ROOT,path,current),current

def test_exact_reader_transitions_preserve_all_topic_assets():
    files={'README.md','evidence.md','experiment.md','interactive.html','interactive.js','lab.yaml',
           'mapping.md','method.md','model.js','results.json','run.py'}
    rows=retail_grain_reader_assets_rows(ROOT)
    assert rows.keys()=={P+n for n in files}
    edited=set()
    for n in files:
        before,after=pair(n)
        p=P+n
        row=rows[p]
        assert bool(row['prior_spans'])==(before!=after)
        if before!=after:
            edited.add(n)
        for label,b in (('before',before),('after',after)):
            assert hashlib.sha256(b).hexdigest()==row[label+'_sha256']
            assert hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()==row[label+'_blob']
        for alg in ('sha256','blob'):
            assert retail_grain_reader_assets_hash(ROOT,p,row['before_'+alg],alg)==row['after_'+alg]
        with pytest.raises(AssertionError):
            before_retail_grain_reader_assets(ROOT,p,after+b'\n')
    assert edited=={'lab.yaml','README.md','mapping.md'}

def test_reader_guide_and_regenerated_numeric_output_are_consistent(tmp_path):
    a,b=map(yaml.safe_load,pair('lab.yaml'))
    a,b=a.pop('sections'),b.pop('sections')
    assert a.keys()==b.keys()
    assert {k for k in a if a[k]!=b[k]}=={'overview','results'}
    assert all(s in b['overview'] for s in ('商品×店舗','9つのうち7つ','8つのうち4つ','27通りのうち22通り',
                                            '8つのうち3つ','欠品がなければ売れた数量'))
    markers=('期ごとにそれぞれ足し','その差の絶対値','過去の単価で金額に換算して足し',
             '販売実績を同じ単価で換算した合計で割り','店舗が実際に支払った費用ではありません')
    offsets=[b['overview'].index(x) for x in markers]
    assert offsets==sorted(offsets)
    assert 'Lab' not in b['overview'] and '教材' not in b['overview']
    out=json.loads(pair('results.json')[1])
    guide=pair('mapping.md')[1].decode().split('## results.json の読み方',1)[1]
    for key in ('zero_sales','window_order','order_loss'):
        assert f'`{key}`' in guide and key in out
    for key in (*out['zero_sales']['A'],*out['window_order']['A'],*out['order_loss'][0]):
        assert f'`{key}`' in guide
    outpath=tmp_path/'results.json'
    subprocess.run([sys.executable,str(ROOT/P/'run.py'),'--out',str(outpath)],check=True,capture_output=True)
    assert outpath.read_bytes()==pair('results.json')[0]==pair('results.json')[1]
