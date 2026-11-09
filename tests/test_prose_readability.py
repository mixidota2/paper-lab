"""Keep mathematical wording and mirrored reader explanations consistent."""
from pathlib import Path
import re
import yaml
import pytest

ROOT = Path(__file__).resolve().parents[1]


def normalized(text):
    return re.sub(r'\s+', '', text)


def test_inventory_threshold_includes_equality_and_explains_clock():
    source = ROOT / 'papers/inventory-common-threshold-history'
    lab = yaml.safe_load((source / 'lab.yaml').read_text())
    method = (source / 'method.md').read_text()
    ui = (source / 'interactive.html').read_text()
    assert '閾値に達したら発注' in lab['summary']
    assert 'zₜ(u)≥ρ' in method
    assert '閾値を超え' not in lab['summary'] + method
    assert '共通閾値ρに達した単位を発注' in ui
    assert '経過時間ではありません' in ui
    assert '需要経路「0 → 0 → 2」' in ui


@pytest.mark.parametrize('slug', [
    'hear-harness-engine-serving-protocol',
    'sim2real-policy-conditioned-inbound-forecast',
    'harness-buys-tokens-not-pass-rate',
    'traffic-forecast-to-decision-value',
    'bridging-forecast-accuracy-inventory-kpis',
])
def test_download_matches_all_mirrored_sections(slug):
    source = ROOT / 'papers' / slug
    lab = yaml.safe_load((source / 'lab.yaml').read_text())
    readme = normalized((source / 'README.md').read_text())
    for value in [*lab['core_idea'].values(), *lab['sections'].values()]:
        if value.endswith('.md'):
            value = (source / value).read_text()
            if value.startswith('# 原論文と最小実験の対応\n'):
                value = value.split('\n', 1)[1]
        assert normalized(value) in readme


def test_assortment_definitions_precede_symbol_only_output():
    source = ROOT / 'papers/assortment-observation-budget'
    ui = (source / 'interactive.html').read_text()
    method = (source / 'method.md').read_text()
    assert ui.index('cut kは収益順') < ui.index('__ASUMMARY__')
    assert ui.index('値引きの設定ではありません') < ui.index('__ASUMMARY__')
    assert method.index('集合を[k]と書き') < method.index('B/Cの収益')
    assert '方策ごとに未知の選好全体にわたる最悪時後悔' in (source / 'evidence.md').read_text()


def test_batch08_definitions_and_comparison_denominators():
    from paper_lab.batch08 import SIM, HARNESS, TRAFFIC
    from paper_lab.display_labels import LABELS
    assert SIM.index('Gは容量目標') < SIM.index('class="flow"')
    sim = yaml.safe_load((ROOT/'papers/sim2real-policy-conditioned-inbound-forecast/lab.yaml').read_text())
    assert '予測誤差を実績で割った割合の絶対値を平均した指標（MAPE）' in sim['sections']['overview']
    assert HARNESS.index('仮定した成功率差Δ') < HARNESS.index('data-power')
    assert TRAFFIC.index('同じ行動集合のhistoricalを分母') < TRAFFIC.index('data-toy')
    assert '一定値の基準予測' in LABELS['traffic-forecast-to-decision-value']['value_percent']
    method=(ROOT/'papers/harness-buys-tokens-not-pass-rate/method.md').read_text()
    assert 'p値は帰無仮説' in method and '仮定した差Δの下で' in method
    guide=(ROOT/'guides/forecast-to-replenishment.md').read_text()
    assert guide.index('GMVは流通取引総額') < guide.index('<!-- EVIDENCE_CARDS -->')
    assert '未実施の計画' in guide and '実データで比較を始めるための計画' in guide


def test_whole_foods_explains_response_and_distinguishes_toy_from_evidence():
    source = ROOT / 'papers/whole-foods-shelf'
    lab = yaml.safe_load((source / 'lab.yaml').read_text())
    assert '面積を変えた割合に対して需要がどれだけの割合で変わるか' in lab['core_idea']['author_claim']
    assert '正則化の偏りへの対処とは異なる' in lab['core_idea']['research_bot_interpretation']
    explanation = lab['sections']['executable_understanding']
    assert 'A部門を広げると、その分だけB部門が狭くなる' in explanation
    assert '棒グラフは等分と選んだ配分の目的値、折れ線は候補ごとの目的値' in explanation
    assert '実売上ではない' in explanation
    assert '構成上の性質' in lab['sections']['evidence']
    assert '信頼区間（CI）' in (source / 'mapping.md').read_text()


