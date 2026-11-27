import hashlib
import json
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = json.loads(Path(__file__).with_name('vn2_figures_full_prose_hashes.json').read_text())['files']
SLUG = 'vn2-stockout-catboost'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def test_vn2_historical_figures_preserve_source_shape_and_exact_reviewed_prose():
    assert set(RECEIPT) == {
        f'papers/{SLUG}/figures/{name}.svg' for name in ('censoring', 'masking', 'order')
    }
    for path, receipt in RECEIPT.items():
        raw = (ROOT / path).read_bytes()
        labels = [
            el.text for el in ElementTree.fromstring(raw).iter()
            if el.tag.rsplit('}', 1)[-1] in {'title', 'text'}
        ]
        assert labels == receipt['final_labels']
        assert sha(raw) == receipt['after_sha256']
        assert sha(('\n\n'.join(labels) + '\n').encode()) == receipt['style_text_sha256']
        prior = raw.decode()
        for old, new in zip(receipt['prior_labels'], receipt['final_labels'], strict=True):
            assert prior.count('>' + new + '<') == 1
            prior = prior.replace('>' + new + '<', '>' + old + '<', 1)
        assert sha(prior.encode()) == receipt['before_sha256']
