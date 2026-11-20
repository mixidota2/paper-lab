"""Equation-led local safety-set geometry for the September 30 FBSDE Lab."""
import json
from html import escape


def widget(result):
    if not isinstance(result, dict) or not result.get('lab30_fbsde'):
        return ''
    frames=[]
    for f in result['frames']:
        upper=max(0,min(f['transit_upper'],f['onhand_upper']))
        width=upper*100
        svg=f'''<svg viewBox="0 0 540 210" role="img" aria-label="両方の上限を守れる発注率を緑で、調整前の発注率4を赤で示す。緑がなければ選べる発注率はない。" style="width:100%;height:auto">
<text x="20" y="24">発注 u → 輸送中 L → 手元 X</text>
<text x="20" y="53">uが現れるまで：Lは1回、Xは2回微分</text>
<path d="M45 120H485" stroke="currentColor"/><rect x="45" y="98" width="{width}" height="22" fill="#137d79"/>
<path d="M445 85V140" stroke="#bf4938" stroke-width="3"/>
<text x="40" y="160">0</text><text x="420" y="160">調整前の発注率4</text>
<text x="45" y="194">緑：両制約を満たす非負の発注率の範囲</text></svg>'''
        if not f['feasible']:
            status='両方の上限を守る発注率がありません。上限を緩めない二次計画には解がありません。'
        elif not f['augmented_initial_safe']:
            status=f'この時点の発注率は {f["order"]:g}。ただしh₁&lt;0なので、定理の初期条件を満たしません。'
        else:
            status=f'この時点の発注率は {f["order"]:g}。hとh₁はともに0以上です。'
        frames.append(svg+f'<p><strong>{status}</strong></p><p>現在の余裕 h = {f["h"]:g}、入荷を考慮した h₁ = {f["h1"]:g}。輸送中在庫の制約から決まる発注率の上限 {f["transit_upper"]:g}、手元在庫の制約から決まる発注率の上限 {f["onhand_upper"]:g}。</p>')
    options=''.join(f'<option value="{i}">{escape(f["label"])}</option>' for i,f in enumerate(result['frames']))
    # Default to the feasible, binding constraint case.
    options=options.replace('value="2"','value="2" selected')
    data=json.dumps(frames,ensure_ascii=False).replace('</','<\\/')
    bars=''
    vals=[('充足率',.562),('容量違反率',.815),('M1：容量に対する平均超過',.050),('M3：10%より多く超える確率',.083)]
    for i,(label,val) in enumerate(vals):
        y=36+i*53
        bars+=f'<text x="12" y="{y}">{label}</text><rect x="240" y="{y-17}" width="{val*250}" height="22" fill="{("#bf4938" if i==1 else "#137d79")}"/><text x="{245+val*250}" y="{y}">{val:.3f}</text>'
    evidence=f'<figure class="teaching"><h3>著者の50商品実験：頻度と超過量を分ける</h3><svg viewBox="0 0 560 230" role="img" aria-label="充足率0.562、容量違反率0.815、M1 0.050、M3 0.083" style="width:100%;height:auto">{bars}</svg><figcaption>表II–IIIの著者報告です。乱数の初期値を変えた8回の実験に基づきます。棒の軸はすべて0〜1ですが、頻度と超過量は別の指標です。Labでの再現結果ではありません。</figcaption></figure>'
    return '<figure class="teaching" data-b21><h3>手元容量を変えると、発注率の上限はどう変わるか</h3><p>h₁ = d − L/τ + γ(Hˣ − X)。X=7、L=4、τ=2、d=1、γ=0.5を固定。</p><label>手元容量 <select>'+options+'</select></label><script type="application/json" data-frames>'+data+'</script><div data-output aria-live="polite">'+frames[2]+'</div><figcaption>式9・15・20を、雑音なしで入荷率が輸送中在庫に比例する例に絞りました。容量をすぐに下げても、手元と輸送中の在庫はその場では変わりません。run.pyで計算したresults.jsonを表示しています。</figcaption></figure>'+evidence
