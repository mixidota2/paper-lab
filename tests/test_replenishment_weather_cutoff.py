"""Keep the weather availability example scoped to an authenticated guide insertion."""
import hashlib
import json
from pathlib import Path
from prose_preservation import historical_lab_public_guide
import re

import pytest

from prose_preservation import before_axial_ingredient_order, before_stockout_example, before_weather_cutoff, weather_cutoff_rewrite_hash

ROOT=Path(__file__).resolve().parents[1]
P='guides/forecast-to-replenishment.md'


def identity(b):
    return {'sha256': hashlib.sha256(b).hexdigest(),
            'blob': hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()}


def test_weather_section_and_existing_guide_are_exact():
    current=historical_lab_public_guide(ROOT,P)
    prior=before_weather_cutoff(ROOT,P,current)
    weather=before_axial_ingredient_order(ROOT,P,before_stockout_example(ROOT,P,current))
    receipt=json.loads((ROOT/'tests/replenishment_weather_cutoff_hashes.json').read_text())
    b,a=identity(prior),identity(weather)
    assert b==receipt['before'] and a==receipt['after']
    for algo in a:
        assert weather_cutoff_rewrite_hash(ROOT,P,b[algo],algo)==a[algo]
        for invalid in (a[algo],'0'*len(a[algo])):
            with pytest.raises(AssertionError):
                weather_cutoff_rewrite_hash(ROOT,P,invalid,algo)
    with pytest.raises(AssertionError):
        before_weather_cutoff(ROOT,P,current+b'\n')
    section=receipt['inserted']
    assert section.encode() in weather and section.encode() not in prior
    assert all(word in section for word in ('10時','9時','11時30分','公開時刻','締切までに届いた予報','後から観測した天気'))
    assert set(re.findall(r'\]\((https?://[^)]+)\)',section))=={
        'https://www.jmbsc.or.jp/jp/online/file/f-online10200.html',
        'https://open-meteo.com/en/docs/single-runs-api',
    }
