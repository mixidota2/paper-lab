from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess

import pytest
import yaml

from prose_preservation import paper_overview_rewrite_hash, zalando_full_rewrite_hash

ROOT = Path(__file__).resolve().parents[1]
PAPER = 'papers/zalando-sales-event-pricing-forecast-optimize/'
CODE = 'paper_lab/zalando05.py'
BASE = 'f7793bc88ab49a347b43e74a9ff45e77bb6fe5ad'
PATHS = {CODE, *(PAPER + n for n in ('lab.yaml', 'README.md', 'mapping.md', 'method.md'))}

def historical(path):
    return subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT)

def local(path):
    return (ROOT / path).read_bytes()

def urls(raw):
    return Counter(re.findall(rb'https?://[^\s)\x27"\x60<]+', raw))

def test_article_keeps_sources_formulas_metadata_and_results():
    for p in PATHS:
        assert urls(local(p)) == urls(historical(p))
    original, rewritten = (yaml.safe_load(s) for s in (historical(PAPER+'lab.yaml'),local(PAPER+'lab.yaml')))
    prose = {'question', 'summary', 'sections', 'core_idea', 'source_review', 'teaching_figures'}
    assert {k:v for k,v in original.items() if k not in prose} == {k:v for k,v in rewritten.items() if k not in prose}
    assert original['sections'].keys() == rewritten['sections'].keys()
    assert all(rewritten['sections'][k] != v for k,v in original['sections'].items() if k != 'method')
    for k in set(original['source_review']) - {'scope'}:
        assert original['source_review'][k] == rewritten['source_review'][k]
    for a,b in zip(original['teaching_figures'], rewritten['teaching_figures'], strict=True):
        assert all(a[k]==b[k] for k in ('id','kind','after','source','locator'))
        assert [i['formula'] for i in a.get('steps',())] == [i['formula'] for i in b.get('steps',())]
    for n in ('run.py','results.json'):
        assert historical(PAPER+n) == local(PAPER+n)
    for n in ('README.md','method.md'):
        a,b=(z.decode() for z in (historical(PAPER+n),local(PAPER+n)))
        formula=r'^\| \((?:3|4|5|7)\) \| ([^|]+)'
        assert re.findall(formula,a,re.M)==re.findall(formula,b,re.M)
    evidence=rewritten['sections']['evidence']
    assert all(s in evidence for s in ('6,204,627','(9)','212日','+6.00% [0.79, 11.03]','+2.23% [−0.83, 5.33]','+0.56% [−3.10, 4.26]','115.02%','93.07%','94.21%','91.57%'))
    assert '売上が対照と同等だったとまでは言えない' in rewritten['sections']['overview']
    assert '100%を超える場合もある' in rewritten['sections']['results']

def test_renderer_computes_same_tables_diagram_shapes_and_controls():
    def run(text):
        ctx={}
        exec(compile(text,CODE,'exec'),ctx)
        return ctx['widget'](json.loads(local(PAPER+'results.json')))
    a,b=map(run,(historical(CODE),local(CODE)))
    for pattern in (r'<script>(.*?)</script>',r'<(?:select|input|rect|path|circle|polyline)[^>]*>',r'<td>([\d,%.−+]+)</td>'):
        assert re.findall(pattern,a,re.S)==re.findall(pattern,b,re.S)

@pytest.mark.parametrize('algo',['sha256','blob'])
def test_archive_and_current_hashes(algo):
    book=json.loads((ROOT/'tests/zalando_full_rewrite_hashes.json').read_text())
    assert book['base']==BASE and set(book['files'])==PATHS
    def digest(raw):
        return (hashlib.sha256(raw) if algo=='sha256' else hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw)).hexdigest()
    for p in PATHS:
        pinned = zalando_full_rewrite_hash(ROOT,p,digest(historical(p)),algo)
        assert paper_overview_rewrite_hash(ROOT,p,pinned,algo)==digest(local(p))
        with pytest.raises(AssertionError):
            zalando_full_rewrite_hash(ROOT,p,digest(local(p)+b'\n'),algo)
