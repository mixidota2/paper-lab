"""教材の操作画面を組み立てる。JavaScriptが使えなくても、初めの結果は読める。"""
import html
import json
from pathlib import Path
from run import SCENARIOS


def suite(label,s):
    status=lambda b:'PASS' if b else 'FAIL'
    v=lambda x:html.escape(json.dumps(x,ensure_ascii=False,separators=(',',':')))
    expectation='自己テストの期待値' if label=='自己テスト' else '仕様の期待値'
    checks=''.join(f'<p class="arc-check"><strong>{c["name"]}：{status(c["passed"])}</strong><br><code>{c["op"]}({v(c["values"])}, 閾値 {c["threshold"]}, 上限 {c["limit"]})</code><br>{expectation} <code>{v(c["expected"])}</code> ／ 実際 <code>{v(c["actual"])}</code></p>' for c in s['checks'])
    return f'<section class="arc-suite"><h4>{label} <b data-gate="{label}">{status(s["passed"])}</b></h4>{checks}</section>'


def document(data):
    first=data['synthetic'][0]['stages'][0]
    options=''.join(f'<option value="{key}">{label}</option>' for key,label in SCENARIOS.items())
    initial='<h3>第1段階：閾値と同じ値も残す</h3><p>初期例の実装は、閾値と同じ値2を取り除いてしまいます。検査に落ちても、次の段階は同じ実装を引き継ぎます。</p>'
    initial+='<div class="arc-grid">'+suite('自己テスト',first['self_test'])+suite('stage F2P',first['f2p'])+suite('stage P2P',first['p2p'])+'</div><p class="arc-verdict">stage gate：<b data-stage-gate>FAIL</b></p><p data-chain-pending>機能全体の検査（chain gate）は、第3段階のコードを使って行います。</p>'
    encoded=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
    script=(Path(__file__).parent/'interactive.js').read_text()
    summary='<h3>教材の5例を集計する</h3>'
    for repair,label in [('false','仮想修正なし'),('true','仮想修正あり')]:
        m=data['metrics'][repair]
        summary+=f'<p><strong>{label}</strong>：'+ ' ／ '.join(f'{title} {m[key]["numerator"]}/{m[key]["denominator"]}' for key,title in [('first','初段合格'),('chain','最終合格'),('last_pass_chain_fail','最後の段階は合格、機能全体は不合格'),('recovery','一度失敗した後の回復')])+'</p>'
    summary+='<p>修正あり・なしの各条件で、手で選んだ5例を同じ重みで数えました。分母は指標によって違います。修正する条件では、結果が変わるように教材の規則を決めています。著者の成績でも、本番での修正の効果を測った値でもありません。</p>'

    return '## 最後の追加と、機能全体の検査結果を見比べる\n\n画面で例を選ぶと、Pythonで計算した記録が表示されます。教材の入力は整数の列です。もともとの合計を残しながら、閾値による絞り込み、件数の制限、文字列での表示を順に足します。実際の言語モデルや、著者の73課題は使いません。\n\n第1段階の仕様は「閾値以上」を残すことです。初期例の実装は `>` を使うので、閾値と同じ2を落とします。第2段階は前の絞り込みを使うため、2は戻りません。第3段階の検査は閾値と同じ値を使わず、表示と件数制限を調べます。機能全体のF2Pは以前の境界値まで戻って確かめ、機能全体のP2Pは元からあった符号付き合計を確かめます。\n\n「前の記録」で戻るのは、読む場所だけです。コードや実験結果は変わりません。修正する条件を選ぶと、第3段階であらかじめ決めた修正を加えます。隠れた検査の結果は使いません。この修正は教材独自で、著者が効果を調べた改善策ではありません。\n\n<section id="arc-toy" aria-label="FeatureArcの自作3段階実験">\n<style>\n#arc-toy{background:#eff5f3;border:1px solid #c8d9d2;border-radius:16px;padding:clamp(12px,3vw,24px);color:#173e35}#arc-toy *{box-sizing:border-box}#arc-toy select{display:block;width:100%;font:inherit;padding:10px;white-space:normal}#arc-toy label{display:block;margin:12px 0}#arc-toy button{font:inherit;min-height:44px;padding:8px 16px;margin:4px;border:1px solid #537b6b;border-radius:6px;background:white;color:#173e35}#arc-toy :focus-visible{outline:3px solid #a04715;outline-offset:3px}#arc-toy button:disabled{opacity:.5}.arc-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr));gap:12px}.arc-suite{background:white;padding:12px;min-width:0;border-radius:8px}.arc-check{border-top:1px solid #d9e4de;padding-top:10px;overflow-wrap:anywhere}.arc-check code{white-space:normal;overflow-wrap:anywhere}.arc-verdict{font-size:1.15rem;border-left:5px solid #346756;padding:12px;background:white}#arc-output{overflow-wrap:anywhere}#arc-output h4{margin-top:0}\n</style>\n<label for="arc-scenario">どの実装と自己テストを比べるか<select id="arc-scenario">'+options+'</select></label>\n<label><input id="arc-repair" type="checkbox"> 第3段階で以前の不具合を直す（教材用の固定した修正）</label>\n<div><button id="arc-prev" type="button" disabled>前の記録</button><button id="arc-next" type="button">次の段階</button><button id="arc-reset" type="button">初期状態に戻す</button></div>\n<noscript>JavaScriptが無効なため、最初の検査結果だけを表示しています。すべての条件を読むには、配布の results.json を開いてください。</noscript>\n<div id="arc-output" aria-live="polite">'+initial+'</div><script id="arc-data" type="application/json">'+encoded+'</script><script>'+script+'</script>'+summary+'</section>\n'
