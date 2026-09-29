"""RetailBench: coupled store and selected-run diagnostics, from source artifacts."""
import json
from html import escape
from paper_lab.batch28 import table


def widget(result):
    if not isinstance(result, dict) or not result.get('lab30_retailbench'):
        return ''
    # The SVG is a conceptual redrawing of Figure 1, not a measured flow chart.
    svg = '<svg viewBox="0 0 620 350" role="img" aria-label="店舗モジュールの結合図" style="width:100%;height:auto"><title>Figure 1の7モジュールを再配置</title><g stroke="#788b95" stroke-width="2"><path d="M120 70L310 70L500 70L500 175L310 280L120 175L120 70M310 70V280M120 175H500M120 70L500 175M500 70L120 175" fill="none"/></g>'
    nodes=[(120,70,'仕入先・発注'),(310,70,'在庫・経年'),(500,70,'棚'),(120,175,'ニュース'),(310,175,'需要・販売'),(500,175,'評価・返品'),(310,280,'資金・記録')]
    for x,y,t in nodes:
        svg+=f'<rect x="{x-78}" y="{y-24}" width="156" height="48" rx="12" fill="#e6f3ee" stroke="#357c6d"/><text x="{x}" y="{y+5}" text-anchor="middle" fill="#153e36" font-size="17">{t}</text>'
    svg+='</svg>'
    out='<figure class="teaching"><h3>1日の終了処理が7つの業務を結ぶ</h3>'+svg+'<figcaption>原論文Figure 1・§2.3の概念再配置。線は業務の結合を示す。入荷・販売・返品・経年・資金を日々更新する。</figcaption></figure>'
    frames=[]
    for row in result['reported']:
        model,framework,days,worth,sales=row
        frames.append(table(['モデル / 枠組み','生存日数','最終純資産','販売数量（個）'],[[model+' / '+framework,days,f'{worth:,.2f}',f'{sales:,}']])+f'<p>180日のうち <strong>{days}</strong> 日。純資産はOracleの {worth/131510.42*100:.1f}%、販売数量は {sales/267998*100:.1f}%。</p>')
    out+=panel('選択された実行をモデルごとに読む','モデル',[r[0] for r in result['reported']],frames,'著者報告 Table 1。生存日数を優先して選んだ実行。Oracleは特権情報を使う。')
    frames=[]
    for f in result['frames']:
        rows=[[p['supplier'],f'{p["final_cash"]:,.0f}'] for p in f['policies']]
        frames.append(table(['人工方策','30日後の現金'],rows)+'<p>現金 = 3,000 + 30 ×（対象商品数 × 10 × 単位粗利 − 600）。単位粗利はPriceFirstが3、QualityFirstが4.5。対象を広げる効果は、この固定需要の仮定に依存する。</p>')
    out+=panel('対象商品数と仕入先の品質を同じ収支で見る','1日の対象商品数',[str(f['products']) for f in result['frames']],frames,'run.pyの人工実験。返品率・原価は説明用の仮定。負の現金でも計算を続けるため生存評価ではない。')
    return out


def panel(title,label,options,frames,caption):
    opts=''.join(f'<option value="{i}">{escape(v)}</option>' for i,v in enumerate(options))
    data=json.dumps(frames,ensure_ascii=False).replace('</','<\\/')
    return f'<figure class="teaching" data-b21><h3>{title}</h3><label>{label} <select>{opts}</select></label><script type="application/json" data-frames>{data}</script><div data-output aria-live="polite">{frames[0]}</div><figcaption>{caption}</figcaption></figure>'
