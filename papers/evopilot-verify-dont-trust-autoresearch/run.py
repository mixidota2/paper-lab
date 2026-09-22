"""Pair-level evidence admission and a broken output-depth evaluator."""
import json,hashlib
from pathlib import Path


def evaluate(ranks,declared_k,broken=False,pool=3000):
    effective=pool if broken else declared_k
    return {'declared_k':declared_k,'effective_k':effective,'hit_rate':sum(r<=effective for r in ranks)/len(ranks)}


def verify(control,treatment,allowed):
    reasons=[]
    required=['base','data','evaluator','effective_k','head','status','artifact']
    if any(k not in arm for arm in [control,treatment] for k in required):return ['missing_evidence']
    if any(a['status']!='success' for a in [control,treatment]):reasons.append('incomplete')
    for key in ['base','data','evaluator','effective_k','head']:
        if control[key]!=treatment[key] and key not in allowed:reasons.append('undeclared_'+key)
    if any(control[k]==treatment[k] for k in allowed):reasons.append('no_op')
    return reasons


def main():
    base={'base':'checkpoint-1','data':'snapshot-1','evaluator':'fixed-v2','effective_k':600,'head':False,'status':'success','artifact':'sha-control'}
    good={**base,'head':True,'artifact':'sha-treatment'}
    cases={'valid':good,'depth_mismatch':{**good,'effective_k':3000},'eval_drift':{**good,'evaluator':'v3'},'data_drift':{**good,'data':'snapshot-2'},'no_op':base,'missing':{k:v for k,v in good.items() if k!='artifact'}}
    decisions={k:verify(base,v,{'head'}) for k,v in cases.items()}
    assert decisions['valid']==[] and all(v for k,v in decisions.items() if k!='valid')
    ranks=list(range(1,3001,30));traces={}
    for mode in ['broken','fixed']:
        traces[mode]=[evaluate(ranks,k,mode=='broken') for k in [1,600]]
    assert traces['broken'][0]['hit_rate']==traces['broken'][1]['hit_rate']
    assert traces['fixed'][0]['hit_rate']<traces['fixed'][1]['hit_rate']
    # Canonical durable record ties verdict to actual pair contents.
    record={'control':base,'treatment':good,'allowed_diff':['head'],'reasons':decisions['valid'],'human_review':'pending'}
    record['record_sha256']=hashlib.sha256(json.dumps(record,sort_keys=True).encode()).hexdigest()
    out={'note':'人工artifactのpair検証。論文の−22 pp、+3.20 pp、オンラインGSRRは入力していない。',
      'scope':{'mutation_rejection':'CONFIRMED','mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'},
      'decisions':decisions,'extreme_k_probe':traces,'durable_record':record,
      'experiments':[{'name':'完了した2 runでも比較を拒否する','metrics':{'clean_admitted_mechanically':{'count':1},'faults_rejected':{'count':5},'human_admission':{'status':'pending'}}}]}
    Path(__file__).with_name('results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');return out
if __name__=='__main__':main()
