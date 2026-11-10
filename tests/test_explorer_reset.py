"""Run actual explorer handlers with a DOM substitute, not a browser/layout claim."""
import json
from pathlib import Path
import subprocess

from paper_lab.display_labels import explorer_axes, explorer_view

ROOT = Path(__file__).resolve().parents[1]


def test_reset_restores_condition_and_scale(tmp_path):
    cases = []
    for path in sorted((ROOT / 'papers').glob('*/results.json')):
        data = json.loads(path.read_text())
        if isinstance(data, dict) and data.get('explorer'):
            slug = path.parent.name
            cases.append({'slug': slug, 'data': explorer_view(slug, data['explorer']),
                          'axes': explorer_axes(slug)})
    assert cases
    # A small independent fixture ensures the scale change alters geometry.
    cases.append({'slug': 'scale-regression-fixture', 'axes': None, 'data': {
        'default': 1, 'label': 'condition', 'unit': '', 'metric': 'value',
        'frames': [
            {'value': 0, 'bars': [{'label': 'a', 'value': 100}], 'note': 'first'},
            {'value': 1, 'bars': [{'label': 'a', 'value': 20},
                                  {'label': 'unknown', 'value': None}], 'note': 'default'},
            {'value': 2, 'bars': [{'label': 'a', 'value': 40}], 'note': 'last'},
        ],
    }})
    payload = tmp_path / 'explorers.json'
    payload.write_text(json.dumps(cases, ensure_ascii=False))
    subprocess.run(['node', str(ROOT / 'tests/explorer_reset_smoke.cjs'),
                    str(payload), str(ROOT / 'paper_lab/templates/interactives.js')], check=True)
