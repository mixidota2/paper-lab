from pathlib import Path
import yaml

def test_orpr_model_size_is_parameter_count():
    lab = Path(__file__).resolve().parents[1] / "papers/orpr-or-guided-pretrain-reinforce-inventory"
    summary = yaml.safe_load((lab / "lab.yaml").read_text())["summary"]
    readme = (lab / "README.md").read_text()
    for text in (summary, readme):
        assert "約93万パラメータのモデルを事前学習する" in text
        assert "約0.93Mの補充方策を事前学習する" not in text


def test_display_names_preserve_raw_keys_and_numeric_values():
    import json
    from copy import deepcopy
    from paper_lab.build import results_to_html
    from paper_lab.display_labels import explorer_view
    root = Path(__file__).resolve().parents[1]
    for path in (root / 'papers').glob('*/results.json'):
        original = json.loads(path.read_text())
        before = deepcopy(original)
        if not isinstance(original, dict):
            continue
        explorer = original.get('explorer')
        view = explorer_view(path.parent.name, explorer)
        def numeric_tree(value):
            if isinstance(value, dict):
                return {k: numeric_tree(v) for k, v in value.items()}
            if isinstance(value, list):
                return [numeric_tree(v) for v in value]
            return '<text>' if isinstance(value, str) else value
        assert numeric_tree(view) == numeric_tree(explorer)
        assert original == before
    data = {'experiments': [{'name': '比較', 'metrics': {'same_runtime_as_reference': True, 'safe_total': 7}}]}
    html = results_to_html(data, 'execution-state-unlearning')
    table = html.split('<details>')[0]
    assert '内部状態全体が一致するか' in table
    assert '忘却対象ではない入力値の合計' in table
    assert 'same_runtime_as_reference' in html.rsplit('<details>', 1)[1]
    assert data['experiments'][0]['metrics']['safe_total'] == 7


def test_orpr_different_units_use_tables_without_bars():
    import json
    from paper_lab.inventory02 import orpr
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root/'papers/orpr-or-guided-pretrain-reinforce-inventory/results.json').read_text())
    output = orpr(data)
    assert '% / pp' not in output
    import re
    panels = re.findall(r'<script type="application/json" data-frames>(.*?)</script>', output)
    frames = json.loads(panels[1])
    assert '<svg' in frames[0]  # Days remain comparable as differences in days.
    for frame in frames[1:]:
        assert '<svg' not in frame and '<rect' not in frame
        assert '<table>' in frame and '比較基準' in frame
    assert '<td>+2.29</td><td>%</td>' in frames[1]
    assert '<td>+0.47</td><td>ポイント</td>' in frames[1]
    assert '<td>-29.95</td><td>%</td>' in frames[2]
    assert '<td>-18.35</td><td>ポイント</td>' in frames[2]


def test_null_display_distinguishes_denominator_from_overflow():
    import subprocess
    root = Path(__file__).resolve().parents[1]
    for slug in ['reasoncast-agentic-demand-forecasting', 'retailbench-long-horizon-store-agents']:
        path = root/'papers'/slug/'interactive.js'
        js = f'''const f=require({str(path)!r}).metricText;
        if(f(null,true)!=='未定義'||f(null,false)!=='計算不能'||f(0,true)!==0)process.exit(1);'''
        subprocess.run(['node', '-e', js], check=True)


