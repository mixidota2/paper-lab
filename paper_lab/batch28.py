"""Render paper-specific teaching widgets directly from reproducible results."""
import json
from html import escape


def table(headers, rows):
    return '<div class="matrix-scroll" tabindex="0" role="region" aria-label="人工実験の比較"><table><thead><tr>'+''.join('<th>'+escape(str(x))+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+escape(str(x))+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'


def number(x):
    return f'{x:.3f}'.rstrip('0').rstrip('.')


def widget(result):
    if not isinstance(result,dict) or 'lab28' not in result: return ''
    kind=result['lab28']; frames=[]
    for f in result['frames']:
        if kind=='reasoncast':
            content='<div class="b21-tokens"><span>Chronos-2の出力を模した固定予測</span><span>→ '+f['route']+'</span><span>→ 補正後</span></div>'
            content+=table(['日','実績','基準予測','補正後'],[[i+1,f['actual'][i],f['base'][i],number(f['prediction'][i])] for i in range(3)])
            content+=f'<p>実績合計に対する絶対誤差の割合（WMAPE）：基準 {number(f["baseline_wmape"])}% → 補正後 {number(f["proposed_wmape"])}%</p>'
        elif kind=='scope':
            content=table(['商品','周期（日）','配送する数量','1配送の台数','1日当たりの評価値'],[[p['item'],p['cycle'],p['load'],p['vehicles'],p['utility']] for p in f['plans']])
            b,p=f['baseline'],f['proposed']
            content+=f'<p>需要の大きい順に選ぶ：{b["item"]}・{b["cycle"]}日・評価値{b["utility"]}。品揃え・周期・配送費用をまとめて選ぶ：{p["item"]}・{p["cycle"]}日・評価値{p["utility"]}。</p>'
        elif kind=='onetrans':
            content='<ol class="b21-search">'+''.join(f'<li>候補 {c["item"]}：log({c["prefix"]}) + {f["beta"]} × {c["offset"]} + log({c["conditional"]}) = <strong>{number(c["score"])}</strong></li>' for c in f['ranking'])+'</ol>'
            content+='<p>上ほど得点が高い。log(prefix)は目的の確率の自然対数、offsetは業務上の加点、log(conditional)は目的を選んだ後の商品確率の自然対数。βだけを動かし、学習済み確率を模した値は固定する。</p>'
        elif kind=='evaluation':
            content='<div class="b21-cards">'+''.join('<div>買い手 '+', '.join(str(i+1) for i in g)+'<br>予測A−実績の合計 <strong>'+str(sum(result['predictions']['A'][i]-result['actual'][i] for i in g))+'</strong></div>' for g in f['groups'])+'</div>'
            content+=table(['予測','WAPE（%）'],[[k,number(v)] for k,v in f['scores'].items()])+f'<p>この条件でWAPEが最小の予測：{f["winner"]}。同じ予測を異なる組にまとめた結果。</p>'
        elif kind=='harness':
            content='<div class="b21-serving"><section><h4>実行前の点検</h4><p>提案：'+escape(f['proposal'])+'</p><strong>'+f['decision']+'</strong></section><section><h4>学習対象モデルへ渡し、学習用履歴へ残す応答</h4><p>'+escape(f['executed'])+'</p><p>点検役だけが参照する履歴は含めない。</p></section></div>'
        else: raise ValueError(kind)
        frames.append(content)
    titles={'reasoncast':'保存済みの3日例：補正なしと誤情報による補正','scope':'配送数量と周期から配送費用の段差を読む','onetrans':'生成の先頭に置く目的の記号を、業務上の加点で選ぶ','evaluation':'同じ予測の誤差を、どこで相殺するか','harness':'点検役を通った応答だけを履歴へ残す'}
    options=''.join(f'<option value="{i}">{escape(f["label"])}</option>' for i,f in enumerate(result['frames']))
    data=json.dumps(frames,ensure_ascii=False).replace('</','<\\/')
    return '<figure class="teaching" data-b21><h3>'+titles[kind]+'</h3><label>人工例の条件 <select>'+options+'</select></label><script type="application/json" data-frames>'+data+'</script><div data-output aria-live="polite">'+frames[0]+'</div><figcaption>run.pyが計算したresults.jsonから生成。著者の測定値ではない。</figcaption></figure>'
