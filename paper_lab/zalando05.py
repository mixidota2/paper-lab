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
        svg='<svg viewBox="0 0 620 310" role="img" aria-label="架空3商品の純売上と長期利益の候補曲線" style="width:100%;height:auto"><path d="M70 30V245H535" fill="none" stroke="currentColor"/>'
        svg+='<polyline points="'+' '.join(f'{x(f):.1f},{y(f):.1f}' for f in fs)+'" fill="none" stroke="#16847a" stroke-width="3"/>'
        for f in fs:
            svg+=f'<circle cx="{x(f):.1f}" cy="{y(f):.1f}" r="3" fill="#16847a"/>'
        f=fs[selected]
        svg+=f'<circle cx="{x(f):.1f}" cy="{y(f):.1f}" r="8" fill="#c96825"/><text x="70" y="21">LTP（架空通貨）</text><text x="370" y="298">NMV（架空通貨）</text><text x="70" y="270">{lo:.0f}</text><text x="490" y="270">{hi:.0f}</text><text x="5" y="55">{top:.0f}</text><text x="5" y="245">{bottom:.0f}</text></svg>'
        return svg
    frames=[]
    for i,f in enumerate(fs):
        rows=[[a['article'],f'{100*a["discount"]:.0f}%',f'{a["demand"]:.1f}',a['stock'],f'{a["sales"]:.1f}',f'{a["nmv"]:.0f}',f'{a["ltp"]:.0f}'] for a in f['articles']]
        frames.append(f'<p><strong>α = {f["alpha"]:.1f}</strong> ／ NMV {f["nmv"]:.0f} ／ LTP {f["ltp"]:.0f} ／ 短期利益 {f["profit"]:.0f}</p>'+frontier(i)+table(['商品','割引','3日需要','在庫 M','販売 min(M,需要)','NMV','LTP'],rows))
    payload=json.dumps(frames,ensure_ascii=False).replace('</','<\\/')
    out='<figure class="teaching" id="zalando-alpha"><h3>価格決定卓：売上を重くすると、どの商品を割り引くか</h3><p>日次LightGBM → 割引×日の需要表 → 在庫上限 → LTP + α NMVで商品別に採点。Fig. 3–4の教材化。</p><label for="zalando-slider">純売上の重み α（0〜2）</label> <input id="zalando-slider" type="range" min="0" max="20" value="0" step="1" style="width:min(100%,360px)"><script type="application/json" data-zframes>'+payload+'</script><div data-zoutput aria-live="polite">'+frames[0]+'</div><figcaption>式(1)、(3)〜(7)を3商品で計算。R=0.2、VAT=0.19、C=0.2P、γ=0.25P。全Pareto解の列挙ではなく、αで選ばれた候補の軌跡。</figcaption></figure>'
    out+='''<script>(()=>{const r=document.getElementById('zalando-alpha');const f=JSON.parse(r.querySelector('[data-zframes]').textContent);r.querySelector('input').addEventListener('input',e=>{r.querySelector('[data-zoutput]').innerHTML=f[+e.target.value]})})();</script>'''
    out+='<figure class="teaching"><h3>在庫で止まり、返品と将来価値で採点が変わる</h3><ol><li>需要：q(d)=q(0)(1−d)<sup>−ε</sup>。割引で増える。</li><li>販売：s(d)=min(M, Σ Sᵗ(d))。表の需要が在庫を超えた部分は売れない。</li><li>純売上：NMV=(1−R)(1−d)Ps/(1+VAT)。返品と税を除く。</li><li>長期利益：LTP=NMV−Cs+[M−s(1−R)]γ。残在庫の将来価値を足す。</li></ol><figcaption>原論文式(3)〜(7)、(12)。一定γは将来の値付け変更を扱わない。</figcaption></figure>'
    evidence=result['paper_evidence']
    metric_frames=[]
    metrics=[('demand_error','Demand Error（価格加重、低いほど良い）'),('gmv_error','GMV Error（純粋な一様誤差ではない）'),('rmse','RMSE（商品を均等に扱う）'),('mape','MAPE（商品を均等に扱う）')]
    for key,label in metrics:
        ordered=sorted(evidence['table2'],key=lambda r:r[key])
        metric_frames.append('<p><strong>'+escape(label)+'：最小は '+ordered[0]['model']+'</strong></p>'+table(['モデル','平均誤差','訓練時間（時間）'],[[r['model'],r[key],r['training_hours']] for r in ordered]))
    out+='<figure class="teaching" data-b21><h3>同じ予測でも、指標を選ぶと勝者が変わる</h3><label>Table 2の評価指標 <select style="max-width:100%;width:100%;min-width:0;box-sizing:border-box">'+''.join(f'<option value="{i}">{escape(label)}</option>' for i,(_,label) in enumerate(metrics))+'</select></label><script type="application/json" data-frames>'+json.dumps(metric_frames,ensure_ascii=False).replace('</','<\\/')+'</script><div data-output aria-live="polite">'+metric_frames[0]+'</div><figcaption>著者報告、212日。異なる単位の誤差を足す重みスライダーにはしていない。モデル間で探索予算も同一ではない。</figcaption></figure>'
    svg='<svg viewBox="0 0 620 250" role="img" aria-label="論文Table 3の予測PCIIと実現PCII、oracle比パーセント" style="width:100%;height:auto">'
    for i,r in enumerate(evidence['table3']):
        for j,(key,color) in enumerate([('forecast','#b97942'),('materialized','#16847a')]):
            y=35+i*90+j*29; w=r[key]*3.4
            svg+=f'<text x="5" y="{y+17}" font-size="12">{r["model"]} {"予測" if j==0 else "実現"}</text><rect x="125" y="{y}" width="{w}" height="23" fill="{color}"/><text x="{130+w}" y="{y+17}" font-size="12">{r[key]:.2f}%</text>'
    svg+='<path d="M465 20V200" stroke="currentColor" stroke-dasharray="4"/><text x="440" y="221">oracle 100%</text><text x="125" y="240">棒の原点 0% ／ PCIIのoracle比</text></svg>'
    out+='<figure class="teaching"><h3>利益の約束は近づくが、実現利益の順位は別</h3>'+svg+'<figcaption>著者のTable 3。α=0のシミュレーション限定。Tweedieは予測との乖離が小さく、実現PCIIはMSEより1.50ポイント低い。</figcaption></figure>'
    svg='<svg viewBox="0 0 620 240" role="img" aria-label="実地試験統合の効果と95パーセント区間" style="width:100%;height:auto">'
    x=lambda v:180+v*28
    svg+=f'<path d="M{x(0)} 20V180" stroke="currentColor" stroke-dasharray="4"/>'
    for i,r in enumerate(evidence['table5']):
        y=45+i*55
        svg+=f'<text x="8" y="{y+5}">{r["metric"]}</text><path d="M{x(r["low"])} {y}H{x(r["high"])}" stroke="#16847a" stroke-width="4"/><circle cx="{x(r["effect"])}" cy="{y}" r="6" fill="#16847a"/><text x="360" y="{y+23}" font-size="12">{r["effect"]:+.2f}% [{r["low"]:.2f}, {r["high"]:.2f}]</text>'
    for v in (-4,0,4,8,12): svg+=f'<text x="{x(v)}" y="205" text-anchor="middle">{v}</text>'
    svg+='<text x="160" y="233">統合効果（%）・95%区間</text></svg>'
    out+='<figure class="teaching"><h3>実地の利益効果は正、売上の区間は0をまたぐ</h3>'+svg+'<figcaption>Table 5のBayesian階層メタ分析。23 A/B、12市場、11波。波別の数値は掲載されていないため捏造しない。</figcaption></figure>'
    out+='<figure class="teaching"><h3>このLabで実行した小規模実験</h3>'+table(['seed','損失','需要RMSE','予測利益/oracle %','実現利益/oracle %'],[[r['seed'],r['loss'],round(r['grid_rmse'],3),round(r['forecast_profit_pct_oracle'],2),round(r['materialized_profit_pct_oracle'],2)] for r in result['experiment']])+'<figcaption>400商品×56日、3 seed。共通特徴・木の設定・在庫・費用を固定。実現はノイズなし期待需要での評価で、実地PCIIの追試ではない。</figcaption></figure>'
    return out