def test_forecast_prose_defines_denominators_and_information_boundaries():
    def lab(slug):
        return yaml.safe_load((ROOT/'papers'/slug/'lab.yaml').read_text())
    vn = lab('vn2-stockout-catboost')
    assert '分母は残った期間数' in vn['sections']['executable_understanding']
    assert '残る期間がなければ平均は未定義' in vn['interactives'][0]['caption']
    cd = lab('contextual-deconvolution')
    assert '保管単価を欠品単価で割った費用比' in cd['sections']['executable_understanding']
    assert '各期は独立で在庫を持ち越さず' in cd['interactives'][0]['caption']
    fc = lab('forecast-critic')
    assert not fc['interactives']
    assert '再現率は不適切な予測の総数のうち検出できた割合' in fc['sections']['executable_understanding']
    assert '監視を導入すれば誤差が10%改善するという結果ではない' in fc['sections']['evidence']
    ap = lab('apollopfn')
    assert not ap['interactives']
    assert '予測誤差の絶対値を全期間で平均' in ap['sections']['executable_understanding']
    assert '販促効果の大きさは既知と仮定' in ap['sections']['executable_understanding']
    for obj in [vn, cd, fc, ap]:
        assert obj['sections']['executable_understanding'].split('\n')[0] in obj['sections']['what_we_verified']
    method = (ROOT/'papers/vn2-stockout-catboost/method.md').read_text()
    assert '予測誤差を二乗して平均し、平方根を取る' in method
    assert '予測誤差の絶対値を平均した平均絶対誤差' in method


def test_order_completion_and_quantity_fill_are_distinct():
    a = ROOT/'papers/accuracy-not-service-intermittent-demand'
    b = ROOT/'papers/bridging-forecast-accuracy-inventory-kpis'
    first = yaml.safe_load((a/'lab.yaml').read_text())
    second = yaml.safe_load((b/'lab.yaml').read_text())
    assert '全明細が揃った注文数を全注文数で割るCOFR' in first['sections']['problem']
    assert '需要数量のうち即時に満たせた数量の割合' in second['sections']['results']
    assert '品目別の比を単純平均した値ではない' in (a/'method.md').read_text()
    assert '評価期間中の需要で更新しない' in (b/'method.md').read_text()
    assert '未納分を翌日へ繰り越さない' in (b/'method.md').read_text()
    # This older download mirrors only its summary and verification scope.
    readme = normalized((a/'README.md').read_text())
    for value in [first['summary'], first['sections']['what_we_verified'], first['sections']['what_we_did_not_verify']]:
        assert normalized(value) in readme


