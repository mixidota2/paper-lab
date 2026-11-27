"""同じ四つの架空の実装を、範囲の違う検査で比べます。実モデルや実サーバーは使いません。"""
import json
from pathlib import Path


class Service:
    def __init__(self, patch):
        self.patch = patch
        self.state = []

    def decode(self, tokens):
        return ' '.join(tokens) if self.patch != 'no-op' else ''

    def request(self, tokens):
        if self.patch == 'local-only':
            return ''  # 利用者向けの入口は変更前のままなので、答えを返さない。
        if self.patch == 'state-leak':
            self.state.extend(tokens)
            return self.decode(self.state)
        return self.decode(tokens)


def checks(patch):
    local = Service(patch).decode(['alpha']) == 'alpha'
    api = Service(patch).request(['alpha']) == 'alpha'
    service = Service(patch)
    first = service.request(['alpha'])
    second = service.request(['beta'])
    state = first == 'alpha' and second == 'beta'
    return dict(local=local, api=api, state=state)


def main():
    variants = {name: checks(name) for name in ['no-op', 'local-only', 'state-leak', 'complete']}
    groups = [('local',), ('local', 'api'), ('local', 'api', 'state')]
    labels = ['関数だけを呼ぶ', '利用者向けの入口まで確認する', '同じ入口に2回続けて送る']
    frames = []
    for i, (group, label) in enumerate(zip(groups, labels)):
        passing = [name for name, result in variants.items() if all(result[k] for k in group)]
        frames.append(dict(value=i+1, note=f'{label}。四つの実装のうち、合格したのは {", ".join(passing)} です。', bars=[dict(label='合格した実装', value=len(passing)), dict(label='不合格の実装', value=4-len(passing))]))
    assert [f['bars'][0]['value'] for f in frames] == [3, 2, 1]
    assert not any(variants['no-op'].values()) and all(variants['complete'].values())
    result = dict(experiment='同じ四つの実装を、採点範囲を変えて比べる例', verification=dict(mechanism='PARTIAL',performance='NOT TESTED',scaling='NOT TESTED',production_applicability='NOT TESTED'), variants=variants, explorer=dict(default=0,label='採点に使う検査を増やす',unit='件',metric='四つの架空の実装の成否',frames=frames), limitation='SGLang、GPU、HTTPサーバー、非公開の採点プログラム、エージェントによる実装は使いません。')
    Path(__file__).with_name('results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(variants,indent=2))


if __name__ == '__main__':
    main()