def test_three_figure_generators_preserve_current_labels(tmp_path):
    import importlib.util
    import json
    import shutil
    root = Path(__file__).resolve().parents[1]
    for slug, names in [
        ('accuracy-not-service-intermittent-demand', ['rank-scatter.svg', 'recentering.svg']),
        ('icegr-baidu-intent-generative-retrieval', ['margin-curve.svg']),
        ('sidinspector-mapping-diagnostics', ['mapping-grid.svg']),
    ]:
        src = root/'papers'/slug
        dst = tmp_path/slug
        shutil.copytree(src, dst)
        spec = importlib.util.spec_from_file_location('local_plot', dst/'plot.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.render(json.loads((dst/'results.json').read_text()))
        for name in names:
            assert (src/name).read_bytes() == (dst/name).read_bytes(), (slug, name)


def test_internal_consistency_of_distillation_and_probe_scope():
    root = Path(__file__).resolve().parents[1]
    one = yaml.safe_load((root/'papers/onetrans-v2-cascade-unification/lab.yaml').read_text())
    assert '精密な順位付けから粗い順位付けへ' in one['sections']['why_it_might_work']
    text = (root/'papers/onetrans-v2-cascade-unification/lab.yaml').read_text()
    assert 'title: 蒸留を受ける側' in text
    assert 'text: 精密な順位付けを教師として学ぶ' in text
    sparse = yaml.safe_load((root/'papers/tsfm-sparse-event-ranking/lab.yaml').read_text())
    assert 'probeで比較した6モデルすべて' in sparse['summary']
    assert '12 TSFM' in sparse['summary']


def test_retail_stop_display_uses_accounting_mode_and_actual_stop():
    import subprocess
    root = Path(__file__).resolve().parents[1]
    folder = root/'papers/retailbench-long-horizon-store-agents'
    js = f'''const assert=require('node:assert/strict');
    const model=require({str(folder/'model.js')!r}),ui=require({str(folder/'interactive.js')!r});
    let x={{...model.defaults,cash:0,rent:100,days:2,demand:0}};
    let a=model.evaluate(x).suppliers[0];
    assert(a.final_cash<0);assert.equal(a.stopped,null);assert(a.trace[1].active);
    assert.equal(ui.stopDayText(x.mode,a.stopped),'対象外（負現金でも継続）');
    x.mode='funded';a=model.evaluate(x).suppliers[0];
    assert.equal(a.stopped,1);assert.equal(a.trace[1].active,false);
    assert.equal(ui.stopDayText(x.mode,a.stopped),1);
    x.cash=10000;a=model.evaluate(x).suppliers[0];
    assert.equal(ui.stopDayText(x.mode,a.stopped),'停止判断なし');
    assert.equal(ui.inputErrorText('priceを入力してください。'),'販売価格pを入力してください。');
    assert.equal(ui.inputErrorText('baseは有限な7日分の値が必要です。'),'基準予測bは、計算で扱える範囲の数値を7日分入力してください。');
    assert(ui.inputErrorText('このLabのschema 2・教材仕様2.0.0のJSONを使ってください。').includes('保存形式2'));
    '''
    subprocess.run(['node','-e',js],check=True)


def test_apollopfn_distinguishes_comparisons():
    import xml.etree.ElementTree as ET
    path = Path(__file__).resolve().parents[1]/'papers/apollopfn/figures/zero-shot.svg'
    text = ''.join(ET.parse(path).getroot().itertext())
    assert '追加学習なしの予測と、表形式モデルとの比較は分けて読む' in text


def test_explorer_axes_match_saved_series():
    import json
    from paper_lab.display_labels import explorer_axes
    root = Path(__file__).resolve().parents[1]
    for slug, first, last in [('whole-foods-shelf', 10, 90), ('vn2-stockout-catboost', 1, 8)]:
        data = json.loads((root/'papers'/slug/'results.json').read_text())
        axes = explorer_axes(slug)
        assert axes['start'] == first
        assert all(len(f['lines'][0]['values']) + first - 1 == last for f in data['explorer']['frames'])
        assert ('面積' if first == 10 else '数量（個）') in axes['caption']


def test_parse_errors_identify_field_without_coercing_missing_values():
    import subprocess
    root = Path(__file__).resolve().parents[1]
    folder = root/'papers/reasoncast-agentic-demand-forecasting'
    script = f'''const assert=require('node:assert/strict');
    const model=require({str(folder/'model.js')!r}),ui=require({str(folder/'interactive.js')!r});
    for(const [key,label] of [['base','基準予測b'],['actual','実績y'],['additive','加算量a'],['level','対数倍率l']]){{
      assert.throws(()=>ui.parseInputValue(model,key,'1,,2',[]),e=>e.message.startsWith(label+'：') && e.message.includes('欠測を0には変換しません'));
      assert.throws(()=>ui.parseInputValue(model,key,'1,Infinity',[]),e=>e.message.startsWith(label+'：') && e.message.includes('計算で扱える範囲'));
      assert.deepEqual(ui.parseInputValue(model,key,'0,1,2,3,4,5,6',[]),[0,1,2,3,4,5,6]);
    }}
    for(const bad of ['金額が有限値を超えました。','境界計算が有限値を超えました。'])assert(ui.inputErrorText(bad).includes('計算できる範囲'));
    assert(ui.inputErrorText('強さは0〜1、経路はSkipまたは補正です。').includes('補正しない（Skip）'));
    '''
    subprocess.run(['node','-e',script],check=True)


def test_orpr_budget_caption_uses_fixed_synthetic_demand():
    import importlib.util
    import json
    from paper_lab.inventory02 import orpr
    folder = Path(__file__).resolve().parents[1]/'papers/orpr-or-guided-pretrain-reinforce-inventory'
    data = json.loads((folder/'results.json').read_text())
    html = orpr(data)
    assert '固定した合成需要の合計×(1−αloss)' in html
    assert '基準販売量' not in html


def test_explorer_display_all_saved_frames_without_browser(tmp_path):
    import json
    import subprocess
    from paper_lab.display_labels import LINE_AXES, explorer_axes, explorer_view
    root = Path(__file__).resolve().parents[1]
    cases = [{'slug': slug, 'data': explorer_view(slug, json.loads((root/'papers'/slug/'results.json').read_text())['explorer']), 'axes': explorer_axes(slug)} for slug in LINE_AXES]
    payload = tmp_path/'cases.json'
    payload.write_text(json.dumps(cases, ensure_ascii=False))
    subprocess.run(['node', str(root/'tests/explorer_display_smoke.js'), str(payload), str(root/'paper_lab/templates/interactives.js')],check=True)
