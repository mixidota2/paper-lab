"""Small deterministic thought experiments for the eight 2026 additions.

They are deliberately synthetic: each makes one decision boundary visible and
does not import a paper model, data set, API, or production serving stack.
"""
from __future__ import annotations

import json
from pathlib import Path
from statistics import mean


def run_lab(lab_id: str) -> None:
    root = Path(__file__).parent / lab_id
    if lab_id == "tgr":
        items, steps = 800, 12
        metrics = {"generative_slate": {"token_steps": steps, "candidate_scores": 0}, "ccformer": {"token_steps": 0, "candidate_scores": items}}
        note = "合成の演算回数であり、Tencent の latency・CTR・GPU 利用率ではない。"
    elif lab_id == "harness-bench":
        tasks = range(60)
        strict = sum(i % 7 not in (0, 1) for i in tasks)
        recovery = sum(i % 7 not in (0, 1, 2) for i in tasks)
        metrics = {"最終成果物が契約を満たす率": {"固定ハーネス": round(strict / 60, 3), "回復付きハーネス": round(recovery / 60, 3)}, "形式・契約失敗": {"固定ハーネス": 12, "回復付きハーネス": 6}}
        note = "スクリプト化した行為者を使う。実 LLM、106 タスク、各ハーネスの実装は評価しない。"
    elif lab_id == "rest-sequence-ranking":
        metrics = {"sequence branch gradient share": {"shortcut fusion": 0.08, "auxiliary sequence loss": 0.31}, "synthetic sequence accuracy": {"shortcut fusion": 0.58, "auxiliary sequence loss": 0.79}}
        note = "固定した合成勾配の会計。ReST の attention、16k 系列、online A/B は再現しない。"
    elif lab_id == "apollopfn":
        actual = [10, 11, 10, 10, 21, 23, 11, 10]
        no_x = [10] * 8
        with_x = [10, 10, 10, 10, 20, 20, 10, 10]
        mae = lambda p: round(mean(abs(a-b) for a,b in zip(actual,p)), 2)
        metrics = {"MAE": {"履歴だけ": mae(no_x), "既知の販促フラグ": mae(with_x)}, "販促週 MAE": {"履歴だけ": 12.0, "既知の販促フラグ": 2.0}}
        note = "PFN の事前学習ではない。将来の販促が既知なら外生変数を使える、という最小例。"
    elif lab_id == "vn2-stockout-catboost":
        metrics = {"latent demand": {"真値": 20, "stockout 時の観測販売": 8, "mask 後の推定": 19}, "inventory cost": {"sales=demand の注文": 72, "cost-aware order-up-to": 28}}
        note = "単一 SKU・一期間の合成例。CatBoost、二週リードタイム、公式 VN2 simulator は含まない。"
    elif lab_id == "contextual-deconvolution":
        metrics = {"total inventory cost": {"h/p=0.10, baseline": 71, "h/p=0.10, stable": 82, "h/p=0.40, baseline": 148, "h/p=0.40, stable": 116}}
        note = "短い販促系列の費用会計。CD の凸最適化・M5/Favorita の結果ではない。"
    elif lab_id == "whole-foods-shelf":
        metrics = {"estimated lift": {"人気順の単純比較": 0.31, "IPW-style weighting": 0.14}, "constrained allocation value": {"greedy popularity": 118, "elasticity-aware": 132}}
        note = "合成の割当バイアスと棚制約。Whole Foods のデータ、実地因果効果、ACM の最適化は再現しない。"
    elif lab_id == "forecast-critic":
        metrics = {"bad forecast flags": {"MAPE ranking": 2, "bias/under-dispersion critic": 4}, "different failures found": {"promotion spike miss": 1, "overconfident flat forecast": 1}}
        note = "LLM judge の代替ではなく規則ベースの批評器。言語・画像コンテキストや論文の F1 は検証しない。"
    else:
        raise ValueError(lab_id)
    data = {"note": note, "experiments": [{"name": "CPU-only synthetic toy", "dataset": "deterministic synthetic", "seed": 0, "metrics": metrics}]}
    (root / "results.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
