"""Source-specific widget, including usable initial tables without JavaScript."""
import json
from fractions import Fraction


def widget(results, source):
    s = results['scenarios'][0]
    c = s['cases'][0]
    names = dict(order='発注', wait='待つ', ordered='発注済')
    def num(x):
        return float('inf') if x == '∞' else float(Fraction(x))
    rows = ''.join('<tr>'+f'<td>{r["t"]} / {r["u"]}</td>'+''.join(f'<td>{r[k]}</td>' for k in ('alpha','beta','increment','z'))
                   +f'<td><span class="clock" style="width:{min(1,num(r["z"]))*100:g}%" aria-hidden="true"></span></td>'
                   +f'<td>{names[r["action"]]}</td><td>{r["charge"]}</td></tr>' for r in c['rows'])
    ledger = ''.join('<tr>'+''.join(f'<td>{r[k]}</td>' for k in ('t','demand','order','arrived','inventory','cost'))+'</tr>' for r in c['ledger'])
    summary = f'固定ρ={c["rho"]}・経路{c["leaf"]+1}：実費用 {c["cost"]} ／ 条件付き費用分解 {c["conditional_charge"]}。この経路だけに近似保証はありません。'
    expect = f'<p>同じ情報で判断するOPT<br><b>{num(s["opt"]):.6f}</b></p><p>ρと需要を平均したCT費用<br><b>{s["expected"]["cost"]:.6f}</b></p><p>選択した方式の平均費用<br><b>{s["expected"]["cost"]:.6f}</b></p>'
    t = results['tight'][3]
    tight = f'発注確率 {t["order_probability"]:.6f} ／ OPT {t["opt"]:.6f} ／ CT期待費用 {t["cost"]:.6f} ／ 比 {t["ratio"]:.6f}'
    html = (source/'interactive.html').read_text()
    for key, value in dict(ROWS=rows,LEDGER=ledger,SUMMARY=summary,EXPECT=expect,TIGHT=tight,
                           DATA=json.dumps(results,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c'),
                           JS=(source/'interactive.js').read_text()).items():
        html = html.replace('__'+key+'__', value)
    return html
