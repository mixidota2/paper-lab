"""Keep the earlier evidence, with discoverable and exact Japanese reading copies."""
from hashlib import sha256
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1] / 'research-data'
SHELF = ROOT / 'shelf'
RECORDS = {
    'chu-2009': (
        '731977357ebff2f8843e89e751180b627514b55bc995d07932349bf092c7d16a',
        'a55ccb9a5b899d6b79e8ccbe5f2bf633393052b08ad38ff7366c070ea6bbbf66',
        ('HK$4,550','HK$5,202','HK$5,681.53','24.8688%','9.2182%','1,579.5 cm','3,159 cm'),
    ),
    'display-variety-2023': (
        'c84258fa5bc03b99f31615515ae819ca207cffabe4f7577af26778aad2c7b387',
        '679603568c4a3cdb7731d41f652ea8f7875498851498bd1fd758ce2ce9fca5c3',
        ('p<0.10','−0.137','0.082','0.872','0.85%','[0.7425092,1.0240036]'),
    ),
}


def test_shelf_index_links_to_summary_and_both_versions():
    index = (SHELF/'README.md').read_bytes()
    assert sha256(index).hexdigest()=='df9632cb56fd6b63d1fd675d12f2a941252f6c392da2cf4f32caab148737e9ec'
    links = re.findall(r'\]\(([^)]+)\)', index.decode())
    assert set(links) == {'shelf-allocation-evidence-2026-10-29.md',
                         *(f'{name}{suffix}.md' for name in RECORDS for suffix in ('','-ja'))}
    assert all((SHELF/target).is_file() for target in links)
    assert '[棚割りの事例資料](shelf/)' in (ROOT/'README.md').read_text()
    assert '原著を読み直した結果ではありません' in index.decode()


def test_japanese_reading_copy_keeps_links_and_distinguishes_measured_and_modeled():
    for name,(before,after,anchors) in RECORDS.items():
        original, japanese = ((SHELF/f'{name}{suffix}.md').read_bytes() for suffix in ('','-ja'))
        assert sha256(original).hexdigest() == before
        assert sha256(japanese).hexdigest() == after
        def urls(data):
            return sorted(re.findall(rb'https://[^\s)]+',data))
        assert urls(original) == urls(japanese)
        assert all(anchor.encode() in original and anchor.encode() in japanese for anchor in anchors)
        assert '実測'.encode() in japanese and '数値の照合'.encode() in japanese
