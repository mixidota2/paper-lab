"""Check the exact prose scope, numerical contracts and reproducible outputs."""
import ast,json,sys,subprocess,yaml,xml.etree.ElementTree as E
from pathlib import Path
from prose_preservation import before_contextual_all_full_prose
ROOT=Path(__file__).resolve().parents[1]
P='papers/contextual-deconvolution/'
def versions(name):
    path=name if name.startswith('papers/') else P+name
    raw=(ROOT/path).read_bytes()
    return before_contextual_all_full_prose(ROOT,path,raw),raw

def test_contextual_numbers_and_other_shared_paper_outputs(tmp_path):
    a,b=map(json.loads,versions('results.json'))
    assert a['verification']==b['verification']
    assert a['explorer']['default']==b['explorer']['default']==4
    for q in (a,b):
        assert len(q['explorer']['frames'])==41
        assert list(q['experiments'][0]['metrics'].values())==[13.6,38.4]
    for x,y in zip(a['explorer']['frames'],b['explorer']['frames'],strict=True):
        assert x['value']==y['value']
        assert [v['value'] for v in x['bars']]==[v['value'] for v in y['bars']]
        assert [v['values'] for v in x['lines']]==[v['values'] for v in y['lines']]
        assert '8/9' in y['note'] and '論文の約0.20とは別' in y['note']
    ns1,ns2={},{}
    for source,ns in zip(versions('papers/_toy_common.py'),(ns1,ns2),strict=True):
        exec(compile(source,'shared teaching code','exec'),ns)
    assert ns1['IDS']==ns2['IDS']
    for key in ns1['IDS']:
        if key!='contextual-deconvolution':
            assert ns1['compute'](key)==ns2['compute'](key)
    p=tmp_path/'contextual-deconvolution'
    p.mkdir()
    (tmp_path/'_toy_common.py').write_bytes(versions('papers/_toy_common.py')[1])
    (p/'run.py').write_bytes(versions('run.py')[1])
    subprocess.run([sys.executable,str(p/'run.py')],check=True,capture_output=True)
    assert (p/'results.json').read_bytes()==versions('results.json')[1]
    for ast_tree in [ast.parse(v) for v in versions('run.py')]:
        assert isinstance(ast_tree.body[0].value,ast.Constant)
    x,y=map(ast.parse,versions('run.py'))
    assert [ast.dump(k) for k in x.body[1:]]==[ast.dump(k) for k in y.body[1:]]

def test_figure_geometry_and_paper_only_overview():
    def shape(p):
        return [(e.tag,e.attrib,None if e.tag.rsplit('}',1)[-1] in {'text','title','desc'} else e.text) for e in E.fromstring(p).iter()]
    for n in ('deconv','bullwhip','tradeoff'):
        a,b=versions(f'figures/{n}.svg')
        assert a!=b and shape(a)==shape(b)
    a,b=map(yaml.safe_load,versions('lab.yaml'))
    for k in ('urls','id','arxiv_id','verification','status'):
        assert a[k]==b[k]
    for x,y in zip(a['teaching_figures'],b['teaching_figures'],strict=True):
        if x['kind']=='equations':
            assert [s['formula'] for s in x['steps']]==[s['formula'] for s in y['steps']]
        else:assert x['rows']==y['rows']
    h=b['sections']['overview']
    assert len(h.split('\n\n'))==2
    assert all(t in h for t in ('M5','在庫シミュレーション','XGBoost','約2割','欠品費が増えました'))
    assert not any(t in h for t in ('Lab','8/9','教材','<figure'))
