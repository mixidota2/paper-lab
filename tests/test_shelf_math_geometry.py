"""Regression fixtures are synthetic, not evidence of a successful browser run."""
import copy
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location('shelf_survey_browser', Path(__file__).with_name('shelf_survey_browser.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def term(kind='msub'):
    # Rect heights/bottoms reproduce the reported 360px α/ip counterexample.
    # Font sizes are illustrative fixture inputs, not claimed CI observations.
    return {'kind': kind, 'children': [
        {'text': 'α', 'width': 8, 'height': 9.03125, 'y': 450.015625, 'bottom': 459.046875, 'fontSize': 20},
        {'text': 'ip', 'width': 9, 'height': 11.484375, 'y': 454, 'bottom': 465.484375, 'fontSize': 14},
    ]}


def test_alpha_ip_taller_glyph_box_can_have_smaller_type_size():
    data = term()
    a, b = data['children']
    assert b['height'] > a['height']
    module.assert_math_term(data)


def test_superscript_taller_glyph_box_is_not_a_size_failure():
    data = term('msup')
    data['children'][1].update(y=440, bottom=451.484375)
    module.assert_math_term(data)


@pytest.mark.parametrize('size', [20, 21, 0, float('nan'), float('inf')])
def test_script_requires_finite_positive_smaller_computed_font_size(size):
    data = term()
    data['children'][1]['fontSize'] = size
    with pytest.raises(AssertionError):
        module.assert_math_term(data)


@pytest.mark.parametrize('kind', ['msub', 'msup'])
def test_smaller_font_does_not_excuse_wrong_vertical_position(kind):
    data = term(kind)
    data['children'][1].update(y=450.015625, bottom=459.046875)
    with pytest.raises(AssertionError):
        module.assert_math_term(data)


def test_fraction_relation_remains_independent_of_type_size():
    data = term('mfrac')
    data['children'][1]['y'] = data['children'][0]['bottom']
    module.assert_math_term(data)
    overlapping = copy.deepcopy(data)
    overlapping['children'][1]['y'] -= 1
    with pytest.raises(AssertionError):
        module.assert_math_term(overlapping)
