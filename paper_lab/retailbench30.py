"""RetailBench: coupled store and selected-run diagnostics, from source artifacts."""
import json
from html import escape
from paper_lab.batch28 import table


def widget(result):
    if not isinstance(result, dict) or not result.get('lab30_retailbench'):
        return ''
    # The SVG is a conceptual redrawing of Figure 1, not a measured flow chart.
    svg = '<svg viewBox="0 0 620 350" role="img" aria-label="店舗シミュレーターを構成する7つの機能" style="width:100%;height:auto"><title>論文の図1をもとにした7つの機能</title><g stroke="#788b95" stroke-width="2"><path d="M120 70L310 70L500 70L500 175L310 280L120 175L120 70M310 70V280M120 175H500M120 70L500 175M500 70L120 175" fill="none"/></g>'
    nodes=[(120,70,'仕入先・発注'),(310,70,'在庫・保管期間'),(500,70,'棚'),(120,175,'ニュース'),(310,175,'需要・販売'),(500,175,'評価・返品'),(310,280,'資金・記録')]
    for x,y,t in nodes:
        svg+=f'<rect x="{x-78}" y="{y-24}" width="156" height="48" rx="12" fill="#e6f3ee" stroke="#357c6d"/><text x="{x}" y="{y+5}" text-anchor="middle" fill="#153e36" font-size="17">{t}</text>'
    svg+='</svg>'
    out='<figure class="teaching"><h3>店舗シミュレーターは日ごとに在庫や現金を更新する</h3>'+svg+'<figcaption>論文の図1と2.3節をもとに、店舗業務の関係を示しました。日々の処理で、入荷、販売、返品を反映し、保管日数や現金を更新します。線は業務同士の関係を表し、処理の順序や影響の大きさは表しません。</figcaption></figure>'
    frames=[]
    for row in result['reported']:
        model,framework,days,worth,sales=row
        frames.append(table(['モデル / 枠組み','営業を続けた日数','最終純資産','販売数量（個）'],[[model+' / '+framework,days,f'{worth:,.2f}',f'{sales:,}']])+f'<p>180日の評価期間のうち、<strong>{days}</strong> 日営業を続けました。参照ルール（Oracle Policy）の値と比べると、最終純資産は {worth/131510.42*100:.1f}%、販売数量は {sales/267998*100:.1f}% です。</p>')
    out+=panel('論文の表1：各モデルの代表1回を比べる','モデル',[r[0] for r in result['reported']],frames,'著者はモデルごとに営業日数が最長の1回を選びました。同じ日数なら最終純資産、それも同じなら販売数量で選んでいます。参照ルールは、著者が手で決めた手順で、LLMと同じ条件の比較相手ではありません。')
    frames=[]
    for f in result['frames']:
        rows=[[p['supplier'],f'{p["final_cash"]:,.0f}'] for p in f['policies']]
        frames.append(table(['仕入先の選び方','30日後の現金'],rows)+'<p>毎日、扱う商品は1種類につき10個売れると仮定し、その日の粗利から家賃600を引きます。販売1個あたりの粗利は、原価が低い仕入先（PriceFirst）だと3、返品が少ない仕入先（QualityFirst）だと4.5です。開始時の現金3,000に30日分の収支を足します。商品の種類を増やしたとき現金がどう変わるかは、1種類あたりの販売数が変わらないという仮定に依存します。</p>')
    out+=panel('Labの計算例：扱う商品の種類と仕入先で、30日後の現金はどう変わるか','1日に扱う商品の種類数',[str(f['products']) for f in result['frames']],frames,'配布するrun.pyで計算した例です。返品率と仕入原価はLabが設定しました。現金がマイナスでも30日間の計算を続けるため、店が営業を続けられる日数は測れません。')
    return out


def panel(title,label,options,frames,caption):
    opts=''.join(f'<option value="{i}">{escape(v)}</option>' for i,v in enumerate(options))
    data=json.dumps(frames,ensure_ascii=False).replace('</','<\\/')
    return f'<figure class="teaching" data-b21><h3>{title}</h3><label>{label} <select>{opts}</select></label><script type="application/json" data-frames>{data}</script><div data-output aria-live="polite">{frames[0]}</div><figcaption>{caption}</figcaption></figure>'
