"""CPU illustration of output-space conflict and candidate-set distillation, not OneRanker."""
import json
import math
from pathlib import Path


def softmax(z):
    e = [math.exp(x-max(z)) for x in z]
    return [x/sum(e) for x in e]


def topk(z, k=2):
    return sorted(range(len(z)), key=lambda i: (-z[i], i))[:k]


def align(steps=200, rate=.2, teacher=None):
    # Fixed candidate pool, frozen teacher, CE gradient p-q. No retrieval discovery.
    z = [2., 1., 0., -1.]
    q = softmax(teacher or [-1., 0., 1., 2.])
    frames = []
    for step in range(steps+1):
        p = softmax(z)
        if step in (0, 10, 50, steps):
            frames.append({'step': step, 'kl_teacher_generator': sum(a*math.log(a/b) for a,b in zip(q,p)),
                           'top2_disagreement': 1-len(set(topk(p)) & set(topk(q)))/2,
                           'generator': p, 'teacher': q})
        z = [a-rate*(b-c) for a,b,c in zip(z,p,q)]
    return frames


def conflict():
    # Same x, contradictory regression targets: interest=x, value=-x.
    # Shared output has optimal w=0. Task-conditioned outputs permit w=(1,-1).
    xs = [-2., -1., 1., 2.]
    def loss(w, sign):
        return sum((w*x-sign*x)**2 for x in xs)/len(xs)
    return {'shared': {'interest_mse': loss(0,1), 'value_mse': loss(0,-1)},
            'task_conditioned': {'interest_mse': loss(1,1), 'value_mse': loss(-1,-1)}}


def experiment():
    return {'kind': 'synthetic mechanism illustration', 'seed': 'deterministic',
            'metrics': conflict(), 'alignment': align(),
            'counterexample': 'A wrong teacher is also imitated; missing candidates cannot be recovered.',
            'not_tested': ['causal attention', 'interest coverage', 'production eCPM', 'latency', 'GMV']}

if __name__ == '__main__':
    result = experiment()
    Path(__file__).with_name('results.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
