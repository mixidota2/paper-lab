"""The optional guess must offer actual choices, not text between options."""
from html.parser import HTMLParser
from pathlib import Path
import hashlib
import json

import pytest

from prose_preservation import reading_prose_hash, reference_guess_markup_hash

ROOT = Path(__file__).resolve().parents[1]
PAPERS = ROOT / 'papers'


class GuessOptions(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_guess = False
        self.options = []
        self.text_outside_option = []
        self.current_option = None
        self.select_count = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'select' and 'data-guess' in dict(attrs):
            self.in_guess = True
            self.select_count += 1
        elif self.in_guess and tag == 'option':
            self.current_option = []

    def handle_endtag(self, tag):
        if self.in_guess and tag == 'option' and self.current_option is not None:
            self.options.append(''.join(self.current_option).strip())
            self.current_option = None
        elif tag == 'select' and self.in_guess:
            self.in_guess = False

    def handle_data(self, data):
        if self.current_option is not None:
            self.current_option.append(data)
        elif self.in_guess and data.strip():
            self.text_outside_option.append(data.strip())


@pytest.mark.parametrize('paper', [
    'reasoncast-agentic-demand-forecasting',
    'retailbench-long-horizon-store-agents',
])
def test_reference_lab_guess_select_offers_all_four_choices(paper):
    parsed = GuessOptions()
    parsed.feed((PAPERS / paper / 'interactive.html').read_text(encoding='utf-8'))
    parsed.close()
    assert parsed.select_count == 1
    assert parsed.options == ['まだ決めていない', '改善する', '同じになる', '悪化する']
    assert parsed.text_outside_option == []


def test_reference_guess_markup_translation_is_exact():
    rows = json.loads((ROOT / 'tests/reference_guess_markup_hashes.json').read_text())['files']
    assert set(rows) == {
        'papers/reasoncast-agentic-demand-forecasting/interactive.html',
        'papers/retailbench-long-horizon-store-agents/interactive.html',
    }
    for path, row in rows.items():
        content = (ROOT / path).read_bytes()
        for algorithm, actual in {
            'sha256': hashlib.sha256(content).hexdigest(),
            'blob': hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest(),
        }.items():
            old = row['before_' + algorithm]
            repaired = reference_guess_markup_hash(ROOT, path, old, algorithm)
            assert repaired == row['after_' + algorithm]
            with pytest.raises(AssertionError):
                reference_guess_markup_hash(ROOT, path, repaired, algorithm)
            if path == 'papers/retailbench-long-horizon-store-agents/interactive.html':
                assert reading_prose_hash(ROOT, path, repaired, algorithm) == actual
                assert reading_prose_hash(ROOT, path, old, algorithm) == actual
                for unreviewed in (actual, '0' * len(old)):
                    with pytest.raises(AssertionError):
                        reading_prose_hash(ROOT, path, unreviewed, algorithm)
            else:
                assert repaired == actual
