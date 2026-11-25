"""Translate only exact old identities of the listed prose revisions."""
import hashlib
import json
import re


def revised_hash(root, path, expected, algorithm='sha256'):
    revisions = json.loads((root / 'tests/prose_revision_hashes.json').read_text())['files']
    if path in revisions:
        row = revisions[path]
        assert expected == row['before_' + algorithm], path
        expected = row['after_' + algorithm]
    return yomiyasu_hash(root, path, expected, algorithm)


def yomiyasu_hash(root, path, expected, algorithm='sha256'):
    """Apply the separately recorded November revision to an exact prior hash."""
    revisions = json.loads((root / 'tests/yomiyasu_revision_hashes.json').read_text())['files']
    if path not in revisions:
        return issue21_hash(root, path, expected, algorithm)
    row = revisions[path]
    assert expected == row['before_' + algorithm], path
    return issue21_hash(root, path, row['after_' + algorithm], algorithm)


def before_yomiyasu_replenishment(root, path, content):
    """Reverse only the reviewed T3 explanation, retaining all historical guards."""
    target = 'papers/assortment-replenishment-hard-constraints/interactive.js'
    if path != target:
        return content
    import hashlib
    row = json.loads((root / 'tests/yomiyasu_revision_hashes.json').read_text())['files'][path]
    assert hashlib.sha256(content.encode()).hexdigest() == row['after_sha256']
    old = '需要の定義が違う利益は順位比較できません。'
    new = '需要の定義が違う場合、利益の順位は比較できません。'
    assert content.count(new) == 1
    restored = content.replace(new, old)
    assert hashlib.sha256(restored.encode()).hexdigest() == row['before_sha256']
    return restored


def issue21_hash(root, path, expected, algorithm='sha256'):
    """Permit only the separately recorded Issue 21 update from exact prior bytes."""
    revisions = json.loads((root / 'tests/issue21_revision_hashes.json').read_text())['files']
    if path in revisions:
        row = revisions[path]
        assert expected == row['before_' + algorithm], path
        expected = row['after_' + algorithm]
    return reading_prose_hash(root, path, expected, algorithm)


