"""InvEvolve order response and certification figures, generated from results.json."""
import json
from html import escape
from paper_lab.batch28 import table


def widget(result):
    if not isinstance(result,dict) or result.get('lab30')!='invevolve': return ''
    frames=[]
    for f in result['frames']:
        svg='<svg viewBox="0 0 600 310" role="img" aria-label="在庫不足と発注量の関係" style="width:100%;height:auto"><path d="M45 20V255H575" stroke="currentColor" fill="none"/>'
        for key,label,color in [('cbs','CBS','#697680'),('tilted','Tilted-CBS','#087f8c'),('pic','Tilted-PIC','#c65432')]:
            points=' '.join(f'{45+r["gap"]*17},{255-r[key]*10}' for r in f['curve'])
            svg+=f'<polyline points="{points}" stroke="{color}" fill="none" stroke-width="3"/>'
        svg+='<text x="48" y="278">不足 Δ：0 → 30</text><text x="48" y="18">発注量 q（上端 23.5）</text><text x="50" y="303" fill="#697680">CBS</text><text x="170" y="303" fill="#087f8c">Tilted-CBS</text><text x="340" y="303" fill="#c65432">Tilted-PIC</text></svg>'
        svg+=f'<p>r_base=4、α={f["alpha"]}、Kp={f["kp"]}。横軸の不足は目標 S から在庫ポジション IP を引いた正の部分。曲線は整数の不足ごとに計算した点を結ぶ。</p>'
        svg+=table(['Δ','CBS','Tilted-CBS','Tilted-PIC'],[[r['gap'],r['cbs'],r['tilted'],r['pic']] for r in f['curve'] if r['gap'] in (0,5,10,20,30)])
        frames.append(svg)
    options=''.join(f'<option value="{i}">{escape(f["label"])}</option>' for i,f in enumerate(result['frames']))
    data=json.dumps(frames,ensure_ascii=False).replace('</','<\\/')
    html='<figure class="teaching" data-b21><h3>固定上限を傾け、比例ゲインで発注を抑える</h3><label>係数 <select>'+options+'</select></label><script type="application/json" data-frames>'+data+'</script><div data-output aria-live="polite">'+frames[0]+'</div><figcaption>§5.3.2 の式を run.py で計算。性能曲線ではない。</figcaption></figure>'
    html+='<figure class="teaching"><h3>平均費用が下がっても、認証は通らない</h3>'
    html+=table(['人工需要の方策','平均費用','改善平均','LCB','UCB'],[[r['policy']]+[round(r[k],3) for k in ('cost','gain','lcb','ucb')] for r in result['replay']])
    html+='<p>256経路、B=114、δ=0.05、比較数N=2。半径は21.093。ξ=0でも両候補のLCBが負なので、配備は参照CBSへ戻る。UCBが大きいだけでは選べない。</p><figcaption>人工需要の最小実験。論文の小標本t半径、需要シフト校正、LLM探索は未実装。</figcaption></figure>'
    return html
