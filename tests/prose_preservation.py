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
    """Reverse the present article edit before examining the protected earlier copy."""
    content = before_assortment_all_full_prose(root, path, content.encode()).decode()
    content = before_assortment_full_prose(root, path, content.encode()).decode()
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
            return retailbench_full_prose_hash(root, path, row['after_' + algorithm], algorithm)
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
    expected = assortment_observation_reader_assets_hash(root, path, expected, algorithm)
    expected = zalando_reader_full_prose_hash(root, path, expected, algorithm)
    expected = bridging_reader_full_prose_hash(root, path, expected, algorithm)
    expected = revise_full_rewrite_hash(root, path, expected, algorithm)
    expected = pinterest_full_rewrite_hash(root, path, expected, algorithm)
    expected = unir2_full_rewrite_hash(root, path, expected, algorithm)
    expected = unir2_reader_assets_hash(root, path, expected, algorithm)
    expected = genpage_full_rewrite_hash(root, path, expected, algorithm)
    expected = sona_full_rewrite_hash(root, path, expected, algorithm)
    expected = tgr_full_rewrite_hash(root, path, expected, algorithm)
    expected = harness_icegr_full_rewrite_hash(root, path, expected, algorithm)
    expected = forecast_pair_full_rewrite_hash(root, path, expected, algorithm)
    expected = semantic_id_pair_full_rewrite_hash(root, path, expected, algorithm)
    expected = quasid_full_rewrite_hash(root, path, expected, algorithm)
    expected = quasid_reader_assets_hash(root, path, expected, algorithm)
    expected = weather_cutoff_rewrite_hash(root, path, expected, algorithm)
    expected = axial_ingredient_order_hash(root, path, expected, algorithm)
    expected = stockout_example_hash(root, path, expected, algorithm)
    expected = sid_ope_full_rewrite_hash(root, path, expected, algorithm)
    expected = sid_ope_reader_full_prose_hash(root, path, expected, algorithm)
    expected = perishable_full_rewrite_hash(root, path, expected, algorithm)
    expected = perishables_reader_assets_hash(root, path, expected, algorithm)
    expected = switch_hurdle_full_rewrite_hash(root, path, expected, algorithm)
    expected = retail_grain_full_rewrite_hash(root, path, expected, algorithm)
    expected = forecast_critic_full_rewrite_hash(root, path, expected, algorithm)
    expected = static_constrained_full_rewrite_hash(root, path, expected, algorithm)
    expected = wrapped_produce_full_rewrite_hash(root, path, expected, algorithm)
    expected = ono_full_rewrite_hash(root, path, expected, algorithm)
    expected = dcdn_full_prose_hash(root, path, expected, algorithm)
    expected = ahe_full_prose_hash(root, path, expected, algorithm)
    expected = flashtrie_full_prose_hash(root, path, expected, algorithm)
    expected = unique_full_prose_hash(root, path, expected, algorithm)
    expected = ogr_full_prose_hash(root, path, expected, algorithm)
    expected = intervention_full_prose_hash(root, path, expected, algorithm)
    expected = vn2_full_prose_hash(root, path, expected, algorithm)
    expected = assortment_full_prose_hash(root, path, expected, algorithm)
    expected = hasterad_full_prose_hash(root, path, expected, algorithm)
    expected = orpr_full_prose_hash(root, path, expected, algorithm)
    expected = deepstock_full_prose_hash(root, path, expected, algorithm)
    expected = source_overview_correction_hash(root, path, expected, algorithm)
    expected = invevolve_full_prose_hash(root, path, expected, algorithm)
    expected = sabreagent_full_prose_hash(root, path, expected, algorithm)
    expected = igpo_full_prose_hash(root, path, expected, algorithm)
    expected = proximal_full_prose_hash(root, path, expected, algorithm)
    expected = radfl_full_prose_hash(root, path, expected, algorithm)
    expected = diff_projection_full_prose_hash(root, path, expected, algorithm)
    expected = fbsde_full_prose_hash(root, path, expected, algorithm)
    expected = scope_full_prose_hash(root, path, expected, algorithm)
    expected = isomorph_full_prose_hash(root, path, expected, algorithm)
    expected = exaone_full_prose_hash(root, path, expected, algorithm)
    expected = eval_grain_full_prose_hash(root, path, expected, algorithm)
    expected = traffic_value_full_prose_hash(root, path, expected, algorithm)
    expected = retailbench_full_prose_hash(root, path, expected, algorithm)
    expected = agentx_full_prose_hash(root, path, expected, algorithm)
    expected = pilot_full_prose_hash(root, path, expected, algorithm)
    expected = autorecsys_full_prose_hash(root, path, expected, algorithm)
    expected = evopilot_full_prose_hash(root, path, expected, algorithm)
    expected = aura_full_prose_hash(root, path, expected, algorithm)
    expected = autolr_full_prose_hash(root, path, expected, algorithm)
    expected = multi_harness_full_prose_hash(root, path, expected, algorithm)
    expected = apollopfn_full_prose_hash(root, path, expected, algorithm)
    expected = otto_full_prose_hash(root, path, expected, algorithm)
    expected = angle_full_prose_hash(root, path, expected, algorithm)
    expected = hear_full_prose_hash(root, path, expected, algorithm)
    expected = series_full_prose_hash(root, path, expected, algorithm)
    expected = uvr_full_prose_hash(root, path, expected, algorithm)
    expected = grace_full_prose_hash(root, path, expected, algorithm)
    expected = common_threshold_full_prose_hash(root, path, expected, algorithm)
    expected = gatesid_full_prose_hash(root, path, expected, algorithm)
    expected = dsi_full_prose_hash(root, path, expected, algorithm)
    expected = netflix_counterfactual_full_prose_hash(root, path, expected, algorithm)
    expected = glide_full_prose_hash(root, path, expected, algorithm)
    expected = overview_figure_relocations_hash(root, path, expected, algorithm)
    expected = hgenpush_full_prose_hash(root, path, expected, algorithm)
    expected = agenttether_full_prose_hash(root, path, expected, algorithm)
    expected = stockout_full_prose_hash(root, path, expected, algorithm)
    expected = onetrans_full_prose_hash(root, path, expected, algorithm)
    expected = spotify_causal_full_prose_hash(root, path, expected, algorithm)
    expected = youtube_rationales_full_prose_hash(root, path, expected, algorithm)
    expected = unirec_full_prose_hash(root, path, expected, algorithm)
    expected = lige_full_prose_hash(root, path, expected, algorithm)
    expected = oxygenrec_full_prose_hash(root, path, expected, algorithm)
    expected = varg_full_prose_hash(root, path, expected, algorithm)
    expected = pushdualgen_full_prose_hash(root, path, expected, algorithm)
    expected = oneranker_full_prose_hash(root, path, expected, algorithm)
    expected = muser_full_prose_hash(root, path, expected, algorithm)
    expected = univa_full_prose_hash(root, path, expected, algorithm)
    expected = sam_full_prose_hash(root, path, expected, algorithm)
    expected = rest_full_prose_hash(root, path, expected, algorithm)
    expected = gr4ad_full_prose_hash(root, path, expected, algorithm)
    expected = gryphonv2_full_prose_hash(root, path, expected, algorithm)
    expected = gryphonilsm_full_prose_hash(root, path, expected, algorithm)
    expected = isd_full_prose_hash(root, path, expected, algorithm)
    expected = snaplgr_full_prose_hash(root, path, expected, algorithm)
    expected = tmall_full_prose_hash(root, path, expected, algorithm)
    expected = recevolve_full_prose_hash(root, path, expected, algorithm)
    expected = dream_full_prose_hash(root, path, expected, algorithm)
    expected = reusegr_full_prose_hash(root, path, expected, algorithm)
    expected = bitemporal_full_prose_hash(root, path, expected, algorithm)
    expected = harnesstokens_full_prose_hash(root, path, expected, algorithm)
    expected = forgetting_iclr_full_prose_hash(root, path, expected, algorithm)
    expected = deletion_prefix_full_prose_hash(root, path, expected, algorithm)
    expected = scaffold_gaia_full_prose_hash(root, path, expected, algorithm)
    expected = wholefoods_all_full_prose_hash(root, path, expected, algorithm)
    expected = wrapped_all_full_prose_hash(root, path, expected, algorithm)
    expected = storewide_all_full_prose_hash(root, path, expected, algorithm)
    expected = retail_grain_all_full_prose_hash(root, path, expected, algorithm)
    expected = switch_hurdle_all_full_prose_hash(root, path, expected, algorithm)
    expected = sim2real_all_full_prose_hash(root, path, expected, algorithm)
    expected = assortment_all_full_prose_hash(root, path, expected, algorithm)
    expected = or_transformer_all_full_prose_hash(root, path, expected, algorithm)
    expected = reasoncast_all_full_prose_hash(root, path, expected, algorithm)
    expected = forecast_critic_all_full_prose_hash(root, path, expected, algorithm)
    expected = t0_context_all_full_prose_hash(root, path, expected, algorithm)
    expected = placement_and_vn2_asset_prose_hash(root, path, expected, algorithm)
    expected = flashvector_all_full_prose_hash(root, path, expected, algorithm)
    expected = ono_reader_all_full_prose_hash(root, path, expected, algorithm)
    expected = sparse_reader_all_full_prose_hash(root, path, expected, algorithm)
    expected = sparse_inspection_full_prose_hash(root, path, expected, algorithm)
    expected = sgc_all_full_prose_hash(root, path, expected, algorithm)
    expected = tgr_reader_all_full_prose_hash(root, path, expected, algorithm)
    expected = genpage_reader_full_prose_hash(root, path, expected, algorithm)
    expected = harness_zero_all_full_prose_hash(root, path, expected, algorithm)
    expected = tagr_all_full_prose_hash(root, path, expected, algorithm)
    expected = swe_serve_full_prose_hash(root, path, expected, algorithm)
    expected = harness_r1_full_prose_hash(root, path, expected, algorithm)
    expected = episem_full_prose_hash(root, path, expected, algorithm)
    expected = execution_state_unlearning_full_prose_hash(root, path, expected, algorithm)
    expected = featurearc_full_prose_hash(root, path, expected, algorithm)
    expected = contextual_all_full_prose_hash(root, path, expected, algorithm)
    expected = trace_all_full_prose_hash(root, path, expected, algorithm)
    return trial_trace_all_full_prose_hash(root, path, expected, algorithm)


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
    previous = shelf_asda_hash(root, path, row['after_' + algorithm], algorithm)
    next_count = json.loads((root / 'tests/root_readme_catalog_120_hashes.json').read_text())
    assert previous == next_count['before'][algorithm], path
    previous = next_count['after'][algorithm]
    next_count = json.loads((root / 'tests/root_readme_catalog_121_hashes.json').read_text())
    assert previous == next_count['before'][algorithm], path
    return next_count['after'][algorithm]


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
    current = before_axial_ingredient_order(root, path, before_stockout_example(root, path, current))
    row = json.loads((root / 'tests/replenishment_weather_cutoff_hashes.json').read_text())
    assert row['file'] == path and hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    block = row['inserted'].encode()
    assert current.count(block) == 1
    prior = current.replace(block, b'', 1)
    assert hashlib.sha256(prior).hexdigest() == row['before']['sha256'], path
    return prior


