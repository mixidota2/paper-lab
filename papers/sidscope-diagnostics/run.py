"""Mapping diagnostics on real user-supplied JSON or a declared six-item fixture.
Usage: uv run run.py --mapping map.json --previous old.json --pairs pairs.json
map.json: {"item_id": [0,1,2], ...}; pairs.json: [["a","b",weight], ...].
This is an independent subset of SIDScope, not its official implementation.
"""
import argparse, hashlib, json, math
from collections import Counter, defaultdict
from pathlib import Path

def validate(mapping):
    if not mapping:raise ValueError('empty mapping')
    lengths={len(v) for v in mapping.values()}
    if len(lengths)!=1 or min(lengths)<1:raise ValueError('fixed nonzero SID depth required')
    if any(not isinstance(v,list) or any(not isinstance(x,int) or isinstance(x,bool) or x<0 for x in v) for v in mapping.values()):raise ValueError('SID levels must be nonnegative integers')

def diagnose(mapping,pairs=(),previous=None):
    validate(mapping); n=len(mapping); depth=len(next(iter(mapping.values())))
    leaves=Counter(tuple(s) for s in mapping.values())
    profiles=[]
    for k in range(1,depth+1):
        counts=Counter(tuple(s[:k]) for s in mapping.values()); total=sum(counts.values())
        entropy=-sum((v/total)*math.log2(v/total) for v in counts.values())
        weights=[(a,b,w) for a,b,w in pairs if a in mapping and b in mapping]
        denominator=sum(w for a,b,w in weights)
        aligned=sum(w for a,b,w in weights if mapping[a][:k]==mapping[b][:k])
        fanout=defaultdict(set)
        for s in mapping.values():fanout[tuple(s[:k-1])].add(s[k-1])
        profiles.append({'depth':k,'active_prefixes':len(counts),'entropy_bits':round(entropy,6),'collision_item_rate':sum(v for v in counts.values() if v>1)/n,'weighted_prefix_alignment':aligned/denominator if denominator else None,'max_fanout':max(map(len,fanout.values()))})
    common=set(mapping)&set(previous or {})
    return {'items':n,'unique_leaves':len(leaves),'collision_item_rate':sum(v for v in leaves.values() if v>1)/n,'duplicate_SID_rate':1-len(leaves)/n,'profiles':profiles,'common_items':len(common),'code_churn':sum(mapping[i]!=previous[i] for i in common)/len(common) if common else None,'D4':'NOT TESTED: popularity input omitted','generator_handoff':'NOT TESTED: mapping alone cannot validate checkpoint reuse'}

def trace(mapping,codes,target):
    reverse=defaultdict(list)
    for i,c in mapping.items():reverse[tuple(c)].append(i)
    return {'valid_paths':sum(bool(reverse[tuple(c)]) for c in codes),'ambiguous_paths':sum(len(reverse[tuple(c)])>1 for c in codes),'target_path_survives':mapping[target] in codes,'unique_item_hit':any(reverse[tuple(c)]==[target] for c in codes)}

# The 12-item OFFICIAL_EXAMPLE in run.py is from SIDScope v1.0.1 examples/reviewer_quickstart_data/sid_codes.csv.
#
# MIT License
#
# Copyright (c) 2026 SIDInspector authors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
OFFICIAL_EXAMPLE = {'101': [4, 10, 1], '102': [4, 10, 2], '103': [4, 11, 1], '104': [4, 11, 1], '105': [7, 20, 1], '106': [7, 20, 2], '107': [7, 21, 1], '108': [9, 30, 1], '109': [9, 30, 2], '110': [9, 31, 1], '111': [9, 31, 2], '112': [9, 31, 3]}


def compute():
    old={'a':[0,0],'b':[0,0],'c':[0,1],'d':[1,0],'e':[1,1],'f':[2,0]}
    fixed={**old,'b':[0,2]}; pairs=[('a','c',3),('d','e',2),('a','f',1)]
    return {'note':'既定入力は説明用6 item。--mappingで実際のJSONを診断できる。D3は渡された重み付き辺で計算し、公式の近傍抽出は省略。','verification':{'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'},'experiments':[{'name':'衝突修復とcheckpoint引き継ぎは別','metrics':{'old':diagnose(old,pairs),'repaired':diagnose(fixed,pairs,old)}}],'official_quickstart_mapping':diagnose(OFFICIAL_EXAMPLE),'trace_before':trace(old,[[0,0],[1,0]],'a'),'trace_after':trace(fixed,[[0,0],[1,0]],'a')}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--mapping',type=Path);p.add_argument('--previous',type=Path);p.add_argument('--pairs',type=Path);p.add_argument('--out',type=Path,default=Path(__file__).with_name('results.json'));a=p.parse_args()
    if a.mapping:
        mapping=json.loads(a.mapping.read_text()); previous=json.loads(a.previous.read_text()) if a.previous else None;pairs=json.loads(a.pairs.read_text()) if a.pairs else []
        result={'input_sha256':hashlib.sha256(a.mapping.read_bytes()).hexdigest(),'diagnostics':diagnose(mapping,pairs,previous)}
    else:result=compute()
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))
