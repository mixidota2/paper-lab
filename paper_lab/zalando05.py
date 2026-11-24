"""Pricing desk: paper-specific figures driven by results.json."""
import json
from html import escape
from paper_lab.batch28 import table as _table


def table(headers, rows):
    return _table(headers, rows).replace('aria-label="人工実験の比較"', 'aria-label="数値の比較（出典は図の注記）"')


def widget(result):
    if not isinstance(result, dict) or result.get('lab05') != 'zalando':
        return ''
    fs=result['frames']
    def frontier(selected):
        # Derive axis bounds from the computed assortment, including repeated choices.
        lo=min(f['nmv'] for f in fs); hi=max(f['nmv'] for f in fs)
        bottom=min(f['ltp'] for f in fs); top=max(f['ltp'] for f in fs)
        x=lambda f:70+440*(f['nmv']-lo)/max(hi-lo,1)
        y=lambda f:245-195*(f['ltp']-bottom)/max(top-bottom,1)
        svg='<svg viewBox="0 0 620 310" role="img" aria-label="架空の3商品で選んだ案の純売上と長期利益" style="width:100%;height:auto"><path d="M70 30V245H535" fill="none" stroke="currentColor"/>'
        svg+='<polyline points="'+' '.join(f'{x(f):.1f},{y(f):.1f}' for f in fs)+'" fill="none" stroke="#16847a" stroke-width="3"/>'
        for f in fs:
            svg+=f'<circle cx="{x(f):.1f}" cy="{y(f):.1f}" r="3" fill="#16847a"/>'
        f=fs[selected]
        svg+=f'<circle cx="{x(f):.1f}" cy="{y(f):.1f}" r="8" fill="#c96825"/><text x="70" y="21">LTP（架空通貨）</text><text x="370" y="298">NMV（架空通貨）</text><text x="70" y="270">{lo:.0f}</text><text x="490" y="270">{hi:.0f}</text><text x="5" y="55">{top:.0f}</text><text x="5" y="245">{bottom:.0f}</text></svg>'
        return svg
    frames=[]
    for i,f in enumerate(fs):
        rows=[[a['article'],f'{100*a["discount"]:.0f}%',f'{a["demand"]:.1f}',a['stock'],f'{a["sales"]:.1f}',f'{a["nmv"]:.0f}',f'{a["ltp"]:.0f}'] for a in f['articles']]
        frames.append(f'<p><strong>α = {f["alpha"]:.1f}</strong> ／ NMV {f["nmv"]:.0f} ／ LTP {f["ltp"]:.0f} ／ 短期利益 {f["profit"]:.0f}</p>'+frontier(i)+'<p>表は横にスクロールできます。金額の単位は架空通貨です。</p><div class="zalando-price-table">'+table(['商品','割引','3日需要','在庫 M','販売 min(M,需要)','NMV','LTP'],rows)+'</div>')
    payload=json.dumps(frames,ensure_ascii=False).replace('</','<\\/')
    out='<figure class="teaching" id="zalando-alpha"><h3>純売上を重視したときに選ばれる割引率</h3><p>著者はLightGBMで日と割引率ごとの需要を予測し、在庫を上限に販売数を求める。その販売数で長期利益LTP + α×純売上NMVを計算し、商品ごとに割引率を選ぶ。この図はFig. 3–4をもとにした教材。</p><label for="zalando-slider">純売上の重み α（0〜2）</label> <input id="zalando-slider" disabled type="range" min="0" max="20" value="0" step="1" style="width:min(100%,360px)"><noscript><p>JavaScriptが無効のため、α = 0 の静的な結果を表示しています。スライダー操作はできません。</p></noscript><script type="application/json" data-zframes>'+payload+'</script><div data-zoutput aria-live="polite">'+frames[0]+'</div><figcaption>Labは式(1)、(3)〜(7)を3商品に当てはめた。R=0.2、VAT=0.19、C=0.2P、γ=0.25P。各点は、そのαで選ばれた案を示す。すべてのPareto解を示した図ではない。</figcaption></figure>'
    out+='''<script>(()=>{const r=document.getElementById('zalando-alpha');const f=JSON.parse(r.querySelector('[data-zframes]').textContent);r.querySelector('input').disabled=false;r.querySelector('input').addEventListener('input',e=>{r.querySelector('[data-zoutput]').innerHTML=f[+e.target.value]})})();</script>'''
    out+='<figure class="teaching"><h3>在庫と返品を考慮した利益の計算</h3><ol><li>需要：q(d)=q(0)(1−d)<sup>−ε</sup>。割引を大きくすると予測需要が増える。</li><li>販売：s(d)=min(M, Σ Sᵗ(d))。表の需要が在庫より多ければ、販売数は在庫の数までとする。</li><li>純売上：NMV=(1−R)(1−d)Ps/(1+VAT)。返品と税を除く。</li><li>長期利益：LTP=NMV−Cs+[M−s(1−R)]γ。残在庫の将来価値を足す。</li></ol><figcaption>原論文式(3)〜(7)、(12)を参照。γを一定に置くため、将来の値付けを変えたときの影響は扱わない。</figcaption></figure>'
    evidence=result['paper_evidence']
    metric_frames=[]
    metrics=[('demand_error','Demand Error（価格で重みを付けた需要の誤差）'),('gmv_error','GMV Error（売上総額の予測のずれ）'),('rmse','RMSE（商品を均等に扱う）'),('mape','MAPE（商品を均等に扱う）')]
    for key,label in metrics:
        ordered=sorted(evidence['table2'],key=lambda r:r[key])
        explanation = ('<p>GMV Errorは、市場と日ごとに、各商品の予測販売数に割引後の価格を掛けて足し、予測GMVを求める。GMV Errorは、予測GMVと実績GMVの差の絶対値を、実績GMVで割った比率だ。値が小さいほど売上総額の予測は実績に近い。ただし、商品ごとの過大予測と過小予測は、合計すると打ち消し合うことがある。この表が示すのはこの比率であり、利益やNMVではない。市場間でさらに重みを付けたか、実績GMVが0の場合にどう処理したかは確認していない。<a href="https://arxiv.org/html/2606.13741v1">原典§3.2式(10)–(11)</a>。</p>' if key == 'gmv_error' else '')
        metric_frames.append(explanation+'<p><strong>'+escape(label)+'：最小は '+ordered[0]['model']+'</strong></p>'+table(['モデル','平均誤差','訓練時間（時間）'],[[r['model'],r[key],r['training_hours']] for r in ordered]))
    out+='<figure class="teaching" data-b21 data-enable-select><h3>評価指標ごとのモデルの順位</h3><label>Table 2の評価指標 <select disabled style="max-width:100%;width:100%;min-width:0;box-sizing:border-box">'+''.join(f'<option value="{i}">{escape(label)}</option>' for i,(_,label) in enumerate(metrics))+'</select></label><noscript><p>JavaScriptが無効のため、Demand Error の静的な比較を表示しています。指標の切り替えはできません。</p></noscript><script type="application/json" data-frames>'+json.dumps(metric_frames,ensure_ascii=False).replace('</','<\\/')+'</script><div data-output aria-live="polite">'+metric_frames[0]+'</div><figcaption>著者が212日分の予測で比べた値を示す。指標は一つずつ切り替え、単位が異なる誤差どうしを足さない。著者が設定の探索に使えた予算はモデル間で異なる。</figcaption></figure>'
    svg='<svg viewBox="0 0 620 250" role="img" aria-label="論文Table 3の予測PCIIと実現PCII、oracle比パーセント" style="width:100%;height:auto">'
    for i,r in enumerate(evidence['table3']):
        for j,(key,color) in enumerate([('forecast','#b97942'),('materialized','#16847a')]):
            y=35+i*90+j*29; w=r[key]*3.4
            svg+=f'<text x="5" y="{y+17}" font-size="12">{r["model"]} {"予測" if j==0 else "実現"}</text><rect x="125" y="{y}" width="{w}" height="23" fill="{color}"/><text x="{130+w}" y="{y+17}" font-size="12">{r[key]:.2f}%</text>'
    svg+='<path d="M465 20V200" stroke="currentColor" stroke-dasharray="4"/><text x="440" y="221">oracle 100%</text><text x="125" y="240">棒の原点 0% ／ PCIIのoracle比</text></svg>'
    out+='<figure class="teaching"><h3>シミュレーションで予測した利益と実現利益</h3>'+svg+'<figcaption>Table 3のうち、α=0で著者が行ったシミュレーションの結果。TweedieはMSEより予測と実現の差が小さいが、実現PCIIはMSEを1.50ポイント下回る。</figcaption></figure>'
    svg='<svg viewBox="0 0 620 240" role="img" aria-label="実地試験統合の効果と95パーセント区間" style="width:100%;height:auto">'
    x=lambda v:180+v*28
    svg+=f'<path d="M{x(0)} 20V180" stroke="currentColor" stroke-dasharray="4"/>'
    for i,r in enumerate(evidence['table5']):
        y=45+i*55
        svg+=f'<text x="8" y="{y+5}">{r["metric"]}</text><path d="M{x(r["low"])} {y}H{x(r["high"])}" stroke="#16847a" stroke-width="4"/><circle cx="{x(r["effect"])}" cy="{y}" r="6" fill="#16847a"/><text x="360" y="{y+23}" font-size="12">{r["effect"]:+.2f}% [{r["low"]:.2f}, {r["high"]:.2f}]</text>'
    for v in (-4,0,4,8,12): svg+=f'<text x="{x(v)}" y="205" text-anchor="middle">{v}</text>'
    svg+='<text x="160" y="233">統合効果（%）・95%区間</text></svg>'
    out+='<figure class="teaching"><h3>実地試験での利益と売上の推定値</h3>'+svg+'<figcaption>著者は12市場・11波で行ったA/B試験23件をベイズ階層モデルで統合した（Table 5）。利益貢献の95%区間は0より上で、純売上の区間は0をまたぐ。実施回ごとの数値は載っていない。</figcaption></figure>'
    out+='<figure class="teaching"><h3>架空データでの価格選択と利益</h3>'+table(['seed','損失','需要RMSE','予測利益/oracle %','実現利益/oracle %'],[[r['seed'],r['loss'],round(r['grid_rmse'],3),round(r['forecast_profit_pct_oracle'],2),round(r['materialized_profit_pct_oracle'],2)] for r in result['experiment']])+'<figcaption>Labは400商品×56日を3つのseedで計算した。入力する特徴、木の設定、在庫、費用は共通にした。この表の実現利益は、ノイズを除いた期待需要で評価した値で、実地のPCIIではない。oracleは将来需要を知る条件で長期利益が最大になる割引を選ぶ。このため、短期利益で比べると100%を超える場合がある。</figcaption></figure>'
    return out
