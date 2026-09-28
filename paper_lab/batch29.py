"""September 29: distinct inventory, gradient, and probability teaching figures."""
import json
from html import escape
from paper_lab.batch28 import table, number


def plot_series(series, ymax, xlabel, ylabel):
    """Accessible SVG with fixed viewBox; supporting numbers appear in nearby text."""
    colors=['#126b73','#c85b36']
    out=f'<svg viewBox="0 0 600 250" role="img" aria-label="{escape(ylabel)}" style="width:100%;height:auto"><path d="M50 20V210H580" fill="none" stroke="currentColor"/><text x="5" y="22">{number(ymax)}</text><text x="25" y="210">0</text>'
    for j,(label,values) in enumerate(series):
        points=' '.join(f'{50+i*520/(len(values)-1):.2f},{210-v*170/ymax:.2f}' for i,v in enumerate(values))
        out+=f'<polyline points="{points}" fill="none" stroke="{colors[j]}" stroke-width="3"/><text x="{60+j*230}" y="242" fill="{colors[j]}">{escape(label)}</text>'
    out+=f'<text x="330" y="225">{escape(xlabel)}</text></svg>'
    return out


def widget(result):
    if not isinstance(result,dict) or 'lab29' not in result:return ''
    kind=result['lab29'];frames=[]
    for f in result['frames']:
        if kind=='sabre':
            content=table(['期','入荷','需要','販売','期末在庫','逸失'],[[i+1,r['arrival'],r['demand'],r['sales'],r['ending'],r['lost']] for i,r in enumerate(f['rows'])])
            content+=f'<p>次の需要3に対する不足：通常のIP計算 <strong>{f["textbook"]}</strong>、販売量で進めた計算 <strong>{f["projected"]}</strong>。差は途中の逸失販売 <strong>{f["lost"]}</strong>。</p>'
            content+=f'<p>不足を0で下限処理した発注量：{f["textbook_order"]} 対 {f["projected_order"]}。負の不足は余剰を意味する。</p>'
            content+=plot_series([('上限なし',[x['base'] for x in result['cap_curve']]),('c=1で上限4',[x['capped'] for x in result['cap_curve']])],12,'IP：0 → 16','発注量：r=4、θ=3')
            content+='<p>曲線はr=4、θ=3を固定した式(4)。c=1ならIPが低くても発注量は4を超えない。</p>'
        elif kind=='or':
            content='<div class="b21-serving"><section><h4>離散：注文を開くY</h4><p>閉じる費用 '+number(f['closed_cost'])+' → 開く費用 '+number(f['open_cost'])+'</p><p>p=0.4でlogit方向のscore勾配 <strong>'+number(f['score_gradient'])+'</strong></p></section><section><h4>連続：数量Q</h4><p>期末在庫 '+number(f['levels'][0])+' → '+number(f['levels'][1])+'</p><p>pathwise <strong>'+number(f['pathwise'])+'</strong> / 中央差分 '+number(f['finite_difference'])+'</p></section></div>'
            content+='<p>負の期末在庫はbacklog。勾配が負なら数量を増やす方向で費用が下がる。固定費K=3は注文を開いたときだけ課金。</p>'
            p=result['permutation']
            content+=table(['商品入力','元の数量表現','逆順後の数量表現'],[[p['input'][i],number(p['item_outputs'][i]),number(p['item_outputs'][2-i])] for i in range(3)])
            content+='<p>商品を逆順にすると出力も逆順。6通りの並べ替えで最大誤差 '+str(p['max_error'])+'。ここでの値は未学習のattention表現で、発注量そのものではない。</p>'
        else:
            content=plot_series([('hurdle',f['probabilities']),('通常のNB',f['nb_probabilities'])],1,'需要量：0 → 20','各需要量の確率（線は点を結ぶ補助）')
            content+=table(['量','hurdle','通常のNB'],[['ゼロ確率',number(f['zero_hurdle']),number(f['zero_nb'])],['平均',number(f['mean']),f['mu']]])
            content+='<p>正の需要の条件付き平均 <strong>'+number(f['positive_mean'])+'</strong>。hurdleの21以上の尾確率 '+f'{f["tail"]:.6f}'+'。数値和0–999の全確率 '+number(f['mass'])+'。</p>'
        frames.append(content)
    titles={'sabre':'欠品を含む経路と、発注上限の曲線','or':'同じ費用をYとQの二つの経路で微分する','hurdle':'ゼロの山と、正の需要の分布を分けて動かす'}
    labels={'sabre':'初期在庫','or':'数量Q（屈曲点を除く）','hurdle':'発生確率とNB平均'}
    options=''.join(f'<option value="{i}">{escape(f["label"])}</option>' for i,f in enumerate(result['frames']))
    data=json.dumps(frames,ensure_ascii=False).replace('</','<\\/')
    return '<figure class="teaching" data-b21><h3>'+titles[kind]+'</h3><label>'+labels[kind]+' <select>'+options+'</select></label><script type="application/json" data-frames>'+data+'</script><div data-output aria-live="polite">'+frames[0]+'</div><figcaption>run.pyの人工実験をresults.jsonから生成。著者の性能値ではない。操作しなくても最初の条件を読める。</figcaption></figure>'
