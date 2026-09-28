"""Render paper-specific teaching widgets directly from reproducible results."""
import json
from html import escape


def table(headers, rows):
    return '<div class="matrix-scroll" tabindex="0" role="region" aria-label="人工実験の比較"><table><thead><tr>'+''.join('<th>'+escape(str(x))+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+escape(str(x))+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'


def number(x):
    return f'{x:.3f}'.rstrip('0').rstrip('.')


def widget(result):
    if not isinstance(result,dict) or 'lab28' not in result: return ''
    kind=result['lab28']; frames=[]
    for f in result['frames']:
        if kind=='reasoncast':
            content='<div class="b21-tokens"><span>Chronos-2相当の固定値</span><span>→ '+f['route']+'</span><span>→ 補正後</span></div>'
            content+=table(['日','実績','基準','補正後'],[[i+1,f['actual'][i],f['base'][i],number(f['prediction'][i])] for i in range(3)])
            content+=f'<p>WMAPE：基準 {number(f["baseline_wmape"])}% → 補正後 {number(f["proposed_wmape"])}%</p>'
        elif kind=='scope':
            content=table(['商品','周期（日）','荷量','台数/配送','効用/日'],[[p['item'],p['cycle'],p['load'],p['vehicles'],p['utility']] for p in f['plans']])
            b,p=f['baseline'],f['proposed']
            content+=f'<p>需要順で選ぶ：{b["item"]}・{b["cycle"]}日・効用{b["utility"]}。全体で選ぶ：{p["item"]}・{p["cycle"]}日・効用{p["utility"]}。</p>'
        elif kind=='onetrans':
            content='<ol class="b21-search">'+''.join(f'<li>候補 {c["item"]}：log({c["prefix"]}) + {f["beta"]} × {c["offset"]} + log({c["conditional"]}) = <strong>{number(c["score"])}</strong></li>' for c in f['ranking'])+'</ol>'
            content+='<p>上ほど得点が高い。βだけを動かし、学習した確率に相当する値は固定する。</p>'
        elif kind=='evaluation':
            content='<div class="b21-cards">'+''.join('<div>買い手 '+', '.join(str(i+1) for i in g)+'<br>Aの符号付き誤差 <strong>'+str(sum(result['predictions']['A'][i]-result['actual'][i] for i in g))+'</strong></div>' for g in f['groups'])+'</div>'
            content+=table(['予測','WAPE（%）'],[[k,number(v)] for k,v in f['scores'].items()])+f'<p>勝者：{f["winner"]}。同じ予測を異なる組にまとめた結果。</p>'
        elif kind=='harness':
            content='<div class="b21-serving"><section><h4>実行前の点検</h4><p>提案：'+escape(f['proposal'])+'</p><strong>'+f['decision']+'</strong></section><section><h4>学生と学習に残す応答</h4><p>'+escape(f['executed'])+'</p><p>私的な点検履歴は含めない。</p></section></div>'
        else: raise ValueError(kind)
        frames.append(content)
    titles={'reasoncast':'介入しない経路と、誤った介入を比べる','scope':'荷量と周期から配送費用の段差を読む','onetrans':'業務上の加点で決定接頭辞の順位を変える','evaluation':'同じ予測の誤差を、どこで相殺するか','harness':'点検役を通った応答だけを履歴へ残す'}
    options=''.join(f'<option value="{i}">{escape(f["label"])}</option>' for i,f in enumerate(result['frames']))
    data=json.dumps(frames,ensure_ascii=False).replace('</','<\\/')
    return '<figure class="teaching" data-b21><h3>'+titles[kind]+'</h3><label>人工例の条件 <select>'+options+'</select></label><script type="application/json" data-frames>'+data+'</script><div data-output aria-live="polite">'+frames[0]+'</div><figcaption>run.pyが計算したresults.jsonから生成。著者の測定値ではない。</figcaption></figure>'
