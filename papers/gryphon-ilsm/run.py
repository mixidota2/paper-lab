"""人工の曲をCPUで再採点する。ILSMの学習や本番での測定は行わない。"""
import json
from math import prod
from pathlib import Path


def experiment(beam_width=3, reverse_ties=False):
    # 3個のSIDについて、各トークンの条件付き確率を固定する。
    paths = {'11': (.6, .8), '12': (.6, .2), '21': (.4, .9)}
    items = [('A', '11', .1), ('B', '11', .9), ('C', '21', .2), ('D', '12', .8)]
    relevant = {'B', 'D'}  # 人工の正解曲。論文のデータではない。
    sids = sorted(paths, key=lambda sid: -prod(paths[sid]))[:beam_width]
    pool = [x for x in items if x[1] in sids]
    # 同点の曲は名前順とその逆順を比べる。
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
    out = {'note': 'Labは人工の曲を手で決めた点で採点し直した。ILSMの学習、論文の性能、本番への適用は検証していない。',
           'experiments': [{'name': '同じ候補を比べる（3個のSIDをすべて使用）', 'metrics': {
               'Recall@2': {'beam': cases[4]['beam_recall@2'], 'item score': cases[4]['item_recall@2']}}}], 'cases': cases}
    Path(__file__).with_name('results.json').write_text(json.dumps(out, ensure_ascii=False, indent=2)+'\n')
    return out

if __name__ == '__main__':
    main()
