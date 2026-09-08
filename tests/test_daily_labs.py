"""Numerical invariants and packaging for the 2026-09-08 batch."""
import importlib.util
import json
from pathlib import Path
from xml.etree import ElementTree

import pytest

from paper_lab.build import build
from paper_lab.models import LabError, lab_from_dict, load_lab

ROOT = Path(__file__).resolve().parents[1]
IDS = ('glide-spotify-sid', 'understanding-sids-isd', 'execution-state-unlearning')


def module(lab_id):
    spec = importlib.util.spec_from_file_location(lab_id, ROOT / 'papers' / lab_id / 'run.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize('lab_id', IDS)
def test_committed_results_match_computation(lab_id):
    actual = json.loads((ROOT / 'papers' / lab_id / 'results.json').read_text())
    assert actual == module(lab_id).compute()
    assert actual['verification'] == {
        'mechanism': 'PARTIAL', 'performance': 'NOT TESTED',
        'scaling': 'NOT TESTED', 'production_applicability': 'NOT TESTED',
    }


def test_channel_share_does_not_determine_lift():
    toy = module(IDS[0])
    cases = [toy.channel_case(p, 0) for p in (0.05, 0.1, 0.2)]
    assert {x['channel_share_percent'] for x in cases} == {34}
    assert [x['relative_lift_percent'] for x in cases] == [-17, 0, 34]
    assert toy.channel_case(1, 34)['relative_lift_percent'] == 0
    assert toy.token_budget(0)['sid_history_tokens'] < toy.token_budget(0)['soft_plus_recent_sid_tokens']


def test_sid_survival_is_irreversible_and_ordering_cannot_add_items():
    toy = module(IDS[1])
    for history in toy.TRAIN:
        for width in (1, 2, 4, 8):
            for support in (False, True):
                output = toy.decode(history, width, support, False)
                previous = set(toy.SIDS)
                for frame in output['trace']:
                    assert set(frame['items']) <= previous
                    previous = set(frame['items'])
                ordered = toy.decode(history, width, support, True)
                assert set(ordered['ranked_items']) == set(output['ranked_items'])
                assert ordered['trace'] == output['trace']
                if width == 8:
                    assert set(output['ranked_items']) == set(toy.SIDS)
    assert 'e' not in toy.decode('x', 1, False, False)['ranked_items']
    assert 'e' in toy.decode('x', 1)['ranked_items']
    assert toy.evaluate(2, True, True, reverse=True)['toy_ndcg_at_2'] < toy.evaluate(2, False, False)['toy_ndcg_at_2']


def test_absent_support_reduces_to_decoder_and_test_labels_do_not_guide_search():
    toy = module(IDS[1])
    original = toy.decode('x', 2)
    toy.TEST = [('x', 'h')]
    assert original == toy.decode('x', 2)
    no_support = toy.decode('x', 2, True, True, budget=0)
    plain = toy.decode('x', 2, False, False, budget=0)
    assert no_support == plain


def test_replay_preserves_full_state_and_cost_at_all_boundaries():
    toy = module(IDS[2])
    for total in (1, 2, 12):
        for tau in range(1, total + 1):
            for checkpoint in range(tau):
                metrics = toy.experiment(total, tau, checkpoint)['metrics']
                replay = metrics['選択的再実行']
                assert replay['same_runtime_as_reference']
                assert replay['safe_total'] == total * (total + 1) // 2
                assert replay['recomputed_steps'] == total - checkpoint
                assert replay['leak_at_probes'] == replay['behavioral_mismatch'] == 0
                scrub = metrics['全文字列の除去']
                assert scrub['leak_at_probes'] == 0
                assert scrub['behavioral_mismatch'] == 1
                assert not scrub['same_runtime_as_reference']


def test_figures_and_downloads_survive_build_and_all_papers_stay_indexed(tmp_path):
    labs = build(root=ROOT, site_dir=tmp_path / 'site')
    index = (tmp_path / 'site/index.html').read_text()
    for lab in labs:
        assert f'papers/{lab.id}.html' in index
    for lab_id in IDS:
        lab = load_lab(ROOT / 'papers' / lab_id)
        page = (tmp_path / 'site/papers' / f'{lab_id}.html').read_text()
        assert 'run.py 単体で実行できます' in page
        assert 'downloads/_toy_common.py' not in page
        assert page.count('class="paper-svg teaching"') == len(lab.figures)
        for f in lab.figures:
            xml = ElementTree.parse(lab.source_dir / f['path']).getroot()
            assert xml.get('viewBox') and xml.find('{http://www.w3.org/2000/svg}desc') is not None
            copy = tmp_path / 'site/figures' / lab_id / f['path']
            assert copy.read_bytes() == (lab.source_dir / f['path']).read_bytes()


def test_unknown_svg_placement_fails():
    import yaml
    directory = ROOT / 'papers' / IDS[0]
    raw = yaml.safe_load((directory / 'lab.yaml').read_text())
    raw['figures'][0]['after'] = 'unknown'
    with pytest.raises(LabError, match='placement'):
        lab_from_dict(raw, directory)
