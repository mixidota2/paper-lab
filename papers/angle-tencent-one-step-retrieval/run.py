"""Finite toy index: shared identifiers, validity pruning, and new-ad insertion.
No neural model is trained. Scores and labels are fixed synthetic inputs.
"""
import json
from pathlib import Path

ADS = [
    {'id': 'A', 'intent': 'survival game', 'abstract': 'Winter', 'valid': False},
    {'id': 'B', 'intent': 'survival game', 'abstract': 'Forest', 'valid': True},
    {'id': 'C', 'intent': 'survival game', 'abstract': 'Forest', 'valid': True},
    {'id': 'D', 'intent': 'mobile game', 'abstract': 'Winter', 'valid': True},
    {'id': 'E', 'intent': 'shopping', 'abstract': 'Boots', 'valid': False},
]
SCORES = {('survival game', 'Winter'): .42,
          ('survival game', 'Forest'): .28,
          ('mobile game', 'Winter'): .20,
          ('shopping', 'Boots'): .10}


def index_ads(ads):
    index = {}
    for ad in ads:
        index.setdefault((ad['intent'], ad['abstract']), []).append(ad['id'])
    return index


def retrieve(ads, width, prune_before):
    index = index_ads(ads)
    valid = {ad['id'] for ad in ads if ad['valid']}
    candidates = sorted(index, key=lambda pair: (-SCORES[pair], pair))
    if prune_before:
        candidates = [p for p in candidates if valid.intersection(index[p])]
    selected = candidates[:width]
    resolved = sorted({a for p in selected for a in index[p] if a in valid})
    return {'selected_pairs': [' / '.join(p) for p in selected],
            'valid_ads': resolved, 'valid_ad_count': len(resolved)}


def main():
    frames = []
    for width in (1, 2, 3):
        for prune in (False, True):
            frames.append({'width': width, 'prune_before': prune,
                           **retrieve(ADS, width, prune)})
    updated = ADS + [{'id': 'F', 'intent': 'survival game', 'abstract': 'Forest', 'valid': True}]
    before = retrieve(ADS, 1, True)
    after = retrieve(updated, 1, True)
    assert retrieve(ADS, 1, False)['valid_ad_count'] == 0
    assert before['valid_ads'] == ['B', 'C']
    assert after['valid_ads'] == ['B', 'C', 'F']
    assert all(a in {'B', 'C', 'D'} for f in frames for a in f['valid_ads'])
    results = {'experiment': 'synthetic finite pair-level selection',
               'verification': {'mechanism': 'PARTIAL', 'performance': 'NOT TESTED',
                                'scaling': 'NOT TESTED', 'production_applicability': 'NOT TESTED'},
               'note': 'Fixed scores; pair-level top-k only. No token trie, LLM, relevance head, DPO or production data.',
               'ads': ADS, 'frames': frames,
               'index_update': {'before': before, 'after': after, 'generation_scores_changed': False},
               'checks_passed': 4}
    Path(__file__).with_name('results.json').write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'checks_passed': 4, 'width_1_post_filter': 0, 'width_1_pre_filter': 2,
                      'after_inserting_new_ad': 3}))


if __name__ == '__main__':
    main()