def reading_prose_hash(root, path, expected, algorithm='sha256'):
    """Permit the reviewed PR 61 text only from the exact preceding identity."""
    rows = json.loads((root / 'tests/reading_prose_revision_hashes.json').read_text())['files']
    if path in rows:
        row = rows[path]
        if row.get('after_reference_guess_markup'):
            # Historical source guards still start at the exact pre-repair
            # bytes. New prose checks can start at the already repaired hash.
            if expected != row['before_' + algorithm]:
                expected = reference_guess_markup_hash(root, path, expected, algorithm)
            assert expected == row['before_' + algorithm], path
            return row['after_' + algorithm]
        assert expected == row['before_' + algorithm], path
        expected = row['after_' + algorithm]
    expected = replenishment_guide_rewrite_hash(root, path, expected, algorithm)
    expected = replenishment_cards_rewrite_hash(root, path, expected, algorithm)
    expected = replenishment_cards_followup_hash(root, path, expected, algorithm)
    expected = store_layout_full_rewrite_hash(root, path, expected, algorithm)
    expected = shelf_full_rewrite_hash(root, path, expected, algorithm)
    expected = generation_retrieval_full_rewrite_hash(root, path, expected, algorithm)
    expected = unipinrec_full_rewrite_hash(root, path, expected, algorithm)
    expected = walmart_full_rewrite_hash(root, path, expected, algorithm)
    expected = placement_options_full_rewrite_hash(root, path, expected, algorithm)
    expected = storewide_full_rewrite_hash(root, path, expected, algorithm)
    expected = assortment_observation_full_rewrite_hash(root, path, expected, algorithm)
    expected = linkedin_full_rewrite_hash(root, path, expected, algorithm)
    expected = accuracy_full_rewrite_hash(root, path, expected, algorithm)
    expected = wholefoods_full_rewrite_hash(root, path, expected, algorithm)
    expected = contextual_full_rewrite_hash(root, path, expected, algorithm)
    expected = zalando_full_rewrite_hash(root, path, expected, algorithm)
    expected = bridging_full_rewrite_hash(root, path, expected, algorithm)
    result = hasterad_registration_hash(root, path, expected, algorithm)
    result = coral_full_rewrite_hash(root, path, result, algorithm)
    expected = prepared_catalog_registration_hash(root, path, result, algorithm)
    if path == 'README.md':
        expected = root_readme_catalog_119_hash(root, path, expected, algorithm)
    expected = tsfm_sparse_rewrite_hash(root, path, expected, algorithm)
    expected = sim2real_full_rewrite_hash(root, path, expected, algorithm)
    expected = index_copy_rewrite_hash(root, path, expected, algorithm)
    expected = or_transformer_full_rewrite_hash(root, path, expected, algorithm)
    expected = diff_projection_source_version_hash(root, path, expected, algorithm)
    expected = arxiv_versioned_overview_hash(root, path, expected, algorithm)
    expected = paper_overview_rewrite_hash(root, path, expected, algorithm)
    expected = revise_full_rewrite_hash(root, path, expected, algorithm)
    expected = pinterest_full_rewrite_hash(root, path, expected, algorithm)
    expected = unir2_full_rewrite_hash(root, path, expected, algorithm)
    expected = genpage_full_rewrite_hash(root, path, expected, algorithm)
    expected = sona_full_rewrite_hash(root, path, expected, algorithm)
    expected = tgr_full_rewrite_hash(root, path, expected, algorithm)
    expected = harness_icegr_full_rewrite_hash(root, path, expected, algorithm)
    expected = forecast_pair_full_rewrite_hash(root, path, expected, algorithm)
    expected = semantic_id_pair_full_rewrite_hash(root, path, expected, algorithm)
    expected = quasid_full_rewrite_hash(root, path, expected, algorithm)
    expected = weather_cutoff_rewrite_hash(root, path, expected, algorithm)
    expected = sid_ope_full_rewrite_hash(root, path, expected, algorithm)
    expected = perishable_full_rewrite_hash(root, path, expected, algorithm)
    expected = switch_hurdle_full_rewrite_hash(root, path, expected, algorithm)
    expected = retail_grain_full_rewrite_hash(root, path, expected, algorithm)
    expected = forecast_critic_full_rewrite_hash(root, path, expected, algorithm)
    expected = static_constrained_full_rewrite_hash(root, path, expected, algorithm)
    return wrapped_produce_full_rewrite_hash(root, path, expected, algorithm)


