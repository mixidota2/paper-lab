"""The reviewed paper summaries change only the overview in source and on the page."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path

import pytest
import yaml

from paper_lab.build import build
from source_overview_corrections import before_hasterad_overview_correction
from prose_preservation import before_swe_serve_full_prose, before_harness_zero_all_full_prose, before_sgc_all_full_prose, before_sparse_reader_all_full_prose, before_ono_reader_all_full_prose, before_flashvector_all_full_prose, before_t0_context_all_full_prose, before_forecast_critic_all_full_prose, before_reasoncast_all_full_prose, before_or_transformer_all_full_prose, before_assortment_all_full_prose, before_sim2real_all_full_prose, before_switch_hurdle_all_full_prose, before_retail_grain_all_full_prose, before_storewide_all_full_prose, before_wrapped_all_full_prose, before_wholefoods_all_full_prose, before_scaffold_gaia_full_prose, before_deletion_prefix_full_prose, before_forgetting_iclr_full_prose, before_harnesstokens_full_prose, before_bitemporal_full_prose, before_reusegr_full_prose, before_dream_full_prose, before_recevolve_full_prose, before_tmall_full_prose, before_snaplgr_full_prose, before_isd_full_prose, before_gryphonilsm_full_prose, before_gryphonv2_full_prose, before_gr4ad_full_prose, before_rest_full_prose, before_sam_full_prose, before_univa_full_prose, before_muser_full_prose, before_oneranker_full_prose, before_pushdualgen_full_prose, before_varg_full_prose, before_oxygenrec_full_prose, before_lige_full_prose, before_unirec_full_prose, before_youtube_rationales_full_prose, before_spotify_causal_full_prose, before_onetrans_full_prose, before_stockout_full_prose, before_agenttether_full_prose, before_hgenpush_full_prose, before_overview_figure_relocations, before_glide_full_prose, before_netflix_counterfactual_full_prose, before_dsi_full_prose, before_gatesid_full_prose, before_common_threshold_full_prose, before_grace_full_prose, before_uvr_full_prose, before_series_full_prose, before_hear_full_prose, before_angle_full_prose, before_otto_full_prose, before_apollopfn_full_prose, before_multi_harness_full_prose, before_autolr_full_prose, before_aura_full_prose, before_evopilot_full_prose, before_autorecsys_full_prose, before_pilot_full_prose, before_agentx_full_prose, before_retailbench_full_prose, before_traffic_value_full_prose, before_eval_grain_full_prose, before_exaone_full_prose, before_isomorph_full_prose, before_scope_full_prose, before_fbsde_full_prose, before_diff_projection_full_prose, before_radfl_full_prose, before_proximal_full_prose, before_igpo_full_prose, before_sabreagent_full_prose, before_invevolve_full_prose, before_deepstock_full_prose, before_orpr_full_prose, before_hasterad_full_prose, before_assortment_full_prose, before_vn2_full_prose, before_intervention_full_prose, before_ogr_full_prose, before_unique_full_prose, before_flashtrie_full_prose, before_pinterest_full_rewrite, before_ahe_full_prose, before_dcdn_full_prose, before_ono_full_rewrite, before_wrapped_produce_full_rewrite, before_static_constrained_full_rewrite, before_forecast_critic_full_rewrite, before_retail_grain_full_rewrite, before_switch_hurdle_full_rewrite, before_perishable_full_rewrite, before_sid_ope_full_rewrite, before_quasid_full_rewrite, before_semantic_id_pair_full_rewrite, before_forecast_pair_full_rewrite, before_harness_icegr_full_rewrite, before_tgr_full_rewrite, before_sona_full_rewrite, before_genpage_full_rewrite, before_unir2_full_rewrite, paper_overview_rewrite_hash, restored_before_paper_overview

ROOT = Path(__file__).resolve().parents[1]


def before_full_article_rewrites(root, path, current):
    current = before_swe_serve_full_prose(root, path, current)
    current = before_harness_zero_all_full_prose(root, path, current)
    current = before_sgc_all_full_prose(root, path, current)
    current = before_sparse_reader_all_full_prose(root, path, current)
    current = before_ono_reader_all_full_prose(root, path, current)
    current = before_flashvector_all_full_prose(root, path, current)
    current = before_t0_context_all_full_prose(root, path, current)
    current = before_forecast_critic_all_full_prose(root, path, current)
    current = before_reasoncast_all_full_prose(root, path, current)
    current = before_or_transformer_all_full_prose(root, path, current)
    current = before_assortment_all_full_prose(root, path, current)
    current = before_sim2real_all_full_prose(root, path, current)
    current = before_switch_hurdle_all_full_prose(root, path, current)
    current = before_retail_grain_all_full_prose(root, path, current)
    current = before_storewide_all_full_prose(root, path, current)
    current = before_wrapped_all_full_prose(root, path, current)
    current = before_wholefoods_all_full_prose(root, path, current)
    current = before_scaffold_gaia_full_prose(root, path, current)
    current = before_deletion_prefix_full_prose(root, path, current)
    current = before_forgetting_iclr_full_prose(root, path, current)
    old = before_harnesstokens_full_prose(root, path, current)
    old = before_bitemporal_full_prose(root, path, old)
    old = before_reusegr_full_prose(root, path, old)
    old = before_dream_full_prose(root, path, old)
    old = before_recevolve_full_prose(root, path, old)
    old = before_tmall_full_prose(root, path, old)
    old = before_snaplgr_full_prose(root, path, old)
    old = before_isd_full_prose(root, path, old)
    old = before_gryphonilsm_full_prose(root, path, old)
    old = before_gryphonv2_full_prose(root, path, old)
    old = before_gr4ad_full_prose(root, path, old)
    old = before_rest_full_prose(root, path, old)
    old = before_sam_full_prose(root, path, old)
    old = before_univa_full_prose(root, path, old)
    old = before_muser_full_prose(root, path, old)
    old = before_oneranker_full_prose(root, path, old)
    old = before_pushdualgen_full_prose(root, path, old)
    old = before_varg_full_prose(root, path, old)
    old = before_oxygenrec_full_prose(root, path, old)
    old = before_lige_full_prose(root, path, old)
    old = before_unirec_full_prose(root, path, old)
    old = before_youtube_rationales_full_prose(root, path, old)
    old = before_spotify_causal_full_prose(root, path, old)
    old = before_onetrans_full_prose(root, path, old)
    old = before_stockout_full_prose(root, path, old)
    old = before_agenttether_full_prose(root, path, old)
    old = before_hgenpush_full_prose(root, path, old)
    old = before_overview_figure_relocations(root, path, old)
    old = before_glide_full_prose(root, path, old)
    old = before_netflix_counterfactual_full_prose(root, path, old)
    old = before_dsi_full_prose(root, path, old)
    old = before_gatesid_full_prose(root, path, old)
    old = before_common_threshold_full_prose(root, path, old)
    old = before_grace_full_prose(root, path, old)
    old = before_uvr_full_prose(root, path, old)
    old = before_series_full_prose(root, path, old)
    old = before_hear_full_prose(root, path, old)
    old = before_angle_full_prose(root, path, old)
    old = before_otto_full_prose(root, path, old)
    old = before_apollopfn_full_prose(root, path, old)
    old = before_multi_harness_full_prose(root, path, old)
    old = before_autolr_full_prose(root, path, old)
    old = before_aura_full_prose(root, path, old)
    old = before_evopilot_full_prose(root, path, old)
    old = before_autorecsys_full_prose(root, path, old)
    old = before_pilot_full_prose(root, path, old)
    old = before_agentx_full_prose(root, path, old)
    old = before_retailbench_full_prose(root, path, old)
    old = before_traffic_value_full_prose(root, path, old)
    old = before_eval_grain_full_prose(root, path, old)
    old = before_exaone_full_prose(root, path, old)
    old = before_isomorph_full_prose(root, path, old)
    old = before_scope_full_prose(root, path, old)
    old = before_fbsde_full_prose(root, path, old)
    old = before_diff_projection_full_prose(root, path, old)
    old = before_radfl_full_prose(root, path, old)
    old = before_proximal_full_prose(root, path, old)
    old = before_igpo_full_prose(root, path, old)
    old = before_sabreagent_full_prose(root, path, old)
    old = before_invevolve_full_prose(root, path, old)
    old = before_hasterad_overview_correction(root, path, old)
    old = before_deepstock_full_prose(root, path, old)
    old = before_orpr_full_prose(root, path, old)
    old = before_hasterad_full_prose(root, path, old)
    old = before_assortment_full_prose(root, path, old)
    old = before_vn2_full_prose(root, path, old)
    old = before_intervention_full_prose(root, path, old)
    old = before_ogr_full_prose(root, path, old)
    old = before_unique_full_prose(root, path, old)
    old = before_flashtrie_full_prose(root, path, old)
    old = before_ahe_full_prose(root, path, old)
    old = before_dcdn_full_prose(root, path, old)
    old = before_ono_full_rewrite(root, path, old)
    old = before_wrapped_produce_full_rewrite(root, path, old)
    old = before_static_constrained_full_rewrite(root, path, old)
    old = before_forecast_critic_full_rewrite(root, path, old)
    old = before_retail_grain_full_rewrite(root, path, old)
    old = before_switch_hurdle_full_rewrite(root, path, old)
    old = before_perishable_full_rewrite(root, path, old)
    old = before_sid_ope_full_rewrite(root, path, old)
    old = before_quasid_full_rewrite(root, path, old)
    old = before_semantic_id_pair_full_rewrite(root, path, old)
    old = before_forecast_pair_full_rewrite(root, path, old)
    old = before_harness_icegr_full_rewrite(root, path, old)
    old = before_tgr_full_rewrite(root, path, old)
    old = before_sona_full_rewrite(root, path, old)
    old = before_genpage_full_rewrite(root, path, old)
    old = before_unir2_full_rewrite(root, path, old)
    return before_pinterest_full_rewrite(root, path, old)


class OverviewText(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.active = False
        self.parts = []
        self.feed(html)

    def handle_starttag(self, name, attrs):
        if name == 'section' and dict(attrs).get('id') == 'overview':
            self.active = True

    def handle_endtag(self, name):
        if name == 'section' and self.active:
            self.active = False

    def handle_data(self, text):
        if self.active:
            self.parts.append(text)


def test_scoped_source_transition_and_rendered_overviews(tmp_path):
    rows = json.loads((ROOT / 'tests/paper_overview_hashes.json').read_text())['files']
    assert len(rows) == 114
    site = tmp_path / 'site'
    build(root=ROOT, site_dir=site)
    anchors = {
        'accuracy-not-service-intermittent-demand': ('20,330件', '−0.555', '63%'),
        'ahe-beta-receipt': ('38課題', '21.9%', '33.3%'),
        'assortment-observation-budget': ('顧客1人', '同じ品揃え', 'ゼロに近づく'),
        'contextual-deconvolution': ('約2割', 'XGBoost', '在庫シミュレーション'),
        'deep-cross-division': ('40.1%', '3.25%', '16.26%'),
        'discounted-perishables-forecast': ('676店舗', '1,077商品', '92.2%'),
        'episem-missing-evidence-recovery': ('6領域', '300組', '10モデル'),
        'featurearc-inherited-defects-chain-gates': ('62.7%', '28.5%', '273実行'),
        'glide-spotify-sid': ('21日間', '5.4%', '14.3%'),
        'grace-meta-ads-gtm-serving': ('23.55%', '40.42%', '条件を満たした候補', '人工データ', '53.6ミリ秒'),
        'hasterad-retail-substitution': ('54店舗', 'ブランド', '10.9%'),
        'inventory-common-threshold-history': ('約1.58倍', '2倍', '累積需要の条件付き確率'),
        'ono-inventory-forecast-selection': ('85,056', '85,093', '約0.04%'),
        'query-prefix-reuse': ('44,225件', '85.82%', '71.45 ms'),
        'retail-forecast-decision-grain': ('4つ', '9つのうち7つ', 'カテゴリ×店舗の計画', '27通りのうち22通り'),
        'sabreagent-design-time-inventory': ('1,320事例', '0.6311', '0.5380'),
        'series-wise-validation': ('11のデータセット', '10種類', '未学習の系列'),
        'shelf-placement-options': ('5店舗・6カテゴリ', '4.0%', '推定利益'),
        'storewide-shelf-decomposition': ('18条件', '16条件', '0.10〜0.29秒', '前半の計算は入っていません'),
        'switch-hurdle-intermittent-demand': ('WRMSSE', '0.6307', '0.6403'),
        'trace-verifier-brittleness': ('25件', '0.250', '15〜36%'),
        'trajectory-deletion-prefix-cost': ('42条件', '9,400回', '26評価', '19評価'),
        'trial-by-trace-evidence-boundaries': ('95課題', '3,420回', '31.1%'),
        'tsfm-sparse-event-ranking': ('5つ', '最大0.031', '30組中29組'),
        'unipinrec': ('0.95%', '0.91%', '11.1%', '63.6%'),
        'walmart-demand-transfer': ('50カテゴリ', '代表5拠点', '誤差が小さくなった'),
        'whole-foods-shelf': ('7.5%', '6.7%', 'シミュレーション'),
        'wrapped-produce-placement-controlled-trial': ('36店舗', '0.32標準偏差', '3.3ポイント'),
        'bridging-forecast-accuracy-inventory-kpis': ('0.43', '0.52', '供給量に上限がない'),
        'case-against-generation-retrieval': ('Recall@10', '4.3〜35.3%', '同じモデル規模'),
        'orpr-or-guided-pretrain-reinforce-inventory': ('331商品', '5.27日', '29.95%', '無作為割り付けではなく'),
        'spotify-incremental-recommendation-causal': ('2日以内', '7.1%', '0.37%', '統計的に有意な差はありません'),
        'constrained-deep-inventory-fbsde': ('50商品', '0.001%未満', '81.5%'),
        'deepstock-policy-regularized-inventory-drl': ('2025年4月', '海外商品で1日', '国内商品で2日', 'シミュレーション'),
        'exaone-demand-routed-tsfm': ('22のデータセット', '1.0667', '1.0742', '1.0818'),
        'reasoncast-agentic-demand-forecasting': ('33.10%', '32.63%', '7.91%', '9.59%'),
        'apollopfn': ('モデルの重みは更新しません', '平均5.7%', 'TabPFN-TS'),
        'evaluation-choices-forecasting-leaderboard': ('19手法中2位', '25手法中23位', '買い手別で17位'),
        'forecast-critic': ('0.88', '0.97', '少なくとも10%'),
        'quasid-collision-qualified-sid': ('TIGER', '0.0211', '0.0230'),
        'scope-coupled-supply-chain-policies': ('18のシナリオ', '1.58%', '実現利益'),
        'sidinspector-mapping-diagnostics': ('23,742商品', '97.7%', 'ReSID/GAOQ'),
        'flashtrie-gpu-beam': ('8億件', '46.3 ms', '1.9 ms', '3.3 ms', '0.71%'),
        'invevolve-whitebox-inventory-evolution': ('25件', '13件', '30件中20件', 'シミュレーション'),
        'netflix-counterfactual-observability': ('11件', '0.8212', '新しい枠'),
        'rest-sequence-ranking': ('1.31%', '11.93%', '50 ms', '実収益の増加率ではありません'),
        'angle-tencent-one-step-retrieval': ('2.16%', '5.01%', '精密ランキング'),
        'gr4ad-ads-generative': ('4.28%', '117%', 'DLRM', 'OneRec-V2', '4億人'),
        'gryphon-v2-cascade': ('7分以上', '1.41%', '1.62%', '応答時間は同程度'),
        'proximal-residual-value-inventory-placement': ('5.0%', '0.950', '配送・移送費用'),
        'intervention-paradox': ('0.94', '64%から38%', '5.8%から8.6%'),
        'igpo-huawei-inventory-grounded-search': ('14日間', '3.17%', '1,000件', '38.9%',
                                               '検索で確認できた商品情報', '検索時に商品カタログを調べる'),
        'isomorph-supply-chain-digital-twin': ('13拠点', '16本', '0.828', '0.721'),
        'agent-reasoning-forgetting-externalized-state': ('67.31%', '36.15%', '0.7376', '0.7178'),
        'autolr-dashen': ('1,586件', '公開判断', '9件', '何割が本番で改善したかは分かりません'),
        'beyond-scalar-dsi-watchtime': ('視聴時間の分布', '1.9〜8.5%', '公開データ3種類'),
        'onetrans-v2-cascade-unification': ('3段階', '利用者を無作為', '9.74%', '共有だけ'),
        'retailbench-long-horizon-store-agents': ('7つのモデル', '180日', '24,350.98', '131,510.42', '平均や実店舗の成績ではありません'),
        'traffic-forecast-to-decision-value': ('29日分', '4.03%', '3.92%', '9交差点のうち2地点', '6.09%', '3.39%', '3.78%', 'すべて0をまたぎました'),
        'vn2-stockout-catboost': ('計3つ学習', '全6回の総合で1位', '4.334ユーロ', '3.763ユーロ', '13.2%'),
        'zalando-sales-event-pricing-forecast-optimize': ('12市場', '23件', '無作為に割り付け', '6.00%', '0.79〜11.03%', '対照と同等だったとまでは言えない'),
        'sim2real-policy-conditioned-inbound-forecast': ('同じ構造', '新ルール導入後の入荷実績', '1.2〜3.1ポイント', '12.5〜18.7ポイント'),
        'linkedin-prediction-to-incrementality': ('8週間', '無作為', '7.20%', '0.31〜14.09%', 'Transformer単体'),
        'pinterest-causal-retrieval-shopping': ('しきい値', '約40%', '0.26%', '1.10%', '85%減らしたのは別の群'),
        'otto-gbdt-vs-dnn-ltr': ('8週間', '1.86%', '0.56%', '1.48%', 'A/Bテストには含まれていません'),
        'uvr-wolt-trial-reorder': ('10カ国', '2週間', '5.5%', '0.16%', '6カ国中5カ国'),
        'genpage-netflix-homepage': ('14日間', '約2億', '0.24%', '0.17〜0.30%', '20%', '既存の候補生成まで'),
        'tgr': ('CCFormer', '3.57%', 'BARGE', '0.60%', 'HiGR', '1.22%', 'TGR-Reason', '13.09%'),
        'sona-yandex-music': ('各群15%', '7日間', '4.53%', '6.30%', '全利用者に展開しておらず'),
        'unir2-sequence-unify': ('5%', '2週間', '1.177%', '2.569%', '推薦の全段階を置き換えた結果でもありません'),
        'gatesid-coldstart-ranking': ('二つの表現', '2週間', '2.6%', '5.6%', '5ミリ秒未満'),
        'icegr-baidu-intent-generative-retrieval': ('5億パラメータ', '最終結果に直接', '3.52%', '15.96%', '7.53%'),
        'ogr-once-generated-ranked': ('3%', '1週間', '1.120%', '本番の応答時間が約2.2倍速くなったという測定結果ではありません'),
        'sid-ope-hierarchy': ('KuaiRand', 'SNIPS', '0.155', '0.087', '同じ数のグループ'),
        'muser-baidu-long-sequence-multi-interest': ('最大10万件', '6通り', '0.26%', '0.89%', '0.2351', '0.2232'),
        'unique-baidu-unified-retrieval-ranking': ('1週間', '0.96%', '1.08%', '99パーセンタイルで89ミリ秒', '推薦画面全体の応答時間ではありません'),
        'unirec-chain-of-attribute': ('ランディングページ', '20%', '5.37%', '4.76%', '5.60%'),
        'snaplgr-snapchat': ('7日間', '0.37%', '4.624%', '11.11%', '視聴時間が2.40倍になったわけではありません'),
        'assortment-replenishment-hard-constraints': ('飲料データ', '最大14%', '補充', '店舗の利益が14%増えたわけではありません'),
        'ra-dfl-risk-aware-decision-focused-inventory': ('4.903', '4.721', '5.380', '観測した売上', '実店舗での費用削減を測った結果ではありません'),
        't0-tsfm-forecasting-with-context': ('36.7', '43.0', '6.3ポイント', '19課題', '11課題', '43%減りました'),
        'youtube-music-llm-rationales-discovery': ('22.43%', '16.93〜27.93%', '8.07%', '理由文だけ', 'YouTube Music全体の利用継続率ではありません'),
        'cq-sid-eg-grpo-tmall': ('2週間','1.15%','0.40%','72.63%','既存の順位付け'),
        'sidscope-diagnostics': ('0.976','0.900','0.083','−0.564から0.205','本番でのA/Bテストはありません'),
        'understanding-sids-isd': ('32.2%','0.0295','0.0387','31.2%','IDを作り直す方法ではありません'),
        'varg-tmall-value-generative-retrieval': ('予備順位付けを通さず','20%','14日間','1.45%','0.22%'),
        'hgenpush-kuaishou-heterogeneous-push-gr': ('投稿者の動画を探す','予備の順位付けを経ず','0.181%','統計的に有意ではありませんでした'),
        'lige-gr-meta-listwise': ('7日間','1.14%','0.72%','0.52%減','別の比較です'),
        'oxygenrec-v2-idgr': ('将来の行動を入力しません','6つの配信面','1.61〜4.44%','4.25%','他の推薦処理を取り除いたという意味ではありません'),
        'pushdualgen-kuaishou': ('14日間','15%を二群に等分','64.46%から69.94%','0.053%から0.033%','文面生成だけの効果ではありません'),
        'agenttether-repair': ('最初に失敗した83件','39件','49件','失敗した課題も3件','全課題に対する成功率ではありません'),
        'scaffold-effects-gaia': ('5つのモデル','3回の試行','最大28ポイント','全モデルの平均ではない'),
        'harness-bench': ('初版の表2','106課題と8モデル','76.2点','52.4点','23.8ポイント'),
        'harness-buys-tokens-not-pass-rate': ('難しいコード修正45課題','約13%','約26%','約8〜9ポイント','約14ポイント','3〜4倍'),
        'gryphon-ilsm': ('0.8209から0.8552','7日間','3,000件から1,000件','0.25%増','従来と同等だったとも'),
        'sam-d2q-aliexpress-doc2query': ('4%','21日間','2.27%','0.53%','3.38%増','この時系列を確定できません'),
        'static-constrained-gr': ('0.033ミリ秒','0.25%','5.1%','実験期間ではありません'),
        'univa-commercial-sid-gar': ('1.50%','初版に5%','第2版に20%','どちらか片方の効果ではありません'),
        'agentx-kuaishou': ('3週間','374案','10件','8倍','約3.7倍','無作為に割り付けた比較でもありません'),
        'aura-disney-agentic-rec-diagnosis': ('それぞれ約10万件','1,911件','±0.1%','本番に出した事例ではありません'),
        'auto-recsys-harness': ('31回','4.0回から1.3回','平均0.5回','対照群のない運用記録'),
        'coral-meta-config-harness': ('0.15%','0.16%','費用を減らせた額','44%','総費用が44%下がったという意味ではありません'),
        'harness-r1': ('44.3%から53.6%','9.3ポイント','同じ重み','全体の改善になるわけではありません'),
        'harness-zero-distillation': ('23.3%から44.3%','41.7%','30.0%','38.0%','全課題を合算した成功率ではありません'),
        'multi-harness-rl': ('1課題を8回ずつ','0.25ポイント','−0.48から+1.02','2.14%から9.27%'),
        'sgc-state-grounded-conditioning': ('200セッション','1,000回答','96.7%','83.5%','26.5%','勝率'),
        'execution-state-unlearning': ('80%','32%','モデルの重みを変更する方法ではありません','選択に影響'),
        'flashvector-unity-serving-stack-agent': ('2.00倍','30倍','1.10倍','広告のクリック率'),
        'hear-harness-engine-serving-protocol': ('481秒から299秒','63.1秒から28.3秒','74.2秒から51.1秒','負荷によって'),
        'swe-serve-inference-serving-agents': ('53課題','19課題','627件','45.9%','69.4%','同じ変更のまま'),
        'dream-taobao-agentic-control': ('2.06%','2.71%','同じ従来方式','足し合わせられません'),
        'evopilot-verify-dont-trust-autoresearch': ('22ポイント','評価に使った候補数は異なって','人の確認','3.20ポイント'),
        'pilot-experiment-lifecycle': ('五つの実験グループ','1.00%','1.40%','53.3%から93.3%','別々の時期'),
        'recevolve-autonomous-rec': ('41件','0.4796から0.5751','3.77%','試行は元に戻し'),
    }
    for path, row in rows.items():
        raw = before_full_article_rewrites(ROOT, path, (ROOT / path).read_bytes())
        previous = restored_before_paper_overview(ROOT, path, raw)
        old, new = map(yaml.safe_load, (previous, raw))
        overview = new['sections'].pop('overview')
        assert overview != old['sections'].pop('overview')
        assert new == old
        for alg in ('sha256', 'blob'):
            assert paper_overview_rewrite_hash(ROOT, path, row['before_' + alg], alg) == row['after_' + alg]
            with pytest.raises(AssertionError):
                paper_overview_rewrite_hash(ROOT, path, row['after_' + alg], alg)
        slug = Path(path).parent.name
        html = (site / 'papers' / f'{slug}.html').read_text()
        parsed = OverviewText(html)
        text = ''.join(parsed.parts)
        assert '概要' in text
        live_overview = (yaml.safe_load((ROOT / path).read_bytes())['sections']['overview']
                         if slug in {'unique-baidu-unified-retrieval-ranking', 'vn2-stockout-catboost',
                                     'hasterad-retail-substitution', 'igpo-huawei-inventory-grounded-search',
                                     'grace-meta-ads-gtm-serving', 'unirec-chain-of-attribute',
                                     'cq-sid-eg-grpo-tmall',
                                     'recevolve-autonomous-rec',
                                     'dream-taobao-agentic-control',
                                     'query-prefix-reuse',
                                     'harness-buys-tokens-not-pass-rate',
                                     'agent-reasoning-forgetting-externalized-state',
                                     'trajectory-deletion-prefix-cost',
                                     'scaffold-effects-gaia', 'whole-foods-shelf',
                                     'wrapped-produce-placement-controlled-trial',
                                     'storewide-shelf-decomposition',
                                     'retail-forecast-decision-grain',
                                     'switch-hurdle-intermittent-demand',
                                     'sim2real-policy-conditioned-inbound-forecast',
                                     'assortment-replenishment-hard-constraints',
                                     'reasoncast-agentic-demand-forecasting',
                                     'forecast-critic',
                                     't0-tsfm-forecasting-with-context',
                                     'flashvector-unity-serving-stack-agent',
                                     'ono-inventory-forecast-selection',
                                     'tsfm-sparse-event-ranking',
                                     'sgc-state-grounded-conditioning',
                                     'harness-zero-distillation',
                                     'swe-serve-inference-serving-agents'} else overview)
        assert live_overview.split('\n')[0] in text
        assert all(value in text for value in anchors[slug])
        with pytest.raises(AssertionError):
            restored_before_paper_overview(ROOT, path, raw + b'\n')


def test_download_mirror_replaces_only_the_overview():
    receipt = json.loads((ROOT / 'tests/paper_overview_hashes.json').read_text())
    assert set(receipt['mirrored']) == {f'papers/{slug}/README.md' for slug in (
        'bridging-forecast-accuracy-inventory-kpis',
        'constrained-deep-inventory-fbsde',
        'deepstock-policy-regularized-inventory-drl',
        'reasoncast-agentic-demand-forecasting',
        'scope-coupled-supply-chain-policies',
        'flashtrie-gpu-beam',
        'invevolve-whitebox-inventory-evolution',
        'beyond-scalar-dsi-watchtime',
        'onetrans-v2-cascade-unification',
        'angle-tencent-one-step-retrieval',
        'gr4ad-ads-generative',
        'proximal-residual-value-inventory-placement',
        'intervention-paradox',
        'igpo-huawei-inventory-grounded-search',
        'isomorph-supply-chain-digital-twin',
        'agent-reasoning-forgetting-externalized-state',
        'retailbench-long-horizon-store-agents',
        'traffic-forecast-to-decision-value',
        'zalando-sales-event-pricing-forecast-optimize',
        'sim2real-policy-conditioned-inbound-forecast',
        'linkedin-prediction-to-incrementality',
        'pinterest-causal-retrieval-shopping',
        'uvr-wolt-trial-reorder',
        'genpage-netflix-homepage',
        'sona-yandex-music',
        'unir2-sequence-unify',
        'gatesid-coldstart-ranking',
        'icegr-baidu-intent-generative-retrieval',
        'ogr-once-generated-ranked',
        'muser-baidu-long-sequence-multi-interest',
        'unique-baidu-unified-retrieval-ranking',
        'unirec-chain-of-attribute',
        'snaplgr-snapchat',
        'ra-dfl-risk-aware-decision-focused-inventory',
        't0-tsfm-forecasting-with-context',
        'youtube-music-llm-rationales-discovery',
        'cq-sid-eg-grpo-tmall',
        'sidscope-diagnostics',
        'varg-tmall-value-generative-retrieval',
        'hgenpush-kuaishou-heterogeneous-push-gr',
        'lige-gr-meta-listwise',
        'oxygenrec-v2-idgr',
        'pushdualgen-kuaishou',
        'harness-buys-tokens-not-pass-rate',
        'sam-d2q-aliexpress-doc2query',
        'static-constrained-gr',
        'univa-commercial-sid-gar',
        'agentx-kuaishou',
        'auto-recsys-harness',
        'coral-meta-config-harness',
        'harness-zero-distillation',
        'sgc-state-grounded-conditioning',
        'flashvector-unity-serving-stack-agent',
        'hear-harness-engine-serving-protocol',
        'swe-serve-inference-serving-agents',
        'dream-taobao-agentic-control',
        'evopilot-verify-dont-trust-autoresearch',
        'pilot-experiment-lifecycle',
        'recevolve-autonomous-rec',
    )}
    for path, row in receipt['mirrored'].items():
        source = before_full_article_rewrites(ROOT, row['source'], (ROOT / row['source']).read_bytes())
        previous = restored_before_paper_overview(ROOT, row['source'], source)
        old, new = (yaml.safe_load(raw)['sections']['overview'].encode() for raw in (previous, source))
        if row.get('mirror_excludes_unchanged_figure'):
            assert Path(path).parent.name in {'genpage-netflix-homepage', 'gatesid-coldstart-ranking', 'agentx-kuaishou'}
            old, old_figure = old.split(b'\n\n<figure', 1)
            new, new_figure = new.split(b'\n\n<figure', 1)
            assert new_figure == old_figure
        if 'prior_mirror' in row:
            slug = Path(path).parent.name
            prior_paragraphs = {
                'proximal-residual-value-inventory-placement': 2,
                'retailbench-long-horizon-store-agents': 1,
                'pinterest-causal-retrieval-shopping': 1,
                'gatesid-coldstart-ranking': 2,
                'icegr-baidu-intent-generative-retrieval': 1,
                'muser-baidu-long-sequence-multi-interest': 1,
                'unique-baidu-unified-retrieval-ranking': 1,
                'unirec-chain-of-attribute': 1,
                'ra-dfl-risk-aware-decision-focused-inventory': 2,
                't0-tsfm-forecasting-with-context': 1,
                'youtube-music-llm-rationales-discovery': 2,
                'cq-sid-eg-grpo-tmall': 2,
                'varg-tmall-value-generative-retrieval': 1,
                'hgenpush-kuaishou-heterogeneous-push-gr': 1,
                'lige-gr-meta-listwise': 1,
                'univa-commercial-sid-gar': 1,
                'auto-recsys-harness': 2,
                'coral-meta-config-harness': 2,
                'flashvector-unity-serving-stack-agent': 1,
                'evopilot-verify-dont-trust-autoresearch': 1,
            }
            assert slug in prior_paragraphs
            old = row['prior_mirror'].encode()
            assert len(old.decode().split('\n\n')) == prior_paragraphs[slug]
        download = before_full_article_rewrites(ROOT, path, (ROOT / path).read_bytes())
        count = row.get('mirror_count',1)
        assert count == (2 if Path(path).parent.name in {'sam-d2q-aliexpress-doc2query', 'harness-zero-distillation', 'swe-serve-inference-serving-agents'} else 1)
        assert download.count(new) == count
        assert download.count(old) == int(Path(path).parent.name in {
            'reasoncast-agentic-demand-forecasting', 'scope-coupled-supply-chain-policies', 'onetrans-v2-cascade-unification',
        })
        restored = download.replace(new, old)
        for alg, before, after in (
            ('sha256', hashlib.sha256(restored).hexdigest(), hashlib.sha256(download).hexdigest()),
            ('blob', *(hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest() for raw in (restored, download))),
        ):
            assert (before, after) == (row['before_' + alg], row['after_' + alg])
            assert paper_overview_rewrite_hash(ROOT, path, before, alg) == after
            with pytest.raises(AssertionError):
                paper_overview_rewrite_hash(ROOT, path, after, alg)
