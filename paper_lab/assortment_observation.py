"""Initial, accessible finite-experiment tables; no executable source import."""
import json
from fractions import Fraction


def widget(results,source):
    a=results['a'][0]
    c=next(c for c in results['cases'] if c['m']==2 and c['preference']==0 and c['scale']=='1')
    rows=''.join('<tr>'+''.join(f'<td>{r[k]}</td>' for k in ('k','exclusion','inclusion','regret'))+'</tr>' for r in a['cuts'])
    comparison=''.join(f'<tr><th scope="row">{p["name"]}</th>'+''.join(f'<td>{v}</td>' for v in (*p['distribution'],p['expected'],p['regret']))+'</tr>' for p in c['policies'])
    bars=''.join(f'<p>{p["name"]}：{p["regret"]}<span class="aob-bar" style="width:{100*float(Fraction(p["regret"]))/3}%" aria-hidden="true"></span></p>' for p in c['policies'])
    replacements=dict(ROWS=rows,COMPARISON=comparison,BARS=bars,
        ASUMMARY='収益r=(3, 2, 1)。最大損失が最も小さい区切りは2です。Aはk=2を選びます。g₀=1、最高収益の半分=3/2。',
        SUMMARY=f'評価用の選好v=(1, 1, 1)、収益の倍率=1。この選好を知っていれば、最適期待収益は{c["oracle"]}です。Cは全2回のうち2回の結果を使い、0回分は使いません。判断に使う経路数は6通りです。',
        OBSERVATION='ここでは観測の一例を示します。Bでは2人のうち0人が買い、Bは[2]を選びます。Cの第1群と第2群の購入結果は(0)と(0)です。各群の平均収益は0と0、判定に使う閾値は1です。Cは[3]を選びます。総観測数が奇数のときは最後の1回も[1]を提示しますが、その結果は判断に使いません。',
        DATA=json.dumps(results,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c'),JS=(source/'interactive.js').read_text())
    html=(source/'interactive.html').read_text()
    for key,value in replacements.items():html=html.replace('__'+key+'__',value)
    return html
