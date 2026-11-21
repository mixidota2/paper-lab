"""Paper Figure 4 geometry and Table 4 mean cost composition."""
import json
from html import escape


def widget(result):
    if not isinstance(result,dict) or not result.get('lab01_projection'):
        return ''
    frames=[]
    display_names={'Free':'どの上限にも達していない（Free）','Pinned':'製品1が個別上限に達した（Pinned）','Competing':'2製品で共有上限に達した（Competing）'}
    explanations={'Free':'どの制約にも達していないので、目標の変化がそのまま生産量の変化になる。','Pinned':'製品1は上限の3を作る。目標z₁を増やしても実際の量x₁は増えない。','Competing':'2製品で容量6を使い切っている。製品1の目標z₁を上げるとx₁が増え、その分x₂が減る。'}
    for case in result['cases']:
        z=case['target']; x=case['projected']; j=case['jacobian']
        def point(v):return (55+v[0]*52,375-v[1]*52)
        zx,zy=point(z); xx,xy=point(x)
        dx,dy=point([x[0]+j[0][0],x[1]+j[1][0]])
        grid=''.join(f'<circle cx="{point((a,b))[0]}" cy="{point((a,b))[1]}" r="3" fill="#78908b"/>' for a in range(4) for b in range(7-a))
        svg=f'''<svg viewBox="0 0 470 425" role="img" aria-label="{case['label']}。緑の領域が共有容量と個別上限を守る行動。赤は目標、青は制約を守る最も近い点。" style="width:100%;max-width:560px;height:auto"><path d="M55 63V375H367" fill="none" stroke="currentColor"/><path d="M55 375H211V219L55 63Z" fill="#137d7922" stroke="#137d79" stroke-width="2"/>{grid}<text x="270" y="410">x₁ 生産量</text><text x="10" y="25">x₂ 生産量</text><text x="228" y="170">x₁ ≤ 3</text><text x="65" y="50">x₁ + x₂ ≤ 6</text><line x1="{zx}" y1="{zy}" x2="{xx}" y2="{xy}" stroke="#bc583c" stroke-dasharray="5 4"/><circle cx="{zx}" cy="{zy}" r="7" fill="#bc583c"/><circle cx="{xx}" cy="{xy}" r="5" fill="#246baf"/><path d="M{xx} {xy}L{dx} {dy}" stroke="#246baf" stroke-width="4"/><text x="{zx+10}" y="{zy-10}">z</text><text x="{xx+10}" y="{xy+20}">x*</text><text x="30" y="397">0</text><text x="205" y="397">3</text><text x="363" y="397">6</text></svg>'''
        frames.append(svg+f'<p><strong>{case["label"]}</strong>：{explanations[case["label"]]}</p><p>z={z} → x*={list(x)}。∂x*/∂z₁=({j[0][0]}, {j[1][0]})。</p><p>切り捨て後の値={case["floor"]} → 整数化した出力={case["integer"]}。青線は、今の生産量x*から、製品1の目標z₁を上げたときに動く方向を示す。整数にする前の変化。</p>')
    options=''.join(f'<option value="{i}">{escape(display_names[c["label"]])}</option>' for i,c in enumerate(result['cases']))
    payload=json.dumps(frames,ensure_ascii=False).replace('</','<\\/')
    interactive=f'<figure class="teaching" data-b21><h3>図4を動かす：目標を上げると、どの製品の量が変わるか</h3><label>どの上限に達しているか <select>{options}</select></label><script type="application/json" data-frames>{payload}</script><div data-output aria-live="polite">{frames[0]}</div><figcaption>run.pyの2製品の例。灰色の点は、制約を守る整数の生産量。目標をわずかに動かしたときの連続出力の変化（局所Jacobian）は中心差分で検算した。整数化を通る学習用の代理勾配とは別の値。</figcaption></figure>'
    bars=''
    for row,(label,values) in enumerate(result['paper_evidence']['setting1'].items()):
        y=45+row*70; h=values['holding']; b=values['backorder']
        bars+=f'<text x="10" y="{y}">{escape(label)}</text><rect x="140" y="{y-20}" width="{h}" height="25" fill="#137d79"/><rect x="{140+h}" y="{y-20}" width="{b}" height="25" fill="#bc583c"/><text x="{145+h+b}" y="{y}">{h+b:.2f}</text><text x="140" y="{y+25}">{h:.2f} + {b:.2f}</text>'
    evidence=f'<figure class="teaching"><h3>ASML設定1：保有費用とバックオーダー費用</h3><svg viewBox="0 0 535 265" role="img" aria-label="表4の平均費用。echelon DBS 286.99、MSP 289.25、提案法277.74。" style="width:100%;height:auto">{bars}<text x="10" y="255">緑：保有費用　赤：バックオーダー費用</text></svg><figcaption>著者の表4から、同じ設定での平均費用を比較した。各棒は0から始まる。費用の分布を表す累積分布（CDF）でも、Labで再現した値でもない。</figcaption></figure>'
    return interactive+evidence
