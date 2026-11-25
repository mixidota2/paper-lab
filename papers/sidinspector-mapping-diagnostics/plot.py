"""An address table: same unique leaves, different behavioral grouping."""
from pathlib import Path

def render(out):
 body='<text x="24" y="30" font-size="20">SIDが重ならなくても、関連商品が別々になる例</text><text x="24" y="60">同じ6商品。関連する対は a–b、c–d、e–f</text>'
 for row,(name,m) in enumerate(out['maps'].items()):
  yy=95+row*120
  label={'aliased':'完全SIDを共有 / D2=0.667, D3=1','unique_unaligned':'全商品を区別、関連する対は別の色 / D2=0, D3=0','unique_aligned':'全商品を区別、関連する対は同じ色 / D2=0, D3=1'}[name]
  body+=f'<text x="24" y="{yy}">{label}</text>'
  for j,(item,code) in enumerate(m.items()):
   xx=24+j*104;color=['#dbedf6','#f8e3cb','#e4dff7'][code[0]]
   body+=f'<rect x="{xx}" y="{yy+12}" width="92" height="65" rx="6" fill="{color}" stroke="#789"/><text x="{xx+46}" y="{yy+36}" text-anchor="middle">{item}</text><text x="{xx+46}" y="{yy+63}" text-anchor="middle">{code[0]} : {code[1]}</text>'
 body+='<text x="24" y="465">色は最初の符号。数値は run.py で計算した架空の例。</text>'
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 670 490" role="img" aria-label="同じ6商品の3通りのSID対応表"><title>SIDで商品を区別できるか、関連商品が同じ色に残るか</title><rect width="670" height="490" fill="#f8fafc"/><g font-family="sans-serif" font-size="15" fill="#17324d">{body}</g></svg>'
 Path(__file__).with_name('mapping-grid.svg').write_text(svg)
