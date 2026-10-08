# 原論文と最小実験の対応

一次資料：[arXiv 2610.04433v1](https://arxiv.org/pdf/2610.04433v1)。2026-10-08照合。PDF SHA-256: `c0c4899a732bb57aab9bac01fb64c83bc343c2a53e65554024ae292113726a32`。

| 原典 | Lab | 境界 |
| --- | --- | --- |
| Appendix F / Fig.A2 | binom(), rejection(), power(), mde(), simulation() | 二項分布を積分し、45/447件を乱数試行と照合。 |
| Appendix G / Table A4 | token_bill() | 定型入力と履歴増加を用いる。出力費用・実圧縮ログは省略。 |
| Table 1 / §4.5 | lab.yaml / results.jsonのpaper | 対応差と探索した効果の著者報告。元試行表の再解析ではない。 |

公式コード：[著者がPDFで案内した公開先](https://github.com/YangzeLiu/what-does-a-harness-buy)。公開commit `3f0c13208c8b71eefcf7b764e2372ac7200c3117` の `analysis/paper_numbers.py`（exact_power / mde_pp_exact）と `reference_outputs/numbers.json` を読み、入力不一致率を照合した。公式スクリプト全体は実行していない。

公式の `data/trials.csv` は元試行表、`analysis/main_table.py` は有効試行の選択、`analysis/tab_a4_budget.py` はtoken分解に対応する。これらの課題別再集計は未実施。
