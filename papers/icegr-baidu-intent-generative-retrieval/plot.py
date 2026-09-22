"""Render Eq. 9 directly; this is an equation plot, not an empirical curve."""
from pathlib import Path
import math

def render(out):
 points=[]
 for i in range(101):
  d=-1+2*i/100;factor=min(1.8,max(.2,1+math.log((2-d)/(2+d))))
  points.append(f'{80+(d+1)*270},{340-(factor-.2)*160}')
 body='<text x="35" y="35" font-size="21">RCPO：marginが大きいpairを弱く重み付け</text><text x="35" y="63">Eq. 9の計算曲線（実験結果ではない）</text>'
 body+='<path d="M80 80 V350 H630" fill="none" stroke="#526979"/>'
 for d in [-1,-.5,0,.5,1]:body+=f'<text x="{80+(d+1)*270}" y="380" text-anchor="middle">{d}</text>'
 for v in [.2,1,1.8]:body+=f'<text x="60" y="{345-(v-.2)*160}" text-anchor="end">{v}</text>'
 body+='<polyline points="'+' '.join(points)+'" fill="none" stroke="#287a66" stroke-width="4"/>'
 body+='<text x="320" y="415">composite score差 Δr</text><text x="30" y="230" transform="rotate(-90 30 230)">βeff / β</text><text x="35" y="455">係数は[0.2,1.8]。gradientは現在のpolicy比にも依存する。</text>'
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 480" role="img" aria-label="RCPO margin係数曲線"><title>RCPO Eq. 9のmargin係数</title><rect width="700" height="480" fill="#f8fafc"/><g font-family="sans-serif" font-size="15" fill="#17324d">{body}</g></svg>'
 Path(__file__).with_name('margin-curve.svg').write_text(svg)
