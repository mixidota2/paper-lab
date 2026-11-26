"""要求を一つずつ処理する合成例。処理の途中で割り込まず、時間は仮定した秒数です。"""
import json, statistics
from pathlib import Path


def schedule(policy,guard=8):
    # 開始時のキャッシュはA。時刻0にB、C、A0が届き、残るAは2秒ごとに来る。
    jobs=[{'id':'B0','context':'B','arrival':0},{'id':'C0','context':'C','arrival':0}]+[{'id':f'A{i}','context':'A','arrival':i*2} for i in range(16)]
    pending=list(jobs)
    cache='A'
    now=0
    trace=[]
    while pending:
        ready=[j for j in pending if j['arrival']<=now]
        if not ready:
            now=min(j['arrival'] for j in pending)
            continue
        oldest=min(ready,key=lambda j:(j['arrival'],jobs.index(j)))
        guarded=policy=='cache_guard' and now-oldest['arrival']>=guard
        warm=[j for j in ready if j['context']==cache]
        j=oldest if policy=='fcfs' or guarded or not warm else warm[0]
        hit=j['context']==cache
        prefill=1 if hit else 6
        first=now+prefill
        trace.append(dict(id=j['id'],context=j['context'],start=now,first=first,end=first+1,ttft=first-j['arrival'],wait=now-j['arrival'],hit=hit,guarded=guarded,cache_before=cache,evicted=None if hit else cache))
        now=first+1
        cache=j['context']
        pending.remove(j)
    assert len({t['id'] for t in trace})==len(jobs)
    assert all(t['start']>=0 for t in trace)
    return {'mean_ttft':statistics.mean(t['ttft'] for t in trace),'max_ttft':max(t['ttft'] for t in trace),'batch':now,'hits':sum(t['hit'] for t in trace),'trace':trace}


PAPER = {'source': 'Table 3–5, v1', 'scbench': [['FCFS', 63.1, 74.2, 79, 481, 19.2], ['Cache', 4.6, 75.8, 93.9, 224, 87.6], ['Guard-40', 28.3, 51.1, 65, 299, 66.1], ['Guard-60', 4.5, 64, 80.4, 230, 84.7]], 'mooncake_100': [['FCFS', 163.9, 122.7], ['Cache', 86.8, 128.3], ['Session+Cache+Guard', 161.7, 108.9]]}


def main():
    cases={p:schedule(p) for p in ['fcfs','cache','cache_guard']}
    # 待機保護は古い要求を次に選ぶ規則で、最初のトークンまでの締切ではない。
    cold=lambda c:max(t['ttft'] for t in c['trace'] if t['context']!='A')
    assert cold(cases['cache_guard'])<cold(cases['cache'])
    assert cases['cache']['mean_ttft']<cases['fcfs']['mean_ttft']
    result={'lab_kind':'hear08','note':'合成例では一度に一つの要求を処理し、文脈一つ分のキャッシュを保存します。待機保護は、次に処理する要求を選ぶときの規則で、TTFTの上限ではありません。','cases':cases,'experiments':[{'name':p,'metrics':{k:v for k,v in c.items() if k!='trace'}} for p,c in cases.items()]}
    result['paper'] = PAPER
    (Path(__file__).parent/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(result['experiments'])

if __name__=='__main__': main()