def test_inventory_learning_explanations_keep_conditions_and_download_mirrors():
    # These passages are mirrored by each download; other README sections differ.
    mirrors = {
        'deepstock-policy-regularized-inventory-drl': ['why_it_might_work', 'evidence', 'executable_understanding'],
        'constrained-deep-inventory-fbsde': ['problem', 'why_it_might_work', 'executable_understanding', 'what_we_did_not_verify'],
        'diff-projection-feasible-multi-echelon-inventory': ['why_it_might_work', 'executable_understanding'],
        'or-transformer-joint-replenishment': ['problem', 'evidence', 'results'],
        'orpr-or-guided-pretrain-reinforce-inventory': ['executable_understanding'],
        'ra-dfl-risk-aware-decision-focused-inventory': ['executable_understanding'],
    }
    labs = {}
    for slug, sections in mirrors.items():
        source = ROOT / 'papers' / slug
        lab = yaml.safe_load((source / 'lab.yaml').read_text())
        labs[slug] = lab
        readme = normalized((source / 'README.md').read_text())
        for section in sections:
            assert normalized(lab['sections'][section]) in readme
    deep = labs['deepstock-policy-regularized-inventory-drl']['sections']
    assert 'ネットワークの出力μ自体も在庫状態によって変わる' in deep['why_it_might_work']
    assert '単調性保証にはならない' in deep['why_it_might_work']
    fbsde = labs['constrained-deep-inventory-fbsde']['sections']
    assert '共通する区間がなければ実行不能' in fbsde['executable_understanding']
    assert '全制約を満たす発注が存在することは保証していない' in fbsde['what_we_did_not_verify']
    projection = labs['diff-projection-feasible-multi-echelon-inventory']['sections']
    assert '等号になっている制約の組（活性集合）' in projection['why_it_might_work']
    assert '通常の微分が常に存在するという主張でもない' in projection['why_it_might_work']
    ort = labs['or-transformer-joint-replenishment']
    assert '需要と発注の有無を固定' in ort['core_idea']['author_claim']
    assert '表現は未学習で、発注量そのものではない' in ort['sections']['results']
    orpr = labs['orpr-or-guided-pretrain-reinforce-inventory']['sections']
    assert '自分以外の報酬平均を引いた差' in orpr['executable_understanding']
    assert '全報酬に同じ定数' in orpr['executable_understanding']
    risk = ROOT / 'papers/ra-dfl-risk-aware-decision-focused-inventory/method.md'
    assert '境界に同じ費用が並ぶ場合も、その確率幅に合う重み' in risk.read_text()
    assert 'w_outは役割が違う' in risk.read_text()


def test_forecast_inventory_batch8_explanations_and_downloads():
    cases = {
        'sabreagent-design-time-inventory': ('problem', 'すべての需要を即時に満たした場合の売上'),
        'invevolve-whitebox-inventory-evolution': ('results', '不確実性を差し引いた信頼下限'),
        'proximal-residual-value-inventory-placement': ('executable_understanding', '一方の拠点への配置量から他方も決まる'),
        'switch-hurdle-intermittent-demand': ('core_idea', 'ゼロ'),
        'scope-coupled-supply-chain-policies': ('executable_understanding', '容量で割った値を整数へ切り上げ'),
        'isomorph-supply-chain-digital-twin': ('executable_understanding', 'その日の新規需要量を分母、そのうち当日に満たせた数量を分子'),
    }
    for slug, (section, explanation) in cases.items():
        source = ROOT / 'papers' / slug
        lab = yaml.safe_load((source / 'lab.yaml').read_text())
        if slug == 'switch-hurdle-intermittent-demand':
            text = lab['core_idea']['author_claim']
            assert '1つの処理ネットワーク（expert）' in text
        else:
            text = lab['sections'][section]
        assert explanation in text
        assert normalized(text) in normalized((source / 'README.md').read_text())
    hurdle = (ROOT / 'papers/switch-hurdle-intermittent-demand/method.md').read_text()
    assert '正の需要が起きる確率の合計で割り直す' in hurdle
    sabre = (ROOT / 'papers/sabreagent-design-time-inventory/method.md').read_text()
    assert '固定したコードの中で、予測の更新や方策パラメータの探索は続く' in sabre
    assert '分位点が下がる場合まで近視眼最適とは主張していない' in sabre


def test_batch9_forecast_metrics_and_decision_boundaries():
    excerpts = {
        'reasoncast-agentic-demand-forecasting': ('method.md', '絶対誤差の総和'),
        'evaluation-choices-forecasting-leaderboard': ('lab.yaml', '符号付きで合計してから絶対値'),
        'exaone-demand-routed-tsfm': ('method.md', '学習用の教師比率'),
        't0-tsfm-forecasting-with-context': ('method.md', '時間・商品をまたいで需要がどう同時に変動するか'),
        'walmart-demand-transfer': ('method.md', '購入を断念する割合を先に除き'),
        'zalando-sales-event-pricing-forecast-optimize': ('lab.yaml', '比較の分母は、真の期待需要を知るoracle'),
    }
    for slug, (name, text) in excerpts.items():
        source = ROOT/'papers'/slug
        assert text in (source/name).read_text()
        if (source/'README.md').exists() and slug != 't0-tsfm-forecasting-with-context':
            assert text in (source/'README.md').read_text()
    inv = yaml.safe_load((ROOT/'papers/invevolve-whitebox-inventory-evolution/lab.yaml').read_text())
    assert '配備する方策を選ぶ' in inv['core_idea']['author_claim']
    assert '配備先を選ぶ' not in inv['core_idea']['author_claim']
    reason = ROOT/'papers/reasoncast-agentic-demand-forecasting'
    for name in ['method.md', 'mapping.md', 'README.md']:
        text = (reason/name).read_text()
        assert '過大予測と過小予測は相殺しません' in text
        assert '実績合計で割らないため表示します' in text


