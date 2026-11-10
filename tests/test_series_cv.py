"""Independent numeric oracles and synthetic DOM dispatch; not browser rendering."""
from copy import deepcopy
from html.parser import HTMLParser
import importlib.util
import json
import math
from pathlib import Path
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'papers/series-wise-validation'
spec = importlib.util.spec_from_file_location('series_toy', SOURCE / 'run.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def test_label_endpoints_and_no_final_test_selection():
    original = m.dataset()
    for cutoff, expected in [(84,80),(88,84),(92,88)]:
        assert m.origins(cutoff)[-1] == expected
        assert all(o+4 <= cutoff for o in m.origins(cutoff))
        assert cutoff+4 > cutoff  # checking only origin <= cutoff would leak labels
    for scheme in ('series','time'):
        selected = m.select(original,scheme)
        changed = deepcopy(original)
        for s in m.IDS:
            changed[s][92:] = [100000+t for t in range(8)]
        assert m.select(changed,scheme) == selected
        assert m.fit(changed,'ABCDEFG',92) == m.fit(original,'ABCDEFG',92)
        for s in 'HIJ':
            changed[s] = [50000]*100
        assert m.select(changed,scheme) == selected


def test_fixed_origin_predictions_do_not_retroactively_read_future():
    a = m.evaluate()
    data = m.dataset()
    data['A'][92] += 100
    b = m.evaluate(data)
    assert a['selection'] == b['selection']
    assert a['records'][0]['prediction'] == b['records'][0]['prediction']
    assert a['records'][1]['prediction'] != b['records'][1]['prediction']
    assert a['records'][0]['actual'][0] + 100 == b['records'][0]['actual'][0]
    for r in a['records']:
        assert max(r['context_times']) == r['origin']
        assert min(r['target_times']) == r['origin']+1
        assert len(r['prediction']) == 4


def test_error_denominators_weights_and_q_zero():
    r = m.evaluate()
    assert len(r['records']) == 50
    # Seasonal lag 4 cancels the period-4 component; five slopes .1 and two .4.
    assert r['Q'] == pytest.approx((5*4*.1+2*4*.4)/7)
    assert r['fixed_final_slope'] == pytest.approx((5*.1+2*.4)/7)
    assert list(r['weights'].values()) == [1,2,3,4,4,3,2,1]
    errors = [e for rec in r['records'] for e in rec['errors']]
    assert len(errors) == 200
    assert r['MAE'] == pytest.approx(sum(errors)/200)
    per_target = []
    for s in m.IDS:
        for t in range(93,101):
            es = [rec['errors'][rec['target_times'].index(t)] for rec in r['records']
                  if rec['series']==s and t in rec['target_times']]
            per_target.append(sum(es)/len(es))
    assert r['equal_target_time_MAE'] == pytest.approx(sum(per_target)/80)
    assert r['equal_target_time_MAE'] != pytest.approx(r['MAE'])
    assert m.evaluate(q=0)['MASE'] is None
    assert m.evaluate(q=2)['MASE'] == pytest.approx(m.evaluate(q=1)['MASE']/2)
    constant = {s:[1]*100 for s in m.IDS}
    tied = m.evaluate(constant)
    assert tied['selection']['chosen']['family'] == 'global'
    assert tied['selection']['chosen']['scale'] == 0
    assert tied['Q'] == 0 and tied['MASE'] is None and tied['MAE'] == 0


@pytest.mark.parametrize('q',[-1,float('nan'),float('inf')])
def test_invalid_q(q):
    with pytest.raises(ValueError): m.evaluate(q=q)


@pytest.mark.parametrize('cutoff',[11,93,84.5])
def test_invalid_training_boundary(cutoff):
    with pytest.raises(ValueError): m.origins(cutoff)


def test_invalid_series_data_and_prediction_inputs():
    for bad in ({}, {**m.dataset(),'A':[0]*99}, {**m.dataset(),'A':[math.nan]*100}):
        with pytest.raises(ValueError): m.evaluate(bad)
    with pytest.raises(ValueError): m.evaluate(scheme='unknown')
    for o in (7,97,92.5):
        with pytest.raises(ValueError): m.predict(m.dataset(),'A',o,'global',1,.1)


def test_table3_rounded_values_sensitivity_and_interval():
    r = m.sensitivity()
    assert r['wins_vs_time'] == 7 and r['ties_vs_time'] == 0
    assert r['delta_sum'] == pytest.approx(.271)
    assert r['per_dataset_delta']['Weather'] == pytest.approx(.195)
    assert r['weather_contribution'] == pytest.approx(.195/.271)
    assert r['displayed_row_mean'] == pytest.approx(9.437/11)
    assert r['published_full_mean'] == .858
    assert m.sensitivity('Holdout',False)['mean_difference_ratio'] == pytest.approx(.008844,abs=5e-7)
    assert m.sensitivity('K-MC-CV',False)['mean_difference_ratio'] == pytest.approx(.010939,abs=5e-7)
    assert m.sensitivity('Kf-CV',False)['mean_difference_ratio'] < 0
    # Cell rounding +/- .0005 -> pair difference +/- .001; correlated denominator.
    lower = .194/(.194+.076+.010)
    upper = .196/(.196+.076-.010)
    assert lower == pytest.approx(.692857142857)
    assert upper == pytest.approx(.748091603053)
    assert all(abs(d) > .001 for d in r['per_dataset_delta'].values())


def assert_nested_close(a,b):
    if isinstance(a,dict):
        assert a.keys()==b.keys()
        for k in a: assert_nested_close(a[k],b[k])
    elif isinstance(a,list):
        assert len(a)==len(b)
        for x,y in zip(a,b): assert_nested_close(x,y)
    elif isinstance(a,(int,float)) and not isinstance(a,bool): assert a==pytest.approx(b,abs=1e-10)
    else: assert a==b


def test_python_js_and_saved_output_agree():
    code = "const m=require(process.argv[1]);console.log(JSON.stringify(['series','time'].flatMap(s=>[null,0,1].map(q=>m.evaluate(undefined,s,q)))));"
    js = json.loads(subprocess.check_output(['node','-e',code,str(SOURCE/'model.js')],text=True))
    py = [m.evaluate(scheme=s,q=q) for s in ('series','time') for q in (None,0,1)]
    # JSON normalizes integer dictionary keys.
    assert_nested_close(json.loads(json.dumps(py)),js)
    saved=json.loads((SOURCE/'results.json').read_text())
    assert_nested_close(saved['toy'],json.loads(json.dumps(m.evaluate())))


class Controls(HTMLParser):
    def __init__(self,text):
        super().__init__(); self.nodes={}; self.select=None; self.option=None; self.feed(text)
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:
            self.nodes[attrs['id']]={'value':attrs.get('value',''),'checked':'checked' in attrs,
                'disabled':'disabled' in attrs,'tag':tag,'textContent':'','innerHTML':''}
        if tag=='select': self.select=attrs['id']; self.first=True
        if tag=='option': self.option=[attrs,'']
    def handle_data(self,data):
        if self.option is not None: self.option[1]+=data
    def handle_endtag(self,tag):
        if tag=='option':
            attrs,text=self.option
            if self.first or 'selected' in attrs: self.nodes[self.select]['value']=attrs.get('value',text)
            self.first=False; self.option=None
        if tag=='select': self.select=None


def test_actual_scripts_controls_invalid_reset_and_json_roundtrip(tmp_path):
    html=(SOURCE/'interactive.html').read_text()
    nodes=Controls(html).nodes
    for k in ('scheme','stage','series','origin','q','method','weather','reset','download'):
        assert nodes['scv-'+k]['disabled']
    assert '<noscript>' in html and 'overflow-x:auto' in html and 'min-width:680px' in html
    # CSS intent only; no real viewport/rendering claim.
    nodes['scv-table-data']={'textContent':(SOURCE/'table3.json').read_text()}
    fixture={'nodes':nodes,'model':str(SOURCE/'model.js'),'ui':str(SOURCE/'interactive.js')}
    code=r"""
const assert=require('node:assert/strict'),fs=require('fs'),vm=require('vm');
const f=FIXTURE, blobs=[], anchors=[], revoked=[], timers=[];
for(const n of Object.values(f.nodes)){n.events={};n.addEventListener=(e,fn)=>n.events[e]=fn;}
const ctx={setTimeout:(fn,ms)=>{assert.equal(ms,1000);timers.push(fn);},document:{getElementById:id=>f.nodes[id],createElement:()=>({click(){anchors.push({...this});}})},
 Blob:class{constructor(parts,opt){this.text=parts.join('');this.type=opt.type;}},
 URL:{createObjectURL:b=>{blobs.push(b);return 'blob:'+blobs.length;},revokeObjectURL:u=>revoked.push(u)}};
vm.createContext(ctx);vm.runInContext(fs.readFileSync(f.model,'utf8'),ctx);vm.runInContext(fs.readFileSync(f.ui,'utf8'),ctx);
const get=k=>f.nodes['scv-'+k],set=(k,v)=>{get(k).value=v;get(k).events.input();};
function save(){const n=revoked.length;get('download').events.click();assert.equal(revoked.length,n);assert.equal(timers.length,1);timers.shift()();const d=JSON.parse(blobs.at(-1).text);assert.equal(get('json').value,blobs.at(-1).text);
 assert.equal(anchors.at(-1).download,'series-cv-synthetic.json');assert.equal(blobs.at(-1).type,'application/json');
 assert.equal(revoked.at(-1),anchors.at(-1).href);assert.equal(d.toy.synthetic,true);
 const q=get('q').value==='auto'?null:Number(get('q').value);
 assert.deepEqual(d.toy,JSON.parse(JSON.stringify(ctx.SeriesCV.evaluate(undefined,get('scheme').value,q))));return d;}
assert.equal(get('origin').value,'92');assert.equal(get('series').value,'H');
assert.equal(get('download').disabled,false);const initial=save();
assert.ok(get('out').textContent.includes('内側MAE='));assert.ok(get('out').textContent.includes('外側MAE='));
assert.equal((get('split').innerHTML.match(/<rect /g)||[]).length,1000);
for(const scheme of ['series','time'])for(const stage of ['inner','outer','final']){
 set('scheme',scheme);set('stage',stage);for(const s of ['A','F','H']){set('series',s);set('origin','96');
 const d=save();assert.equal(d.display.stage,stage);assert.equal(d.display.series,s);assert.equal(d.display.origin,96);}}
set('q','0');assert.equal(save().toy.MASE,null);
set('method','Time-CV');assert.equal(save().table3_sensitivity.weather_contribution,null);
assert.ok(!get('table-out').textContent.includes('Q=0'));
get('weather').checked=false;get('weather').events.change();assert.equal(save().table3_sensitivity.dataset_count,10);
assert.ok(get('table-out').textContent.includes('原著掲載の全11平均='));
for(const [k,v] of [['origin',''],['origin','91'],['origin','97'],['origin','92.5'],['q','NaN'],['q','-1'],['q','101'],['q','5e-324']]){
 get('reset').events.click();const n=blobs.length;set(k,v);assert.equal(get('download').disabled,true);
 assert.ok(get('error').textContent);get('download').events.click();assert.equal(blobs.length,n);}
for(let i=0;i<3;i++){get('reset').events.click();assert.deepEqual(save(),initial);assert.deepEqual(save(),initial);}
assert.equal(blobs.length,28);console.log('28 captured JSON downloads; registered synthetic events; no browser');
""".replace('FIXTURE',json.dumps(fixture,ensure_ascii=False))
    script=tmp_path/'ui.cjs';script.write_text(code)
    subprocess.run(['node',str(script)],check=True)


def test_widget_and_source_contracts():
    from paper_lab.series_cv import widget
    rendered=widget(SOURCE)
    assert 'id="scv-table-data"' in rendered
    assert 'SeriesCV' in rendered and 'scv-split' in rendered
    for name in ('README.md','method.md','mapping.md','evidence.md','experiment.md','lab.yaml'):
        text=(SOURCE/name).read_text()
        assert '/workspace/' not in text
    evidence=(SOURCE/'evidence.md').read_text()
    assert '14.321' in evidence and '33' in evidence


def test_evaluate_rejects_invalid_types_and_overflow_instead_of_null():
    for data in ([], 'invalid', 1, {**m.dataset(),'A':tuple(range(100))},
                 {**m.dataset(),'A':[True]*100}, {**m.dataset(),'A':['1']*100},
                 {**m.dataset(),'A':[None]*100}):
        with pytest.raises(ValueError): m.evaluate(data)
    for value in (math.nan,math.inf,-math.inf,1_000_001,-1_000_001,10**500):
        data=m.dataset();data['A'][92]=value
        with pytest.raises(ValueError):m.evaluate(data)
    data=m.dataset();data['A']=[1e308 if i%2 else -1e308 for i in range(100)]
    with pytest.raises(ValueError):m.evaluate(data)
    for q in (True,'1',1_000_001,10**500):
        with pytest.raises(ValueError):m.evaluate(q=q)
    with pytest.raises(ValueError,match='nonfinite result'):m.evaluate(q=math.nextafter(0.,1.))
    for value in (-1_000_000,1_000_000):
        data={s:[value]*100 for s in m.IDS};r=m.evaluate(data)
        assert r['MAE']==0 and r['MASE'] is None
        json.dumps(r,allow_nan=False)


def test_js_dense_arrays_and_overflow_guard_before_json():
    script=r'''
const assert=require('node:assert/strict'),M=require(process.argv[1]);
for(const index of [0,8,92,99]){const d=M.dataset();delete d.A[index];assert.throws(()=>M.evaluate(d),/密な配列/);}
for(const a of [null,{},'1'.repeat(100),new Float64Array(100),Array(100).fill(true),Array(100).fill('1')]){
 const d=M.dataset();d.A=a;assert.throws(()=>M.evaluate(d));}
for(const d of [null,[],1,'invalid'])assert.throws(()=>M.evaluate(d));
for(const value of [NaN,Infinity,-Infinity,1000001,-1000001]){
 const d=M.dataset();d.A[92]=value;assert.throws(()=>M.evaluate(d));}
const huge=M.dataset();huge.A=Array.from({length:100},(_,i)=>i%2?1e308:-1e308);assert.throws(()=>M.evaluate(huge));
for(const q of [true,'1',1000001,NaN,Infinity])assert.throws(()=>M.evaluate(undefined,'series',q));
assert.throws(()=>M.evaluate(undefined,'series',Number.MIN_VALUE),/非有限/);
const zero=M.evaluate(undefined,'series',0);assert.equal(zero.MASE,null);assert.ok(Number.isFinite(zero.MAE));
for(const value of [-1000000,1000000]){
 const d=Object.fromEntries([...'ABCDEFGHIJ'].map(s=>[s,Array(100).fill(value)])),r=M.evaluate(d);
 assert.equal(r.MAE,0);assert.equal(r.MASE,null);assert.equal(JSON.parse(JSON.stringify(r)).MASE,null);}
console.log('dense arrays, bounded input, finite output guard; null only for Q=0');
'''
    subprocess.run(['node','-e',script,str(SOURCE/'model.js')],check=True)


def test_table3_transcription_matches_supplied_published_display_fixture():
    # Separate literal fixture from the task's published Table3; not raw experiment data.
    expected={
        'ECL':[.596,.592,.591,.595,.600,.604,.577],
        'Exchange':[.151,.153,.147,.145,.145,.147,.155],
        'Traffic':[.702,.671,.688,.691,.691,.677,.692],
        'Weather':[.976,.920,.939,.928,.940,.934,1.115],
        'Hospital':[.811,.814,.797,.796,.804,.804,.804],
        'M1-M':[.904,.901,.909,.912,.903,.903,.920],
        'M1-Q':[1.124,1.138,1.120,1.131,1.121,1.114,1.124],
        'M3-M':[.813,.797,.755,.799,.797,.786,.737],
        'M3-Q':[.832,.827,.891,.819,.848,.865,.874],
        'Tourism-M':[1.320,1.320,1.312,1.333,1.333,1.321,1.323],
        'Tourism-Q':[1.275,1.304,1.494,1.278,1.307,1.290,1.387],
    }
    table=json.loads((SOURCE/'table3.json').read_text())
    assert table['methods']==['Bootstrap','Holdout','Kf-CV','K-MC-CV','K-Bootstrap','K-Holdout','Time-CV']
    assert table['rows']==expected
    assert table['published_mean']==[.864,.858,.877,.857,.863,.859,.883]
    assert m.sensitivity('Holdout',False)['published_full_mean']==.858



def test_q_text_underflow_never_becomes_valid_zero(tmp_path):
    """Actual UI parsing must distinguish an unrepresentable Q from explicit zero."""
    nodes=Controls((SOURCE/'interactive.html').read_text()).nodes
    nodes['scv-table-data']={'textContent':(SOURCE/'table3.json').read_text()}
    fixture={'nodes':nodes,'model':str(SOURCE/'model.js'),'ui':str(SOURCE/'interactive.js')}
    code=r"""
const assert=require('node:assert/strict'),fs=require('fs'),vm=require('vm');
const f=FIXTURE,blobs=[],timers=[];
for(const n of Object.values(f.nodes)){n.events={};n.addEventListener=(e,fn)=>n.events[e]=fn;}
const ctx={setTimeout:(fn,ms)=>{assert.equal(ms,1000);timers.push(fn);},document:{getElementById:id=>f.nodes[id],createElement:()=>({click(){}})},
 Blob:class{constructor(parts){this.text=parts.join('');}},
 URL:{createObjectURL:b=>{blobs.push(b);return 'blob:test';},revokeObjectURL(){}}};
vm.createContext(ctx);vm.runInContext(fs.readFileSync(f.model,'utf8'),ctx);
vm.runInContext(fs.readFileSync(f.ui,'utf8'),ctx);
const get=k=>f.nodes['scv-'+k],setQ=q=>{get('q').value=q;get('q').events.input();};
const invalid=['1e-400','-1e-400','+1e-400','0.01e-400','.00001E-400',' 1e-400 ','1.00e-400','-0.01e-400'];
for(const q of invalid){
 setQ(q);assert.equal(get('download').disabled,true,'underflow must block saving: '+q);
 assert.ok(get('error').textContent,'underflow must explain invalid input: '+q);
 assert.equal(get('out').textContent,'入力不正：結果を保留');
 const n=blobs.length;get('download').events.click();assert.equal(blobs.length,n);
 // Recovery must work without reloading after each failed input.
 setQ('auto');assert.equal(get('download').disabled,false);assert.equal(get('error').textContent,'');
}
for(const q of ['0','-0','+0','0e-400','-0.000E-400',' 0.000e+400 ']){
 setQ(q);assert.equal(get('download').disabled,false,'explicit zero remains valid: '+q);
 get('download').events.click();const saved=JSON.parse(blobs.at(-1).text);
 assert.equal(saved.toy.Q,0);assert.equal(saved.toy.MASE,null);
}
for(const q of ['1e-308','1e-3','100','1.25e1']){
 setQ(q);assert.equal(get('download').disabled,false,'representable Q remains valid: '+q);
 get('download').events.click();const saved=JSON.parse(blobs.at(-1).text);
 assert.equal(saved.toy.Q,Number(q));assert.ok(Number.isFinite(saved.toy.MASE));
}
setQ('5e-324');assert.equal(get('download').disabled,true); // Existing overflow guard remains.
get('reset').events.click();assert.equal(get('q').value,'auto');assert.equal(get('download').disabled,false);
assert.equal(timers.length,blobs.length);while(timers.length)timers.shift()();
console.log('Q text parser: 8 underflow cases, 6 explicit-zero cases, 4 finite cases, recovery and existing overflow guard');
""".replace('FIXTURE',json.dumps(fixture,ensure_ascii=False))
    script=tmp_path/'q-underflow.cjs';script.write_text(code)
    subprocess.run(['node',str(script)],check=True)
