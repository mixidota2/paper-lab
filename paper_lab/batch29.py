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
    return out + f'<p>縦軸：{escape(ylabel)}。横軸：{escape(xlabel)}。</p>'


def widget(result):
    if not isinstance(result,dict) or 'lab29' not in result:return ''
    kind=result['lab29'];frames=[]
    for f in result['frames']:
        if kind=='sabre':
            content=table(
                ['期','入荷数','需要数','販売数','期末の在庫数','売り逃した数'],
                [[i+1,r['arrival'],r['demand'],r['sales'],r['ending'],r['lost']] for i,r in enumerate(f['rows'])])
            content+=(
                f'<p>2期を終え、次に備える目標を3個とします。需要を全量引く計算では<strong>{f["textbook"]}個</strong>、'
                f'販売数だけを引く計算では<strong>{f["projected"]}個</strong>の不足です。不足の差は、途中で売り逃した<strong>{f["lost"]}個</strong>と一致します。</p>'
                f'<p>不足が負なら、在庫が目標を上回っています。不足を0で下限にすると、発注量は順に{f["textbook_order"]}個と{f["projected_order"]}個です。'
                '発注量の差は売り逃した数と一致するとは限りません。次の期はシミュレーションしていません。</p>')
            content+=plot_series(
                [('上限なし',[x['base'] for x in result['cap_curve']]),('1回の上限は4個',[x['capped'] for x in result['cap_curve']])],
                12,'手元と輸送中の在庫の合計（0〜16個）','発注量（個）')
            content+=(
                '<p>入荷を反映する前の手元と輸送中の在庫を足した値を、在庫ポジション（IP）と呼びます。'
                'この図では二つの在庫を別々に動かさず、その合計だけを変えます。'
                '<a href="https://arxiv.org/html/2609.19760v2">原論文の§2.1・§3.5式(4)</a>で、'
                '需要予測r=4にθ=3を掛けると目標は12個です。発注量は不足分で、c=1なら1回の上限は4個です。</p>')
        elif kind=='or':
            content='<div class="b21-serving"><section><h4>共同発注をするか（Y）</h4><p>発注しない場合の費用は '+number(f['closed_cost'])+'、発注する場合の費用は '+number(f['open_cost'])+'</p><p>発注する確率を0.4とした場合、確率を決める値（logit）に対する費用の傾きは <strong>'+number(f['score_gradient'])+'</strong></p></section><section><h4>共同発注する場合の数量（Q）</h4><p>期末在庫：1期目 '+number(f['levels'][0])+'、2期目 '+number(f['levels'][1])+'</p><p>数量Qを変えたときの費用の傾きは <strong>'+number(f['pathwise'])+'</strong>、数量を前後にずらして計算した傾きは '+number(f['finite_difference'])+'</p></section></div>'
            content+='<p>期末在庫が負なら、需要のうち満たせなかった分を翌期に持ち越します。費用の傾きが負なら、発注量を少し増やすと費用は下がります。共同発注したときだけ、固定費3がかかります。</p>'
            p=result['permutation']
            content+=table(['商品を表す入力','最初の順で得た表現','逆順で得た表現'],[[p['input'][i],number(p['item_outputs'][i]),number(p['item_outputs'][2-i])] for i in range(3)])
            content+='<p>商品の入力を逆順にすると、商品別の出力も逆順に並びます。6通りの並べ替えで、順を対応させた出力の最大差は '+str(p['max_error'])+' でした。この値は学習していない自己注意が出す商品表現です。モデルが学習した発注量ではありません。</p>'
        else:
            content=plot_series([('hurdle',f['probabilities']),('通常の負の二項分布（NB）',f['nb_probabilities'])],1,'需要量：0 → 20','各需要量の確率（線は点を結ぶ補助）')
            content+=table(['量','hurdle','通常の負の二項分布（NB）'],[['ゼロ確率',number(f['zero_hurdle']),number(f['zero_nb'])],['平均',number(f['mean']),f['mu']]])
            content+='<p>正の需要の条件付き平均 <strong>'+number(f['positive_mean'])+'</strong>。ゼロと正の需要を分けた分布（hurdle）で21個以上となる確率 '+f'{f["tail"]:.6f}'+'。0〜999の確率を合計した値 '+number(f['mass'])+'。</p>'
        frames.append(content)
    titles={'sabre':'欠品があったときの不足と発注量','or':'発注するかと、発注量を変える場合の費用を比べる','hurdle':'ゼロの山と、正の需要の分布を分けて動かす'}
    labels={'sabre':'初期在庫（個）','or':'比較する数量Q（在庫がゼロになる境目を除く）','hurdle':'発生確率と、ゼロを除く前のNB平均μ'}
    options=''.join(f'<option value="{i}">{escape(f["label"])}</option>' for i,f in enumerate(result['frames']))
    data=json.dumps(frames,ensure_ascii=False).replace('</','<\\/')
    caption=(
        'run.pyで計算した人工例です。著者の報告値ではありません。操作する前から、最初の初期在庫の結果を表示します。'
        if kind=='sabre' else
        'Labが1商品・2期を設定して計算した例です。著者らが報告した性能ではありません。数量を選ぶ前から、最初の結果を表示します。'
        if kind=='or' else
        'run.pyの人工実験をresults.jsonから生成。著者の性能値ではない。操作しなくても最初の条件を読める。')
    return '<figure class="teaching" data-b21><h3>'+titles[kind]+'</h3><label>'+labels[kind]+' <select>'+options+'</select></label><script type="application/json" data-frames>'+data+'</script><div data-output aria-live="polite">'+frames[0]+'</div><figcaption>'+caption+'</figcaption></figure>'
