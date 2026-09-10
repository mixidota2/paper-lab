"""Known dependencies and explicit guards; no LLM diagnosis or learned detector."""
import json
from pathlib import Path


def localize(parents, symptom, anomalous):
    ancestors = set()
    def visit(node):
        if node in ancestors:
            return
        ancestors.add(node)
        for p in parents.get(node, []):
            visit(p)
    visit(symptom)
    possible = ancestors & set(anomalous)
    return min(possible) if possible else None


def guard(step, last, evidence, unresolved, complete=False, after_write=False, loop=False):
    return bool(evidence and unresolved and not complete and step-last >= 3
                and (not after_write or loop))


def adherence(intervene=False, decay=.82):
    # Confidence is a synthetic state, not the paper's first-violation survival statistic.
    confidence, last = 1., -99
    trace, fires = [], []
    for step in range(1,16):
        confidence *= decay
        if intervene and confidence < .55 and guard(step,last,True,True):
            confidence, last = 1., step
            fires.append(step)
        trace.append(confidence)
    return {'mean_guidance_state': sum(trace)/len(trace), 'fires': fires, 'trace': trace}


def experiment():
    # TU1 wrong account -> TU3 transfer -> TU5 failure. TU2,4 unrelated read errors.
    parents = {0: [], 1: [0], 2: [0], 3: [1], 4: [2], 5: [3]}
    anomalies = [1,2,3,4,5]
    counts = {1:1,2:2,3:3,4:5,5:4}
    return {'kind': 'synthetic mechanism illustration', 'seed': 'deterministic',
            'localization': {'true_root': 1, 'recency': max(anomalies),
                             'frequency': max(counts, key=counts.get),
                             'dependency': localize(parents,5,anomalies),
                             'missing_edge_counterexample': localize({**parents,3:[]},5,anomalies)},
            'adherence_proxy': {'one_shot': adherence(), 'checkpoints': adherence(True)},
            'guards': {'no_evidence': guard(10,0,False,True), 'cooldown': guard(2,1,True,True),
                       'complete': guard(10,0,True,True,complete=True),
                       'after_write': guard(10,0,True,True,after_write=True),
                       'loop_after_write': guard(10,0,True,True,after_write=True,loop=True)},
            'not_tested': ['HGT', 'Isolation Forest', 'LLM analyst/verifier', 'tau-bench repair', 'production interventions']}

if __name__ == '__main__':
    result = experiment()
    Path(__file__).with_name('results.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