def axial_ingredient_order_hash(root, path, expected, algorithm='sha256'):
    if path != 'guides/forecast-to-replenishment.md':
        return expected
    row = json.loads((root / 'tests/replenishment_axial_hashes.json').read_text())
    assert row['file'] == path and expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_axial_ingredient_order(root, path, current):
    if path != 'guides/forecast-to-replenishment.md':
        return current
    row = json.loads((root / 'tests/replenishment_axial_hashes.json').read_text())
    assert row['file'] == path and hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    block = row['inserted'].encode()
    assert current.count(block) == 1
    prior = current.replace(block, b'', 1)
    assert hashlib.sha256(prior).hexdigest() == row['before']['sha256'], path
    return prior


def stockout_example_hash(root, path, expected, algorithm='sha256'):
    if path != 'guides/forecast-to-replenishment.md':
        return expected
    row = json.loads((root / 'tests/replenishment_stockout_hashes.json').read_text())
    assert row['file'] == path and expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_stockout_example(root, path, current):
    if path != 'guides/forecast-to-replenishment.md':
        return current
    row = json.loads((root / 'tests/replenishment_stockout_hashes.json').read_text())
    assert row['file'] == path and hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    block = row['inserted'].encode()
    assert current.count(block) == 1, path
    prior = current.replace(block, b'', 1)
    assert hashlib.sha256(prior).hexdigest() == row['before']['sha256'], path
    return prior


def ono_body_rows(root):
    return json.loads((root / 'tests/ono_full_rewrite_hashes.json').read_text())['files']


def ono_full_rewrite_hash(root, path, expected, algorithm='sha256'):
    if not (path.startswith('papers/ono-inventory-forecast-selection/') or path == 'paper_lab/ono_inventory.py'):
        return expected
    row = ono_body_rows(root).get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def before_ono_full_rewrite(root, path, current):
    if not (path.startswith('papers/ono-inventory-forecast-selection/') or path == 'paper_lab/ono_inventory.py'):
        return current
    row = ono_body_rows(root).get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after_sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, old in reversed(row['prior_spans']):
        lines[start:stop] = [old]
    prior = ''.join(lines).encode()
    assert hashlib.sha256(prior).hexdigest() == row['before_sha256'], path
    return prior


def dcdn_prose_rows(root):
    return json.loads((root / 'tests/dcdn_full_prose_hashes.json').read_text())['files']


def dcdn_full_prose_hash(root, path, expected, algorithm='sha256'):
    if not path.startswith('papers/deep-cross-division/'):
        return expected
    row = dcdn_prose_rows(root).get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def before_dcdn_full_prose(root, path, current):
    if not path.startswith('papers/deep-cross-division/'):
        return current
    row = dcdn_prose_rows(root).get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after_sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, old in reversed(row['prior_spans']):
        lines[start:stop] = [old]
    prior = ''.join(lines).encode()
    assert hashlib.sha256(prior).hexdigest() == row['before_sha256'], path
    return prior


def ahe_prose_rows(root):
    return json.loads((root / 'tests/ahe_full_prose_hashes.json').read_text())['files']


def ahe_full_prose_hash(root, path, expected, algorithm='sha256'):
    if not path.startswith('papers/ahe-beta-receipt/'):
        return expected
    row = ahe_prose_rows(root).get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def before_ahe_full_prose(root, path, current):
    if not path.startswith('papers/ahe-beta-receipt/'):
        return current
    row = ahe_prose_rows(root).get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after_sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, old in reversed(row['prior_spans']):
        lines[start:stop] = [old]
    prior = ''.join(lines).encode()
    assert hashlib.sha256(prior).hexdigest() == row['before_sha256'], path
    return prior


