"""Acceptance-rule demonstration; all candidate measurements are synthetic."""
import json,math
from pathlib import Path
def decide(c,noise=.06,slo=250):
    if not c['correct']:return 'reject: correctness'
    if not all(math.isfinite(c[k]) for k in ['local_ratio','stack_ratio','p99_ms']):return 'reject: non-finite'
    if c['p99_ms']>slo:return 'reject: latency SLO'
    if c['stack_ratio']<1:return 'reject: whole-stack regression'
    if min(c['local_ratio'],c['stack_ratio'])<=1+noise:return 'remeasure: noise floor'
    return 'accept'
def main():
    specs=[('局所だけ2倍',2,.98,220,True),('SLO超過',1.3,1.2,270,True),('3%改善',1.1,1.03,230,True),('出力が変化',1.4,1.3,200,False),('全gate通過',1.3,1.2,230,True)]
    candidates=[]
    for name,local,stack,p99,correct in specs:
        c=dict(name=name,local_ratio=local,stack_ratio=stack,p99_ms=p99,correct=correct);c['decision']=decide(c);candidates.append(c)
    r=dict(note='全測定値は説明用の人工fixture。profiling・agent・本番replayは未実行。',verification=dict(mechanism='PARTIAL',performance='NOT TESTED',scaling='NOT TESTED',production_applicability='NOT TESTED'),slo_ms=250,noise_floor=.06,candidates=candidates)
    Path(__file__).with_name('results.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
