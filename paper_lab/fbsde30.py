"""1商品の発注率の計算と、論文が報告した指標を分けて描く。"""
import json
from html import escape


def widget(result):
    if not isinstance(result, dict) or not result.get('lab30_fbsde'):
        return ''
    frames=[]
    for f in result['frames']:
        upper=max(0,min(f['transit_upper'],f['onhand_upper']))
        width=upper*100
        svg=f'''<svg viewBox="0 0 540 210" role="img" aria-label="緑は二つの上限を守る非負の発注率の範囲、赤は調整前の発注率4です。" style="width:100%;height:auto">
<text x="20" y="24">発注で輸送中の在庫Lが増え、入荷が手元の在庫Xに届く</text>
<text x="20" y="53">発注率uが式に現れるのは、Lは1回、Xは2回の微分後</text>
<path d="M45 120H485" stroke="currentColor"/><rect x="45" y="98" width="{width}" height="22" fill="#137d79"/>
<path d="M445 85V140" stroke="#bf4938" stroke-width="3"/>
<text x="40" y="160">0</text><text x="420" y="160">調整前：4</text>
<text x="45" y="194">緑：輸送中と手元の二つの上限を満たす発注率</text></svg>'''
        if not f['feasible']:
            status='上限を緩めないと、二つの上限を守る非負の発注率はありません。'
        elif not f['augmented_initial_safe']:
            status=f'この時点の二次計画は発注率 {f["order"]:g} を選びます。ただし h₁ は負なので、定理の初期条件は満たしません。その後に必ず容量を超えるという意味ではありません。'
        else:
            status=f'この時点の二次計画は発注率 {f["order"]:g} を選びます。手元の空き h と、その変化を加えた h₁ はともに0以上です。'
        frames.append(svg+f'<p><strong>{status}</strong></p><p>今の空きは h={f["h"]:g}、空きの変化も含めると h₁={f["h1"]:g} です。輸送中在庫から決まる発注率の上限は {f["transit_upper"]:g}、手元在庫から決まる上限は {f["onhand_upper"]:g} です。</p>')
    options=''.join(f'<option value="{i}">{escape(f["label"])}</option>' for i,f in enumerate(result['frames']))
    # 最初は手元側の上限まで発注する条件を表示する。
    options=options.replace('value="2"','value="2" selected')
    data=json.dumps(frames,ensure_ascii=False).replace('</','<\\/')
    bars=''
    vals=[('充足率',.562),('手元容量の違反率',.815),('M1：容量比の平均超過',.050),('M3：10%超の超過割合',.083)]
    for i,(label,val) in enumerate(vals):
        y=36+i*53
        bars+=f'<text x="12" y="{y}">{label}</text><rect x="240" y="{y-17}" width="{val*250}" height="22" fill="{("#bf4938" if i==1 else "#137d79")}"/><text x="{245+val*250}" y="{y}">{val:.3f}</text>'
    evidence=f'<figure class="teaching"><h3>50商品で著者が測った充足率と容量超過</h3><svg viewBox="0 0 560 230" role="img" aria-label="著者報告。充足率は0.562、手元容量の違反率は0.815、M1は0.050、M3は0.083です。" style="width:100%;height:auto">{bars}</svg><figcaption>表II・IIIの著者報告です。充足率の分母は需要数量、違反率とM3の分母は需要経路と週の組です。M1は超過しなかった組の0を含めて平均した容量比です。棒はすべて0〜1の尺度ですが、異なる指標です。Labでの再現値ではありません。</figcaption></figure>'
    return '<figure class="teaching" data-b21><h3>手元容量ごとに選べる発注率</h3><p>h₁ = d − L/τ + γ(Hˣ − X) です。手元在庫X=7、輸送中在庫L=4、τ=2、販売率d=1、γ=0.5を固定します。</p><label>手元容量 <select>'+options+'</select></label><script type="application/json" data-frames>'+data+'</script><div data-output aria-live="polite">'+frames[2]+'</div><figcaption>原論文の式(9)・(15)・(20)を、雑音がなく入荷率が輸送中在庫に比例する1商品の例で計算しました。容量だけ変えても、その瞬間に手元や輸送中の在庫は変わりません。値はrun.pyで計算しました。</figcaption></figure>'+evidence
