"""An address table: same unique leaves, different behavioral grouping."""
from pathlib import Path

def render(out):
 body='<text x="24" y="30" font-size="20">一意な住所でも、行動pairが分断される</text><text x="24" y="60">同じ6 item / 行動pairは a–b, c–d, e–f</text>'
 for row,(name,m) in enumerate(out['maps'].items()):
  yy=95+row*120
  label={'aliased':'共有あり / D2=0.667, D3=1','unique_unaligned':'一意・近傍不一致 / D2=0, D3=0','unique_aligned':'一意・近傍一致 / D2=0, D3=1'}[name]
  body+=f'<text x="24" y="{yy}">{label}</text>'
  for j,(item,code) in enumerate(m.items()):
   xx=24+j*104;color=['#dbedf6','#f8e3cb','#e4dff7'][code[0]]
   body+=f'<rect x="{xx}" y="{yy+12}" width="92" height="65" rx="6" fill="{color}" stroke="#789"/><text x="{xx+46}" y="{yy+36}" text-anchor="middle">{item}</text><text x="{xx+46}" y="{yy+63}" text-anchor="middle">{code[0]} : {code[1]}</text>'
 body+='<text x="24" y="465">色は第1 prefix。数値はrun.pyの人工fixture。</text>'
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 670 490" role="img" aria-label="3種類のSID住所表"><title>同じitem集合の住所と行動近傍</title><rect width="670" height="490" fill="#f8fafc"/><g font-family="sans-serif" font-size="15" fill="#17324d">{body}</g></svg>'
 Path(__file__).with_name('mapping-grid.svg').write_text(svg)
