"""Ensure every visible budget state still represents the exact toy outcomes."""
import hashlib
import itertools
import json
import re
from fractions import Fraction
from pathlib import Path

import pytest
import yaml

from prose_preservation import linkedin_full_rewrite_hash, paper_overview_rewrite_hash

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'linkedin-prediction-to-incrementality'
PAPER = ROOT / 'papers' / SLUG
FILES = json.loads((ROOT / 'tests/linkedin_full_rewrite_hashes.json').read_text())['files']


@pytest.mark.parametrize('path, algorithm', itertools.product(FILES, ('blob', 'sha256')))
def test_linkedin_source_guards_match_exact_reviewed_bytes(path, algorithm):
    row = FILES[path]
    digest = linkedin_full_rewrite_hash(ROOT, path, row['before_' + algorithm], algorithm)
    raw = (ROOT / path).read_bytes()
    actual = (hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()
              if algorithm == 'blob' else hashlib.sha256(raw).hexdigest())
    assert digest == row['after_' + algorithm]
    assert actual == paper_overview_rewrite_hash(ROOT, path, digest, algorithm)
    with pytest.raises(AssertionError):
        linkedin_full_rewrite_hash(ROOT, path, row['after_' + algorithm], algorithm)
    with pytest.raises(AssertionError):
        linkedin_full_rewrite_hash(ROOT, path, '0' * len(digest), algorithm)
    assert linkedin_full_rewrite_hash(ROOT, f'other/{path}', digest, algorithm) == digest


def test_linkedin_figure_renders_the_recomputed_choices_in_each_frame():
    spec = yaml.safe_load((PAPER / 'lab.yaml').read_text())
    html = spec['sections']['executable_understanding']
    script = re.search(r'<script type="application/json" data-frames>(.*?)</script>', html).group(1)
    frames = json.loads(script)
    assert '<div data-output>' + frames[0] + '</div><figcaption>' in html
    assert re.findall(r'<option value="(\d)">(\d)</option>', html) == [('0','2'),('1','3'),('2','5')]
    stored = json.loads((PAPER / 'results.json').read_text())
    rows = [{**row, **{key: Fraction(str(row[key])) for key in ('mu0', 'mu1')}} for row in stored['rows']]
    cost = lambda group: sum(r['cost'] for r in group)
    uplift = lambda group: sum(r['mu1'] - r['mu0'] for r in group)
    response = lambda group: sum(r['mu1'] for r in group)
    all_groups = [group for size in range(5) for group in itertools.combinations(rows, size)]
    untreated = sum(r['mu0'] for r in rows)
    for budget, frame in zip((2, 3, 5), frames, strict=True):
        display = re.findall(r'<tr><th>[^<]+</th><td>([^<]+)</td><td>(\d)</td><td>([0-9.]+)</td></tr>', frame)
        assert len(display) == 2
        for key, target, (names, shown_cost, shown_uplift) in zip(
            ('response', 'incremental'), (response, uplift), display, strict=True
        ):
            available = [g for g in all_groups if cost(g) <= budget]
            winners = [g for g in available if target(g) == max(map(target, available))]
            assert len(winners) == 1
            best = winners[0]
            expected = stored['budgets'][str(budget)][key]
            assert [r['user'] for r in best] == names.split('・') == expected['selected']
            assert cost(best) == int(shown_cost) == expected['cost']
            assert uplift(best) == Fraction(shown_uplift) == Fraction(str(expected['incremental_value']))
            assert untreated + uplift(best) == Fraction(str(expected['expected_total_outcome']))
