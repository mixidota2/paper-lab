"""Deterministic playbook-memory simulation. No LLM, jobs, or measured human timings."""
import json
from pathlib import Path


def simulate(remember=True, versioned=True, workers=4):
    memory = set()
    free_at = [0] * workers
    trace = []
    for iteration in range(1, 32):
        version = 'A' if iteration <= 20 else 'B'
        categories = ['hardware', 'package', 'submission', 'input-name']
        if iteration == 28:
            categories += ['new-compiler-error']
        # Immutable per-job snapshot: overlapping jobs cannot use lessons from the future.
        worker = min(range(workers), key=lambda w: free_at[w])
        start = free_at[worker]
        known = {key for finished, key in memory if finished <= start}
        keys = [(version if versioned else '*', c) for c in categories]
        failures = [k for k in keys if not remember or k not in known]
        finish = start + 2880 + 30 * len(failures)  # synthetic 2-day training + recovery
        human_minutes = 8 + 12 * len(failures)  # synthetic review + fixes
        free_at[worker] = finish
        if remember:
            memory.update((finish, k) for k in keys)
        trace.append({'iteration': iteration, 'baseline': version, 'worker': worker,
                      'start_min': start, 'finish_min': finish, 'major_fixes': len(failures),
                      'human_min': human_minutes,
                      'unsafe_reuse': version == 'B' and not versioned and len(failures) == 0})
    return {'human_minutes': sum(t['human_min'] for t in trace), 'wall_clock_minutes': max(free_at),
            'major_fixes': sum(t['major_fixes'] for t in trace), 'trace': trace}


def main():
    runs = {'no_memory': simulate(False), 'versioned_memory': simulate(),
            'unversioned_memory': simulate(versioned=False), 'serial_memory': simulate(workers=1)}
    mature = runs['versioned_memory']['trace']
    assert mature[19]['major_fixes'] == 0
    assert mature[20]['major_fixes'] > 0
    assert mature[-1]['major_fixes'] == 0
    assert runs['versioned_memory']['human_minutes'] < runs['no_memory']['human_minutes']
    assert any(t['unsafe_reuse'] for t in runs['unversioned_memory']['trace'])
    result = {'note': '全時間・失敗系列はLabの仮定。原論文31反復の復元ではない。自然言語の学習能力と分散基盤はNOT TESTED。',
              'assumptions': {'training_minutes': 2880, 'recovery_minutes_per_fix': 30,
                              'review_human_minutes': 8, 'human_minutes_per_fix': 12,
                              'parallel_workers': 4, 'baseline_change_iteration': 21},
              'experiments': [{'name': '人の作業時間と経過時間を分ける', 'metrics': {
                  k: {field: value[field] for field in ('human_minutes', 'wall_clock_minutes', 'major_fixes')}
                  for k, value in runs.items()}}], 'runs': runs}
    Path(__file__).with_name('results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
