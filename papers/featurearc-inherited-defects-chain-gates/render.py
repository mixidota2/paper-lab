"""Build the original teaching widget; static initial state survives without JS."""
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
    initial='<h3>第1段階：境界を含む絞込み</h3><p>絞込みを実装したが、境界の値2を落としている。失敗しても状態は引き継がれる。</p>'
    initial+='<div class="arc-grid">'+suite('自己テスト',first['self_test'])+suite('stage F2P',first['f2p'])+suite('stage P2P',first['p2p'])+'</div><p class="arc-verdict">stage gate：<b data-stage-gate>FAIL</b></p><p data-chain-pending>chain gate：未実行。第3段階の最終コードを待つ。</p>'
    encoded=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
    script=(Path(__file__).parent/'interactive.js').read_text()
    summary='<h3>手作り5例の集計（著者の成功率ではない）</h3>'
    for repair,label in [('false','仮想修正なし'),('true','仮想修正あり')]:
        m=data['metrics'][repair]
        summary+=f'<p><strong>{label}</strong>：'+ ' ／ '.join(f'{title} {m[key]["numerator"]}/{m[key]["denominator"]}' for key,title in [('first','初段合格'),('chain','最終合格'),('last_pass_chain_fail','最終段階合格後のchain失敗'),('recovery','一度失敗した後の回復')])+'</p>'
    summary+='<p>各条件5例を等重みで集計。分母は指標ごとに異なる。修正ありの高い比率は、欠陥を直すと決めた人工例の結果であり、修復方策の効果推定ではない。</p>'

    return '## 自分で試す：最後の追加が通っても、境界値は戻らない\n\nこの実験は自作の決定論的なプログラムです。実LLM・著者の73課題を実行していません。選択に応じたPythonの実行記録を表示します。入力は整数列で、元からある合計処理を保ちながら、絞込み・件数制限・文字列表示を順に追加します。\n\n第1段階は「閾値以上」を残す仕様です。初期例では `>` と実装したため値2を落とします。第2段階もその絞込みを呼ぶので、同じ欠陥が残ります。第3段階の局所テストは境界値を使わず、表示と件数制限だけを確かめます。chain F2Pは境界値を含む要求全体を、chain P2Pは開始前からある符号付き合計を検査します。\n\n「前へ」は保存済み記録の閲覧で、実行時のrollbackではありません。仮想修正は隠れたテストを読まず第3段階に固定の修正を加える教材独自の介入であり、論文が検証した改善策ではありません。\n\n<section id="arc-toy" aria-label="FeatureArcの自作3段階実験">\n<style>\n#arc-toy{background:#eff5f3;border:1px solid #c8d9d2;border-radius:16px;padding:clamp(12px,3vw,24px);color:#173e35}#arc-toy *{box-sizing:border-box}#arc-toy select{display:block;width:100%;font:inherit;padding:10px;white-space:normal}#arc-toy label{display:block;margin:12px 0}#arc-toy button{font:inherit;min-height:44px;padding:8px 16px;margin:4px;border:1px solid #537b6b;border-radius:6px;background:white;color:#173e35}#arc-toy :focus-visible{outline:3px solid #a04715;outline-offset:3px}#arc-toy button:disabled{opacity:.5}.arc-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr));gap:12px}.arc-suite{background:white;padding:12px;min-width:0;border-radius:8px}.arc-check{border-top:1px solid #d9e4de;padding-top:10px;overflow-wrap:anywhere}.arc-check code{white-space:normal;overflow-wrap:anywhere}.arc-verdict{font-size:1.15rem;border-left:5px solid #346756;padding:12px;background:white}#arc-output{overflow-wrap:anywhere}#arc-output h4{margin-top:0}\n</style>\n<label for="arc-scenario">実装と自己テストの選択<select id="arc-scenario">'+options+'</select></label>\n<label><input id="arc-repair" type="checkbox"> 教材独自の仮想介入：第3段階で以前の欠陥を修正する</label>\n<div><button id="arc-prev" type="button" disabled>前の記録</button><button id="arc-next" type="button">次の段階</button><button id="arc-reset" type="button">初期状態に戻す</button></div>\n<noscript>JavaScriptが無効です。初期条件の実際の検査結果を以下に表示します。全条件は配布results.jsonにあります。</noscript>\n<div id="arc-output" aria-live="polite">'+initial+'</div><script id="arc-data" type="application/json">'+encoded+'</script><script>'+script+'</script>'+summary+'</section>\n'