def test_batch10_retail_constraints_and_evaluation_scope():
    expected = {
        'assortment-replenishment-hard-constraints': ('lab.yaml', '商品ごとの棚在庫条件と棚幅の条件'),
        'shelf-placement-options': ('lab.yaml', '取り出し余白は置ける面数の判定に使い'),
        'storewide-shelf-decomposition': ('lab.yaml', '採用品の基礎需要比で配った流入'),
        'tsfm-sparse-event-ranking': ('lab.yaml', '同点を恣意的に並べ替えて成績を上げることはしない'),
        'wrapped-produce-placement-controlled-trial': ('lab.yaml', '無作為割付ではない'),
        'retailbench-long-horizon-store-agents': ('method.md', '日初の現金で買える整数個数と潜在需要の小さい方'),
    }
    for slug, (name, excerpt) in expected.items():
        assert excerpt in (ROOT/'papers'/slug/name).read_text()
    for name in ['lab.yaml', 'README.md']:
        text = (ROOT/'papers/tsfm-sparse-event-ranking'/name).read_text()
        assert '需要が発生したかを教師として学ぶ出力部（head）' in text
        assert '同点を恣意的に並べ替えて成績を上げることはしない' in text
    for name in ['method.md', 'README.md', 'mapping.md']:
        text = (ROOT/'papers/retailbench-long-horizon-store-agents'/name).read_text()
        assert '日初の現金で買える整数個数と潜在需要の小さい方' in text
        assert '翌日以降は取引も家賃も0' in text


def test_batch11_recommendation_conditions_and_metric_meaning():
    expected = {
        'otto-gbdt-vs-dnn-ltr': ('method.md', '学習時に重みを動かす勾配の大きさまで等しくなるとは限らない'),
        'static-constrained-gr': ('lab.yaml', '許可集合Cのどれかの先頭部分であるときだけ'),
        'tgr': ('lab.yaml', '全階層で正しい枝を選んだ場合だけ到達成功'),
        'unipinrec': ('method.md', '同じ履歴とモデルを使う限り'),
        'beyond-scalar-dsi-watchtime': ('lab.yaml', '人工分布の確率で重み付けして平均する'),
        'netflix-counterfactual-observability': ('lab.yaml', '重みの合計で割る'),
    }
    for slug, (name, excerpt) in expected.items():
        assert excerpt in (ROOT/'papers'/slug/name).read_text()
    for name in ['lab.yaml', 'README.md']:
        assert '実際のattention演算数や応答時間ではない' in (ROOT/'papers/unipinrec'/name).read_text()
        assert '人工分布の確率で重み付けして平均する' in (ROOT/'papers/beyond-scalar-dsi-watchtime'/name).read_text()


def test_batch12_generation_training_and_serving_boundaries():
    expected = {
        'varg-tmall-value-generative-retrieval': ('lab.yaml', '正解番号そのものを当てるexact lossも残す'),
        'cq-sid-eg-grpo-tmall': ('method.md', '配信時に正解SIDを渡す仕掛けではない'),
        'pushdualgen-kuaishou': ('lab.yaml', '訓練でcopyの損失が共有重みへ与える影響は残る'),
        'hgenpush-kuaishou-heterogeneous-push-gr': ('lab.yaml', '比そのものの算術平均ではなく、幾何平均'),
        'univa-commercial-sid-gar': ('lab.yaml', 'α=0にすると配信時の価値加算は消えるが、RL済み生成方策は残る'),
        'flashtrie-gpu-beam': ('lab.yaml', '現在のprefixから続く枝があるとは限らない'),
    }
    for slug, (name, excerpt) in expected.items():
        assert excerpt in (ROOT/'papers'/slug/name).read_text()
    for name in ['lab.yaml', 'README.md']:
        assert '通知説明文（copy）を必要な場合だけ生成する' in (ROOT/'papers/pushdualgen-kuaishou'/name).read_text()
        assert '前のtokenによって確率表を変えない非自己回帰（NAR）' in (ROOT/'papers/flashtrie-gpu-beam'/name).read_text()


