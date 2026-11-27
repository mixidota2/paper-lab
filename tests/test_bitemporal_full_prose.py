"""Keep the author findings, input choices and local three-branch result separate."""
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import yaml

from prose_preservation import before_bitemporal_full_prose

ROOT=Path(__file__).resolve().parents[1]
REL='papers/bitemporal-inventory-replay/'
P=ROOT/REL

def before(n):
    return before_bitemporal_full_prose(ROOT,REL+n,(P/n).read_bytes())

def test_author_results_and_unchanged_inventory_cases():
    now=yaml.safe_load((P/'lab.yaml').read_bytes())
    prior=yaml.safe_load(before('lab.yaml'))
    for k in ('id','arxiv_id','authors','title','urls','verification','source_review','status'):
        assert now[k]==prior[k]
    ov=now['sections']['overview']
    assert len(ov.split('\n\n'))==2
    assert all(x in ov for x in ('36,672件','56.8%','86.5%','94.8%','選択済みの報告','開始時の在庫'))
    assert all(x not in ov for x in ('2日目','3日目','Lab','人工例','<figure','<table'))
    e=now['sections']['evidence']
    assert all(x in e for x in ('一次資料','192回答','96回答','34.9ポイント','76.0%','93.2%','208件','166件'))
    a,b=(json.loads(x) for x in ((P/'results.json').read_bytes(),before('results.json')))
    for data in (a,b):
        del data['note'],data['experiments'][0]['name']
    assert a==b

def test_three_detail_controls_and_figure_elements():
    md=(P/'experiment.md').read_text()
    boxes=re.findall(r'<details(?=[^>]*name="bitemporal-cutoff")(?=[^>]*data-cutoff="(\d+)")[^>]*>(.*?)</details>',md,re.S)
    assert [n for n,_ in boxes]==['2','4','6']
    for (n,html),want in zip(boxes,[['0個','3個','1個','3個','4日目'],['3個','3個','1個','0個','なし'],['5個','0個','3個','0個','なし']],strict=True):
        assert re.findall(r'<dd>([^<]+)</dd>',html)==want
        assert '同じ予定を適用した後' in html
    g=ET.parse(P/'figures/cutoffs.svg').getroot()
    assert g.attrib['role']=='img' and g.attrib['aria-labelledby']=='title desc'
    s=' '.join(x for x in g.itertext() if x)
    assert all(x in s for x in ('入荷した日','報告が届いた日','締切が2日目','締切が4日目'))
