"""Paper Figure 4 geometry and Table 4 mean cost composition."""
import json
from html import escape


def widget(result):
    if not isinstance(result,dict) or not result.get('lab01_projection'):
        return ''
    frames=[]
    explanations={'Free':'制約から離れた点。目標の変化がそのまま行動へ伝わる。','Pinned':'第1座標は上限3に固定。z₁を増やしてもx₁は動かない。','Competing':'共有容量6が活性。z₁の増加はx₁を増やし、x₂を減らす。'}
    for case in result['cases']:
        z=case['target']; x=case['projected']; j=case['jacobian']
        def point(v):return (55+v[0]*52,375-v[1]*52)
        zx,zy=point(z); xx,xy=point(x)
        dx,dy=point([x[0]+j[0][0],x[1]+j[1][0]])
        grid=''.join(f'<circle cx="{point((a,b))[0]}" cy="{point((a,b))[1]}" r="3" fill="#78908b"/>' for a in range(4) for b in range(7-a))
        svg=f'''<svg viewBox="0 0 470 425" role="img" aria-label="{case['label']}。緑の領域が共有容量と個別上限を守る行動。赤が目標、青が射影。" style="width:100%;max-width:560px;height:auto"><path d="M55 63V375H367" fill="none" stroke="currentColor"/><path d="M55 375H211V219L55 63Z" fill="#137d7922" stroke="#137d79" stroke-width="2"/>{grid}<text x="270" y="410">x₁ 生産量</text><text x="10" y="25">x₂ 生産量</text><text x="228" y="170">x₁ ≤ 3</text><text x="65" y="50">x₁ + x₂ ≤ 6</text><line x1="{zx}" y1="{zy}" x2="{xx}" y2="{xy}" stroke="#bc583c" stroke-dasharray="5 4"/><circle cx="{zx}" cy="{zy}" r="7" fill="#bc583c"/><circle cx="{xx}" cy="{xy}" r="5" fill="#246baf"/><path d="M{xx} {xy}L{dx} {dy}" stroke="#246baf" stroke-width="4"/><text x="{zx+10}" y="{zy-10}">z</text><text x="{xx+10}" y="{xy+20}">x*</text><text x="30" y="397">0</text><text x="205" y="397">3</text><text x="363" y="397">6</text></svg>'''
        frames.append(svg+f'<p><strong>{case["label"]}</strong>：{explanations[case["label"]]}</p><p>z={z} → x*={list(x)}。∂x*/∂z₁=({j[0][0]}, {j[1][0]})。</p><p>floor={case["floor"]} → 整数写像={case["integer"]}。青線は局所勾配の方向を表す。</p>')
    options=''.join(f'<option value="{i}">{escape(c["label"])}</option>' for i,c in enumerate(result['cases']))
    payload=json.dumps(frames,ensure_ascii=False).replace('</','<\\/')
    interactive=f'<figure class="teaching" data-b21><h3>図4を動かす：目標の変化はどこへ進むか</h3><label>活性制約の状態 <select>{options}</select></label><script type="application/json" data-frames>{payload}</script><div data-output aria-live="polite">{frames[0]}</div><figcaption>run.pyの2変数縮約。灰色の点は実行可能な整数行動。局所Jacobianを中心差分で検算した。</figcaption></figure>'
    bars=''
    for row,(label,values) in enumerate(result['paper_evidence']['setting1'].items()):
        y=45+row*70; h=values['holding']; b=values['backorder']
        bars+=f'<text x="10" y="{y}">{escape(label)}</text><rect x="140" y="{y-20}" width="{h}" height="25" fill="#137d79"/><rect x="{140+h}" y="{y-20}" width="{b}" height="25" fill="#bc583c"/><text x="{145+h+b}" y="{y}">{h+b:.2f}</text><text x="140" y="{y+25}">{h:.2f} + {b:.2f}</text>'
    evidence=f'<figure class="teaching"><h3>ASML設定1：保有費用とバックオーダー費用</h3><svg viewBox="0 0 535 265" role="img" aria-label="表4の平均費用。echelon DBS 286.99、MSP 289.25、提案法277.74。" style="width:100%;height:auto">{bars}<text x="10" y="255">緑：保有費用　赤：バックオーダー費用</text></svg><figcaption>著者の表4の平均費用。各棒は0を起点とする。同一設定内の比較であり、費用CDFや本Labの再現結果ではない。</figcaption></figure>'
    return interactive+evidence