def test_batch13_sid_diagnostic_denominators_and_decision_boundaries():
    expected = {
        'understanding-sids-isd': ('method.md', '探索候補を削る前にこの値で順位を付け直す'),
        'quasid-collision-qualified-sid': ('lab.yaml', 'その群のpair数とεの和で割る'),
        'sidinspector-mapping-diagnostics': ('lab.yaml', '全近傍edgeの重み合計で割る'),
        'sidscope-diagnostics': ('method.md', '更新前後に共通するitemのうちコードが変わった割合'),
        'gatesid-coldstart-ranking': ('lab.yaml', '商品ごとの重み付き損失を平均して順位付けの損失へ加える'),
        'glide-spotify-sid': ('method.md', '同じSIDからどのエピソードを返すかを決めるtie-breaker'),
    }
    for slug, (name, excerpt) in expected.items():
        assert excerpt in (ROOT/'papers'/slug/name).read_text()
    inspector = (ROOT/'papers/sidinspector-mapping-diagnostics/method.md').read_text()
    assert 'itemごとに求めた割合の平均' in inspector
    scope = (ROOT/'papers/sidscope-diagnostics/method.md').read_text()
    assert 'item数から一意のleaf数を引いた差を、それぞれ全item数で割る' in scope


def test_batch14_training_denominators_and_candidate_boundaries():
    expected = {
        'snaplgr-snapchat': ('method.md', '同じSIDの動画から保存する候補を選ぶ段階'),
        'icegr-baidu-intent-generative-retrieval': ('method.md', '正解SIDのlog確率をそのSIDの長さで割る'),
        'gr4ad-ads-generative': ('method.md', '順位差の絶対値を、候補数に応じた最大の順位差で割っている'),
        'unique-baidu-unified-retrieval-ranking': ('lab.yaml', '一様な使用率より多く使われるcodeの距離を大きくし'),
        'unir2-sequence-unify': ('method.md', '前向きの計算ではbase経路の値を使う'),
        'unirec-chain-of-attribute': ('lab.yaml', 'その属性が現れる確率で重み付けした平均'),
    }
    for slug, (name, excerpt) in expected.items():
        assert excerpt in (ROOT/'papers'/slug/name).read_text()
    unirec = (ROOT/'papers/unirec-chain-of-attribute/lab.yaml').read_text()
    assert 'すべての生成prefixで精度が上がる保証' in (ROOT/'papers/unirec-chain-of-attribute/method.md').read_text()
    assert '商品数の均等化ではない' in unirec
    assert '同じ履歴・ユーザー情報を条件にすると、属性を知る前より平均では大きくならない' in unirec
    assert '属性がSIDについて追加の情報を持つと、その分だけ小さくなる' in unirec
    assert '正解属性を与えるteacher forcingと、誤る可能性のある属性を生成する推論は違う' in unirec
    assert '属性段で落とした商品は後段SIDだけでは戻せない' in unirec
    unir2 = (ROOT/'papers/unir2-sequence-unify/lab.yaml').read_text()
    assert '調整できる自由度をそろえる' in unir2


def test_batch15_causal_comparisons_and_group_denominators():
    expected = {
        'spotify-incremental-recommendation-causal': ('method.md', 'その群の件数で割り、得られた平均を足す'),
        'linkedin-prediction-to-incrementality': ('lab.yaml', '送信あり・なしの両方を観測できること'),
        'pinterest-causal-retrieval-shopping': ('lab.yaml', '均等割当のこの例で'),
        'sona-yandex-music': ('lab.yaml', '同じ向きに厳密な順位を付けた割合'),
        'uvr-wolt-trial-reorder': ('method.md', '正解を含む各クラスへε/|domain|を配り'),
        'youtube-music-llm-rationales-discovery': ('lab.yaml', '音楽的な特徴や好みとの接点まで正しいとは限らない'),
    }
    for slug, (name, excerpt) in expected.items():
        assert excerpt in (ROOT/'papers'/slug/name).read_text()
    for name in ['lab.yaml', 'README.md']:
        assert '同じ向きに厳密な順位を付けた割合' in (ROOT/'papers/sona-yandex-music'/name).read_text()
        assert 'trialとreorderそれぞれのsession数で割って平均する' in (ROOT/'papers/uvr-wolt-trial-reorder'/name).read_text()
        assert '送信あり・なしの両方を観測できること' in (ROOT/'papers/linkedin-prediction-to-incrementality'/name).read_text()
    assert '有限個のログで必ず真値に一致するという意味ではない' in (ROOT/'papers/pinterest-causal-retrieval-shopping/method.md').read_text()


