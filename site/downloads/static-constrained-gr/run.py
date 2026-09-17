"""Reference CSR trie, exhaustively compared with a dictionary trie on tiny IDs."""
import json
import itertools
from pathlib import Path

CATALOG=[(0,0,0),(0,0,1),(0,1,0),(1,0,0),(1,1,1)]
FRESH=[(0,0,1),(1,1,1)]

def build(paths):
    nodes=[{}]
    for path in paths:
        state=0
        for token in path:
            if token not in nodes[state]:
                nodes[state][token]=len(nodes); nodes.append({})
            state=nodes[state][token]
    ptr=[0]; tokens=[]; destinations=[]
    for row in nodes:
        for token,dst in sorted(row.items()):tokens.append(token); destinations.append(dst)
        ptr.append(len(tokens))
    return nodes,ptr,tokens,destinations

def walk(path, csr):
    _,ptr,tokens,destinations=csr; state=0
    for token in path:
        matches=[j for j in range(ptr[state],ptr[state+1]) if tokens[j]==token]
        if not matches:return False
        state=destinations[matches[0]]
    return True

def compute():
    csr=build(FRESH); nodes,ptr,tokens,dst=csr
    checked=0
    for length in range(4):
        for path in itertools.product(range(2),repeat=length):
            expected=any(p[:length]==path for p in FRESH)
            assert walk(path,csr)==expected;checked+=1
    # Candidate scores fixed for both controls. Filtering after top-1 loses the fresh path.
    scores={p:5-i for i,p in enumerate(CATALOG)}
    unconstrained=sorted(CATALOG,key=scores.get,reverse=True)[:1]
    post=[p for p in unconstrained if p in FRESH]
    constrained=sorted(FRESH,key=scores.get,reverse=True)[:1]
    return {"note":"2値・3段の人工IDをCPUで全列挙。STATICのTPU kernelや遅延を再現する実験ではない。",
      "experiments":[{"name":"有効SIDと鮮度制約を分ける", "metrics":{"生成後filterの件数":len(post),"制約内top-1の件数":len(constrained),"照合したprefix数":checked}}],
      "csr":{"indptr":ptr,"tokens":tokens,"next_state":dst},"post_filter":post,"constrained":constrained,
      "checks":{"csr_prefix_equivalence":"CONFIRMED","fresh_subset_compliance":"CONFIRMED","accelerator_speed":"NOT TESTED"}}


def main():
    result = compute()
    Path(__file__).with_name("results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
