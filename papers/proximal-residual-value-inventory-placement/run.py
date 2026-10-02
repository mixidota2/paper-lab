"""Figure 3 exact counterexample and separable PWL + quadratic state potential.

Scalar convex minimization by bisection; no learned policy or State-prox backward.
"""
import json
from pathlib import Path


def allocate(state, budget, kind):
    total = sum(state) + budget
    lo, hi = state[0], state[0] + budget
    if kind == 'counterexample':
        # Appendix C.1: H=[[2,3],[3,5]], a=(0,1).
        x = min(hi, max(lo, 2 * total - 2))
    else:
        # R(x)=|x1-.5|+2|x2-3|, Phi(x)=||x||²/2, tau=1.
        # Action control substitutes ||x-I||²/2; it is a Lab-designed contrast.
        def derivative(x):
            y = total - x
            s1 = -1 if x < .5 else 1
            s2 = -2 if y < 3 else 2
            return s1-s2 + x-y - (state[0]-state[1] if kind == 'action' else 0)
        for _ in range(70):
            mid = (lo+hi)/2
            if derivative(mid) < 0:
                lo = mid
            else:
                hi = mid
        x = (lo+hi)/2
    answer = [x, total-x]
    assert all(answer[i] >= state[i]-1e-10 for i in range(2))
    return answer


def path(kind, count):
    state = [0., 0.]
    states = [state]
    for _ in range(count):
        state = allocate(state, 2/count, kind)
        states.append(state)
    return states


def main():
    cases = []
    for kind in ['counterexample', 'state', 'action']:
        one = path(kind, 1)[-1]
        for count in [1, 2, 5, 20, 500]:
            states = path(kind, count)
            tv = sum(abs(a-b) for a, b in zip(one, states[-1]))/4
            cases.append(dict(kind=kind, count=count, states=states, final=states[-1], tv=tv))
            if kind == 'state':
                assert tv < 1e-10
    assert path('counterexample', 1)[-1] == [2, 0]
    assert path('counterexample', 2)[-1] == [1, 1]
    result = dict(lab02='proximal', note='図3の反例と分離可能な2拠点縮約。Amazonの学習済み方策・費用は再現していない。',
                  cases=cases, pcsp_inverse_shock=[2, -1],
                  paper_evidence={'oos': {'Historical proxy': [1., 0.], 'Direct neural RL': [1.012, .002],
                    'State-prox': [.950, .028], 'State-prox without potential': [1.070, .038]},
                    'in_sample_state_prox': [.851, .022], 'tv_500_oos': {'State-prox': .00201, 'Direct neural RL': .12716}},
                  experiments=[dict(name='固定環境の分割配置', metrics={
                      '図3 一括配置': path('counterexample', 1)[-1],
                      '図3 2回配置': path('counterexample', 2)[-1],
                      '状態potential 最大TV': max(c['tv'] for c in cases if c['kind']=='state'),
                      '行動正則化 最大TV': max(c['tv'] for c in cases if c['kind']=='action')})])
    Path(__file__).with_name('results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')


if __name__ == '__main__':
    main()
