"""Hand-authored expansion candidates demonstrate Boolean retrieval, not SAM training."""
import json
from pathlib import Path

ITEMS = {'a': 'summer shirt', 'b': 'evening dress', 'c': 'travel bag'}
# (candidate query, valid relevance gate). Labels are illustrative, not model outputs.
CANDIDATES = {'a': [('red short sleeve shirt', True), ('leather bag', False)],
              'b': [('floral dress', True)], 'c': [('leather bag', True)]}
QUERIES = {'red shirt': {'a'}, 'floral dress': {'b'}, 'leather bag': {'c'}}


def retrieve(index, query):
    terms = set(query.split())
    return {item for item, tokens in index.items() if terms <= tokens}


def evaluate(mode):
    index = {item: set(title.split()) for item, title in ITEMS.items()}
    for item, candidates in CANDIDATES.items():
        for query, valid in candidates:
            if mode == 'all' or mode == 'gated' and valid:
                index[item].update(query.split())
    trace = []
    for query, relevant in QUERIES.items():
        found = retrieve(index, query)
        trace.append(dict(query=query, retrieved=sorted(found), relevant=sorted(relevant), true_positive=len(found & relevant), false_positive=len(found-relevant)))
    return dict(new_tokens=sum(len(tokens-set(ITEMS[item].split())) for item,tokens in index.items()), true_positive=sum(row['true_positive'] for row in trace), false_positive=sum(row['false_positive'] for row in trace), trace=trace)


def main():
    modes = {mode: evaluate(mode) for mode in ['title', 'all', 'gated']}
    assert [modes[m]['true_positive'] for m in modes] == [0,3,3]
    assert [modes[m]['false_positive'] for m in modes] == [0,1,0]
    assert [modes[m]['new_tokens'] for m in modes] == [0,7,5]
    result = dict(experiment='synthetic Boolean document expansion', verification=dict(mechanism='PARTIAL',performance='NOT TESTED',scaling='NOT TESTED',production_applicability='NOT TESTED'), modes=modes, limitation='Candidates and gates are hand-authored. No image model, business-reward estimator, GRPO, or production traffic.')
    result['explorer'] = dict(default=0, label='索引へ入れる展開語', unit='件', metric='3クエリの取得結果', frames=[dict(value=i, note=label + '。候補とgateは手作りの固定値。', bars=[dict(label='関連商品', value=modes[mode]['true_positive']), dict(label='誤取得', value=modes[mode]['false_positive'])]) for i, (mode, label) in enumerate([('title', 'タイトルのみ'), ('all', '候補を無条件で追加'), ('gated', '意味gateを通した候補だけ追加')])])
    Path(__file__).with_name('results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(modes,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
