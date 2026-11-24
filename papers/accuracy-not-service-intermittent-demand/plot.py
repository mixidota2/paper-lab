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
 body='<text x="35" y="30" font-size="21">予測誤差と注文完納率の順位（著者集計）</text>'
 body+=f'<text x="35" y="55">38手法を比較。両軸とも1位が良い。順位相関 ρ = {rho:.6f}</text>'
 body+='<path d="M70 80 V420 H620" fill="none" stroke="#607d8b"/>'
 for k in [1,10,20,30,38]:
  xx=70+(k-1)/37*550;yy=80+(k-1)/37*340
  body+=f'<text x="{xx}" y="446" text-anchor="middle">{k}</text><text x="54" y="{yy+5}" text-anchor="end">{k}</text>'
 body+='<text x="350" y="478" text-anchor="middle">予測誤差の順位（右ほど誤差が大きい）</text><text x="13" y="262" transform="rotate(-90 13 262)">完納率の順位（下ほど完納率が低い）</text>'
 for r in rows:
  xx=70+(float(r['mase_rank'])-1)/37*550;yy=80+(float(r['cofr_rank'])-1)/37*340
  label=html.escape(r['method']);body+=f'<circle cx="{xx}" cy="{yy}" r="5" fill="#156b8a" opacity=".8"><title>{label}：予測誤差の順位{r["mase_rank"]}、注文完納率の順位{r["cofr_rank"]}</title></circle>'
  if r['method'] in ['WMA','ADIDA','Croston','TimesFM']:
   body+=f'<text x="{xx+8 if xx<500 else xx-8}" y="{yy-8}" text-anchor="{"start" if xx<500 else "end"}">{label}</text>'
 (D/'rank-scatter.svg').write_text(svg('著者が公開した順位を使い、予測誤差と注文完納率を比べた散布図',body))
 body='<text x="35" y="32" font-size="21">ゼロを含める場合と除く場合の平均（人工データ10点）</text>'
 xs=[0,0,0,0,2,0,0,0,6,0]
 for j,v in enumerate(xs):
  xx=65+j*58;body+=f'<rect x="{xx}" y="{350-v*40}" width="28" height="{max(v*40,2)}" fill="#348cac"/><text x="{xx+12}" y="376">{j+1}</text>'
 for c,color,label in [(.8,'#995526','ゼロを含む平均 0.8'),(4,'#9550a0','正の需要だけの平均 4.0')]:
  yy=350-c*40;body+=f'<path d="M45 {yy} H650" stroke="{color}" stroke-dasharray="7 4"/><text x="{300 if c==4 else 400}" y="{yy-10}" fill="{color}">{label}</text>'
 body+='<text x="35" y="423">標準偏差はゼロを含むと1.833、正の需要だけだと2.0</text><text x="35" y="450">Labは元の単位に戻せることを確認した。Chronos-2は実行していない。</text>'
 (D/'recentering.svg').write_text(svg('人工データ10点で、ゼロを含む平均と、正の需要だけの平均を比べる図',body))
 result['author_aggregate_audit']={'n':len(rows),'rank_pearson_from_published_ranks':rho,'csv_sha256':hashlib.sha256((D/'author-orderbook.csv').read_bytes()).hexdigest(),'scope':'著者が公開した順位表から相関を計算し直した。モデルや注文処理は再実行していない。'}
 return result
if __name__=='__main__':
 out=render(json.loads((D/'results.json').read_text()));(D/'results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
