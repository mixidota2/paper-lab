"""IME event-order regression checks, not native browser or input-method QA."""
import json
import subprocess

import pytest

from test_library_navigation import RUNNER, library


CASES = {
    'fallback_pageshow_releases_stale_conversion_without_losing_edits': r"""
const a=app(origin,{throwWrite:true});a.edit({search:'EXAONE'});
assert.equal(a.visible().length,1);assert.equal(a.win.location.href,origin);
a.form.dispatchEvent(new Event('compositionstart'));a.e.search.value='nothing matches';
a.form.dispatchEvent(new Event('input'));assert.equal(a.visible().length,1);
const ordinary=new Event('pageshow');ordinary.persisted=false;a.win.dispatchEvent(ordinary);
a.form.dispatchEvent(new Event('change'));assert.equal(a.visible().length,1);
a.travel(origin,'pageshow');
assert.equal(a.e.search.value,'nothing matches');assert.equal(a.visible().length,0);
assert.equal(a.win.location.href,origin);assert.equal(a.calls.length,0);
a.edit({search:'EXAONE'});assert.equal(a.visible().length,1);
assert.equal(a.calls.length,0);assert.match(a.status.textContent,/URLに残せません/);
""",
    'missed_start_stays_guarded_until_composition_end': r"""
const a=app(), initial=a.visible();a.e.search.value='EXAONE';
const input=new Event('input');input.isComposing=true;a.form.dispatchEvent(input);
const submit=new Event('submit',{cancelable:true});a.form.dispatchEvent(submit);
assert.equal(submit.defaultPrevented,true);
a.form.dispatchEvent(new Event('change'));
assert.deepEqual(a.visible(),initial);assert.equal(a.calls.length,0);
a.form.dispatchEvent(new Event('compositionend'));a.check();
assert.equal(a.visible().length,1);assert.equal(a.calls.length,1);
a.edit({search:''});assert.equal(a.visible().length,114);
""",
    'draft_waits_for_conversion_commit': r"""
const a=app(), initial=a.visible();
a.form.dispatchEvent(new Event('compositionstart'));
for(const text of ['E','EX','EXA','EXAONE']){
  a.e.search.value=text;
  a.form.dispatchEvent(new Event('input'));
  a.form.dispatchEvent(new Event('change'));
  assert.deepEqual(a.visible(),initial,'keep results stable during conversion');
  assert.equal(a.calls.length,0,'do not save partial conversion text');
}
a.form.dispatchEvent(new Event('compositionend'));a.check();
assert.equal(a.visible().length,1);
assert.equal(new URL(a.win.location.href).searchParams.get('search'),'EXAONE');
assert.equal(a.calls.length,1);
""",
    'confirming_enter_does_not_submit_draft': r"""
const a=app(), initial=a.visible();
a.form.dispatchEvent(new Event('compositionstart'));
a.e.search.value='EXAONE';
const event=new Event('submit',{cancelable:true});a.form.dispatchEvent(event);
assert.equal(event.defaultPrevented,true);
assert.deepEqual(a.visible(),initial);assert.equal(a.calls.length,0);
a.form.dispatchEvent(new Event('compositionend'));a.check();
assert.equal(a.visible().length,1);assert.equal(a.calls.length,1);
""",
    'composing_input_property_is_respected': r"""
const a=app(), initial=a.visible();a.e.search.value='EXAONE';
const event=new Event('input');event.isComposing=true;a.form.dispatchEvent(event);
assert.deepEqual(a.visible(),initial);assert.equal(a.calls.length,0);
a.form.dispatchEvent(new Event('compositionend'));a.check();
assert.equal(a.visible().length,1);assert.equal(a.calls.length,1);
""",
    'trailing_events_do_not_duplicate_history': r"""
const a=app();
for(const text of ['EXAONE','recommender','日本語 + & # 🧪']){
  a.form.dispatchEvent(new Event('compositionstart'));a.e.search.value=text;
  a.form.dispatchEvent(new Event('input'));
  const n=a.calls.length;
  a.form.dispatchEvent(new Event('compositionend'));a.check();
  assert.equal(a.calls.length,n+1);
  a.form.dispatchEvent(new Event('input'));a.form.dispatchEvent(new Event('change'));
  assert.equal(a.calls.length,n+1);
  assert.deepEqual(app(a.win.location.href).values(),a.values());
}
""",
    'clear_discards_active_conversion': r"""
const a=app(origin+'?search=EXAONE&keep=one#library');
a.form.dispatchEvent(new Event('compositionstart'));a.e.search.value='draft';
a.form.dispatchEvent(new Event('input'));a.clear.dispatchEvent(new Event('click'));a.check();
assert.deepEqual(a.values(),f.defaults);assert.equal(a.visible().length,114);
assert.equal(a.doc.activeElement,a.e.search);
assert.equal(new URL(a.win.location.href).searchParams.get('keep'),'one');
const n=a.calls.length;a.form.dispatchEvent(new Event('compositionend'));a.check();
assert.equal(a.calls.length,n);
a.edit({search:'EXAONE'});assert.equal(a.visible().length,1);
""",
    'navigation_cancels_conversion_state': r"""
const a=app(origin+'?search=EXAONE');
a.form.dispatchEvent(new Event('compositionstart'));a.e.search.value='draft';
a.form.dispatchEvent(new Event('input'));
a.travel(origin+'?topic=retail-supply');
assert.equal(a.e.search.value,'');assert.equal(a.e.topic.value,'retail-supply');
const n=a.calls.length;a.form.dispatchEvent(new Event('compositionend'));a.check();
assert.equal(a.calls.length,n);
a.edit({search:'EXAONE',topic:''});assert.equal(a.visible().length,1);
""",
    'cancelled_conversion_preserves_saved_query': r"""
const a=app(origin+'?search=EXAONE'), before=a.visible();
a.form.dispatchEvent(new Event('compositionstart'));a.e.search.value='draft';
a.form.dispatchEvent(new Event('input'));assert.deepEqual(a.visible(),before);
a.e.search.value='EXAONE';a.form.dispatchEvent(new Event('compositionend'));a.check();
assert.deepEqual(a.visible(),before);assert.equal(a.calls.length,0);
""",
    'history_failure_keeps_committed_filter_working': r"""
const a=app(origin,{throwWrite:true});
a.form.dispatchEvent(new Event('compositionstart'));a.e.search.value='EXAONE';
a.form.dispatchEvent(new Event('input'));assert.equal(a.status.hidden,true);
a.form.dispatchEvent(new Event('compositionend'));a.check();
assert.equal(a.visible().length,1);assert.equal(a.status.hidden,false);
assert.match(a.status.textContent,/URLに残せません/);
a.form.dispatchEvent(new Event('compositionstart'));a.e.search.value='nothing matches';
a.form.dispatchEvent(new Event('input'));assert.equal(a.visible().length,1);
a.form.dispatchEvent(new Event('compositionend'));a.check();
assert.equal(a.visible().length,0);
a.clear.dispatchEvent(new Event('click'));a.check();assert.equal(a.visible().length,114);
""",
}


@pytest.mark.parametrize('case', CASES)
def test_library_composition(case, library, tmp_path):
    source = RUNNER.replace('FIXTURE', json.dumps(library, ensure_ascii=False)).replace('CASE', CASES[case])
    path = tmp_path / f'{case}.cjs'
    path.write_text(source)
    subprocess.run(['node', str(path)], check=True)
