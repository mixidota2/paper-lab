from pathlib import Path
import hashlib,json
import yaml

from prose_preservation import before_sim2real_all_full_prose, before_harnesstokens_full_prose
ROOT=Path(__file__).resolve().parents[1]
REL='papers/harness-buys-tokens-not-pass-rate/'
P=ROOT/REL

def old(path):return before_harnesstokens_full_prose(ROOT,path,(ROOT/path).read_bytes())

def test_author_v2_and_lab_v1_are_separate():
    d=yaml.safe_load((P/'lab.yaml').read_bytes())
    previous=yaml.safe_load(old(REL+'lab.yaml'))
    for k in ('id','arxiv_id','title','authors','verification','status'):
        assert d[k]==previous[k]
    assert d['source_review']['version']=='v2' and d['urls']['pdf'].endswith('v2')
    s=d['sections'];t=s['overview']
    assert len(t.split('\n\n'))==2
    assert all(w in t for w in ('難しいコード修正45課題','約13%','約26%','約8〜9ポイント','約14ポイント','3〜4倍'))
    assert all(w not in t for w in ('Lab','人工例','<figure','<table','22%','事前に定めた'))
    assert all(w in s['evidence'] for w in ('13.3%','25.6%','+0.2ポイント','実行後に±5','27件成功','1.03倍','4.28元','1.36元'))
    assert '第1版' in s['executable_understanding']

def test_results_and_old_receipt_numbers_are_unchanged():
    for file,keys in (('official-check.json',('scope',)),('results.json',('note',))):
        a,b=(json.loads(v) for v in ((P/file).read_bytes(),old(REL+file)))
        for row in (a,b):
            for k in keys:del row[k]
            if file=='results.json':
                for x in row['experiments']:del x['name']
        assert a==b


def test_dedicated_widget_leaves_shared_renderer_exact():
    from paper_lab.harness_cost import HARNESS, HARNESS_JS, widget
    build_text = (ROOT / 'paper_lab/build.py').read_text()
    path = 'paper_lab/batch08.py'
    prior = before_sim2real_all_full_prose(ROOT, path, (ROOT / path).read_bytes())
    assert hashlib.sha256(prior).hexdigest() == 'ede12f233a1c6bbd58e89d06a2a0365f8c00dae3f08df6a8ea5abaee41ff4eed'
    assert 'if lab.id == "harness-buys-tokens-not-pass-rate":\n                html += harness_cost_widget(lab.results)' in build_text
    assert widget({'lab_kind':'sim08'}) == ''
    assert widget({'lab_kind':'hear08'}) == ''
    assert widget({'lab_kind':'traffic08'}) == ''
    source = HARNESS + HARNESS_JS
    assert all(x in source for x in ('第1版','第2版','25.6%','実行後','data-n','data-q','data-bill'))
    released = widget(json.loads((P / 'results.json').read_text()))
    assert released.count('data-batch08>') == 1
    assert released.count('class="b08 harness08"') == 1
