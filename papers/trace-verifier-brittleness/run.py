"""Original deterministic TRACE teaching example; no author code or API calls.
uv run run.py --test ; uv run run.py
"""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parent
NAMES={'read':'read_stock','write':'set_stock','report':'report_stock'}
ALIASES={'read':'fetch_count','write':'replace_count','report':'send_count'}
REVERSE={v:k for d in [NAMES,ALIASES] for k,v in d.items()}


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def rollout(agent,alias):
    """Task: correct stock 8 to 5, verify and report. Scripts are designed cases."""
    names=ALIASES if alias else NAMES
    state={'stock':8}
    # 'sensitive' genuinely omits the write when names change.
    operations=[('read',None)]
    if agent=='careful' or (agent=='sensitive' and not alias):operations.append(('write',5))
    operations += [('read',None),('report',None)]
    trace=[]
    for op,arg in operations:
        if op=='write':state['stock']=arg
        trace.append({'tool':names[op],'argument':arg,'observation':state['stock']})
    canonical=[{**step,'tool':REVERSE[step['tool']]} for step in trace]
    return {'trace':trace,'canonical':canonical,'state':state,
            'canonical_hash':digest(canonical),'state_hash':digest(state),
            'success':state['stock']==5}


def score(record,normalize=False):
    """INTENTIONALLY defective coverage: literal tool names. Outcome gates credit.
    Not TRACE Appendix A's composite score. Normalization changes scoring only.
    """
    observed={NAMES[REVERSE[s['tool']]] if normalize else s['tool'] for s in record['trace']}
    coverage=len(observed & set(NAMES.values()))/3
    return float(record['success'])*(.5+.5*coverage)


def case(agent,alias,normalize):
    base=rollout(agent,False);changed=rollout(agent,alias)
    raw=score(changed);corrected=score(changed,normalize)
    return {'agent':agent,'alias':alias,'normalize':normalize,'base':base,'changed':changed,
            'original_score':score(base),'raw_score':raw,'rescored':corrected,
            'raw_gap':score(base)-raw,'gap_after':score(base)-corrected,
            'behavior_same':base['canonical_hash']==changed['canonical_hash'],
            'state_same':base['state_hash']==changed['state_hash']}


def frame(c):
    before=c['base'];after=c['changed']
    def steps(r):return '<ol>'+''.join(f'<li><code>{s["tool"]}</code>({s["argument"]}) → 在庫{s["observation"]}</li>' for s in r['trace'])+'</ol>'
    def bar(label,value,color):return f'<p>{label} <strong>{value:.2f}</strong></p><div style="background:#e1e9e7;height:18px"><div style="background:{color};width:{value*100}%;height:18px"></div></div>'
    interpretation=('同じ操作・最終状態で点数だけが落ちた。採点時の正規化で戻るので、この例の原因は名前への依存。' if c['agent']=='careful' and c['alias'] else '必要な書込みを省いたため最終状態は誤り。名前を正規化しても成功にはならない。' if not after['success'] else '必要な操作が実行され、採点器が認識する名前もそろっている。')
    return f'''<h3>1. 実行を比較する</h3><div class="trace-columns"><div><strong>元の実行</strong>{steps(before)}</div><div><strong>比較する実行</strong>{steps(after)}</div></div>
<h3>2. 操作と状態を確かめる</h3><p>正規の操作列：<strong>{'同じ' if c['behavior_same'] else '違う'}</strong> ／ 最終状態：<strong>{'同じ' if c['state_same'] else '違う'}</strong> ／比較側の在庫：{after['state']['stock']}（正解5）</p>
<details><summary>名前を除いた操作列・状態のSHA-256を見る</summary><p>元の操作列</p><code>{before['canonical_hash']}</code><p>比較側の操作列</p><code>{after['canonical_hash']}</code><p>元の状態</p><code>{before['state_hash']}</code><p>比較側の状態</p><code>{after['state_hash']}</code></details>
<h3>3. 同じ記録を採点し直す</h3>{bar('元の実行の点数',c['original_score'],'#526f9d')}{bar('比較側・修正前の点数',c['raw_score'],'#ae5327')}{bar('比較側・現在の採点方式',c['rescored'],'#007868')}
<p>元−比較の差：修正前 {c['raw_gap']:.2f} → 現在 {c['gap_after']:.2f}。実行のやり直しはない。</p><p><strong>{interpretation}</strong></p>'''


