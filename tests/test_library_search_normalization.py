"""Unicode search equivalence on generated cards; not native input-method QA."""
import json
import subprocess

import pytest

from test_library_navigation import RUNNER as BASE_RUNNER, library


# Extend the reusable harness oracle without changing existing regression tests.
RUNNER = BASE_RUNNER.replace(
    "c.dataset.search.includes(e.search.value.trim().toLocaleLowerCase('ja'))",
    "c.dataset.search.normalize('NFKC').toLocaleLowerCase('ja').includes("
    "e.search.value.normalize('NFKC').trim().toLocaleLowerCase('ja'))",
)
assert RUNNER != BASE_RUNNER

CASES = {
    'fullwidth_latin_matches_actual_labs': r"""
for(const [plain,wide] of [['EXAONE','ＥＸＡＯＮＥ'],['Netflix','Ｎｅｔｆｌｉｘ'],['SIDScope','ＳＩＤＳｃｏｐｅ']]){
  const expected=app(origin+'?search='+encodeURIComponent(plain));
  assert.ok(expected.visible().length>0,plain+' has real matching cards');
  const actual=app();actual.edit({search:wide});
  assert.deepEqual(actual.visible(),expected.visible());
}
""",
    'halfwidth_katakana_and_combining_marks': r"""
for(const [plain,alternate] of [['モデル','ﾓﾃﾞﾙ'],['データ','テ\u3099ータ']]){
  const expected=app(origin+'?search='+encodeURIComponent(plain));
  assert.ok(expected.visible().length>0);
  const actual=app();actual.edit({search:alternate});
  assert.deepEqual(actual.visible(),expected.visible());
}
""",
    'card_text_is_normalized_too': r"""
f.cards.forEach(c=>c.search='unrelated');
f.cards[0].search='ＡＢＣ ｶﾞﾗｽ cafe\u0301 ①';
for(const word of ['abc','ガラス','café','1']){
  const actual=app();actual.edit({search:word});assert.deepEqual(actual.visible(),[0]);
}
""",
    'literal_input_url_and_unrelated_context_are_preserved': r"""
const original='　ＥＸＡＯＮＥ　';
const a=app(origin+'?keep=one&keep=two#library');a.e.search.focus();
a.edit({search:original});
assert.equal(a.visible().length,1);assert.equal(a.e.search.value,original);
assert.equal(new URL(a.win.location.href).searchParams.get('search'),original);
assert.deepEqual(new URL(a.win.location.href).searchParams.getAll('keep'),['one','two']);
assert.equal(new URL(a.win.location.href).hash,'#library');assert.equal(a.doc.activeElement,a.e.search);
const b=app(a.win.location.href);assert.deepEqual(b.visible(),a.visible());
assert.equal(b.e.search.value,original);assert.equal(b.calls.length,0);
const n=a.calls.length;a.edit({search:original},'change');assert.equal(a.calls.length,n);
""",
    'ime_commit_keeps_draft_guard': r"""
const a=app(),all=a.visible();a.form.dispatchEvent(new Event('compositionstart'));
for(const text of ['Ｅ','ＥＸＡ','ＥＸＡＯＮＥ']){
  a.e.search.value=text;const event=new Event('input');event.isComposing=true;
  a.form.dispatchEvent(event);assert.deepEqual(a.visible(),all);assert.equal(a.calls.length,0);
}
a.form.dispatchEvent(new Event('compositionend'));a.check();
assert.equal(a.visible().length,1);
assert.equal(new URL(a.win.location.href).searchParams.get('search'),'ＥＸＡＯＮＥ');
""",
    'filters_sort_navigation_and_clear_still_apply': r"""
const a=app();a.edit({search:'ﾓﾃﾞﾙ',topic:'recommender-systems',verdict:'Must Read',sort:'title'});
const b=app();b.edit({search:'モデル',topic:'recommender-systems',verdict:'Must Read',sort:'title'});
assert.ok(a.visible().length>0);assert.deepEqual(a.visible(),b.visible());
const saved=a.win.location.href;a.edit({search:'no such paper'});assert.equal(a.visible().length,0);
a.travel(saved);assert.deepEqual(a.visible(),b.visible());assert.equal(a.e.search.value,'ﾓﾃﾞﾙ');
a.clear.dispatchEvent(new Event('click'));a.check();assert.equal(a.visible().length,114);
""",
    'unavailable_history_and_window_do_not_block_search': r"""
for(const mode of [{throwWrite:true},{noWindow:true}]){
 const a=app(origin,mode);a.edit({search:'ＥＸＡＯＮＥ'});
 assert.equal(a.visible().length,1);assert.equal(a.e.search.value,'ＥＸＡＯＮＥ');
 assert.equal(a.calls.length,0);
}
""",
    'matching_stays_literal_not_fuzzy_or_accent_blind': r"""
f.cards.forEach(c=>c.search='unrelated');f.cards[0].search='café モデル [x] a+b';
const a=app();
for(const word of ['cafe','もでる','.*','<script>']){
 a.edit({search:word});assert.deepEqual(a.visible(),[]);
}
for(const word of ['café','ﾓﾃﾞﾙ','[x]','a+b']){
 a.edit({search:word});assert.deepEqual(a.visible(),[0]);
}
""",
}


@pytest.mark.parametrize('case', CASES)
def test_library_search_normalization(case, library, tmp_path):
    source = RUNNER.replace('FIXTURE', json.dumps(library, ensure_ascii=False)).replace('CASE', CASES[case])
    path = tmp_path / f'{case}.cjs'
    path.write_text(source)
    subprocess.run(['node', str(path)], check=True)
