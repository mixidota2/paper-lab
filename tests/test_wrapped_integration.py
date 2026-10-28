"""WRAPPED semantics, real inline JS, preservation and protected-review planning."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

import pytest

from catalog_expectations import EXISTING, WRAPPED, TRACE, EPISEM, assert_catalog
from wrapped_review import assert_reported, assert_synthetic, inspect_wrapped_keyboard

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'papers'/WRAPPED


def test_catalog_rejects_replacement_of_an_existing_lab():
    assert_catalog(EXISTING | {TRACE,EPISEM})
    with pytest.raises(AssertionError):
        assert_catalog((EXISTING - {sorted(EXISTING)[0]}) | {TRACE,EPISEM,'invented-replacement'})


def test_wrapped_experiment_and_regeneration(tmp_path):
    shutil.copy2(SOURCE/'run.py',tmp_path/'run.py')
    subprocess.run([sys.executable,str(tmp_path/'run.py'),'--test'],check=True,capture_output=True)
    subprocess.run([sys.executable,str(tmp_path/'run.py')],check=True,capture_output=True)
    for name in ['results.json','evidence.md','experiment.md']:
        assert (tmp_path/name).read_bytes() == (SOURCE/name).read_bytes()


def test_actual_widget_scripts_select_all_states_and_reset():
    # Executes the shipped inline JS, with only DOM events/outputs stubbed.
    scripts = [re.findall(r'<script>(.*?)</script>',(SOURCE/name).read_text(),re.S)[0]
               for name in ['evidence.md','experiment.md']]
    harness = r'''
const fs=require('node:fs'), vm=require('node:vm');
const scripts=JSON.parse(fs.readFileSync(0,'utf8')), nodes={};
for(const [key,value] of Object.entries({outcome:'household',time:'2',ci:'',control:'1',shock:'0',mismatch:'1',simulation:'',reset:''})){
 nodes['wrapped-'+key]={value,innerHTML:'',events:{},addEventListener(t,f){this.events[t]=f;}};
}
const context={document:{getElementById(id){if(!nodes[id])throw Error(id);return nodes[id];}}};
for(const script of scripts)vm.runInNewContext(script,context);
function change(key,value){const n=nodes['wrapped-'+key];n.value=String(value);n.events.change();}
const result={reported:[],synthetic:[]};
for(const outcome of ['household','store'])for(let time=0;time<3;time++){
 change('outcome',outcome);change('time',time);
 result.reported.push({outcome,time,html:nodes['wrapped-ci'].innerHTML});
}
for(let c=0;c<3;c++)for(let s=0;s<3;s++)for(let m=0;m<3;m++){
 change('control',c);change('shock',s);change('mismatch',m);
 result.synthetic.push({c,s,m,html:nodes['wrapped-simulation'].innerHTML});
}
nodes['wrapped-reset'].events.click();
result.reset={values:['control','shock','mismatch'].map(x=>String(nodes['wrapped-'+x].value)),html:nodes['wrapped-simulation'].innerHTML};
process.stdout.write(JSON.stringify(result));
'''
    result = json.loads(subprocess.check_output(['node','-e',harness],input=json.dumps(scripts),text=True))
    data = json.loads((SOURCE/'results.json').read_text())
    assert len(result['reported']) == 6 and len(result['synthetic']) == 27
    for item in result['reported']:
        assert_reported(item['html'],data,item['outcome'],item['time'])
    for item in result['synthetic']:
        assert_synthetic(item['html'],data,item['c'],item['s'],item['m'])
    assert result['reset']['values'] == ['1','0','1']
    assert_synthetic(result['reset']['html'],data,1,0,1)
    # A stale/wrong selection must fail semantic and geometry checks.
    with pytest.raises(AssertionError):
        assert_reported(result['reported'][0]['html'],data,'store',0)
    with pytest.raises(AssertionError):
        assert_synthetic(result['synthetic'][0]['html'],data,2,2,2)


@pytest.mark.parametrize('broken', [None, 'ignored-key', 'stale-output', 'ignored-reset',
                                  'missing-focus', 'missing-key-events', 'untrusted-key-events',
                                  'ignored-return-key'])
def test_keyboard_gate_rejects_missing_interaction_or_output(broken):
    # This exercises the gate's failure paths, not native browser key behavior.
    # The protected macOS job remains required for the real native select.
    text = (SOURCE/'experiment.md').read_text()
    frames = json.loads(re.search(r'const frames=(.*?);const controls=', text, re.S)[1])
    data = json.loads((SOURCE/'results.json').read_text())
    values = ['2','2','2']
    output = [frames[26]]
    events = []
    focused = [None]

    def render():
        c,s,m = map(int,values)
        output[0] = frames[c*9+s*3+m]

    class Control:
        def __init__(self, index):
            self.index = index

        def input_value(self):
            return values[self.index]

        def focus(self):
            if broken != 'missing-focus':
                focused[0] = self.index

        def evaluate(self, expression):
            if 'document.activeElement' in expression:
                return focused[0] == self.index
            if 'addEventListener' in expression:
                events.clear()
                return
            return events

        def press(self, key):
            assert self.index == focused[0] == 0 and key in ('0','+')
            if broken != 'missing-key-events':
                events.extend({'type': kind, 'key': key, 'trusted': broken != 'untrusted-key-events'}
                              for kind in ['keydown','keypress','keyup'])
            if broken != 'ignored-key' and not (broken == 'ignored-return-key' and key == '+'):
                values[0] = {'0':'1', '+':'2'}[key]
            if broken != 'stale-output':
                render()

    class Reset:
        def focus(self):
            focused[0] = 'reset'

        def press(self, key):
            assert key == 'Enter' and focused[0] == 'reset'
            if broken != 'ignored-reset':
                values[:] = ['1','0','1']
                render()

    class Simulation:
        def inner_html(self):
            return output[0]

    class Page:
        def locator(self, selector):
            return {'#wrapped-reset':Reset(), '#wrapped-simulation':Simulation()}[selector]

    controls = [Control(i) for i in range(3)]
    if broken:
        with pytest.raises(AssertionError):
            inspect_wrapped_keyboard(Page(),data,controls)
    else:
        inspect_wrapped_keyboard(Page(),data,controls)
