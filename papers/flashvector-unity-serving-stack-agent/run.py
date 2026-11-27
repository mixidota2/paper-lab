"""架空の測定値で変更を採用するか判定する。実際の配信の測定はしない。"""
import json,math
from pathlib import Path
def decide(c,noise=.06,slo=250):
    # 出力、有限性、応答時間、全体の処理件数、測定の揺れを順に確認する。
    if not c['correct']:return 'reject: correctness'
    if not all(math.isfinite(c[k]) for k in ['local_ratio','stack_ratio','p99_ms']):return 'reject: non-finite'
    if c['p99_ms']>slo:return 'reject: latency SLO'
    if c['stack_ratio']<1:return 'reject: whole-stack regression'
    if min(c['local_ratio'],c['stack_ratio'])<=1+noise:return 'remeasure: noise floor'
    return 'accept'
def main():
    specs=[('一部だけ2倍速い',2,.98,220,True),('応答時間が上限を超える',1.3,1.2,270,True),('全体で3%改善',1.1,1.03,230,True),('出力が変わる',1.4,1.3,200,False),('すべての条件を満たす',1.3,1.2,230,True)]
    candidates=[]
    for name,local,stack,p99,correct in specs:
        c=dict(name=name,local_ratio=local,stack_ratio=stack,p99_ms=p99,correct=correct);c['decision']=decide(c);candidates.append(c)
    r=dict(note='Labはすべての測定値を説明用に用意しました。処理時間を測ったり、言語モデルや本番の配信要求を使ったりしていません。',verification=dict(mechanism='PARTIAL',performance='NOT TESTED',scaling='NOT TESTED',production_applicability='NOT TESTED'),slo_ms=250,noise_floor=.06,candidates=candidates)
    Path(__file__).with_name('results.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
