"""商品に語を追加したときの全語一致を人工データで調べる。SAM-D2Qは学習しない。"""
import json
from pathlib import Path

ITEMS = {'a': 'summer shirt', 'b': 'evening dress', 'c': 'travel bag'}
# 追加候補と、商品に合うかどうかを手で決めた。モデルの出力ではない。
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
    result = dict(experiment='人工データで、商品に語を追加したときの全語一致を調べる。', verification=dict(mechanism='PARTIAL',performance='NOT TESTED',scaling='NOT TESTED',production_applicability='NOT TESTED'), modes=modes, limitation='Labは追加候補と採否を手で決めた。画像モデル、商業価値の推定、GRPO、本番トラフィックは使っていない。')
    result['explorer'] = dict(default=0, label='比較条件', unit='番', metric='3種類の検索語で候補に入った件数', frames=[dict(value=i, note=label + '。追加候補と、その候補を採用するかどうかはLabが手で決めた。', bars=[dict(label='関連商品', value=modes[mode]['true_positive']), dict(label='誤取得', value=modes[mode]['false_positive'])]) for i, (mode, label) in enumerate([('title', 'タイトルのみ'), ('all', '追加候補をすべて使う'), ('gated', '商品に合う候補だけを追加')])])
    Path(__file__).with_name('results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(modes,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