def flashtrie_full_prose_hash(root, path, expected, algorithm='sha256'):
    if not path.startswith('papers/flashtrie-gpu-beam/'):
        return expected
    row = json.loads((root / 'tests/flashtrie_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_flashtrie_full_prose(root, path, current):
    if not path.startswith('papers/flashtrie-gpu-beam/'):
        return current
    row = json.loads((root / 'tests/flashtrie_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, old in reversed(row['prior_spans']):
        lines[start:stop] = [old]
    prior = ''.join(lines).encode()
    assert hashlib.sha256(prior).hexdigest() == row['before']['sha256'], path
    return prior


def unique_full_prose_hash(root, path, expected, algorithm='sha256'):
    if not path.startswith('papers/unique-baidu-unified-retrieval-ranking/'):
        return expected
    row = json.loads((root / 'tests/unique_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_unique_full_prose(root, path, current):
    if not path.startswith('papers/unique-baidu-unified-retrieval-ranking/'):
        return current
    row = json.loads((root / 'tests/unique_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, old in reversed(row['prior_spans']):
        lines[start:stop] = [old]
    prior = ''.join(lines).encode()
    assert hashlib.sha256(prior).hexdigest() == row['before']['sha256'], path
    return prior


def ogr_full_prose_hash(root, path, expected, algorithm='sha256'):
    if not path.startswith('papers/ogr-once-generated-ranked/'):
        return expected
    row = json.loads((root / 'tests/ogr_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_ogr_full_prose(root, path, current):
    if not path.startswith('papers/ogr-once-generated-ranked/'):
        return current
    row = json.loads((root / 'tests/ogr_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, old in reversed(row['prior_spans']):
        lines[start:stop] = [old]
    prior = ''.join(lines).encode()
    assert hashlib.sha256(prior).hexdigest() == row['before']['sha256'], path
    return prior


def intervention_full_prose_hash(root, path, expected, algorithm='sha256'):
    if not path.startswith('papers/intervention-paradox/'):
        return expected
    row = json.loads((root / 'tests/intervention_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_intervention_full_prose(root, path, current):
    if not path.startswith('papers/intervention-paradox/'):
        return current
    row = json.loads((root / 'tests/intervention_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, old in reversed(row['prior_spans']):
        lines[start:stop] = [old]
    prior = ''.join(lines).encode()
    assert hashlib.sha256(prior).hexdigest() == row['before']['sha256'], path
    return prior


def vn2_full_prose_hash(root, path, expected, algorithm='sha256'):
    if not path.startswith('papers/vn2-stockout-catboost/'):
        return expected
    row = json.loads((root / 'tests/vn2_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_vn2_full_prose(root, path, current):
    if not path.startswith('papers/vn2-stockout-catboost/'):
        return current
    row = json.loads((root / 'tests/vn2_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, old in reversed(row['prior_spans']):
        lines[start:stop] = [old]
    prior = ''.join(lines).encode()
    assert hashlib.sha256(prior).hexdigest() == row['before']['sha256'], path
    return prior


def assortment_full_prose_hash(root, path, expected, algorithm='sha256'):
    if not path.startswith('papers/assortment-replenishment-hard-constraints/'):
        return expected
    row = json.loads((root / 'tests/assortment_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_assortment_full_prose(root, path, current):
    if not path.startswith('papers/assortment-replenishment-hard-constraints/'):
        return current
    row = json.loads((root / 'tests/assortment_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, old in reversed(row['prior_spans']):
        lines[start:stop] = [old]
    prior = ''.join(lines).encode()
    assert hashlib.sha256(prior).hexdigest() == row['before']['sha256'], path
    return prior


def hasterad_full_prose_hash(root, path, expected, algorithm='sha256'):
    if not path.startswith('papers/hasterad-retail-substitution/'):
        return expected
    row = json.loads((root / 'tests/hasterad_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_hasterad_full_prose(root, path, current):
    if not path.startswith('papers/hasterad-retail-substitution/'):
        return current
    row = json.loads((root / 'tests/hasterad_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def orpr_full_prose_hash(root, path, expected, algorithm='sha256'):
    if path != 'paper_lab/inventory02.py' and not path.startswith('papers/orpr-or-guided-pretrain-reinforce-inventory/'):
        return expected
    row = json.loads((root / 'tests/orpr_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_orpr_full_prose(root, path, current):
    if path != 'paper_lab/inventory02.py' and not path.startswith('papers/orpr-or-guided-pretrain-reinforce-inventory/'):
        return current
    row = json.loads((root / 'tests/orpr_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


from source_overview_corrections import source_overview_correction_hash


def deepstock_full_prose_hash(root, path, expected, algorithm='sha256'):
    if path != 'paper_lab/deepstock01.py' and not path.startswith('papers/deepstock-policy-regularized-inventory-drl/'):
        return expected
    row = json.loads((root / 'tests/deepstock_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_deepstock_full_prose(root, path, current):
    if path != 'paper_lab/deepstock01.py' and not path.startswith('papers/deepstock-policy-regularized-inventory-drl/'):
        return current
    row = json.loads((root / 'tests/deepstock_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def invevolve_full_prose_hash(root, path, expected, algorithm='sha256'):
    if path != 'paper_lab/invevolve30.py' and not path.startswith('papers/invevolve-whitebox-inventory-evolution/'):
        return expected
    row = json.loads((root / 'tests/invevolve_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_invevolve_full_prose(root, path, current):
    if path != 'paper_lab/invevolve30.py' and not path.startswith('papers/invevolve-whitebox-inventory-evolution/'):
        return current
    row = json.loads((root / 'tests/invevolve_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def sabreagent_full_prose_hash(root, path, expected, algorithm='sha256'):
    if path != 'paper_lab/batch29.py' and not path.startswith('papers/sabreagent-design-time-inventory/'):
        return expected
    row = json.loads((root / 'tests/sabreagent_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_sabreagent_full_prose(root, path, current):
    if path != 'paper_lab/batch29.py' and not path.startswith('papers/sabreagent-design-time-inventory/'):
        return current
    row = json.loads((root / 'tests/sabreagent_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def igpo_full_prose_hash(root, path, expected, algorithm='sha256'):
    if path != 'paper_lab/display_labels.py' and not path.startswith('papers/igpo-huawei-inventory-grounded-search/'):
        return expected
    row = json.loads((root / 'tests/igpo_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_igpo_full_prose(root, path, current):
    if path != 'paper_lab/display_labels.py' and not path.startswith('papers/igpo-huawei-inventory-grounded-search/'):
        return current
    row = json.loads((root / 'tests/igpo_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def proximal_full_prose_hash(root, path, expected, algorithm='sha256'):
    if path != 'paper_lab/inventory02.py' and not path.startswith('papers/proximal-residual-value-inventory-placement/'):
        return expected
    row = json.loads((root / 'tests/proximal_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_proximal_full_prose(root, path, current):
    if path != 'paper_lab/inventory02.py' and not path.startswith('papers/proximal-residual-value-inventory-placement/'):
        return current
    row = json.loads((root / 'tests/proximal_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def radfl_full_prose_hash(root, path, expected, algorithm='sha256'):
    if path != 'paper_lab/inventory02.py' and not path.startswith('papers/ra-dfl-risk-aware-decision-focused-inventory/'):
        return expected
    row = json.loads((root / 'tests/radfl_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_radfl_full_prose(root, path, current):
    if path != 'paper_lab/inventory02.py' and not path.startswith('papers/ra-dfl-risk-aware-decision-focused-inventory/'):
        return current
    row = json.loads((root / 'tests/radfl_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def diff_projection_full_prose_hash(root, path, expected, algorithm='sha256'):
    if path != 'paper_lab/projection01.py' and not path.startswith('papers/diff-projection-feasible-multi-echelon-inventory/'):
        return expected
    row = json.loads((root / 'tests/diff_projection_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_diff_projection_full_prose(root, path, current):
    if path != 'paper_lab/projection01.py' and not path.startswith('papers/diff-projection-feasible-multi-echelon-inventory/'):
        return current
    row = json.loads((root / 'tests/diff_projection_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def fbsde_full_prose_hash(root, path, expected, algorithm='sha256'):
    if path != 'paper_lab/fbsde30.py' and not path.startswith('papers/constrained-deep-inventory-fbsde/'):
        return expected
    row = json.loads((root / 'tests/fbsde_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_fbsde_full_prose(root, path, current):
    if path != 'paper_lab/fbsde30.py' and not path.startswith('papers/constrained-deep-inventory-fbsde/'):
        return current
    row = json.loads((root / 'tests/fbsde_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def scope_full_prose_hash(root, path, expected, algorithm='sha256'):
    if path != 'paper_lab/batch28.py' and not path.startswith('papers/scope-coupled-supply-chain-policies/'):
        return expected
    row = json.loads((root / 'tests/scope_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_scope_full_prose(root, path, current):
    if path != 'paper_lab/batch28.py' and not path.startswith('papers/scope-coupled-supply-chain-policies/'):
        return current
    row = json.loads((root / 'tests/scope_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def isomorph_full_prose_hash(root, path, expected, algorithm='sha256'):
    if path != 'paper_lab/isomorph30.py' and not path.startswith('papers/isomorph-supply-chain-digital-twin/'):
        return expected
    row = json.loads((root / 'tests/isomorph_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_isomorph_full_prose(root, path, current):
    if path != 'paper_lab/isomorph30.py' and not path.startswith('papers/isomorph-supply-chain-digital-twin/'):
        return current
    row = json.loads((root / 'tests/isomorph_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def exaone_full_prose_hash(root, path, expected, algorithm='sha256'):
    if path != 'paper_lab/exaone05.py' and not path.startswith('papers/exaone-demand-routed-tsfm/'):
        return expected
    row = json.loads((root / 'tests/exaone_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_exaone_full_prose(root, path, current):
    if path != 'paper_lab/exaone05.py' and not path.startswith('papers/exaone-demand-routed-tsfm/'):
        return current
    row = json.loads((root / 'tests/exaone_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def eval_grain_full_prose_hash(root, path, expected, algorithm='sha256'):
    if path != 'paper_lab/batch28.py' and not path.startswith('papers/evaluation-choices-forecasting-leaderboard/'):
        return expected
    row = json.loads((root / 'tests/eval_grain_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_eval_grain_full_prose(root, path, current):
    if path != 'paper_lab/batch28.py' and not path.startswith('papers/evaluation-choices-forecasting-leaderboard/'):
        return current
    row = json.loads((root / 'tests/eval_grain_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def traffic_value_full_prose_hash(root, path, expected, algorithm='sha256'):
    if path not in ('paper_lab/batch08.py', 'paper_lab/display_labels.py') and not path.startswith('papers/traffic-forecast-to-decision-value/'):
        return expected
    row = json.loads((root / 'tests/traffic_value_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_traffic_value_full_prose(root, path, current):
    if path not in ('paper_lab/batch08.py', 'paper_lab/display_labels.py') and not path.startswith('papers/traffic-forecast-to-decision-value/'):
        return current
    row = json.loads((root / 'tests/traffic_value_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous



def retailbench_full_prose_row(root, path):
    if path != 'paper_lab/retailbench30.py' and not path.startswith('papers/retailbench-long-horizon-store-agents/'):
        return None
    rows = json.loads((root / 'tests/retailbench_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def retailbench_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = retailbench_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_retailbench_full_prose(root, path, current):
    row = retailbench_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def agentx_full_prose_row(root, path):
    if not path.startswith('papers/agentx-kuaishou/'):
        return None
    rows = json.loads((root / 'tests/agentx_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def agentx_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = agentx_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_agentx_full_prose(root, path, current):
    row = agentx_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def pilot_full_prose_row(root, path):
    if not path.startswith('papers/pilot-experiment-lifecycle/'):
        return None
    rows = json.loads((root / 'tests/pilot_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def pilot_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = pilot_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_pilot_full_prose(root, path, current):
    row = pilot_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def autorecsys_full_prose_row(root, path):
    if not path.startswith('papers/auto-recsys-harness/'):
        return None
    rows = json.loads((root / 'tests/autorecsys_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def autorecsys_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = autorecsys_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_autorecsys_full_prose(root, path, current):
    row = autorecsys_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def evopilot_full_prose_row(root, path):
    if not path.startswith('papers/evopilot-verify-dont-trust-autoresearch/'):
        return None
    rows = json.loads((root / 'tests/evopilot_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def evopilot_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = evopilot_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_evopilot_full_prose(root, path, current):
    row = evopilot_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def aura_full_prose_row(root, path):
    if not path.startswith('papers/aura-disney-agentic-rec-diagnosis/'):
        return None
    rows = json.loads((root / 'tests/aura_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def aura_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = aura_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_aura_full_prose(root, path, current):
    row = aura_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def autolr_full_prose_row(root, path):
    if path != 'paper_lab/display_labels.py' and not path.startswith('papers/autolr-dashen/'):
        return None
    rows = json.loads((root / 'tests/autolr_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def autolr_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = autolr_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_autolr_full_prose(root, path, current):
    row = autolr_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def multi_harness_full_prose_row(root, path):
    if not path.startswith('papers/multi-harness-rl/'):
        return None
    rows = json.loads((root / 'tests/multi_harness_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def multi_harness_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = multi_harness_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_multi_harness_full_prose(root, path, current):
    row = multi_harness_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def apollopfn_full_prose_row(root, path):
    if path != 'papers/_toy_common.py' and not path.startswith('papers/apollopfn/'):
        return None
    rows = json.loads((root / 'tests/apollopfn_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def apollopfn_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = apollopfn_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_apollopfn_full_prose(root, path, current):
    if path == 'papers/_toy_common.py':
        current = before_rest_full_prose(root, path, current)
    row = apollopfn_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def otto_full_prose_row(root, path):
    if not path.startswith('papers/otto-gbdt-vs-dnn-ltr/'):
        return None
    rows = json.loads((root / 'tests/otto_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def otto_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = otto_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_otto_full_prose(root, path, current):
    row = otto_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def angle_full_prose_row(root, path):
    if not path.startswith('papers/angle-tencent-one-step-retrieval/'):
        return None
    rows = json.loads((root / 'tests/angle_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def angle_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = angle_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_angle_full_prose(root, path, current):
    row = angle_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def hear_full_prose_row(root, path):
    if path != 'paper_lab/batch08.py' and not path.startswith('papers/hear-harness-engine-serving-protocol/'):
        return None
    rows = json.loads((root / 'tests/hear_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def hear_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = hear_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_hear_full_prose(root, path, current):
    row = hear_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def series_full_prose_row(root, path):
    if not path.startswith('papers/series-wise-validation/'):
        return None
    rows = json.loads((root / 'tests/series_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def series_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = series_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_series_full_prose(root, path, current):
    row = series_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def uvr_full_prose_row(root, path):
    if path != 'paper_lab/display_labels.py' and not path.startswith('papers/uvr-wolt-trial-reorder/'):
        return None
    rows = json.loads((root / 'tests/uvr_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def uvr_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = uvr_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_uvr_full_prose(root, path, current):
    row = uvr_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def grace_full_prose_row(root, path):
    if path != 'paper_lab/display_labels.py' and not path.startswith('papers/grace-meta-ads-gtm-serving/'):
        return None
    rows = json.loads((root / 'tests/grace_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def grace_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = grace_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_grace_full_prose(root, path, current):
    row = grace_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def common_threshold_full_prose_row(root, path):
    if path != 'paper_lab/inventory_ct.py' and not path.startswith('papers/inventory-common-threshold-history/'):
        return None
    rows = json.loads((root / 'tests/common_threshold_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def common_threshold_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = common_threshold_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_common_threshold_full_prose(root, path, current):
    row = common_threshold_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def gatesid_full_prose_row(root, path):
    if path != 'paper_lab/templates/interactives.js' and not path.startswith('papers/gatesid-coldstart-ranking/'):
        return None
    rows = json.loads((root / 'tests/gatesid_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def gatesid_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = gatesid_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_gatesid_full_prose(root, path, current):
    row = gatesid_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def dsi_full_prose_row(root, path):
    if not path.startswith('papers/beyond-scalar-dsi-watchtime/'):
        return None
    rows = json.loads((root / 'tests/dsi_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def dsi_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = dsi_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_dsi_full_prose(root, path, current):
    row = dsi_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def netflix_counterfactual_full_prose_row(root, path):
    if not path.startswith('papers/netflix-counterfactual-observability/'):
        return None
    rows = json.loads((root / 'tests/netflix_counterfactual_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def netflix_counterfactual_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = netflix_counterfactual_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_netflix_counterfactual_full_prose(root, path, current):
    row = netflix_counterfactual_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def glide_full_prose_row(root, path):
    if not path.startswith('papers/glide-spotify-sid/'):
        return None
    rows = json.loads((root / 'tests/glide_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def glide_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = glide_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_glide_full_prose(root, path, current):
    row = glide_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def overview_figure_relocations_row(root, path):
    if path not in ('papers/agentx-kuaishou/lab.yaml','papers/genpage-netflix-homepage/lab.yaml'):
        return None
    rows = json.loads((root / 'tests/overview_figure_relocations_hashes.json').read_text())['files']
    return rows.get(path)


def overview_figure_relocations_hash(root, path, expected, algorithm='sha256'):
    row = overview_figure_relocations_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_overview_figure_relocations(root, path, current):
    row = overview_figure_relocations_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def hgenpush_full_prose_row(root, path):
    if not path.startswith('papers/hgenpush-kuaishou-heterogeneous-push-gr/'):
        return None
    rows = json.loads((root / 'tests/hgenpush_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def hgenpush_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = hgenpush_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_hgenpush_full_prose(root, path, current):
    row = hgenpush_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def agenttether_full_prose_row(root, path):
    if not path.startswith('papers/agenttether-repair/'):
        return None
    rows = json.loads((root / 'tests/agenttether_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def agenttether_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = agenttether_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_agenttether_full_prose(root, path, current):
    row = agenttether_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def stockout_full_prose_row(root, path):
    if not path.startswith('papers/stockout-data-debt/'):
        return None
    rows = json.loads((root / 'tests/stockout_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def stockout_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = stockout_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_stockout_full_prose(root, path, current):
    row = stockout_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def onetrans_full_prose_row(root, path):
    if not path.startswith('papers/onetrans-v2-cascade-unification/') and path != 'paper_lab/batch28.py':
        return None
    rows = json.loads((root / 'tests/onetrans_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def onetrans_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = onetrans_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_onetrans_full_prose(root, path, current):
    row = onetrans_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def spotify_causal_full_prose_row(root, path):
    if not path.startswith('papers/spotify-incremental-recommendation-causal/'):
        return None
    rows = json.loads((root / 'tests/spotify_causal_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def spotify_causal_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = spotify_causal_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_spotify_causal_full_prose(root, path, current):
    row = spotify_causal_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def youtube_rationales_full_prose_row(root, path):
    if not path.startswith('papers/youtube-music-llm-rationales-discovery/'):
        return None
    rows = json.loads((root / 'tests/youtube_rationales_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def youtube_rationales_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = youtube_rationales_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_youtube_rationales_full_prose(root, path, current):
    row = youtube_rationales_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def unirec_full_prose_row(root, path):
    if not path.startswith('papers/unirec-chain-of-attribute/'):
        return None
    rows = json.loads((root / 'tests/unirec_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def unirec_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = unirec_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_unirec_full_prose(root, path, current):
    row = unirec_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def lige_full_prose_row(root, path):
    if not path.startswith('papers/lige-gr-meta-listwise/'):
        return None
    rows = json.loads((root / 'tests/lige_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def lige_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = lige_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_lige_full_prose(root, path, current):
    row = lige_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def oxygenrec_full_prose_row(root, path):
    if not path.startswith('papers/oxygenrec-v2-idgr/'):
        return None
    rows = json.loads((root / 'tests/oxygenrec_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def oxygenrec_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = oxygenrec_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_oxygenrec_full_prose(root, path, current):
    row = oxygenrec_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def varg_full_prose_row(root, path):
    if not path.startswith('papers/varg-tmall-value-generative-retrieval/'):
        return None
    rows = json.loads((root / 'tests/varg_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def varg_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = varg_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_varg_full_prose(root, path, current):
    row = varg_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def pushdualgen_full_prose_row(root, path):
    if not path.startswith('papers/pushdualgen-kuaishou/'):
        return None
    rows = json.loads((root / 'tests/pushdualgen_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def pushdualgen_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = pushdualgen_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_pushdualgen_full_prose(root, path, current):
    row = pushdualgen_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def oneranker_full_prose_row(root, path):
    if not path.startswith('papers/oneranker-ads/'):
        return None
    rows = json.loads((root / 'tests/oneranker_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def oneranker_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = oneranker_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_oneranker_full_prose(root, path, current):
    row = oneranker_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def muser_full_prose_row(root, path):
    if not path.startswith('papers/muser-baidu-long-sequence-multi-interest/'):
        return None
    rows = json.loads((root / 'tests/muser_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def muser_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = muser_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_muser_full_prose(root, path, current):
    row = muser_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def univa_full_prose_row(root, path):
    if not path.startswith('papers/univa-commercial-sid-gar/'):
        return None
    rows = json.loads((root / 'tests/univa_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def univa_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = univa_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_univa_full_prose(root, path, current):
    row = univa_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def sam_full_prose_row(root, path):
    if not path.startswith('papers/sam-d2q-aliexpress-doc2query/'):
        return None
    rows = json.loads((root / 'tests/sam_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def sam_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = sam_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_sam_full_prose(root, path, current):
    row = sam_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def rest_full_prose_row(root, path):
    if path != 'papers/_toy_common.py' and not path.startswith('papers/rest-sequence-ranking/'):
        return None
    rows = json.loads((root / 'tests/rest_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def rest_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = rest_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_rest_full_prose(root, path, current):
    row = rest_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def gr4ad_full_prose_row(root, path):
    if not path.startswith('papers/gr4ad-ads-generative/'):
        return None
    rows = json.loads((root / 'tests/gr4ad_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def gr4ad_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = gr4ad_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_gr4ad_full_prose(root, path, current):
    row = gr4ad_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def gryphonv2_full_prose_row(root, path):
    if not path.startswith('papers/gryphon-v2-cascade/'):
        return None
    rows = json.loads((root / 'tests/gryphonv2_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def gryphonv2_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = gryphonv2_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_gryphonv2_full_prose(root, path, current):
    row = gryphonv2_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def gryphonilsm_full_prose_row(root, path):
    if not path.startswith('papers/gryphon-ilsm/'):
        return None
    rows = json.loads((root / 'tests/gryphonilsm_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def gryphonilsm_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = gryphonilsm_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_gryphonilsm_full_prose(root, path, current):
    row = gryphonilsm_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def isd_full_prose_row(root, path):
    if not path.startswith('papers/understanding-sids-isd/'):
        return None
    rows = json.loads((root / 'tests/isd_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def isd_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = isd_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_isd_full_prose(root, path, current):
    row = isd_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def snaplgr_full_prose_row(root, path):
    if not path.startswith('papers/snaplgr-snapchat/'):
        return None
    rows = json.loads((root / 'tests/snaplgr_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def snaplgr_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = snaplgr_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_snaplgr_full_prose(root, path, current):
    row = snaplgr_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def tmall_full_prose_row(root, path):
    if not path.startswith('papers/cq-sid-eg-grpo-tmall/'):
        return None
    rows = json.loads((root / 'tests/tmall_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def tmall_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = tmall_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_tmall_full_prose(root, path, current):
    row = tmall_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def recevolve_full_prose_row(root, path):
    if not path.startswith('papers/recevolve-autonomous-rec/'):
        return None
    rows = json.loads((root / 'tests/recevolve_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def recevolve_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = recevolve_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_recevolve_full_prose(root, path, current):
    row = recevolve_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def dream_full_prose_row(root, path):
    if not path.startswith('papers/dream-taobao-agentic-control/'):
        return None
    rows = json.loads((root / 'tests/dream_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def dream_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = dream_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_dream_full_prose(root, path, current):
    row = dream_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def reusegr_full_prose_row(root, path):
    if not path.startswith('papers/query-prefix-reuse/'):
        return None
    rows = json.loads((root / 'tests/reusegr_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def reusegr_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = reusegr_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_reusegr_full_prose(root, path, current):
    row = reusegr_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def bitemporal_full_prose_row(root, path):
    if not path.startswith('papers/bitemporal-inventory-replay/'):
        return None
    rows = json.loads((root / 'tests/bitemporal_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def bitemporal_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = bitemporal_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_bitemporal_full_prose(root, path, current):
    row = bitemporal_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def harnesstokens_full_prose_row(root, path):
    if not path.startswith('papers/harness-buys-tokens-not-pass-rate/'):
        return None
    rows = json.loads((root / 'tests/harnesstokens_full_prose_hashes.json').read_text())['files']
    return rows.get(path)


def harnesstokens_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = harnesstokens_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_harnesstokens_full_prose(root, path, current):
    row = harnesstokens_full_prose_row(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def before_forgetting_iclr_full_prose(root, path, current):
    prefix = 'papers/agent-reasoning-forgetting-externalized-state/'
    if not path.startswith(prefix) and path != 'paper_lab/forgetting05.py':
        return current
    row = json.loads((root / 'tests/forgetting_iclr_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, prior in reversed(row['prior_spans']):
        lines[start:stop] = [prior]
    previous = ''.join(lines).encode()
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def forgetting_iclr_full_prose_hash(root, path, expected, algorithm='sha256'):
    prefix = 'papers/agent-reasoning-forgetting-externalized-state/'
    if not path.startswith(prefix) and path != 'paper_lab/forgetting05.py':
        return expected
    row = json.loads((root / 'tests/forgetting_iclr_full_prose_hashes.json').read_text())['files'].get(path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def deletion_prefix_full_prose_for_path(root, path):
    if not path.startswith('papers/trajectory-deletion-prefix-cost/'):
        return None
    return json.loads((root / 'tests/deletion_prefix_full_prose_hashes.json').read_text())['files'].get(path)


def deletion_prefix_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = deletion_prefix_full_prose_for_path(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_deletion_prefix_full_prose(root, path, current):
    import base64
    import zlib
    row = deletion_prefix_full_prose_for_path(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    previous = zlib.decompress(base64.b64decode(row['prior_zlib_b64'], validate=True))
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def scaffold_gaia_full_prose_for_path(root, path):
    if not path.startswith('papers/scaffold-effects-gaia/'):
        return None
    return json.loads((root / 'tests/scaffold_gaia_full_prose_hashes.json').read_text())['files'].get(path)


def scaffold_gaia_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = scaffold_gaia_full_prose_for_path(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_scaffold_gaia_full_prose(root, path, current):
    import base64
    import zlib
    row = scaffold_gaia_full_prose_for_path(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    previous = zlib.decompress(base64.b64decode(row['prior_zlib_b64'], validate=True))
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def wholefoods_all_full_prose_for_path(root, path):
    if not path.startswith('papers/whole-foods-shelf/'):
        return None
    return json.loads((root / 'tests/wholefoods_all_full_prose_hashes.json').read_text())['files'].get(path)


def wholefoods_all_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = wholefoods_all_full_prose_for_path(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_wholefoods_all_full_prose(root, path, current):
    import base64
    import zlib
    row = wholefoods_all_full_prose_for_path(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    previous = zlib.decompress(base64.b64decode(row['prior_zlib_b64'], validate=True))
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def wrapped_all_full_prose_for_path(root, path):
    if not path.startswith('papers/wrapped-produce-placement-controlled-trial/'):
        return None
    return json.loads((root / 'tests/wrapped_all_full_prose_hashes.json').read_text())['files'].get(path)


def wrapped_all_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = wrapped_all_full_prose_for_path(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_wrapped_all_full_prose(root, path, current):
    import base64
    import zlib
    row = wrapped_all_full_prose_for_path(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    previous = zlib.decompress(base64.b64decode(row['prior_zlib_b64'], validate=True))
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def storewide_all_full_prose_for_path(root, path):
    if not path.startswith('papers/storewide-shelf-decomposition/'):
        return None
    return json.loads((root / 'tests/storewide_all_full_prose_hashes.json').read_text())['files'].get(path)


def storewide_all_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = storewide_all_full_prose_for_path(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_storewide_all_full_prose(root, path, current):
    import base64
    import zlib
    row = storewide_all_full_prose_for_path(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    previous = zlib.decompress(base64.b64decode(row['prior_zlib_b64'], validate=True))
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def retail_grain_all_full_prose_for_path(root, path):
    if not path.startswith('papers/retail-forecast-decision-grain/'):
        return None
    return json.loads((root / 'tests/retail_grain_all_full_prose_hashes.json').read_text())['files'].get(path)


def retail_grain_all_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = retail_grain_all_full_prose_for_path(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_retail_grain_all_full_prose(root, path, current):
    import base64
    import zlib
    row = retail_grain_all_full_prose_for_path(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    previous = zlib.decompress(base64.b64decode(row['prior_zlib_b64'], validate=True))
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def switch_hurdle_all_full_prose_for_path(root, path):
    if not path.startswith('papers/switch-hurdle-intermittent-demand/'):
        return None
    return json.loads((root / 'tests/switch_hurdle_all_full_prose_hashes.json').read_text())['files'].get(path)


def switch_hurdle_all_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = switch_hurdle_all_full_prose_for_path(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_switch_hurdle_all_full_prose(root, path, current):
    import base64
    import zlib
    row = switch_hurdle_all_full_prose_for_path(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    previous = zlib.decompress(base64.b64decode(row['prior_zlib_b64'], validate=True))
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def sim2real_all_full_prose_for_path(root, path):
    if path != 'paper_lab/batch08.py' and not path.startswith('papers/sim2real-policy-conditioned-inbound-forecast/'):
        return None
    return json.loads((root / 'tests/sim2real_all_full_prose_hashes.json').read_text())['files'].get(path)


def sim2real_all_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = sim2real_all_full_prose_for_path(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_sim2real_all_full_prose(root, path, current):
    import base64
    import zlib
    row = sim2real_all_full_prose_for_path(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    previous = zlib.decompress(base64.b64decode(row['prior_zlib_b64'], validate=True))
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def assortment_all_full_prose_for_path(root, path):
    if not path.startswith('papers/assortment-replenishment-hard-constraints/'):
        return None
    return json.loads((root / 'tests/assortment_all_full_prose_hashes.json').read_text())['files'].get(path)


def assortment_all_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = assortment_all_full_prose_for_path(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_assortment_all_full_prose(root, path, current):
    import base64
    import zlib
    row = assortment_all_full_prose_for_path(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    previous = zlib.decompress(base64.b64decode(row['prior_zlib_b64'], validate=True))
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def or_transformer_all_full_prose_for_path(root, path):
    if path != 'paper_lab/batch29.py' and not path.startswith('papers/or-transformer-joint-replenishment/'):
        return None
    return json.loads((root / 'tests/or_transformer_all_full_prose_hashes.json').read_text())['files'].get(path)


def or_transformer_all_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = or_transformer_all_full_prose_for_path(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_or_transformer_all_full_prose(root, path, current):
    import base64
    import zlib
    row = or_transformer_all_full_prose_for_path(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    previous = zlib.decompress(base64.b64decode(row['prior_zlib_b64'], validate=True))
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def reasoncast_all_full_prose_for_path(root, path):
    if path != 'paper_lab/batch28.py' and not path.startswith('papers/reasoncast-agentic-demand-forecasting/'):
        return None
    return json.loads((root / 'tests/reasoncast_all_full_prose_hashes.json').read_text())['files'].get(path)


def reasoncast_all_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = reasoncast_all_full_prose_for_path(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_reasoncast_all_full_prose(root, path, current):
    import base64
    import zlib
    row = reasoncast_all_full_prose_for_path(root, path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after']['sha256'], path
    previous = zlib.decompress(base64.b64decode(row['prior_zlib_b64'], validate=True))
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def forecast_critic_all_full_prose_for_path(root,path):
    if path!='papers/_toy_common.py' and not path.startswith('papers/forecast-critic/'):
        return None
    return json.loads((root/'tests/forecast_critic_all_full_prose_hashes.json').read_text())['files'].get(path)


def forecast_critic_all_full_prose_hash(root,path,expected,algorithm='sha256'):
    row=forecast_critic_all_full_prose_for_path(root,path)
    if row is None:
        return expected
    assert expected==row['before'][algorithm],path
    return row['after'][algorithm]


def before_forecast_critic_all_full_prose(root,path,current):
    if path == 'papers/_toy_common.py':
        current = before_tgr_reader_all_full_prose(root,path,current)
    import base64,zlib
    row=forecast_critic_all_full_prose_for_path(root,path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest()==row['after']['sha256'],path
    prior=zlib.decompress(base64.b64decode(row['prior_zlib_b64'],validate=True))
    assert hashlib.sha256(prior).hexdigest()==row['before']['sha256'],path
    return prior


def t0_context_all_full_prose_for_path(root,path):
    if not path.startswith('papers/t0-tsfm-forecasting-with-context/'):
        return None
    return json.loads((root/'tests/t0_context_all_full_prose_hashes.json').read_text())['files'].get(path)

def t0_context_all_full_prose_hash(root,path,expected,algorithm='sha256'):
    row=t0_context_all_full_prose_for_path(root,path)
    if row is None:
        return expected
    assert expected==row['before'][algorithm],path
    return row['after'][algorithm]

def before_t0_context_all_full_prose(root,path,current):
    import base64,zlib
    row=t0_context_all_full_prose_for_path(root,path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest()==row['after']['sha256'],path
    prior=zlib.decompress(base64.b64decode(row['prior_zlib_b64'],validate=True))
    assert hashlib.sha256(prior).hexdigest()==row['before']['sha256'],path
    return prior


def flashvector_all_full_prose_for_path(root,path):
    if not path.startswith('papers/flashvector-unity-serving-stack-agent/'):
        return None
    return json.loads((root/'tests/flashvector_all_full_prose_hashes.json').read_text())['files'].get(path)

def flashvector_all_full_prose_hash(root,path,expected,algorithm='sha256'):
    row=flashvector_all_full_prose_for_path(root,path)
    if row is None:
        return expected
    assert expected==row['before'][algorithm],path
    return row['after'][algorithm]

def before_flashvector_all_full_prose(root,path,current):
    import base64,zlib
    row=flashvector_all_full_prose_for_path(root,path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest()==row['after']['sha256'],path
    prior=zlib.decompress(base64.b64decode(row['prior_zlib_b64'],validate=True))
    assert hashlib.sha256(prior).hexdigest()==row['before']['sha256'],path
    return prior


def placement_and_vn2_asset_prose_hash(root, path, expected, algorithm='sha256'):
    if path == 'papers/shelf-placement-options/model.js':
        manifest = 'placement_model_full_prose_hashes.json'
    elif path in {
        'papers/vn2-stockout-catboost/figures/censoring.svg',
        'papers/vn2-stockout-catboost/figures/masking.svg',
        'papers/vn2-stockout-catboost/figures/order.svg',
    }:
        manifest = 'vn2_figures_full_prose_hashes.json'
    else:
        return expected
    row = json.loads((root / 'tests' / manifest).read_bytes())['files'][path]
    assert expected == row['before_' + algorithm], path
    raw = (root / path).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == row['after_sha256'], path
    assert hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['after_blob'], path
    return row['after_' + algorithm]


def ono_reader_all_full_prose_for_path(root,path):
    if not path.startswith('papers/ono-inventory-forecast-selection/'):
        return None
    return json.loads((root/'tests/ono_reader_all_full_prose_hashes.json').read_text())['files'].get(path)

def ono_reader_all_full_prose_hash(root,path,expected,algorithm='sha256'):
    row=ono_reader_all_full_prose_for_path(root,path)
    if row is None:
        return expected
    assert expected==row['before'][algorithm],path
    return row['after'][algorithm]

def before_ono_reader_all_full_prose(root,path,current):
    import base64,zlib
    row=ono_reader_all_full_prose_for_path(root,path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest()==row['after']['sha256'],path
    prior=zlib.decompress(base64.b64decode(row['prior_zlib_b64'],validate=True))
    assert hashlib.sha256(prior).hexdigest()==row['before']['sha256'],path
    return prior


def sparse_reader_all_full_prose_for_path(root,path):
    if not path.startswith('papers/tsfm-sparse-event-ranking/'):
        return None
    return json.loads((root/'tests/sparse_reader_all_full_prose_hashes.json').read_text())['files'].get(path)

def sparse_reader_all_full_prose_hash(root,path,expected,algorithm='sha256'):
    row=sparse_reader_all_full_prose_for_path(root,path)
    if row is None:
        return expected
    assert expected==row['before'][algorithm],path
    return row['after'][algorithm]

def before_sparse_reader_all_full_prose(root,path,current):
    import base64,zlib
    row=sparse_reader_all_full_prose_for_path(root,path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest()==row['after']['sha256'],path
    prior=zlib.decompress(base64.b64decode(row['prior_zlib_b64'],validate=True))
    assert hashlib.sha256(prior).hexdigest()==row['before']['sha256'],path
    return prior


def sgc_all_full_prose_for_path(root,path):
    if not path.startswith('papers/sgc-state-grounded-conditioning/'):
        return None
    return json.loads((root/'tests/sgc_all_full_prose_hashes.json').read_text())['files'].get(path)

def sgc_all_full_prose_hash(root,path,expected,algorithm='sha256'):
    row=sgc_all_full_prose_for_path(root,path)
    if row is None:
        return expected
    assert expected==row['before'][algorithm],path
    return row['after'][algorithm]

def before_sgc_all_full_prose(root,path,current):
    import base64,zlib
    row=sgc_all_full_prose_for_path(root,path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest()==row['after']['sha256'],path
    prior=zlib.decompress(base64.b64decode(row['prior_zlib_b64'],validate=True))
    assert hashlib.sha256(prior).hexdigest()==row['before']['sha256'],path
    return prior


def tgr_reader_all_full_prose_for_path(root,path):
    if not (path.startswith('papers/tgr/') or path=='papers/_toy_common.py'):
        return None
    return json.loads((root/'tests/tgr_reader_all_full_prose_hashes.json').read_text())['files'].get(path)

def tgr_reader_all_full_prose_hash(root,path,expected,algorithm='sha256'):
    row=tgr_reader_all_full_prose_for_path(root,path)
    if row is None:
        return expected
    assert expected==row['before'][algorithm],path
    return row['after'][algorithm]

def before_tgr_reader_all_full_prose(root,path,current):
    import base64,zlib
    if path == 'papers/_toy_common.py':
        current = before_contextual_all_full_prose(root, path, current)
    row=tgr_reader_all_full_prose_for_path(root,path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest()==row['after']['sha256'],path
    prior=zlib.decompress(base64.b64decode(row['prior_zlib_b64'],validate=True))
    assert hashlib.sha256(prior).hexdigest()==row['before']['sha256'],path
    return prior


def genpage_reader_full_prose_row(root,path):
    if path not in {'papers/genpage-netflix-homepage/results.json','papers/genpage-netflix-homepage/run.py'}:
        return None
    return json.loads((root/'tests/genpage_reader_full_prose_hashes.json').read_bytes())['files'][path]

def genpage_reader_full_prose_hash(root,path,expected,algorithm='sha256'):
    row=genpage_reader_full_prose_row(root,path)
    if row is None:
        return expected
    assert expected==row['before'][algorithm],path
    return row['after'][algorithm]

def before_genpage_reader_full_prose(root,path,current):
    import base64,zlib
    row=genpage_reader_full_prose_row(root,path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest()==row['after']['sha256'],path
    prior=zlib.decompress(base64.b64decode(row['prior_zlib_b64'],validate=True))
    assert hashlib.sha256(prior).hexdigest()==row['before']['sha256'],path
    return prior


def harness_zero_all_full_prose_for_path(root,path):
    if not path.startswith('papers/harness-zero-distillation/'):
        return None
    return json.loads((root/'tests/harness_zero_all_full_prose_hashes.json').read_text())['files'].get(path)

def harness_zero_all_full_prose_hash(root,path,expected,algorithm='sha256'):
    row=harness_zero_all_full_prose_for_path(root,path)
    if row is None:
        return expected
    assert expected==row['before'][algorithm],path
    return row['after'][algorithm]

def before_harness_zero_all_full_prose(root,path,current):
    import base64,zlib
    row=harness_zero_all_full_prose_for_path(root,path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest()==row['after']['sha256'],path
    prior=zlib.decompress(base64.b64decode(row['prior_zlib_b64'],validate=True))
    assert hashlib.sha256(prior).hexdigest()==row['before']['sha256'],path
    return prior


def tagr_all_full_prose_row(root,path):
    if not path.startswith('papers/tagr-live-sid/'):
        return None
    return json.loads((root/'tests/tagr_all_full_prose_hashes.json').read_text())['files'].get(path)

def tagr_all_full_prose_hash(root,path,expected,algorithm='sha256'):
    row=tagr_all_full_prose_row(root,path)
    if row is None:
        return expected
    assert expected==row['before'][algorithm],path
    return row['after'][algorithm]

def before_tagr_all_full_prose(root,path,current):
    import base64,zlib
    row=tagr_all_full_prose_row(root,path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest()==row['after']['sha256'],path
    prior=zlib.decompress(base64.b64decode(row['prior_zlib_b64'],validate=True))
    assert hashlib.sha256(prior).hexdigest()==row['before']['sha256'],path
    return prior


def swe_serve_full_prose_for_path(root,path):
    if not path.startswith('papers/swe-serve-inference-serving-agents/'):
        return None
    return json.loads((root/'tests/swe_serve_full_prose_hashes.json').read_text())['files'].get(path)

def swe_serve_full_prose_hash(root,path,expected,algorithm='sha256'):
    row=swe_serve_full_prose_for_path(root,path)
    if row is None:
        return expected
    assert expected==row['before'][algorithm],path
    return row['after'][algorithm]

def before_swe_serve_full_prose(root,path,current):
    import base64,zlib
    row=swe_serve_full_prose_for_path(root,path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest()==row['after']['sha256'],path
    prior=zlib.decompress(base64.b64decode(row['prior_zlib_b64'],validate=True))
    assert hashlib.sha256(prior).hexdigest()==row['before']['sha256'],path
    return prior


def harness_r1_full_prose_for_path(root,path):
    if not path.startswith('papers/harness-r1/'):
        return None
    return json.loads((root/'tests/harness_r1_full_prose_hashes.json').read_text())['files'].get(path)

def harness_r1_full_prose_hash(root,path,expected,algorithm='sha256'):
    row=harness_r1_full_prose_for_path(root,path)
    if row is None:
        return expected
    assert expected==row['before'][algorithm],path
    return row['after'][algorithm]

def before_harness_r1_full_prose(root,path,current):
    import base64,zlib
    row=harness_r1_full_prose_for_path(root,path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest()==row['after']['sha256'],path
    prior=zlib.decompress(base64.b64decode(row['prior_zlib_b64'],validate=True))
    assert hashlib.sha256(prior).hexdigest()==row['before']['sha256'],path
    return prior


def episem_full_prose_for_path(root,path):
    if not path.startswith('papers/episem-missing-evidence-recovery/'):
        return None
    return json.loads((root/'tests/episem_full_prose_hashes.json').read_text())['files'].get(path)

def episem_full_prose_hash(root,path,expected,algorithm='sha256'):
    row=episem_full_prose_for_path(root,path)
    if row is None:
        return expected
    assert expected==row['before'][algorithm],path
    return row['after'][algorithm]

def before_episem_full_prose(root,path,current):
    import base64,zlib
    row=episem_full_prose_for_path(root,path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest()==row['after']['sha256'],path
    prior=zlib.decompress(base64.b64decode(row['prior_zlib_b64'],validate=True))
    assert hashlib.sha256(prior).hexdigest()==row['before']['sha256'],path
    return prior


def execution_state_unlearning_full_prose_for_path(root,path):
    if not path.startswith('papers/execution-state-unlearning/'):
        return None
    return json.loads((root/'tests/execution_state_unlearning_full_prose_hashes.json').read_text())['files'].get(path)

def execution_state_unlearning_full_prose_hash(root,path,expected,algorithm='sha256'):
    row=execution_state_unlearning_full_prose_for_path(root,path)
    if row is None:
        return expected
    assert expected==row['before'][algorithm],path
    return row['after'][algorithm]

def before_execution_state_unlearning_full_prose(root,path,current):
    import base64,zlib
    row=execution_state_unlearning_full_prose_for_path(root,path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest()==row['after']['sha256'],path
    prior=zlib.decompress(base64.b64decode(row['prior_zlib_b64'],validate=True))
    assert hashlib.sha256(prior).hexdigest()==row['before']['sha256'],path
    return prior


def featurearc_full_prose_for_path(root,path):
    if not path.startswith('papers/featurearc-inherited-defects-chain-gates/'):
        return None
    return json.loads((root/'tests/featurearc_full_prose_hashes.json').read_text())['files'].get(path)

def featurearc_full_prose_hash(root,path,expected,algorithm='sha256'):
    row=featurearc_full_prose_for_path(root,path)
    if row is None:
        return expected
    assert expected==row['before'][algorithm],path
    return row['after'][algorithm]

def before_featurearc_full_prose(root,path,current):
    import base64,zlib
    row=featurearc_full_prose_for_path(root,path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest()==row['after']['sha256'],path
    prior=zlib.decompress(base64.b64decode(row['prior_zlib_b64'],validate=True))
    assert hashlib.sha256(prior).hexdigest()==row['before']['sha256'],path
    return prior


def contextual_all_full_prose_row(root,path):
    if path != 'papers/_toy_common.py' and not path.startswith('papers/contextual-deconvolution/'):
        return None
    return json.loads((root/'tests/contextual_all_full_prose_hashes.json').read_text())['files'].get(path)

def contextual_all_full_prose_hash(root,path,expected,algorithm='sha256'):
    row=contextual_all_full_prose_row(root,path)
    if row is None:
        return expected
    assert expected==row['before'][algorithm],path
    return row['after'][algorithm]

def before_contextual_all_full_prose(root,path,current):
    import base64,zlib
    row=contextual_all_full_prose_row(root,path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest()==row['after']['sha256'],path
    old=zlib.decompress(base64.b64decode(row['prior_zlib_b64'],validate=True))
    assert hashlib.sha256(old).hexdigest()==row['before']['sha256'],path
    return old


def trace_all_full_prose_row(root,path):
    if not path.startswith('papers/trace-verifier-brittleness/'):
        return None
    return json.loads((root/'tests/trace_all_full_prose_hashes.json').read_text())['files'].get(path)

def trace_all_full_prose_hash(root,path,expected,algorithm='sha256'):
    row=trace_all_full_prose_row(root,path)
    if row is None:
        return expected
    assert expected==row['before'][algorithm],path
    return row['after'][algorithm]

def before_trace_all_full_prose(root,path,current):
    import base64,zlib
    row=trace_all_full_prose_row(root,path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest()==row['after']['sha256'],path
    old=zlib.decompress(base64.b64decode(row['prior_zlib_b64'],validate=True))
    assert hashlib.sha256(old).hexdigest()==row['before']['sha256'],path
    return old


def trial_trace_all_full_prose_row(root,path):
    if path != 'paper_lab/trial_trace.py' and not path.startswith('papers/trial-by-trace-evidence-boundaries/'):
        return None
    return json.loads((root/'tests/trial_trace_all_full_prose_hashes.json').read_text())['files'].get(path)

def trial_trace_all_full_prose_hash(root,path,expected,algorithm='sha256'):
    row=trial_trace_all_full_prose_row(root,path)
    if row is None:
        return expected
    assert expected==row['before'][algorithm],path
    return row['after'][algorithm]

def before_trial_trace_all_full_prose(root,path,current):
    import base64,zlib
    row=trial_trace_all_full_prose_row(root,path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest()==row['after']['sha256'],path
    old=zlib.decompress(base64.b64decode(row['prior_zlib_b64'],validate=True))
    assert hashlib.sha256(old).hexdigest()==row['before']['sha256'],path
    return old


def perishables_reader_assets_rows(root):
    return json.loads((root / 'tests/perishables_reader_assets_hashes.json').read_text())['files']


def perishables_reader_assets_hash(root, path, expected, algorithm='sha256'):
    if not path.startswith('papers/discounted-perishables-forecast/'):
        return expected
    row = perishables_reader_assets_rows(root).get(path)
    if row is None:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def before_perishables_reader_assets(root, path, current):
    if not path.startswith('papers/discounted-perishables-forecast/'):
        return current
    row = perishables_reader_assets_rows(root).get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after_sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, old in reversed(row['prior_spans']):
        lines[start:stop] = [old]
    prior = ''.join(lines).encode()
    assert hashlib.sha256(prior).hexdigest() == row['before_sha256'], path
    return prior


def bridging_reader_full_prose_row(root, path):
    if not path.startswith('papers/bridging-forecast-accuracy-inventory-kpis/'):
        return None
    return json.loads((root / 'tests/bridging_reader_full_prose_hashes.json').read_text())['files'].get(path)


def bridging_reader_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = bridging_reader_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_bridging_reader_full_prose(root, path, content):
    import base64
    import zlib

    row = bridging_reader_full_prose_row(root, path)
    if row is None:
        return content
    assert hashlib.sha256(content).hexdigest() == row['after']['sha256'], path
    previous = zlib.decompress(base64.b64decode(row['prior_zlib_b64'], validate=True))
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def zalando_reader_full_prose_row(root, path):
    if path != 'paper_lab/zalando05.py' and not path.startswith('papers/zalando-sales-event-pricing-forecast-optimize/'):
        return None
    return json.loads((root / 'tests/zalando_reader_full_prose_hashes.json').read_text())['files'].get(path)


def zalando_reader_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = zalando_reader_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_zalando_reader_full_prose(root, path, content):
    import base64
    import zlib

    row = zalando_reader_full_prose_row(root, path)
    if row is None:
        return content
    assert hashlib.sha256(content).hexdigest() == row['after']['sha256'], path
    previous = zlib.decompress(base64.b64decode(row['prior_zlib_b64'], validate=True))
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def assortment_observation_reader_assets_rows(root):
    return json.loads((root / 'tests/assortment_observation_reader_assets_hashes.json').read_text())['files']


def assortment_observation_reader_assets_hash(root, path, expected, algorithm='sha256'):
    if not path.startswith('papers/assortment-observation-budget/'):
        return expected
    row = assortment_observation_reader_assets_rows(root).get(path)
    if row is None or not row['prior_spans']:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def before_assortment_observation_reader_assets(root, path, current):
    if path != 'paper_lab/assortment_observation.py' and not path.startswith('papers/assortment-observation-budget/'):
        return current
    row = assortment_observation_reader_assets_rows(root).get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after_sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, old in reversed(row['prior_spans']):
        lines[start:stop] = [old]
    prior = ''.join(lines).encode()
    assert hashlib.sha256(prior).hexdigest() == row['before_sha256'], path
    return prior


def sparse_inspection_full_prose_row(root, path):
    if path != 'paper_lab/sparse05.py' and not path.startswith('papers/tsfm-sparse-event-ranking/'):
        return None
    return json.loads((root / 'tests/sparse_inspection_full_prose_hashes.json').read_text())['files'].get(path)


def sparse_inspection_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = sparse_inspection_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_sparse_inspection_full_prose(root, path, content):
    import base64
    import zlib

    row = sparse_inspection_full_prose_row(root, path)
    if row is None:
        return content
    assert hashlib.sha256(content).hexdigest() == row['after']['sha256'], path
    previous = zlib.decompress(base64.b64decode(row['prior_zlib_b64'], validate=True))
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def quasid_reader_assets_rows(root):
    return json.loads((root / 'tests/quasid_reader_assets_hashes.json').read_text())['files']


def quasid_reader_assets_hash(root, path, expected, algorithm='sha256'):
    if not path.startswith('papers/quasid-collision-qualified-sid/'):
        return expected
    row = quasid_reader_assets_rows(root).get(path)
    if row is None or not row['prior_spans']:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def before_quasid_reader_assets(root, path, current):
    if not path.startswith('papers/quasid-collision-qualified-sid/'):
        return current
    row = quasid_reader_assets_rows(root).get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after_sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, old in reversed(row['prior_spans']):
        lines[start:stop] = [old]
    prior = ''.join(lines).encode()
    assert hashlib.sha256(prior).hexdigest() == row['before_sha256'], path
    return prior


def sid_ope_reader_full_prose_row(root, path):
    if not path.startswith('papers/sid-ope-hierarchy/'):
        return None
    return json.loads((root / 'tests/sid_ope_reader_full_prose_hashes.json').read_text())['files'].get(path)


def sid_ope_reader_full_prose_hash(root, path, expected, algorithm='sha256'):
    row = sid_ope_reader_full_prose_row(root, path)
    if row is None:
        return expected
    assert expected == row['before'][algorithm], path
    return row['after'][algorithm]


def before_sid_ope_reader_full_prose(root, path, content):
    import base64
    import zlib

    row = sid_ope_reader_full_prose_row(root, path)
    if row is None:
        return content
    assert hashlib.sha256(content).hexdigest() == row['after']['sha256'], path
    previous = zlib.decompress(base64.b64decode(row['prior_zlib_b64'], validate=True))
    assert hashlib.sha256(previous).hexdigest() == row['before']['sha256'], path
    return previous


def unir2_reader_assets_rows(root):
    return json.loads((root / 'tests/unir2_reader_assets_hashes.json').read_text())['files']


def unir2_reader_assets_hash(root, path, expected, algorithm='sha256'):
    if not path.startswith('papers/unir2-sequence-unify/'):
        return expected
    row = unir2_reader_assets_rows(root).get(path)
    if row is None or not row['prior_spans']:
        return expected
    assert expected == row['before_' + algorithm], path
    return row['after_' + algorithm]


def before_unir2_reader_assets(root, path, current):
    if not path.startswith('papers/unir2-sequence-unify/'):
        return current
    row = unir2_reader_assets_rows(root).get(path)
    if row is None:
        return current
    assert hashlib.sha256(current).hexdigest() == row['after_sha256'], path
    lines = current.decode().splitlines(keepends=True)
    for start, stop, old in reversed(row['prior_spans']):
        lines[start:stop] = [old]
    prior = ''.join(lines).encode()
    assert hashlib.sha256(prior).hexdigest() == row['before_sha256'], path
    return prior
