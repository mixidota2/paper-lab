from pathlib import Path
import json, math, re, runpy
import yaml

from prose_preservation import before_univa_full_prose

ROOT=Path(__file__).resolve().parents[1]
SLUG='univa-commercial-sid-gar'
P=ROOT/'papers'/SLUG

def previous(name):
    return before_univa_full_prose(ROOT,'papers/'+SLUG+'/'+name,(P/name).read_bytes())

def test_univa_paper_overview_figures_and_experiment_boundaries_survive():
    old = yaml.safe_load(previous('lab.yaml'))
    new = yaml.safe_load((P/'lab.yaml').read_bytes())
    assert old['sections']['overview']==new['sections']['overview']
    assert new['sections']['overview'] in (P/'README.md').read_text()
    assert old['urls']==new['urls'] and old['verification']==new['verification']
    for row, prior in zip(new['teaching_figures'],old['teaching_figures'],strict=True):
        for key in ('id','source','locator','after'):
            assert row[key]==prior[key]
        if 'steps' in row:
            assert [x['formula'] for x in row['steps']]==[x['formula'] for x in prior['steps']]
        if 'bars' in row:
            assert [x['value'] for x in row['bars']]==[x['value'] for x in prior['bars']]
    evidence=new['sections']['evidence']
    assert all(x in evidence for x in ('5%','20%','GARだけの効果ではない','同時期の本番対照','62Mから80M'))
    assert '上位100件' in new['core_idea']['author_claim']


def test_univa_probes_and_prefix_normalization_survive():
    new = json.loads((P/'results.json').read_bytes())
    old = json.loads(previous('results.json'))
    assert new['ads']==old['ads']
    assert new['frames']==old['frames']
    assert new['experiments'][0]['metrics']==old['experiments'][0]['metrics']
    assert runpy.run_path(str(P/'run.py'))['compute']()==new
    script=yaml.safe_load((P/'lab.yaml').read_bytes())['sections']['executable_understanding']
    assert json.loads(re.search(r'data-probe-data>(.*?)</script>',script,re.S)[1])==new
    assert all(script.count('data-'+k)==1 for k in ('alpha','beam','mask'))
    run=runpy.run_path(str(P/'run.py'))
    full={x['path']:x['score'] for x in run['beam'](.5,20,False)}
    constrained={x['path']:x['score'] for x in run['beam'](.5,20,True)}
    # Within A the difference between valid and invalid sibling scores is 0.9.
    assert math.isclose(full['A/a1']-full['A/a2'],.9,abs_tol=2e-6)
    assert math.isclose(constrained['A/a1'],-math.log1p(math.exp(.5)),abs_tol=2e-6)
    assert set(constrained)=={'A/a1','B/b1','B/b2'}
