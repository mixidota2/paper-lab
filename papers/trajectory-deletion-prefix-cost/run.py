"""順序を付けた記号を使い、再利用できる入力と通常料金の入力を数える作例。"""
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def lcp(previous, current):
    for i, (a, b) in enumerate(zip(previous, current)):
        if a != b:
            return i
    return min(len(previous), len(current))


def ledger(prompts, outputs, cache_price=.1):
    if len(prompts) != len(outputs) or not 0 <= cache_price <= 1:
        raise ValueError('Invalid trace or price')
    rows = []
    previous = []
    for prompt, output in zip(prompts, outputs):
        if output < 0:
            raise ValueError('Negative output')
        c = lcp(previous, prompt)
        # 色分けには、各入力で記号が重複しないという作例の前提を使う。
        # 一致する先頭の長さと費用は、記号を順番に比較して計算する。
        old = set(previous[c:])
        rebilled = sum(token in old for token in prompt[c:])
        new = len(prompt) - c - rebilled
        rows.append(dict(prompt=prompt, n=len(prompt), c=c, new=new,
                         rebilled=rebilled, output=output,
                         first_changed=c if c < min(len(previous), len(prompt)) else None,
                         cost=(len(prompt)-c) + cache_price*c + 5*output))
        previous = prompt
    return dict(rows=rows, total=sum(r['cost'] for r in rows),
                tokens=sum(r['n'] for r in rows))


def scenario(discount=.9, position=1, timing=4, retrieval=0):
    """通常の呼び出しは6回で、指定したターンから2記号を一度だけ消す。
    position が3なら削除しない。対象がまだなければ、入力に現れるまで待つ。
    retrieval を指定したときの追加呼び出しは仮定で、モデルの挙動を予測しない。
    """
    if discount not in (0, .5, .9, 1) or position not in range(4) or timing not in (2,4,6) or retrieval not in (0,2,4):
        raise ValueError('Unsupported teaching condition')
    turns = [[f'T{t}.{j}' for j in range(1,5)] for t in range(1,7)]
    prompts, changed, out, changed_out = [], [], [], []
    history = ['S1','S2']
    active = None if position == 3 else max(timing, position+2)
    removed = set(turns[position][1:3]) if position < 3 else set()
    changed_history = history.copy()
    for call in range(1,7):
        baseline = history.copy()
        prompts.append(baseline);out.append(2)
        if active == call:
            changed_history = [t for t in changed_history if t not in removed]
        current = changed_history.copy()
        changed.append(current);changed_out.append(2)
        if active == call and retrieval:
            # 追加の読み取りでは、R の記号を入力に足し、出力を1記号数える。
            changed_history += [f'R{j}' for j in range(retrieval)]
            changed.append(changed_history.copy());changed_out.append(1)
        history += turns[call-1]
        changed_history += turns[call-1]
    assert all(len(prompt) == len(set(prompt)) for prompt in prompts + changed), 'Teaching IDs must be unique per prompt'
    return dict(args=dict(discount=discount,position=position,timing=timing,retrieval=retrieval),
                rewrite_call=active, removed=sorted(removed),
                baseline=ledger(prompts,out,1-discount), changed=ledger(changed,changed_out,1-discount))


def results():
    return {'note':'同じ記号列を使い、履歴を消した場合と残した場合の費用を比べる。実モデルの動作や著者のログ、実際の請求は再現していない。',
            'reported':{'source':'https://arxiv.org/html/2610.35496v1',
                        'locator':'§III, Table II, §VI-A',
                        'runs':9400,'tasks':100,'agents':2,'delayed_evaluations':42,
                        'flat_below_one':26,'flat_significantly_cheaper':6,
                        'cached_below_one':0,'cached_significantly_more_expensive':26},
            'synthetic':[scenario(*a) for a in itertools.product((0,.5,.9,1),range(4),(2,4,6),(0,2,4))]}


if __name__ == '__main__':
    (ROOT/'results.json').write_text(json.dumps(results(),ensure_ascii=False,separators=(',',':'))+'\n')
    import runpy
    runpy.run_path(str(ROOT/'render.py'))
    print('作例の144条件を生成しました。実モデル、外部API、著者コードは使っていません。')
