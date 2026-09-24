"""Executable verifier-boundary illustration; no SGLang or agent evaluation."""
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
            return ''  # Public path still uses the old implementation.
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
    labels = ['局所検査', '局所＋API', '局所＋API＋状態']
    frames = []
    for i, (group, label) in enumerate(zip(groups, labels)):
        passing = [name for name, result in variants.items() if all(result[k] for k in group)]
        frames.append(dict(value=i+1, note=f'{label}：合格は {", ".join(passing)}。同じ4パッチを採点。', bars=[dict(label='合格パッチ', value=len(passing)), dict(label='不合格パッチ', value=4-len(passing))]))
    assert [f['bars'][0]['value'] for f in frames] == [3, 2, 1]
    assert not any(variants['no-op'].values()) and all(variants['complete'].values())
    result = dict(experiment='synthetic verifier boundary', verification=dict(mechanism='PARTIAL',performance='NOT TESTED',scaling='NOT TESTED',production_applicability='NOT TESTED'), variants=variants, explorer=dict(default=0,label='追加する検査群',unit='件',metric='合成4パッチの成否',frames=frames), limitation='No SGLang, GPU, HTTP server, hidden benchmark tests, or agent model execution.')
    Path(__file__).with_name('results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(variants,indent=2))


if __name__ == '__main__':
    main()