def render():
    cases=[case(a,b,c) for a in ['careful','sensitive','weak'] for b in [False,True] for c in [False,True]]
    reported={'source':'https://arxiv.org/html/2610.11678v1#A5.T6',
              'main_unseen_tasks':88,'main_repeats':3,'positive_control_tasks':158,'positive_control_repeats':2,
              'equivalent_uncorrected':'7/8','equivalent_bonferroni':'6/8',
              'qwen_format':{'delta':-.059,'ci95':[-.123,.008],'ci90':[-.114,-.004],
                             'excess_flips_pp':9.3,'excess_flips_ci95_pp':[2.7,16.1],'label':'inconclusive'}}
    result={'note':'reportedは論文の転記。syntheticは自作の決定的な在庫修正例。論文の独立再現ではない。',
            'reported':reported,'synthetic':cases,'verification':{'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'}}
    (ROOT/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    frames=[frame(c) for c in cases]
    widget='''<style>
.trace-widget{background:#f7faf9;border:1px solid #9eaeb8;border-radius:16px;padding:clamp(12px,3vw,24px);color:#182c35;max-width:100%}.trace-widget label{display:block;margin:14px 0;font-weight:650}.trace-widget select{display:block;width:100%;padding:10px;font:inherit;background:white;color:#182c35;border:1px solid #6c818c;border-radius:6px}.trace-widget code{overflow-wrap:anywhere;word-break:break-all}.trace-columns{display:grid;grid-template-columns:1fr 1fr;gap:16px}.trace-widget output{display:block}.trace-widget li{font-size:.9rem}@media(max-width:600px){.trace-columns{grid-template-columns:1fr}}
</style>
<div class="trace-widget" id="trace-toy"><p><strong>合成実験：在庫8を5へ直し、確認して報告する</strong></p>
<label>行動するスクリプト<select id="trace-agent"><option value="0">名前に依存せず正しく直す</option><option value="1">別名になると書込みを省く</option><option value="2">いつも書込みを省く</option></select></label>
<label>ツールの名前<select id="trace-alias"><option value="0">元の名前</option><option value="1" selected>同じ操作を別名で呼ぶ</option></select></label>
<label>採点器の名前の扱い<select id="trace-normalize"><option value="0">元の名前だけを数える</option><option value="1">別名を正規化してから数える</option></select></label>
<button type="button" id="trace-reset">最初の名前依存の例へ戻す</button>
<output id="trace-output" aria-live="polite">'''+frames[2]+'''</output>
<noscript>切替にはJavaScriptが必要です。初期表示は、同じ行動でも別名だけで点が落ちる例です。</noscript></div>
<script>
(()=>{const frames='''+json.dumps(frames,ensure_ascii=False)+''';const c=['agent','alias','normalize'].map(x=>document.getElementById('trace-'+x));const update=()=>{const [a,b,n]=c.map(x=>+x.value);document.getElementById('trace-output').innerHTML=frames[a*4+b*2+n];};c.forEach(x=>x.addEventListener('change',update));document.getElementById('trace-reset').addEventListener('click',()=>{c.forEach((x,i)=>x.value=[0,1,0][i]);update();});})();
</script>
'''
    intro='''まず初期表示で操作列と最終状態が同じことを確かめる。採点器を「別名を正規化」に変えると、実行はそのままで点数が戻る。次にスクリプトを「別名になると書込みを省く」へ変える。この失敗は採点器を修正しても残る。最後に「いつも書込みを省く」を選ぶと、差が0でも成功しないことが分かる。

'''
    end='''

### このLabの採点規則は、意図的に小さく作った

最終在庫が5ならH=1、そうでなければH=0とする。元の3種類のツール名を何種類使ったかの比率をCと置き、S = H(0.5 + 0.5C)で採点する。正しい実行でも別名にするとC=0になり、1.00が0.50へ落ちる。採点時だけ別名を戻せばC=1となる。

これは論文Appendix Aの複合採点式ではない。論文の0.250という報告値に合わせた実装でもない。書込みを省いた行動失敗ではH=0なので、採点器の名前修正だけで救済されないようにした自作例だ。意味を保った名前変更なら、名前を除いた操作列と最終状態のhashが一致することをテストする。hash一致はこの決定的な記録の一致を示すだけで、未知の環境での意味同等性を自動証明しない。

乱数もモデルAPIも使わない。再実行ノイズはこの例では発生せず、実際のLLMエージェントで同じ程度に安定するという主張はしない。
'''
    (ROOT/'experiment.md').write_text(intro+widget+end)


class Checks(unittest.TestCase):
    def test_alias_invariance_and_rescore(self):
        c=case('careful',True,True)
        self.assertTrue(c['behavior_same']);self.assertTrue(c['state_same'])
        self.assertEqual(c['raw_score'],.5);self.assertEqual(c['rescored'],1)
    def test_genuine_failure_remains(self):
        c=case('sensitive',True,True)
        self.assertFalse(c['behavior_same']);self.assertFalse(c['state_same'])
        self.assertEqual(c['rescored'],0)
    def test_consistent_failure_is_not_success(self):
        c=case('weak',True,True)
        self.assertEqual(c['gap_after'],0);self.assertFalse(c['changed']['success'])
    def test_rescoring_does_not_mutate(self):
        r=rollout('careful',True);old=digest(r);score(r,True);self.assertEqual(old,digest(r))


if __name__=='__main__':
    if '--test' in sys.argv:unittest.main(argv=[sys.argv[0]])
    else:render();print('Generated results.json and experiment.md; no model calls.')
