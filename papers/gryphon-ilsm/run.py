"""CPU-only synthetic scoring example; no trained ILSM or production measurement."""
import json
from math import prod
from pathlib import Path


def experiment(beam_width=3, reverse_ties=False):
    # Conditional token probabilities for three distinct SID paths.
    paths = {'11': (.6, .8), '12': (.6, .2), '21': (.4, .9)}
    items = [('A', '11', .1), ('B', '11', .9), ('C', '21', .2), ('D', '12', .8)]
    relevant = {'B', 'D'}  # Synthetic held-out labels, not paper data.
    sids = sorted(paths, key=lambda sid: -prod(paths[sid]))[:beam_width]
    pool = [x for x in items if x[1] in sids]
    # Explicit tie policy; repeat with the reverse to expose arbitrary collision order.
    beam = sorted(pool, key=lambda x: (-prod(paths[x[1]]), -ord(x[0]) if reverse_ties else ord(x[0])))
    scored = sorted(pool, key=lambda x: -x[2])
    recall = lambda xs: len({x[0] for x in xs[:2]} & relevant) / len(relevant)
    return {'beam_width': beam_width, 'reverse_ties': reverse_ties,
            'pool': [x[0] for x in pool], 'beam_order': [x[0] for x in beam],
            'item_order': [x[0] for x in scored], 'beam_recall@2': recall(beam),
            'item_recall@2': recall(scored), 'reachable_recall_ceiling': len(set(x[0] for x in pool) & relevant)/2,
            'item_scores': {x[0]: x[2] for x in pool},
            'sid_likelihoods': {sid: prod(paths[sid]) for sid in sids}}


def main():
    cases = [experiment(k, tie) for k in (1, 2, 3) for tie in (False, True)]
    out = {'note': '合成例。手で設定した item score による再順位付け。ILSM 学習・論文性能・本番適用は未検証。',
           'experiments': [{'name': '同じ候補集合で比較（全3 SID）', 'metrics': {
               'Recall@2': {'beam': cases[4]['beam_recall@2'], 'item score': cases[4]['item_recall@2']}}}], 'cases': cases}
    Path(__file__).with_name('results.json').write_text(json.dumps(out, ensure_ascii=False, indent=2)+'\n')
    return out

if __name__ == '__main__':
    main()
