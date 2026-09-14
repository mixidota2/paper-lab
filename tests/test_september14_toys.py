"""Guard the teaching experiments' information and comparison boundaries."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def module(paper):
    spec = importlib.util.spec_from_file_location(paper, ROOT / 'papers' / paper / 'run.py')
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def test_generation_has_no_future_or_item_leakage_and_ranking_excludes_history():
    mask = module('unir2-sequence-unify').visibility()
    for i, row in enumerate(mask['rows'][:4]):
        assert not any(row['allowed'][i + 4:])
        assert all(row['allowed'][:3])
    for row in mask['rows'][4:]:
        assert not any(row['allowed'][:2])
        assert all(row['allowed'][2:])


def test_detach_changes_base_update_without_removing_adapter_capacity():
    toy = module('unir2-sequence-unify')
    detached, coupled = toy.seesaw(True), toy.seesaw(False)
    assert detached[0] == coupled[0]
    assert detached[-1]['adapter'] != 0 and coupled[-1]['adapter'] != 0
    assert detached[-1]['ntp_ce'] == detached[0]['ntp_ce']
    assert coupled[-1]['ntp_ce'] > coupled[0]['ntp_ce']
    assert detached[-1]['ranking_bce'] < detached[0]['ranking_bce']


def test_collision_denominator_counts_occupied_sids_not_items():
    toy = module('gr4ad-ads-generative')
    metrics = toy.collision_metrics(['a', 'a', 'a', 'b'])
    assert metrics['collision_pct'] == 50
    assert metrics['items_in_collisions_pct'] == 75
    assert metrics['compression'] == 2
    assert toy.experiment(0, 4) == toy.experiment(0, 4)


def test_parallel_jobs_cannot_read_unfinished_lessons_and_shift_requires_revalidation():
    toy = module('auto-recsys-harness')
    run = toy.simulate()
    assert [r['major_fixes'] for r in run['trace'][:4]] == [4] * 4
    assert run['trace'][4]['major_fixes'] == 0
    assert run['trace'][19]['major_fixes'] == 0
    assert run['trace'][20]['major_fixes'] > 0
    assert run['trace'][-1]['major_fixes'] == 0
    assert any(r['unsafe_reuse'] for r in toy.simulate(versioned=False)['trace'])
