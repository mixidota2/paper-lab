# EpiSEM：欠けた証拠を回収し、両世界で判断する

EpiSEM-Bench（arXiv 2610.31650v1、2026-10-22、告知10月23日）の評価設計を読むための自作Lab。Worth Readingは評価設計への判断であり、モデル順位や本番安全への推薦ではない。

2つの自作task、5つのscripted policy、critical/irrelevant mask、SE/RE、回収順序を切り替える。通常再読、独立audit、commit終端を追い、UCR・SBM・PURの分母を確かめる。実LLM、著者300 task、実際の支払い・送信・APIは動かさない。

## 再実行

```bash
uv sync --locked --extra dev --python 3.12
uv run --locked python papers/episem-missing-evidence-recovery/run.py
uv run --locked pytest -q -ra --fail-on-skip
uv run --locked paper-lab build --out /tmp/episem-new-full-site
uv run --locked python tests/review_103.py --preflight \
  --site /tmp/episem-new-full-site --out /tmp/episem-new-preflight
```

全papers/を入力し、毎回新しい出力先を使う。限定ビルドで公開サイトを上書きしない。run.pyは標準ライブラリだけでresults.jsonを再生成する。model.jsとinteractive.jsは既存ビルドで配布される。

実ブラウザー検査は既存の保護付きmacOS CIで行う。360/768/1440pxの操作、ステップ送り、reset、JavaScript無効時の説明を対象にする。ローカルのmock・Node検証を実ブラウザーの証拠とは扱わない。署名、loopback CDP、Seatbelt、ProtectionStopを維持し、Linux保護失敗の経路を再試行しない。

## 確認範囲

- CONFIRMED：自作toyの決定的な数値、通常再読による欠落の持続、audit回収、終端、指標集計をローカルテストで検証済み。実ブラウザー検査は別の必須ゲートとする。
- PARTIAL：EpiSEMの評価設計を小さな例で表現。2 taskのbool規則、完全audit、固定全mask列挙に簡略化。
- NOT OBSERVED：著者の公開コードリンクと実験記録の配布。
- NOT TESTED：実モデル、物理的な実行、認証・回収源の障害、本番安全、信頼区間、反復安定性。

原典の§3、式(1)(2)、Appendix B/EをHTMLとPDFで照合。出典と省略はmapping.mdに記載する。TRACEは判定器への感度、本Labは観測証拠と世界状態の分離を扱う。
