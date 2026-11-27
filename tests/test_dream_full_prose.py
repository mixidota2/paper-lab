"""Check paper/experiment boundaries and browser display of deterministic values."""
import json
from pathlib import Path
import re
import runpy
import yaml

from prose_preservation import before_dream_full_prose

ROOT=Path(__file__).resolve().parents[1]
REL='papers/dream-taobao-agentic-control/'
P=ROOT/REL

def before(n):
    return before_dream_full_prose(ROOT,REL+n,(P/n).read_bytes())

def test_dream_article_distinguishes_indicators_and_meanings():
    d=yaml.safe_load((P/'lab.yaml').read_bytes())
    old=yaml.safe_load(before('lab.yaml'))
    for k in ('id','title','urls','authors','topics','source_review','verification'):
        assert d[k]==old[k]
    a=d['sections']['overview']
    assert len(a.split('\n\n'))==2
    assert all(x in a for x in ('2.06%','2.71%','同じ従来方式','足し合わせられません','既定の設定'))
    assert all(x not in a for x in ('Lab','人工','<figure','<table','run.py'))
    e=d['sections']['evidence']
    assert all(x in e for x in ('一次資料','0.65ポイント','約0.637%','同じ基準','代理指標','pIPVは0.99%下がり'))
    for n,o in zip(d['teaching_figures'],old['teaching_figures'],strict=True):
        assert all(n[x]==o[x] for x in ('id','kind','after','locator','source'))
        assert [v['formula'] for v in n.get('steps',[]) ]==[v['formula'] for v in o.get('steps',[])]
        assert [v['value'] for v in n.get('bars',[]) ]==[v['value'] for v in o.get('bars',[])]

def test_dream_figures_show_unchanged_values():
    current=json.loads((P/'results.json').read_bytes())
    assert current==json.loads(json.dumps(runpy.run_path(str(P/'run.py'))['compute']()))
    original=json.loads(before('results.json'))
    for d in (current, original):
        del d['note']
        for row in d['experiments']: del row['name']
    assert current==original
    a=yaml.safe_load((P/'lab.yaml').read_bytes())['sections']['executable_understanding']
    frames=json.loads(a.split('<script type="application/json" data-frames>')[1].split('</script>')[0])
    assert len(frames)==len(current['cases'])==6
    for f,c in zip(frames,current['cases'],strict=True):
        assert [float(val) for val in re.findall(r'<td>([\d.]+)</td>',f)]==list(c['parameters'].values())
    assert '既定値' in frames[0] and '1.4' in frames[1]
    assert '数値ではない値' in frames[-1]