def test_batch16_candidate_units_and_conditional_comparisons():
    expected = {
        'angle-tencent-one-step-retrieval': ('method.md', 'kは広告件数ではなく組の数'),
        'igpo-huawei-inventory-grounded-search': ('lab.yaml', '対応商品がある要求のうち、商品を返さず棄権した要求の割合'),
        'sam-d2q-aliexpress-doc2query': ('lab.yaml', 'その商品のタイトルまたは追加した検索語の集合に含まれる場合だけ'),
        'case-against-generation-retrieval': ('method.md', '同じ候補集合内で確率分布へ正規化'),
        'ogr-once-generated-ranked': ('method.md', 'そのユーザーの候補集合の平均より高いか低いか'),
        'lige-gr-meta-listwise': ('method.md', 'それまでに選んだ動画の継続確率を順に掛けた値'),
    }
    for slug, (name, excerpt) in expected.items():
        assert excerpt in (ROOT/'papers'/slug/name).read_text()
    for name in ['lab.yaml', 'README.md']:
        assert '対応商品がない要求のうち、商品を返して一致とした要求の割合' in (ROOT/'papers/igpo-huawei-inventory-grounded-search'/name).read_text()
        assert 'どれかの語が合うだけでは取得しない' in (ROOT/'papers/sam-d2q-aliexpress-doc2query'/name).read_text()
        assert '平均点が低い枝にも最高点の候補があり得る' in (ROOT/'papers/case-against-generation-retrieval'/name).read_text()
    assert '非関連広告を学習全体から捨てるのではなく、関連性の判定には使う' in (ROOT/'papers/angle-tencent-one-step-retrieval/lab.yaml').read_text()


def test_batch17_cascade_comparison_units_and_loss_denominators():
    expected = {
        'gryphon-ilsm': ('lab.yaml', '候補から脱落した正解曲も分母に残す'),
        'gryphon-v2-cascade': ('lab.yaml', '学生の同点は一致に数えない'),
        'oneranker-ads': ('lab.yaml', '集合内の並び順の一致は測らない'),
        'onetrans-v2-cascade-unification': ('method.md', '同じ接頭辞を持つ候補には同じ加点が付く'),
        'muser-baidu-long-sequence-multi-interest': ('lab.yaml', '分母は異なる組の数ではない'),
        'oxygenrec-v2-idgr': ('lab.yaml', '不一致位置のlog確率も損失に含まれる'),
    }
    for slug, (name, excerpt) in expected.items():
        assert excerpt in (ROOT/'papers'/slug/name).read_text()
    for name in ['method.md', 'README.md']:
        assert '施策の因果効果を推定する手法という意味ではない' in (ROOT/'papers/onetrans-v2-cascade-unification'/name).read_text()
    assert '全候補をまとめた平均ではない' in (ROOT/'papers/gryphon-v2-cascade/lab.yaml').read_text()
    assert 'どの位置も選ばれない経路の損失はゼロになる' in (ROOT/'papers/oxygenrec-v2-idgr/lab.yaml').read_text()


