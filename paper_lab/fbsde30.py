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
        svg=f'''<svg viewBox="0 0 540 210" role="img" aria-label="発注率の実行可能区間。0から上限までが緑、名目発注は4。" style="width:100%;height:auto">
<text x="20" y="24">発注 u → 輸送中 L → 手元 X</text>
<text x="20" y="53">L：1階微分にu　／　X：2階微分にu</text>
<path d="M45 120H485" stroke="currentColor"/><rect x="45" y="98" width="{width}" height="22" fill="#137d79"/>
<path d="M445 85V140" stroke="#bf4938" stroke-width="3"/>
<text x="40" y="160">0</text><text x="420" y="160">名目4</text>
<text x="45" y="194">緑：両制約を満たす非負発注の範囲</text></svg>'''
        if not f['feasible']:
            status='共通領域なし。緩和なしではQPが実行不能。'
        elif not f['augmented_initial_safe']:
            status=f'局所QP解 {f["order"]:g}。ただしh₁&lt;0で、定理の初期条件を満たさない。'
        else:
            status=f'QP解 {f["order"]:g}。hとh₁はともに非負。'
        frames.append(svg+f'<p><strong>{status}</strong></p><p>現在の余裕 h = {f["h"]:g}、入荷を考慮した h₁ = {f["h1"]:g}。輸送中の上限 {f["transit_upper"]:g}、手元の上限 {f["onhand_upper"]:g}。</p>')
    options=''.join(f'<option value="{i}">{escape(f["label"])}</option>' for i,f in enumerate(result['frames']))
    # Default to the feasible, binding constraint case.
    options=options.replace('value="2"','value="2" selected')
    data=json.dumps(frames,ensure_ascii=False).replace('</','<\\/')
    bars=''
    vals=[('充足率',.562),('容量違反率',.815),('M1：平均相対超過',.050),('M3：10%超過の確率',.083)]
    for i,(label,val) in enumerate(vals):
        y=36+i*53
        bars+=f'<text x="12" y="{y}">{label}</text><rect x="240" y="{y-17}" width="{val*250}" height="22" fill="{("#bf4938" if i==1 else "#137d79")}"/><text x="{245+val*250}" y="{y}">{val:.3f}</text>'
    evidence=f'<figure class="teaching"><h3>著者の50商品実験：頻度と超過量を分ける</h3><svg viewBox="0 0 560 230" role="img" aria-label="充足率0.562、容量違反率0.815、M1 0.050、M3 0.083" style="width:100%;height:auto">{bars}</svg><figcaption>表II–III、8 seedの著者報告。すべて0–1の軸だが、指標の定義は異なる。論文の再現結果ではない。</figcaption></figure>'
    return '<figure class="teaching" data-b21><h3>容量を変え、到着待ち在庫が削る発注余地を見る</h3><p>h₁ = d − L/τ + γ(Hˣ − X)。X=7、L=4、τ=2、d=1、γ=0.5を固定。</p><label>手元容量 <select>'+options+'</select></label><script type="application/json" data-frames>'+data+'</script><div data-output aria-live="polite">'+frames[2]+'</div><figcaption>式9・15・20の決定論的な線形縮約。容量を瞬時に下げても、在庫や到着待ちは消えない。run.py → results.jsonから生成。</figcaption></figure>'+evidence
