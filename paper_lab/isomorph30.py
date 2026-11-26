"""ISOMORPHの論文の物流網と、Labの人工例を描きます。"""
import json
from html import escape
from paper_lab.batch29 import plot_series


def network():
    nodes=[('SF',50,45),('StLouis',50,120),('Orlando',50,195),('Nashville',175,120),('Atlanta',290,120),('Chicago',405,45),('Charlotte',405,120),('Memphis',405,220),('Columbus',530,45),('Richmond',530,135),('Philadelphia',670,45),('Baltimore',670,180),('NewYork',800,110)]
    edges=[(0,3),(1,3),(2,3),(3,4),(4,5),(4,6),(4,7),(5,8),(6,9),(8,10),(9,10),(9,11),(8,11),(7,11),(10,12),(11,12)]
    svg='<svg style="width:100%;height:auto" viewBox="0 0 870 260" role="img" aria-label="13拠点と16本の輸送路。3供給元、9中間倉庫、ニューヨークの到着先"><defs><marker id="iso-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#678"/></marker></defs>'
    for a,b in edges:
        _,x,y=nodes[a];_,xx,yy=nodes[b]
        svg+=f'<path d="M{x+12} {y} L{xx-14} {yy}" stroke="#678" stroke-width="2" marker-end="url(#iso-arrow)"/>'
    for name,x,y in nodes:
        svg+=f'<circle cx="{x}" cy="{y}" r="10" fill="#126b73"/><text x="{x}" y="{y+27}" font-size="13" text-anchor="middle" fill="currentColor">{name}</text>'
    return '<figure class="teaching"><h3>論文が設定した13拠点と16本の輸送路</h3>'+svg+'</svg><figcaption>図1と表11をもとに、どの拠点がつながるかを示しました。拠点の位置は地理座標ではありません。SFはサンフランシスコ、StLouisはセントルイスです。矢印は荷物を送る方向を示します。</figcaption></figure>'


def widget(result):
    if not isinstance(result,dict) or result.get('lab30')!='isomorph':return ''
    frames=[]
    for f in result['frames']:
        r=f['rows']
        content=plot_series([('新規需要',[x['demand'] for x in r]),('翌日へ持ち越す注文',[x['backlog'] for x in r])],220,'経過日数（1〜84日）','新規需要と翌日へ持ち越す注文の数量（個）')
        content+=plot_series([('当日需要充足率',[x['fill'] for x in r]),('その日の出荷が容量に占める割合',[x['utilization'] for x in r])],1,'経過日数（1〜84日）','比率（0–1）')
        content+=f'<p>84日目に残る注文は {f["ending_backlog"]}個です。当日需要充足率は {f["current_demand_fill"]:.3f}、数量の保存則の最大誤差は {f["conservation_max_error"]}です。</p>'
        frames.append(content)
    options=''.join(f'<option value="{i}">{escape(f["label"])}</option>' for i,f in enumerate(result['frames']))
    payload=json.dumps(frames,ensure_ascii=False).replace('</','<\\/')
    return network()+'<figure class="teaching" data-b21><h3>1日の輸送容量と翌日へ持ち越す注文</h3><label>1日の輸送容量 <select>'+options+'</select></label><script type="application/json" data-frames>'+payload+'</script><div data-output aria-live="polite">'+frames[0]+'</div><figcaption>Labは1本の輸送路だけを使います。容量を切り替えても需要と他の設定は変わりません。上の13拠点を計算した結果ではありません。</figcaption></figure>'
