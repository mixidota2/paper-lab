import json
from pathlib import Path
from xml.etree import ElementTree

import yaml

from prose_preservation import before_glide_full_prose


ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'papers/glide-spotify-sid/'


def read_pair(name):
    path = PREFIX + name
    current = (ROOT / path).read_bytes()
    return before_glide_full_prose(ROOT, path, current), current


def test_glide_overview_and_experiment_stay_paper_and_numeric():
    before, after = map(yaml.safe_load, read_pair('lab.yaml'))
    assert before['sections']['overview'] == after['sections']['overview']
    assert '21日間' in after['sections']['overview']
    assert '5.4%' in after['sections']['overview'] and '14.3%' in after['sections']['overview']
    assert '合成例' not in after['sections']['overview']

    before, after = map(json.loads, read_pair('results.json'))
    for result in (before, after):
        del result['note']
        for e in result['experiments']:
            del e['name'], e['dataset']
    assert before == after


def test_glide_svg_layout_and_reported_scores_are_unchanged():
    for name in ('ab-design', 'cascade', 'conditioning', 'quantizers'):
        old, new = map(ElementTree.fromstring, read_pair('figures/'+name+'.svg'))
        assert [(e.tag, e.attrib) for e in old.iter()] == [(e.tag, e.attrib) for e in new.iter()]
        reported = {'ab-design': ('5.4%', '14.3%', '34%'),
                    'quantizers': ('0.856', '0.657')}.get(name, ())
        txt = ' '.join(new.itertext())
        assert all(value in txt for value in reported)
