"""在庫を修正する架空の課題で、操作の違いと採点による点差を調べる。
著者のコードやモデルAPIは使わない。uv run run.py --test で検査する。
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
    """在庫を8から5へ直し、確認して報告する。スクリプトの動作はあらかじめ決める。"""
    names=ALIASES if alias else NAMES
    state={'stock':8}
    # sensitiveはツールが別名になると在庫を書き換えない。
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
    """元のツール名を何種類使ったかを数える。在庫が違えば点数は0。
    論文付録Aの式は使わず、採点時に名前を読み替えても記録は変えない。
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
    interpretation=('操作と最終状態は同じです。採点時に別名を元に戻すと点数が戻るため、名前の違いが減点の原因だと分かります。' if c['agent']=='careful' and c['alias'] else 'スクリプトが必要な書き込みを省いたので、最終在庫は誤ったままです。採点時に名前を戻しても在庫は直りません。' if not after['success'] else 'スクリプトは必要な操作を行い、採点器は使われた名前も認識しました。')
    return f'''<h3>1. 実行を比較する</h3><div class="trace-columns"><div><strong>元の実行</strong>{steps(before)}</div><div><strong>比較する実行</strong>{steps(after)}</div></div>
<h3>2. 操作と状態を確かめる</h3><p>正規の操作列：<strong>{'同じ' if c['behavior_same'] else '違う'}</strong> ／ 最終状態：<strong>{'同じ' if c['state_same'] else '違う'}</strong> ／比較側の在庫：{after['state']['stock']}（正解5）</p>
<details><summary>名前をそろえた操作列と最終状態のSHA-256を見る</summary><p>元の操作列</p><code>{before['canonical_hash']}</code><p>比較側の操作列</p><code>{after['canonical_hash']}</code><p>元の状態</p><code>{before['state_hash']}</code><p>比較側の状態</p><code>{after['state_hash']}</code></details>
<h3>3. 同じ記録を採点し直す</h3>{bar('元の実行の点数',c['original_score'],'#526f9d')}{bar('比較側・修正前の点数',c['raw_score'],'#ae5327')}{bar('比較側・現在の採点方式',c['rescored'],'#007868')}
<p>元−比較の差：修正前 {c['raw_gap']:.2f} → 現在 {c['gap_after']:.2f}。採点だけを切り替え、実行のやり直しはない。</p><p><strong>{interpretation}</strong></p>'''


def render():
    cases=[case(a,b,c) for a in ['careful','sensitive','weak'] for b in [False,True] for c in [False,True]]
    reported={'source':'https://arxiv.org/html/2610.11678v1#A5.T6',
              'main_unseen_tasks':88,'main_repeats':3,'positive_control_tasks':158,'positive_control_repeats':2,
              'equivalent_uncorrected':'7/8','equivalent_bonferroni':'6/8',
              'qwen_format':{'delta':-.059,'ci95':[-.123,.008],'ci90':[-.114,-.004],
                             'excess_flips_pp':9.3,'excess_flips_ci95_pp':[2.7,16.1],'label':'inconclusive'}}
    result={'note':'reportedには著者の報告値を、syntheticにはLabが作った在庫の記録を入れています。Labは論文の値を再計算していません。',
            'reported':reported,'synthetic':cases,'verification':{'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'}}
    (ROOT/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    frames=[frame(c) for c in cases]
    widget='''<style>
.trace-widget{background:#f7faf9;border:1px solid #9eaeb8;border-radius:16px;padding:clamp(12px,3vw,24px);color:#182c35;max-width:100%}.trace-widget label{display:block;margin:14px 0;font-weight:650}.trace-widget select{display:block;width:100%;padding:10px;font:inherit;background:white;color:#182c35;border:1px solid #6c818c;border-radius:6px}.trace-widget code{overflow-wrap:anywhere;word-break:break-all}.trace-columns{display:grid;grid-template-columns:1fr 1fr;gap:16px}.trace-widget output{display:block}.trace-widget li{font-size:.9rem}@media(max-width:600px){.trace-columns{grid-template-columns:1fr}}
</style>
<div class="trace-widget" id="trace-toy"><p><strong>架空の在庫を8から5に直し、確認して報告する</strong></p>
<label>在庫を操作するスクリプト<select id="trace-agent"><option value="0">名前が変わっても在庫を直す</option><option value="1">別名のときは書き込みを省く</option><option value="2">いつも書き込みを省く</option></select></label>
<label>ツールの名前<select id="trace-alias"><option value="0">元の名前</option><option value="1" selected>同じ操作を別名で呼ぶ</option></select></label>
<label>採点器が別名をどう扱うか<select id="trace-normalize"><option value="0">元の名前だけを数える</option><option value="1">別名を元に戻してから数える</option></select></label>
<button type="button" id="trace-reset">最初の条件に戻す</button>
<output id="trace-output" aria-live="polite">'''+frames[2]+'''</output>
<noscript>JavaScriptを無効にすると、条件を切り替えられません。最初の表示では同じ操作でも、名前が違うと減点されます。</noscript></div>
<script>
(()=>{const frames='''+json.dumps(frames,ensure_ascii=False)+''';const c=['agent','alias','normalize'].map(x=>document.getElementById('trace-'+x));const update=()=>{const [a,b,n]=c.map(x=>+x.value);document.getElementById('trace-output').innerHTML=frames[a*4+b*2+n];};c.forEach(x=>x.addEventListener('change',update));document.getElementById('trace-reset').addEventListener('click',()=>{c.forEach((x,i)=>x.value=[0,1,0][i]);update();});})();
</script>
'''
    intro='''最初の表示では、どちらの実行でも同じ操作をして在庫を5に直します。採点器を「別名を元に戻してから数える」に変えると、記録は同じままで点数が戻ります。次に「別名のときは書き込みを省く」を選ぶと、採点を変えても在庫の誤りが残ります。「いつも書き込みを省く」では、点差がなくても両方が失敗します。

'''
    end='''

### 教材の採点規則

最終在庫が5ならH=1、それ以外ならH=0とします。元の3種類の名前のうち、何種類を呼んだかを3で割った値がCです。同じ名前を何回呼んでも1種類です。点数は S = H(0.5 + 0.5C) とします。必要な操作をしても名前がすべて別名ならC=0なので、1.00が0.50に下がります。採点時にだけ元の名前に戻せばC=1に戻ります。

この式は論文付録Aの採点式とは違い、著者が報告した0.250を再現するものでもありません。書き込みを省き、在庫が直らなければH=0です。名前をそろえた操作列と最終状態のハッシュは、それぞれ保存した内容が同じかを確かめるために使います。別の環境でも操作の意味が同じとは限りません。

この教材は乱数もモデルAPIも使わず、同じ条件なら同じ結果を出します。実際の言語モデルを動かし直したときの合否のばらつきは扱いません。
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
    else:render();print('モデルを呼ばずに results.json と experiment.md を作成しました。')
