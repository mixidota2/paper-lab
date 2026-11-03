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
        ASUMMARY='r=(3, 2, 1)：最適cut 2、採用 k=2。g₀=1、半額上界=3/2。',
        SUMMARY=f'選好v=(1, 1, 1)、収益倍率=1、同じ選好の最適期待収益={c["oracle"]}。Cの総観測 2／判断に使用 2／判断に不使用 0。有効経路 6。',
        OBSERVATION='例示経路（平均ではありません）：B 購入 0/2 → [2]。C 観測ID (0) と (0)、平均収益 0 / 0 → [3]。閾値=1。奇数の余りは[1]に提示しますが判断には使いません。',
        DATA=json.dumps(results,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c'),JS=(source/'interactive.js').read_text())
    html=(source/'interactive.html').read_text()
    for key,value in replacements.items():html=html.replace('__'+key+'__',value)
    return html
