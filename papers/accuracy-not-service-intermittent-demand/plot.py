"""SVG figures from frozen author aggregates and separately labelled toy inputs."""
from pathlib import Path
import csv,html,math,hashlib,json
from statistics import mean
D=Path(__file__).parent

def svg(title,body):
 return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 500" role="img" aria-label="{title}"><title>{title}</title><rect width="700" height="500" fill="#f8fafc"/><g font-family="sans-serif" font-size="14" fill="#17324d">{body}</g></svg>'

def render(result):
 rows=list(csv.DictReader((D/'author-orderbook.csv').open()))
 x=[float(r['mase_rank']) for r in rows];y=[float(r['cofr_rank']) for r in rows]
 a,b=mean(x),mean(y)
 rho=sum((i-a)*(j-b) for i,j in zip(x,y))/math.sqrt(sum((i-a)**2 for i in x)*sum((j-b)**2 for j in y))
 body='<text x="35" y="30" font-size="21">著者公開集計：精度順位 × 注文COFR順位</text>'
 body+=f'<text x="35" y="55">38手法 / 小さい順位ほど良い / ρ = {rho:.6f}</text>'
 body+='<path d="M70 80 V420 H620" fill="none" stroke="#607d8b"/>'
 for k in [1,10,20,30,38]:
  xx=70+(k-1)/37*550;yy=80+(k-1)/37*340
  body+=f'<text x="{xx}" y="446" text-anchor="middle">{k}</text><text x="54" y="{yy+5}" text-anchor="end">{k}</text>'
 body+='<text x="350" y="478" text-anchor="middle">精度順位 → 悪い</text><text x="13" y="262" transform="rotate(-90 13 262)">COFR順位 → 悪い</text>'
 for r in rows:
  xx=70+(float(r['mase_rank'])-1)/37*550;yy=80+(float(r['cofr_rank'])-1)/37*340
  label=html.escape(r['method']);body+=f'<circle cx="{xx}" cy="{yy}" r="5" fill="#156b8a" opacity=".8"><title>{label}: accuracy {r["mase_rank"]}, COFR {r["cofr_rank"]}</title></circle>'
  if r['method'] in ['WMA','ADIDA','Croston','TimesFM']:
   body+=f'<text x="{xx+8 if xx<500 else xx-8}" y="{yy-8}" text-anchor="{"start" if xx<500 else "end"}">{label}</text>'
 (D/'rank-scatter.svg').write_text(svg('精度とCOFRの順位散布図。公式凍結集計の再描画',body))
 body='<text x="35" y="32" font-size="21">中心だけでなくscaleも変わる（人工10点）</text>'
 xs=[0,0,0,0,2,0,0,0,6,0]
 for j,v in enumerate(xs):
  xx=65+j*58;body+=f'<rect x="{xx}" y="{350-v*40}" width="28" height="{max(v*40,2)}" fill="#348cac"/><text x="{xx+12}" y="376">{j+1}</text>'
 for c,color,label in [(.8,'#995526','全体平均 0.8'),(4,'#9550a0','非ゼロ平均 4.0')]:
  yy=350-c*40;body+=f'<path d="M45 {yy} H650" stroke="{color}" stroke-dasharray="7 4"/><text x="400" y="{yy-10}" fill="{color}">{label}</text>'
 body+='<text x="35" y="423">学習contextだけで計算。全体std 1.833 / 非ゼロstd 2.0</text><text x="35" y="450">変換と逆変換の往復を検証。Chronosの推論は実行していない。</text>'
 (D/'recentering.svg').write_text(svg('人工間欠系列の全体平均と非ゼロ条件付き平均',body))
 result['author_aggregate_audit']={'n':len(rows),'rank_pearson_from_published_ranks':rho,'csv_sha256':hashlib.sha256((D/'author-orderbook.csv').read_bytes()).hexdigest(),'scope':'凍結集計の算術監査。モデル・注文replayの独立再現ではない。'}
 return result
if __name__=='__main__':
 out=render(json.loads((D/'results.json').read_text()));(D/'results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
