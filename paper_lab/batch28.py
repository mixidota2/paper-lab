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
            content=table(['商品','補充の間隔（日）','1回に運ぶ荷量','1回に使う車両の台数','1日あたりの評価値'],
                          [[p['item'],p['cycle'],p['load'],p['vehicles'],p['utility']] for p in f['plans']])
            b,p=f['baseline'],f['proposed']
            content+=(
                f'<p>需要が多い商品を先に選ぶと、商品{b["item"]}を{b["cycle"]}日おきに配送します。1日あたりの評価値は{b["utility"]}です。'
                f'商品と間隔を全候補から選ぶと、商品{p["item"]}を{p["cycle"]}日おきに配送し、評価値は{p["utility"]}です。</p>')
        elif kind=='onetrans':
            content='<ol class="b21-search">'+''.join(f'<li>候補 {c["item"]}：log({c["prefix"]}) + {f["beta"]} × {c["offset"]} + log({c["conditional"]}) = <strong>{number(c["score"])}</strong></li>' for c in f['ranking'])+'</ol>'
            content+='<p>上ほど得点が高い。log(prefix)は目的の確率の自然対数、offsetは業務上の加点、log(conditional)は目的を選んだ後の商品確率の自然対数。βだけを動かし、学習済み確率を模した値は固定する。</p>'
        elif kind=='evaluation':
            content='<div class="b21-cards">'+''.join('<div>買い手 '+', '.join(str(i+1) for i in g)+'<br>組内のAの予測値から実績を引いた合計： <strong>'+str(sum(result['predictions']['A'][i]-result['actual'][i] for i in g))+'</strong></div>' for g in f['groups'])+'</div>'
            content+=table(['予測','組ごとの絶対誤差を足して実績総額で割った値（WAPE、%）'],[[k,number(v)] for k,v in f['scores'].items()])+f'<p>この組分けでは、予測{f["winner"]}の方がWAPEは小さいです。買い手各社の実績と予測値は変わりません。</p>'
        elif kind=='harness':
            content='<div class="b21-serving"><section><h4>実行前の点検</h4><p>提案：'+escape(f['proposal'])+'</p><strong>'+f['decision']+'</strong></section><section><h4>学習対象モデルへ渡し、学習用履歴へ残す応答</h4><p>'+escape(f['executed'])+'</p><p>点検役だけが参照する履歴は含めない。</p></section></div>'
        else: raise ValueError(kind)
        frames.append(content)
    titles={'reasoncast':'保存済みの3日例：補正なしと誤情報による補正','scope':'配車費ごとの品揃えと補充間隔','onetrans':'生成の先頭に置く目的の記号を、業務上の加点で選ぶ','evaluation':'組分けによるWAPEの違い','harness':'点検役を通った応答だけを履歴へ残す'}
    options=''.join(f'<option value="{i}">{escape(f["label"])}</option>' for i,f in enumerate(result['frames']))
    data=json.dumps(frames,ensure_ascii=False).replace('</','<\\/')
    label='1回の配送で車両1台にかかる費用' if kind=='scope' else '買い手の組分け' if kind=='evaluation' else '人工例の条件'
    caption=(
        '1拠点へ1商品を配送する人工例です。配車に使う台数を計算し、実際の配送経路は求めません。'
        '全候補の中に需要が多い商品を先に選ぶ方式の候補が含まれるため、前者の評価値は後者を下回りません。'
        'SCOPEの学習や、現場での結果を示す図ではありません。'
        if kind=='scope' else
        '4社の実績と予測を固定した人工例です。組の中で予測の過不足が打ち消し合うかを比べます。論文の測定値ではありません。'
        if kind=='evaluation' else 'run.pyが計算したresults.jsonから生成。著者の測定値ではない。')
    return '<figure class="teaching" data-b21><h3>'+titles[kind]+'</h3><label>'+label+' <select>'+options+'</select></label><script type="application/json" data-frames>'+data+'</script><div data-output aria-live="polite">'+frames[0]+'</div><figcaption>'+caption+'</figcaption></figure>'
