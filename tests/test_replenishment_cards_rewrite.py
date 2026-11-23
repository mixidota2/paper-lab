"""Preserve the structure and signed measurements of all seven revised cards."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

import pytest
import yaml

from paper_lab.replenishment_guide import FIELDS, load_cards
from prose_preservation import replenishment_cards_followup_hash, replenishment_cards_rewrite_hash

ROOT = Path(__file__).resolve().parents[1]
PATH = 'guides/replenishment-evidence.yaml'
BASE = '5c97429443b48dd3d3e6568e4dd7087525bc8b63'
NUMBER = re.compile(r'[+−-]?\d+(?:[,\d]*\d)?(?:\.\d+)?%?')


def historical_bytes():
    return subprocess.check_output(['git', 'show', f'{BASE}:{PATH}'], cwd=ROOT)


def test_card_prose_only_all_cards_rewritten_and_numbers_kept_in_their_fields():
    old = yaml.safe_load(historical_bytes())
    new = load_cards(ROOT / PATH)
    assert {k: v for k, v in new.items() if k != 'cards'} == {
        k: v for k, v in old.items() if k != 'cards'
    }
    assert len(new['cards']) == len(old['cards']) == 7
    prose = {'title', 'comparison', 'followup', *FIELDS}
    for before, after in zip(old['cards'], new['cards'], strict=True):
        assert {k: v for k, v in after.items() if k not in prose} == {
            k: v for k, v in before.items() if k not in prose
        }
        assert all(before[k] != after[k] for k in ('title', *FIELDS))
        for key in FIELDS:
            live, prior = NUMBER.findall(after[key]), NUMBER.findall(before[key])
            if (after['id'], key) == ('zalando', 'policy'):
                # The old ordinal gives the same probability boundary in prose.
                assert prior == ['12', '75'] and '費用の75分位' in before[key]
                assert live == ['12', '75%'] and '以下に収まる割合が75%以上' in after[key]
            else:
                assert live == prior, (after['id'], key)
        assert after['comparison'].keys() == before['comparison'].keys()
        assert all(after['comparison'][k] != before['comparison'][k] for k in before['comparison'])
        assert after['followup']['checked'] == before['followup']['checked']
        assert after['followup']['scope'] != before['followup']['scope']
        assert NUMBER.findall(after['followup']['scope']) == NUMBER.findall(before['followup']['scope'])


@pytest.mark.parametrize('algorithm', ['sha256', 'blob'])
def test_only_exact_version_of_evidence_yaml_is_accepted(algorithm):
    manifest = json.loads((ROOT / 'tests/replenishment_cards_rewrite_hashes.json').read_text())
    assert manifest['base'] == BASE
    assert manifest['files'].keys() == {PATH}

    def digest(raw):
        if algorithm == 'sha256':
            return hashlib.sha256(raw).hexdigest()
        return hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()

    current = (ROOT / PATH).read_bytes()
    frozen = replenishment_cards_rewrite_hash(ROOT, PATH, digest(historical_bytes()), algorithm)
    assert replenishment_cards_followup_hash(ROOT, PATH, frozen, algorithm) == digest(current)
    assert digest(current + b'\n') != digest(current)
    with pytest.raises(AssertionError):
        replenishment_cards_rewrite_hash(ROOT, PATH, digest(current), algorithm)
    assert replenishment_cards_rewrite_hash(ROOT, 'other', 'unchanged', algorithm) == 'unchanged'


def test_five_explanations_keep_exact_frozen_source_except_for_reviewed_fields():
    record = json.loads((ROOT / 'tests/replenishment_cards_followup_hashes.json').read_text())
    assert record['files'].keys() == {PATH}
    changes = record['changed_fields']
    assert set(changes) == {
        'zalando:forecast', 'zalando:policy', 'jd-e2e:task',
        'fengyi-override:operation', 'waste-markdown:limitation',
    }
    current = (ROOT / PATH).read_text()
    recovered = current
    cards = {c['id']: c for c in load_cards(ROOT / PATH)['cards']}
    for card_field, values in changes.items():
        card, field = card_field.split(':')
        assert cards[card][field] == values['after']
        assert values['after'] != values['before']
        shown = f"  {field}: {values['after']}\n"
        assert recovered.count(shown) == 1
        recovered = recovered.replace(shown, f"  {field}: {values['before']}\n", 1)

    raw = recovered.encode()
    old = {
        'sha256': hashlib.sha256(raw).hexdigest(),
        'blob': hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest(),
    }
    frozen = json.loads((ROOT / 'tests/replenishment_cards_rewrite_hashes.json').read_text())
    for algorithm, digest in old.items():
        assert digest == frozen['files'][PATH]['after_' + algorithm]
        assert digest == record['files'][PATH]['before_' + algorithm]
        with pytest.raises(AssertionError):
            replenishment_cards_followup_hash(ROOT, PATH, 'unreviewed', algorithm)