def pinterest_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    if not path.startswith('papers/pinterest-causal-retrieval-shopping/'):
        return expected
    row = json.loads((root / 'tests/pinterest_full_rewrite_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def unir2_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    if not path.startswith('papers/unir2-sequence-unify/'):
        return expected
    row = json.loads((root / 'tests/unir2_full_rewrite_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def before_unir2_full_rewrite(root, path, current):
    if path not in ('papers/unir2-sequence-unify/lab.yaml', 'papers/unir2-sequence-unify/README.md'):
        return current
    row = json.loads((root / 'tests/unir2_full_rewrite_hashes.json').read_text())['files'][path]
    assert hashlib.sha256(current).hexdigest() == row['after_sha256'], path
    assert row['prior_spans'], path
    lines = current.decode().splitlines(keepends=True)
    for start, end, old in reversed(row['prior_spans']):
        lines[start:end] = [old]
    data = ''.join(lines).encode()
    assert hashlib.sha256(data).hexdigest() == row['before_sha256'], path
    return data


def genpage_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    if not path.startswith('papers/genpage-netflix-homepage/'):
        return expected
    row = json.loads((root / 'tests/genpage_full_rewrite_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def before_genpage_full_rewrite(root, path, current):
    if path not in ('papers/genpage-netflix-homepage/lab.yaml', 'papers/genpage-netflix-homepage/README.md'):
        return current
    row = json.loads((root / 'tests/genpage_full_rewrite_hashes.json').read_text())['files'][path]
    assert hashlib.sha256(current).hexdigest() == row['after_sha256'], path
    assert row['prior_spans'], path
    lines = current.decode().splitlines(keepends=True)
    for start, end, old in reversed(row['prior_spans']):
        lines[start:end] = [old]
    data = ''.join(lines).encode()
    assert hashlib.sha256(data).hexdigest() == row['before_sha256'], path
    return data


def sona_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    if not path.startswith('papers/sona-yandex-music/'):
        return expected
    row = json.loads((root / 'tests/sona_full_rewrite_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def before_sona_full_rewrite(root, path, current):
    if path not in ('papers/sona-yandex-music/lab.yaml', 'papers/sona-yandex-music/README.md'):
        return current
    row = json.loads((root / 'tests/sona_full_rewrite_hashes.json').read_text())['files'][path]
    assert hashlib.sha256(current).hexdigest() == row['after_sha256'], path
    assert row['prior_spans'], path
    lines = current.decode().splitlines(keepends=True)
    for start, end, old in reversed(row['prior_spans']):
        lines[start:end] = [old]
    data = ''.join(lines).encode()
    assert hashlib.sha256(data).hexdigest() == row['before_sha256'], path
    return data


def tgr_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    if not path.startswith('papers/tgr/'):
        return expected
    row = json.loads((root / 'tests/tgr_full_rewrite_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def before_tgr_full_rewrite(root, path, current):
    if path not in ('papers/tgr/lab.yaml', 'papers/tgr/method.md'):
        return current
    row = json.loads((root / 'tests/tgr_full_rewrite_hashes.json').read_text())['files'][path]
    assert hashlib.sha256(current).hexdigest() == row['after_sha256'], path
    data = current.decode().splitlines(keepends=True)
    for start, end, old in reversed(row['prior_spans']):
        data[start:end] = [old]
    prior = ''.join(data).encode()
    assert hashlib.sha256(prior).hexdigest() == row['before_sha256'], path
    return prior


def harness_icegr_body_rows(root):
    return json.loads((root / 'tests/harness_icegr_full_rewrite_hashes.json').read_text())['files']


def harness_icegr_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    if not path.startswith(('papers/harness-bench/', 'papers/icegr-baidu-intent-generative-retrieval/')):
        return expected
    row = harness_icegr_body_rows(root).get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def before_harness_icegr_full_rewrite(root, path, current):
    if not path.startswith(('papers/harness-bench/', 'papers/icegr-baidu-intent-generative-retrieval/')):
        return current
    row = harness_icegr_body_rows(root).get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after_sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, old in reversed(row['prior_spans']):
        lines[start:stop] = [old]
    prior = ''.join(lines).encode()
    assert hashlib.sha256(prior).hexdigest() == row['before_sha256'], path
    return prior


def forecast_pair_body_rows(root):
    return json.loads((root / 'tests/forecast_pair_full_rewrite_hashes.json').read_text())['files']


def forecast_pair_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    if not path.startswith(('papers/t0-tsfm-forecasting-with-context/', 'papers/reasoncast-agentic-demand-forecasting/')):
        return expected
    row = forecast_pair_body_rows(root).get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def before_forecast_pair_full_rewrite(root, path, current):
    if not path.startswith(('papers/t0-tsfm-forecasting-with-context/', 'papers/reasoncast-agentic-demand-forecasting/')):
        return current
    row = forecast_pair_body_rows(root).get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after_sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, old in reversed(row['prior_spans']):
        lines[start:stop] = [old]
    prior = ''.join(lines).encode()
    assert hashlib.sha256(prior).hexdigest() == row['before_sha256'], path
    return prior


def semantic_id_pair_body_rows(root):
    return json.loads((root / 'tests/semantic_id_pair_full_rewrite_hashes.json').read_text())['files']


def semantic_id_pair_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    if not path.startswith(('papers/sidinspector-mapping-diagnostics/', 'papers/sidscope-diagnostics/')):
        return expected
    row = semantic_id_pair_body_rows(root).get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def before_semantic_id_pair_full_rewrite(root, path, current):
    if not path.startswith(('papers/sidinspector-mapping-diagnostics/', 'papers/sidscope-diagnostics/')):
        return current
    row = semantic_id_pair_body_rows(root).get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after_sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, old in reversed(row['prior_spans']):
        lines[start:stop] = [old]
    prior = ''.join(lines).encode()
    assert hashlib.sha256(prior).hexdigest() == row['before_sha256'], path
    return prior


def quasid_body_rows(root):
    return json.loads((root / 'tests/quasid_full_rewrite_hashes.json').read_text())['files']


def quasid_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    if not path.startswith(('papers/quasid-collision-qualified-sid/',)):
        return expected
    row = quasid_body_rows(root).get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def before_quasid_full_rewrite(root, path, current):
    if not path.startswith(('papers/quasid-collision-qualified-sid/',)):
        return current
    row = quasid_body_rows(root).get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after_sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, old in reversed(row['prior_spans']):
        lines[start:stop] = [old]
    prior = ''.join(lines).encode()
    assert hashlib.sha256(prior).hexdigest() == row['before_sha256'], path
    return prior


def sid_ope_body_rows(root):
    return json.loads((root / 'tests/sid_ope_full_rewrite_hashes.json').read_text())['files']


def sid_ope_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    if not path.startswith(('papers/sid-ope-hierarchy/',)):
        return expected
    row = sid_ope_body_rows(root).get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def before_sid_ope_full_rewrite(root, path, current):
    if not path.startswith(('papers/sid-ope-hierarchy/',)):
        return current
    row = sid_ope_body_rows(root).get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after_sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, old in reversed(row['prior_spans']):
        lines[start:stop] = [old]
    prior = ''.join(lines).encode()
    assert hashlib.sha256(prior).hexdigest() == row['before_sha256'], path
    return prior


def perishable_body_rows(root):
    return json.loads((root / 'tests/perishable_full_rewrite_hashes.json').read_text())['files']


def perishable_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    if not path.startswith(('papers/discounted-perishables-forecast/',)):
        return expected
    row = perishable_body_rows(root).get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def before_perishable_full_rewrite(root, path, current):
    if not path.startswith(('papers/discounted-perishables-forecast/',)):
        return current
    row = perishable_body_rows(root).get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after_sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, old in reversed(row['prior_spans']):
        lines[start:stop] = [old]
    prior = ''.join(lines).encode()
    assert hashlib.sha256(prior).hexdigest() == row['before_sha256'], path
    return prior


def switch_hurdle_body_rows(root):
    return json.loads((root / 'tests/switch_hurdle_full_rewrite_hashes.json').read_text())['files']


def switch_hurdle_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    if not path.startswith(('papers/switch-hurdle-intermittent-demand/',)):
        return expected
    row = switch_hurdle_body_rows(root).get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def before_switch_hurdle_full_rewrite(root, path, current):
    if not path.startswith(('papers/switch-hurdle-intermittent-demand/',)):
        return current
    row = switch_hurdle_body_rows(root).get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after_sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, old in reversed(row['prior_spans']):
        lines[start:stop] = [old]
    prior = ''.join(lines).encode()
    assert hashlib.sha256(prior).hexdigest() == row['before_sha256'], path
    return prior


def retail_grain_body_rows(root):
    return json.loads((root / 'tests/retail_grain_full_rewrite_hashes.json').read_text())['files']


def retail_grain_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    if not path.startswith(('papers/retail-forecast-decision-grain/',)):
        return expected
    row = retail_grain_body_rows(root).get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def before_retail_grain_full_rewrite(root, path, current):
    if not path.startswith(('papers/retail-forecast-decision-grain/',)):
        return current
    row = retail_grain_body_rows(root).get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after_sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, old in reversed(row['prior_spans']):
        lines[start:stop] = [old]
    prior = ''.join(lines).encode()
    assert hashlib.sha256(prior).hexdigest() == row['before_sha256'], path
    return prior


def forecast_critic_body_rows(root):
    return json.loads((root / 'tests/forecast_critic_full_rewrite_hashes.json').read_text())['files']


def forecast_critic_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    if not path.startswith(('papers/forecast-critic/',)):
        return expected
    row = forecast_critic_body_rows(root).get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def before_forecast_critic_full_rewrite(root, path, current):
    if not path.startswith(('papers/forecast-critic/',)):
        return current
    row = forecast_critic_body_rows(root).get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after_sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, old in reversed(row['prior_spans']):
        lines[start:stop] = [old]
    prior = ''.join(lines).encode()
    assert hashlib.sha256(prior).hexdigest() == row['before_sha256'], path
    return prior


def static_constrained_body_rows(root):
    return json.loads((root / 'tests/static_constrained_full_rewrite_hashes.json').read_text())['files']


def static_constrained_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    if not path.startswith(('papers/static-constrained-gr/',)):
        return expected
    row = static_constrained_body_rows(root).get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def before_static_constrained_full_rewrite(root, path, current):
    if not path.startswith(('papers/static-constrained-gr/',)):
        return current
    row = static_constrained_body_rows(root).get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after_sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, old in reversed(row['prior_spans']):
        lines[start:stop] = [old]
    prior = ''.join(lines).encode()
    assert hashlib.sha256(prior).hexdigest() == row['before_sha256'], path
    return prior


def wrapped_produce_body_rows(root):
    return json.loads((root / 'tests/wrapped_produce_full_rewrite_hashes.json').read_text())['files']


def wrapped_produce_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    if not path.startswith(('papers/wrapped-produce-placement-controlled-trial/',)):
        return expected
    row = wrapped_produce_body_rows(root).get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def before_wrapped_produce_full_rewrite(root, path, current):
    if not path.startswith(('papers/wrapped-produce-placement-controlled-trial/',)):
        return current
    row = wrapped_produce_body_rows(root).get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after_sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, old in reversed(row['prior_spans']):
        lines[start:stop] = [old]
    prior = ''.join(lines).encode()
    assert hashlib.sha256(prior).hexdigest() == row['before_sha256'], path
    return prior


def before_pinterest_full_rewrite(root, path, current):
    if not path.startswith('papers/pinterest-causal-retrieval-shopping/'):
        return current
    row = json.loads((root / 'tests/pinterest_full_rewrite_hashes.json').read_text())['files'][path]
    assert hashlib.sha256(current).hexdigest() == row['after_sha256'], path
    assert row['prior_spans'], path
    lines = current.decode().splitlines(keepends=True)
    for start, end, old in reversed(row['prior_spans']):
        lines[start:end] = [old]
    data = ''.join(lines).encode()
    assert hashlib.sha256(data).hexdigest() == row['before_sha256'], path
    return data


def revise_rewrite_receipt(root):
    return json.loads((root / 'tests/revise_full_rewrite_hashes.json').read_text())['files']


def revise_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    """Accept only the reviewed full REVISE text from the pinned overview version."""
    if not path.startswith('papers/revise-recovery/'):
        return expected
    row = revise_rewrite_receipt(root).get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def before_revise_full_rewrite(root, path, current):
    """Replay the earlier overview-only checks on their exact input."""
    if not path.startswith('papers/revise-recovery/'):
        return current
    row = revise_rewrite_receipt(root)[path]
    assert hashlib.sha256(current).hexdigest() == row['after_sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, old in reversed(row['prior_spans']):
        lines[start:stop] = [old]
    original = ''.join(lines).encode()
    assert hashlib.sha256(original).hexdigest() == row['before_sha256'], path
    return original



def or_transformer_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    """Accept only the exact reviewed OR-Transformer document bundle."""
    row = json.loads((root / 'tests/or_transformer_full_rewrite_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]



def diff_projection_source_version_hash(root, path, expected, algorithm='sha256'):
    """Accept only the verified source pin and distinct versioned comparison."""
    row = json.loads((root / 'tests/diff_projection_source_version_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def arxiv_versioned_overview_hash(root, path, expected, algorithm='sha256'):
    """Allow the exact summary and citations to the reviewed arXiv versions."""
    row = json.loads((root / 'tests/arxiv_versioned_overview_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def paper_overview_rewrite_hash(root, path, expected, algorithm='sha256'):
    """Permit the reviewed overview only on its exact previously reviewed file."""
    receipt = json.loads((root / 'tests/paper_overview_hashes.json').read_text())
    row = receipt['files'].get(path) or receipt.get('generated_from', {}).get(path) or receipt.get('mirrored', {}).get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def restored_before_paper_overview(root, path, raw):
    """Recover and verify the historical file for phase-specific byte checks."""
    row = json.loads((root / 'tests/paper_overview_hashes.json').read_text())['files'].get(path)
    if row is None:
        return raw
    assert hashlib.sha256(raw).hexdigest() == row['after_sha256'], path
    pattern = rb'^  overview: [^\n]+\n(?:    [^\n]+\n|\n(?=    [^\n]+\n))*'
    matches = list(re.finditer(pattern, raw, re.M))
    assert len(matches) == 1, path
    field = matches[0]
    assert hashlib.sha256(field.group()).hexdigest() == row['new_field_sha256'], path
    predecessor = raw[:field.start()] + row['prior_field'].encode() + raw[field.end():]
    assert hashlib.sha256(predecessor).hexdigest() == row['before_sha256'], path
    return predecessor


def root_readme_rewrite_hash(root, path, expected, algorithm='sha256'):
    """Recognize the exact rewritten root README without rewriting prior approvals."""
    if path != 'README.md':
        return expected
    row = json.loads((root / 'tests/root_readme_rewrite_hashes.json').read_text())['files'][path]
    assert expected == row['before_' + algorithm], path
    return root_readme_catalog_119_hash(root, path, row['after_' + algorithm], algorithm, historical=True)


def replenishment_guide_rewrite_hash(root, path, expected, algorithm='sha256'):
    """Apply the complete guide rewrite only to the exact preceding guide."""
    row = json.loads((root / 'tests/replenishment_guide_rewrite_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def replenishment_cards_rewrite_hash(root, path, expected, algorithm='sha256'):
    """Apply the seven evidence-card rewrites only from the exact prior bytes."""
    row = json.loads((root / 'tests/replenishment_cards_rewrite_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def replenishment_cards_followup_hash(root, path, expected, algorithm='sha256'):
    """Explain five terms only from the frozen rewrite bytes."""
    row = json.loads((root / 'tests/replenishment_cards_followup_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def hasterad_registration_hash(root, path, expected, algorithm='sha256'):
    """Accept the three exact README count corrections, not arbitrary changes."""
    row = json.loads((root / 'tests/hasterad_registration_hashes.json').read_text())['files'].get(path)
    if row is not None:
        assert expected == row['before_' + algorithm], path
        expected = row['after_' + algorithm]
    return dcdn_ono_registration_hash(root, path, expected, algorithm)


def dcdn_ono_registration_hash(root, path, expected, algorithm='sha256'):
    """Accept only the three README count corrections tied to these two papers."""
    row = json.loads((root / 'tests/dcdn_ono_registration_hashes.json').read_text())['files'].get(path)
    if row is not None:
        assert expected == row['before_' + algorithm], path
        expected = row['after_' + algorithm]
    return reference_guess_markup_hash(root, path, expected, algorithm)


def reference_guess_markup_hash(root, path, expected, algorithm='sha256'):
    """Accept only the exact option markup repair, independently of prose review."""
    row = json.loads((root / 'tests/reference_guess_markup_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def store_layout_field_example_hash(root, path, expected, algorithm='sha256'):
    """Recognize the reviewed store timing example only on its exact guide base."""
    row = json.loads((root / 'tests/store_layout_field_example_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return store_layout_calculation_hash(root, path, row['after_' + algorithm], algorithm)


def store_layout_calculation_hash(root, path, expected, algorithm='sha256'):
    """Accept the exact synthetic calculation addition from its reviewed predecessor."""
    if path != 'guides/store-layout-fixed-counts.md':
        return expected
    row = json.loads((root / 'tests/store_layout_calculation_hashes.json').read_text())
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def before_store_layout_calculation(root, raw):
    """Leave the earlier field example covered by its original byte guard."""
    row = json.loads((root / 'tests/store_layout_calculation_hashes.json').read_text())
    assert hashlib.sha256(raw).hexdigest() == row['after_sha256']
    section = row['section'].encode()
    new = row['after_end'].encode()
    assert raw.count(section) == raw.count(new) == 1
    old = raw.replace(section, b'', 1).replace(new, row['before_end'].encode(), 1)
    assert hashlib.sha256(old).hexdigest() == row['before_sha256']
    return old


def coral_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    """Recognize four exact source and authored CORAL identities; reject any other input."""
    row = json.loads((root / 'tests/coral_full_rewrite_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return coral_role_clarification_hash(root, path, row['after_' + algorithm], algorithm)


def coral_role_clarification_hash(root, path, expected, algorithm='sha256'):
    """Recognize only the exact published-to-clarified CORAL source transition."""
    row = json.loads((root / 'tests/coral_role_clarification_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def store_layout_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    """Permit only the separately recorded full fixed-count layout guide rewrite."""
    row = json.loads((root / 'tests/store_layout_full_rewrite_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return store_layout_normandy_hash(root, path, row['after_' + algorithm], algorithm)


def store_layout_normandy_hash(root, path, expected, algorithm='sha256'):
    """Add the verified Normandy abstract only to the exact reviewed prior guide."""
    row = json.loads((root / 'tests/store_layout_normandy_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return store_layout_field_example_hash(root, path, row['after_' + algorithm], algorithm)


def shelf_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    """Accept the reviewed shelf guide only from its exact prior identity."""
    row = json.loads((root / 'tests/shelf_full_rewrite_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return shelf_streicher_hash(root, path, row['after_' + algorithm], algorithm)


def shelf_streicher_hash(root, path, expected, algorithm='sha256'):
    """Approve only the exact published guide plus the reviewed aisle case."""
    row = json.loads((root / 'tests/shelf_streicher_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return shelf_tsukuba_hash(root, path, row['after_' + algorithm], algorithm)


def shelf_tsukuba_hash(root, path, expected, algorithm='sha256'):
    """Add the Tsukuba case only to the exact prior shelf guide."""
    row = json.loads((root / 'tests/shelf_tsukuba_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return shelf_hermans_hash(root, path, row['after_' + algorithm], algorithm)


def shelf_hermans_hash(root, path, expected, algorithm='sha256'):
    """Append the exact verified category sales case to its guide predecessor."""
    if path != 'guides/shelf-decisions.md':
        return expected
    row = json.loads((root / 'tests/shelf_hermans_hashes.json').read_text())
    assert expected == row['before_' + algorithm], path
    return shelf_asda_hash(root, path, row['after_' + algorithm], algorithm)


def generation_retrieval_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    """Permit only the recorded full rewrite of the generation-retrieval article."""
    row = json.loads((root / 'tests/generation_retrieval_full_rewrite_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def unipinrec_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    """Accept the revised Pinterest article only from exact historical inputs."""
    row = json.loads((root / 'tests/unipinrec_full_rewrite_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def wholefoods_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    """Translate only the exact reviewed Whole Foods article originals."""
    row = json.loads((root / 'tests/wholefoods_full_rewrite_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def contextual_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    """Translate only the reviewed contextual deconvolution article sources."""
    row = json.loads((root / 'tests/contextual_full_rewrite_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def zalando_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    """Translate only the exact reviewed Zalando article and figure prose."""
    row = json.loads((root / 'tests/zalando_full_rewrite_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def bridging_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    """Translate only the exact reviewed TruckParts article and display prose."""
    row = json.loads((root / 'tests/bridging_full_rewrite_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def tsfm_sparse_rewrite_hash(root, path, expected, algorithm='sha256'):
    """Accept only the four reviewed sparse-event Lab prose revisions."""
    row = json.loads((root / 'tests/tsfm_sparse_rewrite_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def sim2real_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    """Permit only exact before/after identities for the SIM2REAL prose."""
    row = json.loads((root / 'tests/sim2real_full_rewrite_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def index_copy_rewrite_hash(root, path, expected, algorithm='sha256'):
    """Recognize only the reviewed homepage copy from its exact prior identity."""
    if path != 'paper_lab/templates/index.html':
        return expected
    row = json.loads((root / 'tests/index_copy_rewrite_hashes.json').read_text())['files'][path]
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def linkedin_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    """Permit only the exact reviewed LinkedIn reader-facing source transition."""
    row = json.loads((root / 'tests/linkedin_full_rewrite_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def accuracy_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    """Allow only the exact reviewed Accuracy Is Not Service copy changes."""
    row = json.loads((root / 'tests/accuracy_full_rewrite_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def walmart_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    """Permit only the seven reviewed Walmart changes from exact prior inputs."""
    row = json.loads((root / 'tests/walmart_full_rewrite_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def placement_options_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    """Accept only the eleven exact draft placement copy updates from known bytes."""
    row = json.loads((root / 'tests/placement_options_full_rewrite_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def storewide_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    """Match only the exact known source and rewritten content for this Lab."""
    row = json.loads((root / 'tests/storewide_full_rewrite_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def assortment_observation_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    """Require exact prior and rewritten bytes for the nine reviewed prose files."""
    row = json.loads((root / 'tests/assortment_observation_full_rewrite_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def prepared_catalog_registration_hash(root, path, expected, algorithm='sha256'):
    """Apply exactly the catalog count update after all older reviewed edits."""
    row = json.loads((root / 'tests/prepared_catalog_registration_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return receipt_catalog_registration_hash(root, path, row['after_' + algorithm], algorithm)


def receipt_catalog_registration_hash(root, path, expected, algorithm='sha256'):
    """Preserve the first catalog review and accept only the next exact count."""
    row = json.loads((root / 'tests/receipt_catalog_registration_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def root_readme_catalog_119_hash(root, path, expected, algorithm='sha256', *, historical=False):
    """Port previously reviewed prose onto the current exact catalog size."""
    row = json.loads((root / 'tests/root_readme_catalog_119_hashes.json').read_text())['files'][path]
    key = 'reviewed_' if historical else 'before_'
    assert expected == row[key + algorithm], path
    return shelf_asda_hash(root, path, row['after_' + algorithm], algorithm)


def shelf_asda_hash(root, path, expected, algorithm='sha256'):
    row = json.loads((root / 'tests/shelf_asda_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def weather_cutoff_rewrite_hash(root, path, expected, algorithm='sha256'):
    if path != 'guides/forecast-to-replenishment.md':
        return expected
    row = json.loads((root / 'tests/replenishment_weather_cutoff_hashes.json').read_text())
    assert row['file'] == path and expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_weather_cutoff(root, path, current):
    if path != 'guides/forecast-to-replenishment.md':
        return current
    row = json.loads((root / 'tests/replenishment_weather_cutoff_hashes.json').read_text())
    assert row['file'] == path and hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    block = row['inserted'].encode()
    assert current.count(block) == 1
    prior = current.replace(block, b'', 1)
    assert hashlib.sha256(prior).hexdigest() == row['before']['sha256'], path
    return prior
