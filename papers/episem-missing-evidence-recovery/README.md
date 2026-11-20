# EpiSEM：必要な事実を確かめ、実行するかを判断する

EpiSEM-Bench（arXiv 2610.31650v1、2026年10月22日、告知10月23日）は、ツールから返った情報が正しくても、判断に必要な事実が欠ける場合を扱います。同じ依頼について、許可される世界と禁止される世界の両方で、情報を確かめてから適切に行動できるかを測ります。このLabは評価方法を「読む価値あり」と判断しています。モデルの順位を推奨したり、本番での安全を保証したりするものではありません。

教材では自作の2タスクと、あらかじめ決めた5種類の判断規則を使います。隠す事実の組み合わせ（mask）は、安全規則に関わる事実（critical）と、可否にも実行時の入力値にも関わらない事実（irrelevant）で別々に選べます。SEでは通常の読み直しだけが可能です。REでは別の照会手段（audit）も使え、照会の順番を変えられます。処理が終わるまでの経過をたどり、UCR・SBM・PURがそれぞれ何を分母にするか確かめます。実際の言語モデル、著者の300タスク、実際の支払いや送信、外部APIは使いません。

## 再実行

```bash
uv sync --locked --extra dev --python 3.12
uv run --locked python papers/episem-missing-evidence-recovery/run.py
uv run --locked pytest -q -ra --fail-on-skip
uv run --locked paper-lab build --out /tmp/episem-new-full-site
uv run --locked python tests/review_103.py --preflight \
  --site /tmp/episem-new-full-site --out /tmp/episem-new-preflight
```

全論文が入った `papers/` を入力にし、毎回新しい出力先を指定してください。一部の論文だけで公開サイトを上書きしないでください。run.py はPythonの標準ライブラリだけを使って results.json を作り直します。model.js と interactive.js は既存のビルドで配布されます。

実ブラウザーの検査は、保護を有効にした既存のmacOS CIで行います。画面幅360/768/1440pxでの操作、ステップ送り、初期設定へのリセット、JavaScript無効時の説明を確かめます。ローカルのモックやNode.jsでの検査は、実ブラウザーで動いた証拠にはなりません。署名、ループバック接続でのCDP、Seatbelt、ProtectionStopは維持し、Linuxで保護に失敗した経路は再試行しません。

## 確認範囲

- CONFIRMED：自作toyの決定的な数値、通常再読によって欠落が戻らないこと、auditによる回収、終端、指標集計をローカルテストで検証済み。実ブラウザー検査は別途必須とする。
- PARTIAL：EpiSEMの評価設計を小さな例で表現。2 taskのbool規則、全欠落を正しい値で返す完全audit、全maskを固定して列挙する方法に簡略化。
- NOT OBSERVED：著者の公開コードリンクと実験記録の配布。
- NOT TESTED：実モデル、物理的な実行、認証・回収源の障害、本番安全、信頼区間、反復安定性。

本文§3、式(1)(2)、付録B・EはHTML版とPDF版を照合しています。出典と教材で省いた条件は mapping.md にあります。TRACEが判定に使う仕組みによって評価がどう変わるかを扱うのに対し、このLabでは実際の状態を変えず、見える情報だけを変えた評価を扱います。
