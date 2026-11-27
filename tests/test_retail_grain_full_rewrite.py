"""Keep a precise receipt for both research editions and unchanged toy mechanics."""
from hashlib import sha1, sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re

import pytest
import yaml

from prose_preservation import before_retail_grain_all_full_prose, before_retail_grain_full_rewrite, retail_grain_full_rewrite_hash

ROOT = Path(__file__).resolve().parents[1]
P = 'papers/retail-forecast-decision-grain/'


def prior(path):
    return before_retail_grain_all_full_prose(ROOT,path,(ROOT/path).read_bytes())

def ident(data):
    return {'sha256': sha256(data).hexdigest(),
            'blob': sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()}


def test_retail_grain_exact_transition():
    files = ('README.md', 'mapping.md', 'method.md', 'lab.yaml', 'evidence.md',
             'experiment.md', 'interactive.js', 'interactive.html')
    rows = json.loads((ROOT/'tests/retail_grain_full_rewrite_hashes.json').read_text())['files']
    assert set(rows) == {P+name for name in files}
    for path,row in rows.items():
        new = prior(path)
        old = before_retail_grain_full_rewrite(ROOT,path,new)
        for kind in ('sha256','blob'):
            assert ident(old)[kind] == row['before_'+kind]
            assert ident(new)[kind] == row['after_'+kind]
            assert retail_grain_full_rewrite_hash(ROOT,path,ident(old)[kind],kind) == ident(new)[kind]
            for invalid in (ident(new)[kind], '0'*len(ident(new)[kind])):
                with pytest.raises(AssertionError):
                    retail_grain_full_rewrite_hash(ROOT,path,invalid,kind)
        with pytest.raises(AssertionError):
            before_retail_grain_full_rewrite(ROOT,path,new+b'\n')


def test_retail_grain_keeps_exact_overview_equations_and_toy():
    f=P+'lab.yaml'
    current=prior(f)
    original=before_retail_grain_full_rewrite(ROOT,f,current)
    overview=re.compile(rb'^  overview:.*?(?=^  problem:)',re.S | re.M)
    assert len(overview.findall(current)) == 1
    assert overview.findall(current) == overview.findall(original)
    a,b=map(yaml.safe_load,(original,current))
    for k in ('urls','source_review','title','authors','verification','verdict'):
        assert a[k]==b[k]
    for x,y in zip(a['teaching_figures'],b['teaching_figures'],strict=True):
        for n in ('kind','id','after','source','locator'):
            assert x[n]==y[n]
        assert [v['formula'] for v in x.get('steps',[])]==[v['formula'] for v in y.get('steps',[])]
    for file,blob in (('run.py','cda6ea7b1a99b2b838e4f76a2964a584e8615fe5'),
                      ('model.js','76250c28db1d60c2e42a3ed9c13b573f7f76a959'),
                      ('results.json','89242fa1228c8bb0a6e234817c54b668b16740bb')):
        assert ident(prior(P+file))['blob']==blob


class Shape(HTMLParser):
    def __init__(self,s):
        self.parts=[]
        super().__init__()
        self.feed(s)
    def handle_starttag(self,tag,attrs):
        self.parts.append((tag,attrs))
    def handle_endtag(self,tag):
        self.parts.append((tag,))


def test_retail_grain_keeps_markup_and_makes_editions_distinct():
    path=P+'interactive.html'
    after=prior(path)
    before=before_retail_grain_full_rewrite(ROOT,path,after)
    assert Shape(after.decode()).parts==Shape(before.decode()).parts
    ev=prior(P+'evidence.md').decode()
    part1,part2=ev.split('## 第3版（v3）',1)
    assert all(s in part1 for s in ('一次資料','2610.25170v1','うち7つ','| 4 | 3 | 1（M5） |','| 3 | 5 | 0 |'))
    assert all(s in part2 for s in ('2610.25170v3','27通り','22通り','最小だったのは3つ','0.040','0.311','0.061',
                                   '販売履歴がない新商品を予測した試験ではありません','第3版の元データ、コードや実験は再実行していません'))
    link=re.compile(rb'\]\(([^)]*)\)')
    for name in ('README.md','evidence.md','experiment.md','method.md','mapping.md','lab.yaml'):
        p=P+name
        after=prior(p)
        before=before_retail_grain_full_rewrite(ROOT,p,after)
        assert set(link.findall(before))<=set(link.findall(after))
