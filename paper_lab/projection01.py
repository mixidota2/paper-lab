"""初版の図4をもとにした射影の例と、初版の表4の費用内訳を表示する。"""
import json
from html import escape


def widget(result):
    if not isinstance(result,dict) or not result.get('lab01_projection'):
        return ''
    frames=[]
    display_names={'Free':'制約に達していない（Free）','Pinned':'製品1が個別上限に達する（Pinned）','Competing':'2製品で共有上限に達する（Competing）'}
    explanations={'Free':'この点の近くでは制約に達しないので、目標を変えた分だけ連続値の生産量も変わります。','Pinned':'製品1の連続値は上限の3です。目標z₁を少し増やしても、x₁は増えません。','Competing':'2製品の連続値は合計6です。製品1の目標z₁を少し増やすとx₁が増え、その分だけx₂が減ります。'}
    for case in result['cases']:
        z=case['target']; x=case['projected']; j=case['jacobian']
        def point(v):return (55+v[0]*52,375-v[1]*52)
        zx,zy=point(z); xx,xy=point(x)
        dx,dy=point([x[0]+j[0][0],x[1]+j[1][0]])
        grid=''.join(f'<circle cx="{point((a,b))[0]}" cy="{point((a,b))[1]}" r="3" fill="#78908b"/>' for a in range(4) for b in range(7-a))
        svg=f'''<svg viewBox="0 0 470 425" role="img" aria-label="{case['label']}。緑の領域は共有と個別の制約を守る生産量です。赤は目標、青い点は領域内で目標に最も近い連続値です。" style="width:100%;max-width:560px;height:auto"><path d="M55 63V375H367" fill="none" stroke="currentColor"/><path d="M55 375H211V219L55 63Z" fill="#137d7922" stroke="#137d79" stroke-width="2"/>{grid}<text x="270" y="410">x₁ 生産量</text><text x="10" y="25">x₂ 生産量</text><text x="228" y="170">x₁ ≤ 3</text><text x="65" y="50">x₁ + x₂ ≤ 6</text><line x1="{zx}" y1="{zy}" x2="{xx}" y2="{xy}" stroke="#bc583c" stroke-dasharray="5 4"/><circle cx="{zx}" cy="{zy}" r="7" fill="#bc583c"/><circle cx="{xx}" cy="{xy}" r="5" fill="#246baf"/><path d="M{xx} {xy}L{dx} {dy}" stroke="#246baf" stroke-width="4"/><text x="{zx+10}" y="{zy-10}">z</text><text x="{xx+10}" y="{xy+20}">x*</text><text x="30" y="397">0</text><text x="205" y="397">3</text><text x="363" y="397">6</text></svg>'''
        frames.append(svg+f'<p><strong>{case["label"]}</strong>：{explanations[case["label"]]}</p><p>z={z} → x*={list(x)}。∂x*/∂z₁=({j[0][0]}, {j[1][0]})。</p><p>切り捨てると{case["floor"]}、優先度を使って整数に直すと{case["integer"]}です。青い線は、製品1の目標を増やしたときに連続値x*が動く方向です。動かない条件では、線は点に重なります。</p>')
    options=''.join(f'<option value="{i}">{escape(display_names[c["label"]])}</option>' for i,c in enumerate(result['cases']))
    payload=json.dumps(frames,ensure_ascii=False).replace('</','<\\/')
    interactive=f'<figure class="teaching" data-b21><h3>制約に達したときの生産量の変化</h3><label>制約のかかり方 <select>{options}</select></label><script type="application/json" data-frames>{payload}</script><div data-output aria-live="polite">{frames[0]}</div><figcaption>初版の図4をもとに、run.pyで2製品を計算しました。灰色の点は制約を守る整数の生産量です。目標を両側に少し動かしても、連続値が解析式どおりに変わることを中心差分で確認しました。整数化で使う近似の勾配とは異なります。</figcaption></figure>'
    bars=''
    labels = {'echelon_DBS': 'echelon DBS', 'MSP': 'MSP', 'Ours': '提案法'}
    for row,(label,values) in enumerate(result['paper_evidence']['setting1'].items()):
        y=45+row*70; h=values['holding']; b=values['backorder']
        bars+=f'<text x="10" y="{y}">{escape(labels[label])}</text><rect x="140" y="{y-20}" width="{h}" height="25" fill="#137d79"/><rect x="{140+h}" y="{y-20}" width="{b}" height="25" fill="#bc583c"/><text x="{145+h+b}" y="{y}">{h+b:.2f}</text><text x="140" y="{y+25}">{h:.2f} + {b:.2f}</text>'
    evidence=f'<figure class="teaching"><h3>初版（v1）表4：ASML設定1の平均費用</h3><svg viewBox="0 0 535 265" role="img" aria-label="初版の表4、設定1の平均費用。echelon DBSは286.99、MSPは289.25、提案法は277.74です。" style="width:100%;height:auto">{bars}<text x="10" y="255">緑：保有費用　赤：バックオーダー費用</text></svg><figcaption>著者が初版の表4で報告した値です。各棒は0から始まり、保有費用とバックオーダー費用を足した平均を表します。費用の分布でも、改訂版の表5の値でもありません。Labは費用を再計算していません。</figcaption></figure>'
    return interactive+evidence
