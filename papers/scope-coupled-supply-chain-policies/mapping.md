# 原論文・公式コード対応

[一次資料PDF](https://arxiv.org/pdf/2607.28488)。確認箇所：Figures 1–2; §3.1–3.3; Eqs. (1)–(6); Tables 1–2。保存済みPDFのSHA-256：`0e0ea2b7b37d2a34c9aa11be36332ac0df193508e4e6044475e9d26ea060c5a9`。

## 紙面と最小実験の対応

utility() → 式(1)–(2)の荷量と費用の簡略版。experiment()の全探索 → 式(3)–(4)の完了価値の教育例。ニューラル方策の再実装ではない。

Performance / Scaling / Production applicabilityはNOT TESTED。学習、複数供給元、実際の道路距離、在庫動態、実店舗での品揃え変更は試していない。U_refの代理係数が現場の利益や欠品費用を正しく表すかも未検証。

## 公式コードの確認範囲

確認したPDF内で本手法の公式実装URLを特定できなかった。公開実装が存在しないとの断定はしない。公式コードの実行はNOT TESTED。

## 原本と生成物

lab.yamlは本文と図の定義、method.mdは手法説明、run.pyは人工実験、results.jsonは実行結果、mapping.mdは対応表。HTMLはこれらから生成する。PDFの報告値と人工実験値は別に表示する。
