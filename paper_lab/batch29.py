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
            content='<div class="b21-serving"><section><h4>離散：共同発注を行うかの判断Y</h4><p>発注しない場合の費用 '+number(f['closed_cost'])+' → 発注する場合の費用 '+number(f['open_cost'])+'</p><p>p=0.4で発注確率を決めるlogit方向の勾配 <strong>'+number(f['score_gradient'])+'</strong></p></section><section><h4>連続：数量Q</h4><p>期末在庫 '+number(f['levels'][0])+' → '+number(f['levels'][1])+'</p><p>数量Qを変えたときの費用の微分 <strong>'+number(f['pathwise'])+'</strong> / 中央差分 '+number(f['finite_difference'])+'</p></section></div>'
            content+='<p>負の期末在庫は未充足分で、翌期へ持ち越す。勾配が負なら数量を増やす方向で費用が下がる。固定費K=3は共同発注するときだけ課金。</p>'
            p=result['permutation']
            content+=table(['商品入力','元の数量表現','逆順後の数量表現'],[[p['input'][i],number(p['item_outputs'][i]),number(p['item_outputs'][2-i])] for i in range(3)])
            content+='<p>商品を逆順にすると出力も逆順。6通りの並べ替えで最大誤差 '+str(p['max_error'])+'。ここでの値は未学習のattention表現で、発注量そのものではない。</p>'
        else:
            content=plot_series([('hurdle',f['probabilities']),('通常の負の二項分布（NB）',f['nb_probabilities'])],1,'需要量：0 → 20','各需要量の確率（線は点を結ぶ補助）')
            content+=table(['量','hurdle','通常の負の二項分布（NB）'],[['ゼロ確率',number(f['zero_hurdle']),number(f['zero_nb'])],['平均',number(f['mean']),f['mu']]])
            content+='<p>正の需要の条件付き平均 <strong>'+number(f['positive_mean'])+'</strong>。ゼロと正の需要を分けた分布（hurdle）で21個以上となる確率 '+f'{f["tail"]:.6f}'+'。0〜999の確率を合計した値 '+number(f['mass'])+'。</p>'
        frames.append(content)
    titles={'sabre':'欠品があったときの不足と発注量','or':'同じ費用をYとQの二つの経路で微分する','hurdle':'ゼロの山と、正の需要の分布を分けて動かす'}
    labels={'sabre':'初期在庫（個）','or':'数量Q（屈曲点を除く）','hurdle':'発生確率と、ゼロを除く前のNB平均μ'}
    options=''.join(f'<option value="{i}">{escape(f["label"])}</option>' for i,f in enumerate(result['frames']))
    data=json.dumps(frames,ensure_ascii=False).replace('</','<\\/')
    caption=(
        'run.pyで計算した人工例です。著者の報告値ではありません。操作する前から、最初の初期在庫の結果を表示します。'
        if kind=='sabre' else
        'run.pyの人工実験をresults.jsonから生成。著者の性能値ではない。操作しなくても最初の条件を読める。')
    return '<figure class="teaching" data-b21><h3>'+titles[kind]+'</h3><label>'+labels[kind]+' <select>'+options+'</select></label><script type="application/json" data-frames>'+data+'</script><div data-output aria-live="polite">'+frames[0]+'</div><figcaption>'+caption+'</figcaption></figure>'