def test_batch18_weighting_diagnostics_and_decision_boundaries():
    expected = {
        'rest-sequence-ranking': ('lab.yaml', '予測値を固定した地点での計算'),
        'tagr-live-sid': ('method.md', '分母はログの生件数ではない'),
        'sid-ope-hierarchy': ('lab.yaml', '推定の偏りが消えたことを意味しない'),
        'genpage-netflix-homepage': ('lab.yaml', 'その部分の途中で作品を追加してもスコアを計算し直さない'),
        'agentx-kuaishou': ('method.md', '現時点では採用を決めない'),
        'aura-disney-agentic-rec-diagnosis': ('lab.yaml', '参照先の内容が診断を裏付けるかまでは判定しない'),
    }
    for slug, (name, excerpt) in expected.items():
        assert excerpt in (ROOT/'papers'/slug/name).read_text()
    for name in ['lab.yaml', 'README.md']:
        assert 'その部分の途中で作品を追加してもスコアを計算し直さない' in (ROOT/'papers/genpage-netflix-homepage'/name).read_text()
    assert 'どちらも広告数を分母にする' in (ROOT/'papers/tagr-live-sid/lab.yaml').read_text()
    assert 'その差を合計して課題数で割る' in (ROOT/'papers/agentx-kuaishou/lab.yaml').read_text()
    assert 'その平方根を取る' in (ROOT/'papers/sid-ope-hierarchy/lab.yaml').read_text()


def test_batch19_experiment_state_and_aggregation_contracts():
    expected = {
        'coral-meta-config-harness': ('lab.yaml', '各設定値と提案値の差を二乗して合計し'),
        'dream-taobao-agentic-control': ('lab.yaml', '等号も呼び出し条件に含む'),
        'pilot-experiment-lifecycle': ('method.md', '施策によって変わった行動で事後的に群を分けない'),
        'auto-recsys-harness': ('lab.yaml', '実行中の別jobが後で得る知識は先取りしない'),
        'autolr-dashen': ('lab.yaml', '同じrunで何度採択しても、この件数には一度だけ数える'),
        'recevolve-autonomous-rec': ('lab.yaml', '同点の負例も正例より前に数える'),
    }
    for slug, (name, excerpt) in expected.items():
        assert excerpt in (ROOT/'papers'/slug/name).read_text()
    for name in ['lab.yaml', 'README.md']:
        assert '各設定値と提案値の差を二乗して合計し' in (ROOT/'papers/coral-meta-config-harness'/name).read_text()
    assert 'IPVの重みとscatter幅を補正し' in (ROOT/'papers/dream-taobao-agentic-control/lab.yaml').read_text()
    assert '全条件を満たしたbucketの割合ではない' in (ROOT/'papers/pilot-experiment-lifecycle/lab.yaml').read_text()
    assert '上位に正例が入らないqueryもゼロとして含める' in (ROOT/'papers/recevolve-autonomous-rec/lab.yaml').read_text()
    assert '並行jobの所要時間を足した値とは異なる' in (ROOT/'papers/auto-recsys-harness/method.md').read_text()
    assert "下表は200seedの集計。" in (ROOT/"papers/autolr-dashen/lab.yaml").read_text()


def test_batch20_harness_denominators_and_intervention_boundaries():
    phrases = {
        'harness-bench': ('lab.yaml', '一つでも欠ければ不合格'),
        'harness-r1': ('method.md', '全課題を一つにまとめた成功率とは区別'),
        'harness-zero-distillation': ('lab.yaml', '各領域の率を同じ重みで平均'),
        'multi-harness-rl': ('lab.yaml', '群の全件数で平均し、その平方根'),
        'scaffold-effects-gaia': ('lab.yaml', '上限は初回呼出しを含まず'),
        'intervention-paradox': ('lab.yaml', '実際に観測した整数の件数ではない'),
    }
    for slug, (name, text) in phrases.items():
        assert text in (ROOT/'papers'/slug/name).read_text()
    root = ROOT/'papers/harness-zero-distillation'
    for name in ('lab.yaml', 'README.md'):
        assert '課題を全領域で合算した成功率ではない' in (root/name).read_text()
    for name in ('method.md', 'README.md'):
        assert 'その推論文を模倣するようには学習させない' in (root/name).read_text()
    for name in ('lab.yaml', 'README.md'):
        assert '成功したタスクはそこで止める' in (ROOT/'papers/scaffold-effects-gaia'/name).read_text()
    method = (ROOT/'papers/intervention-paradox/method.md').read_text()
    assert 'r+d>0' in method and '境界と等しい場合は期待成功率の差がゼロ' in method
    assert '同じbatchの全課題で修正前後の報酬差を平均' in (ROOT/'papers/harness-r1/lab.yaml').read_text()


