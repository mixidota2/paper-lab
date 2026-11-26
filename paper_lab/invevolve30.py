"""InvEvolve order quantities and paired cost comparisons from results.json."""
import json
from html import escape
from paper_lab.batch28 import table


def widget(result):
    if not isinstance(result,dict) or result.get('lab30')!='invevolve': return ''
    frames=[]
    for f in result['frames']:
        svg='<svg viewBox="0 0 600 310" role="img" aria-label="CBS、Tilted-CBS、Tilted-PICで在庫不足に応じて変わる発注量" style="width:100%;height:auto"><path d="M45 20V255H575" stroke="currentColor" fill="none"/>'
        for key,label,color in [('cbs','CBS','#697680'),('tilted','Tilted-CBS','#087f8c'),('pic','Tilted-PIC','#c65432')]:
            points=' '.join(f'{45+r["gap"]*17},{255-r[key]*10}' for r in f['curve'])
            svg+=f'<polyline points="{points}" stroke="{color}" fill="none" stroke-width="3"/>'
        svg+='<text x="48" y="278">目標に足りない在庫 Δ（0〜30個）</text><text x="48" y="18">発注量 q（個）</text><text x="50" y="303" fill="#697680">CBS</text><text x="170" y="303" fill="#087f8c">Tilted-CBS</text><text x="340" y="303" fill="#c65432">Tilted-PIC</text></svg>'
        svg+=f'<p>基準の発注上限は4個です。上限を引き上げる係数は α={f["alpha"]}、Tilted-PICで不足に掛ける係数は Kp={f["kp"]} です。目標在庫に対して、手元と入荷予定を合わせても足りない量を横軸に取り、整数の不足量で計算した点を線で結びました。</p>'
        svg+=table(['不足量（個）','CBS','Tilted-CBS','Tilted-PIC'],[[r['gap'],r['cbs'],r['tilted'],r['pic']] for r in f['curve'] if r['gap'] in (0,5,10,20,30)])
        frames.append(svg)
    options=''.join(f'<option value="{i}">{escape(f["label"])}</option>' for i,f in enumerate(result['frames']))
    data=json.dumps(frames,ensure_ascii=False).replace('</','<\\/')
    html='<figure class="teaching" data-b21><h3>不足量に応じた3方式の発注量</h3><label>上限の係数 α と不足に掛ける係数 Kp <select>'+options+'</select></label><script type="application/json" data-frames>'+data+'</script><div data-output aria-live="polite">'+frames[0]+'</div><figcaption>原論文の§5.3.2の式をrun.pyで計算しました。方策の費用や優劣を表す図ではありません。</figcaption></figure>'
    html+='<figure class="teaching"><h3>人工需要での費用と採用条件</h3>'
    html+=table(['方策','1日あたりの平均費用','CBSに対する平均改善量','改善量の信頼下限（LCB）','改善量の信頼上限（UCB）'],[[r['policy']]+[round(r[k],3) for k in ('cost','gain','lcb','ucb')] for r in result['replay']])
    html+='<p>256経路の計算で、改善量の上限を B=114、失敗確率を δ=0.05、比較数を N=2 としました。信頼区間の半幅は21.093です。平均費用は両候補で下がりましたが、参照CBSに対する信頼下限が ξ=0 を下回るため、どちらにも切り替えません。</p><figcaption>配備では、固定の参照方策に対する信頼下限が条件を満たした候補から、同じ参照方策に対する信頼上限で選びます。この例では、探索中の最良方策を入れ替える処理、少ないデータ向けのt分布による計算、需要分布の差の推定は実行していません。</figcaption></figure>'
    return html
