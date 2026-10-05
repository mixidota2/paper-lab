# 原論文とLabの対応

一次資料：[When, Not How Much, arXiv:2609.39386v1](https://arxiv.org/pdf/2609.39386v1)、2026-09-30。供給PDFをpdftotextで抽出し、本文・付録を確認した。

| 原典の場所 | 論点 | Labの実装・表示 | 省略・変更 |
| --- | --- | --- | --- |
| §1 pp.1–2、Figure 1 p.2 | 平均の因数分解、中央値が0になる条件 | run.py quantiles()、確率分布slider | 真の人工分布を使用。TSFM予測ではない |
| §3.1、Table 2 pp.4–5 | 64時点、混合ラベル窓 | experiment()、horizon=64 | 履歴364/336時点や実データを使用しない |
| §3.3、Appendix B.1 pp.16–17 | 閾値AP、同点を条件にしたAP₀ | metric()、validate() | AUCは未実装。AP₀を発生率で代用しない |
| Appendix B.3 p.17 | 窓のプーリングによる偽の順位能力 | validate()のskill=1/15照合 | 窓単位の評価を維持 |
| Tables 3–4 pp.6–7 | 点予測とprobeの比較 | README Evidence | 著者報告の丸め値。独立再現ではない |
| Tables 14–18 pp.20–24 | データ別の絶対AP skill | results.json reported、dataset dot plot | Chronos-2を代表例として固定。他の最高モデルに切り替えない |
| Appendix F.1–F.2 pp.33–36、Table 27 | 近ゼロと厳密な0の区別、9分位点平均 | quantiles()、README Evidence | 人工分布では厳密な0。原論文では厳密な全0予測は観測されていない |
| Appendix C.3 p.19 | 64出力の線形probe | experiment()のロジスティックhead | 1変数xの発生分類に縮約。凍結表現・64出力学習・正則化選択は省略 |
| Appendix A.2、E.1、E.4 | 欠測、集計単位、感度分析 | README Evidence | 実データの再集計なし |

公式コード：供給PDF中では本研究全体のコード公開先を確認できなかった。Table 11のAmazon / Salesforce / Google / Datadog等のcheckpointは比較対象のモデルであり、本Labのコードや本研究の公式実装ではない。外部リポジトリを推測して補わない。

図の生成元はpaper_lab/sparse05.py。数値はresults.json、文章はREADMEとlab.yaml、再実行はrun.pyから行う。HTMLの直接編集は不要。
