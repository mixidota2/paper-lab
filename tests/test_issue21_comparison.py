"""Issue 21: one evidence source, scoped dates and honest comparison."""
import copy
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import yaml
import pytest
from paper_lab.replenishment_guide import load_cards, render_cards, render_comparison, survey_dates

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'guides/replenishment-evidence.yaml'
BASE = '9d73076d9ade3ff3af9fc673a5e243d2a5609369'

def test_historical_evidence_values_and_dates_preserved():
    old = yaml.safe_load(subprocess.check_output(['git', 'show', BASE+':guides/replenishment-evidence.yaml'], cwd=ROOT))
    new = load_cards(SOURCE)
    assert new['updated'] == '2026-11-18'
    assert new['checked'] == old['checked']
    # Preserve the complete historical equality assertion at its exact release,
    # and require the same live metadata for every rewritten card.
    archived = yaml.safe_load(subprocess.check_output(['git', 'show', '5c97429443b48dd3d3e6568e4dd7087525bc8b63:guides/replenishment-evidence.yaml'], cwd=ROOT))
    prose = {'title', 'task', 'scope', 'forecast', 'policy', 'result', 'operation', 'limitation'}
    for before, historical, after in zip(old['cards'], archived['cards'], new['cards'], strict=True):
        assert {key: historical[key] for key in before} == before
        assert {key: after[key] for key in before.keys() - prose} == {key: before[key] for key in before.keys() - prose}
    assert '2026-11-02（5件）' in survey_dates(new)
    assert '2026-11-17（2件）' in survey_dates(new)
    assert '全提案採用' in new['cards'][0]['comparison']['assessment']
    amazon = new['cards'][2]
    assert '指定DOI' in amazon['followup']['scope']
    assert '取得できず' in amazon['followup']['scope']

def test_comparison_tracks_yaml_without_repeating_effect_values():
    data = load_cards(SOURCE)
    table = render_comparison(data)
    assert table.count('data-comparison-row') == 7
    assert 'tabindex="0"' in table and '<caption>' in table
    for card in data['cards']:
        assert card['result'] not in table
        assert card["company"] in table
        assert card['followup']['scope'] in table
        for source in card['sources']:
            assert source['url'].replace('&','&amp;') in table
    data['cards'][0]['comparison']['decision'] = '<new & decision>'
    html = render_comparison(data)
    assert '&lt;new &amp; decision&gt;' in html and '<new & decision>' not in html
    assert '<new & decision>' not in render_cards(data)
    assert '確認範囲' in table or '再読した範囲' in table

@pytest.mark.parametrize('change', ['missing-summary', 'blank-summary', 'missing-scope', 'future-review', 'future-card', 'bad-update'])
def test_incomplete_or_misdated_followup_rejected(tmp_path, change):
    data = copy.deepcopy(load_cards(SOURCE))
    card = data['cards'][0]
    if change == 'missing-summary': del card['comparison']['decision']
    if change == 'blank-summary': card['comparison']['connection'] = ' '
    if change == 'missing-scope': del card['followup']['scope']
    if change == 'future-review': card['followup']['checked'] = '2026-11-19'
    if change == 'future-card': card['checked'] = '2026-11-19'
    if change == 'bad-update': data['updated'] = '2026-11-01'
    path = tmp_path / 'cards.yaml'
    path.write_text(yaml.safe_dump(data, allow_unicode=True))
    with pytest.raises(ValueError): load_cards(path)

def test_exact_revision_manifest_and_mutation_rejection():
    import hashlib, json
    from prose_preservation import issue21_hash, replenishment_cards_followup_hash, replenishment_cards_rewrite_hash, replenishment_guide_rewrite_hash, weather_cutoff_rewrite_hash
    manifest = json.loads((ROOT/'tests/issue21_revision_hashes.json').read_text())
    assert manifest['base'] == BASE
    assert set(manifest['files']) == {'guides/forecast-to-replenishment.md', 'guides/replenishment-evidence.yaml', 'paper_lab/templates/guide.html'}
    for path, row in manifest['files'].items():
        old = subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
        new = (ROOT/path).read_bytes()
        for algorithm in ('sha256','blob'):
            def digest(raw):
                return hashlib.sha256(raw).hexdigest() if algorithm == 'sha256' else hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
            assert digest(old) == row['before_'+algorithm]
            exact_after_issue21 = row['after_'+algorithm]
            if path == 'guides/forecast-to-replenishment.md':
                reading = json.loads((ROOT/'tests/reading_prose_revision_hashes.json').read_text())['files'][path]
                assert reading['before_'+algorithm] == exact_after_issue21
                expected_live = replenishment_guide_rewrite_hash(ROOT, path, reading['after_'+algorithm], algorithm)
                expected_live = weather_cutoff_rewrite_hash(ROOT, path, expected_live, algorithm)
            elif path == 'guides/replenishment-evidence.yaml':
                rewritten = replenishment_cards_rewrite_hash(ROOT, path, exact_after_issue21, algorithm)
                expected_live = replenishment_cards_followup_hash(ROOT, path, rewritten, algorithm)
            else:
                expected_live = exact_after_issue21
            assert digest(new) == issue21_hash(ROOT,path,digest(old),algorithm) == expected_live
            assert digest(new+b'\n') != expected_live
            with pytest.raises(AssertionError):
                issue21_hash(ROOT,path,'unreviewed',algorithm)
