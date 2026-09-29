"""Network-specific September 30 visualization; values from source artifacts."""
import json
from html import escape
from paper_lab.batch29 import plot_series


def network():
    nodes=[('SF',50,45),('StLouis',50,120),('Orlando',50,195),('Nashville',175,120),('Atlanta',290,120),('Chicago',405,45),('Charlotte',405,120),('Memphis',405,220),('Columbus',530,45),('Richmond',530,135),('Philadelphia',670,45),('Baltimore',670,180),('NewYork',800,110)]
    edges=[(0,3),(1,3),(2,3),(3,4),(4,5),(4,6),(4,7),(5,8),(6,9),(8,10),(9,10),(9,11),(8,11),(7,11),(10,12),(11,12)]
    svg='<svg style="width:100%;height:auto" viewBox="0 0 870 260" role="img" aria-label="3供給元から9倉庫を経てNewYorkへ至る13拠点16辺"><defs><marker id="iso-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#678"/></marker></defs>'
    for a,b in edges:
        _,x,y=nodes[a];_,xx,yy=nodes[b]
        svg+=f'<path d="M{x+12} {y} L{xx-14} {yy}" stroke="#678" stroke-width="2" marker-end="url(#iso-arrow)"/>'
    for name,x,y in nodes:
        svg+=f'<circle cx="{x}" cy="{y}" r="10" fill="#126b73"/><text x="{x}" y="{y+27}" font-size="13" text-anchor="middle" fill="currentColor">{name}</text>'
    return '<figure class="teaching"><h3>13拠点・16辺で荷物を運ぶ</h3>'+svg+'</svg><figcaption>Figure 1・Table 11を再構成。地理座標は使わず接続だけを示す。SFはSan Francisco、StLouisはSt. Louis。矢印は輸送方向。</figcaption></figure>'


def widget(result):
    if not isinstance(result,dict) or result.get('lab30')!='isomorph':return ''
    frames=[]
    for f in result['frames']:
        r=f['rows']
        content=plot_series([('需要',[x['demand'] for x in r]),('滞留',[x['backlog'] for x in r])],220,'1 → 84日','需要と滞留（個）')
        content+=plot_series([('当日需要充足率',[x['fill'] for x in r]),('辺使用率',[x['utilization'] for x in r])],1,'1 → 84日','比率（0–1）')
        content+=f'<p>期末滞留 {f["ending_backlog"]}個。当日需要充足率 {f["current_demand_fill"]:.3f}。保存則の誤差 {f["conservation_max_error"]}。</p>'
        frames.append(content)
    options=''.join(f'<option value="{i}">{escape(f["label"])}</option>' for i,f in enumerate(result['frames']))
    payload=json.dumps(frames,ensure_ascii=False).replace('</','<\\/')
    return network()+'<figure class="teaching" data-b21><h3>同じ需要のもとで輸送容量を動かす</h3><label>1日あたり容量 <select>'+options+'</select></label><script type="application/json" data-frames>'+payload+'</script><div data-output aria-live="polite">'+frames[0]+'</div><figcaption>run.pyの1辺の教材実験。公式13拠点モデルの出力ではない。容量以外の設定と需要は共通。</figcaption></figure>'