def test_batch21_memory_repair_and_cost_aggregation_boundaries():
    phrases = {
        'agent-reasoning-forgetting-externalized-state': ('lab.yaml', '削除は要求列の開始前だけに行う'),
        'agenttether-repair': ('lab.yaml', '必要な介入間隔が空いていることを免除しない'),
        'execution-state-unlearning': ('method.md', '秘密を返した問いの割合ではない'),
        'revise-recovery': ('lab.yaml', '親の状態や副作用の検査は省かない'),
        'sgc-state-grounded-conditioning': ('lab.yaml', '見送りを挟んだ再提案は数えない'),
        'trajectory-deletion-prefix-cost': ('method.md', '課題ごとの費用比を先に平均した値ではない'),
    }
    for slug, (name, phrase) in phrases.items():
        assert phrase in (ROOT/'papers'/slug/name).read_text()
    for slug in ('agent-reasoning-forgetting-externalized-state', 'sgc-state-grounded-conditioning'):
        assert phrases[slug][1] in (ROOT/'papers'/slug/'README.md').read_text()
    assert '実LLMの監査能力の証拠にはならない' in (ROOT/'papers/execution-state-unlearning/method.md').read_text()
    assert '介入の再実行や削除の抽選の変動を含まない' in (ROOT/'papers/trajectory-deletion-prefix-cost/method.md').read_text()


def test_batch22_evidence_continuation_and_serving_units():
    phrases = {
        'episem-missing-evidence-recovery': ('method.md', '事実が見えないことと、その事実が偽であることは別'),
        'evopilot-verify-dont-trust-autoresearch': ('lab.yaml', '許可した変更が実際には起きていない場合も拒否'),
        'featurearc-inherited-defects-chain-gates': ('method.md', 'その段階は継続率の集計へ戻さない'),
        'flashvector-unity-serving-stack-agent': ('lab.yaml', '途中で不合格になれば、以降の判定へ進まない'),
        'grace-meta-ads-gtm-serving': ('method.md', '同じ広告が全ての属性を満たすことは異なる'),
        'swe-serve-inference-serving-agents': ('lab.yaml', '同じサービスのインスタンスへ続けて要求を送る'),
        'trace-verifier-brittleness': ('method.md', 'ツール名の種類であり、呼出し回数ではない'),
    }
    for slug, (name, phrase) in phrases.items():
        assert phrase in (ROOT/'papers'/slug/name).read_text()
    assert phrases['swe-serve-inference-serving-agents'][1] in (ROOT/'papers/swe-serve-inference-serving-agents/README.md').read_text()
    flash = (ROOT/'papers/flashvector-unity-serving-stack-agent/lab.yaml').read_text()
    order = ('出力の一致、測定値が有限であること、p99 SLO、全体throughputの退行がないこと、'
             '局所と全体の改善がnoiseを超えることの順')
    assert order in flash
    assert '実traffic replayやagentの実行ではない' in flash
    assert '分母0は0%にせず、未定義' in (ROOT/'papers/featurearc-inherited-defects-chain-gates/method.md').read_text()
    assert '必要な書込みが抜けていれば' in (ROOT/'papers/trace-verifier-brittleness/method.md').read_text()


def test_root_readme_catalog_and_validation_scope():
    readme = (ROOT/'README.md').read_text()
    count = len(list((ROOT/'papers').glob('*/lab.yaml')))
    assert f'{count}件のLabと、2件のテーマガイド' in readme
    assert f'全{count}件のLabの読み込み' in readme
    assert (ROOT/'guides/shelf-decisions.md').is_file()
    assert (ROOT/'guides/forecast-to-replenishment.md').is_file()
    assert 'pytestに加えて全サイトのビルドと静的preflight' in readme
    assert '共通閾値・ORPR・予測精度と在庫指標のLab、原稿と事例カードが必要' in readme
    assert '数値・式・出典・比較対象・未検証の範囲は省きません' in readme
    assert '実ブラウザー確認は任意' in readme
    assert '保護設定を変更して回避しません' in readme
