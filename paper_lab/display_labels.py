"""Reader-facing explanations; stored result keys and numeric values stay unchanged."""
from copy import deepcopy

LABELS = {'agentx-kuaishou': {'利益あり': '改善条件を満たす例', '効果・有意性・guardrailを通過': '効果量・信頼区間・副作用に関する判定条件をすべて満たす'},
 'execution-state-unlearning': {'same_runtime_as_reference': '参照用の再実行と内部状態全体が一致するか',
                                'safe_total': '忘却対象ではない入力値の合計'},
 'igpo-huawei-inventory-grounded-search': {'在庫の状態': '商品カタログの状態',
                                           '在庫を参照：正答': '現時点の商品カタログを参照：正答数',
                                           'probeが商品cを見落とす': '検索が商品cを取得できない'},
 'ogr-once-generated-ranked': {'OGR総演算': '全処理で数えた演算回数'},
 'traffic-forecast-to-decision-value': {'value_percent': '意思決定損失の削減率（過去平均予測を基準、%）'},
 'vn2-stockout-catboost': {'非欠品日のみ：平均': '在庫上限に達しなかった期間だけの平均'},
 'pilot-experiment-lifecycle': {'証明済みのpromote': '判定用の証明書を与えた候補の採用'},
 'auto-recsys-harness': {'human_minutes': '人が作業した時間（分）', 'wall_clock_minutes': '開始から終了までの経過時間（分）'},
 'autolr-dashen': {'mean_reported_gain': '報告に採用された改善量の平均'},
 'coral-meta-config-harness': {'予算10へ射影する数値ツール': '提案を予算10以内へ調整する計算'},
 'cq-sid-eg-grpo-tmall': {'疎報酬の8サンプルにexpertを注入': 'ほとんど報酬が付かない8候補に、正例として用意した候補を追加する'},
 'evopilot-verify-dont-trust-autoresearch': {'完了した2 runでも比較を拒否する': '二つの実験が完了しても、比較条件が合わなければ結果の比較を認めない'},
 'forecast-critic': {'警告する不自然さの閾値': '警告を出す基準スコア', '陽性6/10': '10件中6件を問題ありと人為的に設定'},
 'genpage-netflix-homepage': {'forward回数': 'モデルを順方向に計算した回数'},
 'harness-buys-tokens-not-pass-rate': {'n45_mde50_pp': '45課題・検出力50%で検出できる最小差（ポイント）'},
 'intervention-paradox': {'50タスクpilotの判断のばらつき': '50課題の事前試験で生じる判断のばらつき'},
 'invevolve-whitebox-inventory-evolution': {'人工需要の方策応答と保守的な認証。論文の追試ではない。': '人工需要に対する方策の応答と、採用条件を保守的に判定する計算を示す。論文の追試ではない。'},
 'isomorph-supply-chain-digital-twin': {'1辺': '1本の輸送経路'},
 'quasid-collision-qualified-sid': {'encoder上の2点の角度': '二つの表現ベクトルの角度'},
 'rest-sequence-ranking': {'系列枝への補助損失の重み λ': '履歴を処理する部分に加える補助損失の重み λ',
                           '主損失から系列枝への勾配絶対値': '主損失から履歴の処理部分へ伝わる勾配の絶対値'},
 'revise-recovery': {'oracle_equal': '全再実行と同じ結果になったか'},
 't0-tsfm-forecasting-with-context': {'t0の重みは未実行': 't0の学習済みモデルは動かしていない'},
 'tsfm-sparse-event-ranking': {'ロジスティック発生head': '需要が発生するかを予測するロジスティック回帰'},
 'univa-commercial-sid-gar': {'等頻度bin': '件数が同じになるよう区切った区分'},
 'uvr-wolt-trial-reorder': {'trial重み': '初回注文を重視する重み'},
 'case-against-generation-retrieval': {'残す候補の枝': '探索の第1段で残す候補群の数'},
 'whole-foods-shelf': {'A部門の面積弾力性 β': 'A部門の面積に対する反応を決める係数 β'}}


def display_text(slug, text):
    text = str(text)
    for old, new in sorted(LABELS.get(slug, {}).items(), key=lambda pair: -len(pair[0])):
        text = text.replace(old, new)
    return text


def explorer_view(slug, explorer):
    """Only human-facing explorer fields, never IDs, keys, values or controls."""
    result = deepcopy(explorer)
    if not isinstance(result, dict):
        return result
    if 'label' in result:
        result['label'] = display_text(slug, result['label'])
    for frame in result.get('frames', []):
        if 'note' in frame:
            frame['note'] = display_text(slug, frame['note'])
        for bar in frame.get('bars', []):
            if 'label' in bar:
                bar['label'] = display_text(slug, bar['label'])
    return result


LINE_AXES = {
    'vn2-stockout-catboost': ('期間', 1, '人工例の期間1〜8', '需要と販売の数量（個）'),
    'whole-foods-shelf': ('A部門の面積', 10, 'A部門の面積10〜90（教材内の面積単位）', '人工例の目的値'),
    'case-against-generation-retrieval': ('枝', 1, '候補を分けた枝1〜4', '人工例の関連度スコア'),
    'tgr': ('深さ', 1, '探索の深さ（1段目から）', '目標への到達率（%）'),
    'forecast-critic': ('人工例', 1, '合成した予測例1〜10', '不自然さの規則スコアと警告の閾値'),
    'contextual-deconvolution': ('期間', 1, '人工例の期間1〜8', '需要と在庫の数量（教材内の単位）'),
    'apollopfn': ('期間', 1, '人工例の期間1〜16', '需要と予測の数量（教材内の単位）'),
}


def explorer_axes(slug):
    """Display-only axis semantics, separate from the saved experiment payload."""
    if slug not in LINE_AXES:
        return None
    label, start, horizontal, vertical = LINE_AXES[slug]
    return {'label': label, 'start': start, 'caption': f'横軸：{horizontal}。縦軸：{vertical}。'}
