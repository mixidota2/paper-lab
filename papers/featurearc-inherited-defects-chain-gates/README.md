# FeatureArc：以前の欠陥と最後の合否を分ける

Worth Reading。受入検査の設計を読むための自作教材。モデル順位の推奨ではない。

## 再実行

リポジトリrootで、既存の固定依存を利用する。

```bash
uv sync --locked --extra dev --python 3.12
uv run --locked python papers/featurearc-inherited-defects-chain-gates/run.py
uv run --locked pytest -q -ra --fail-on-skip tests/test_featurearc.py
uv run --locked pytest -q -ra --fail-on-skip
uv run --locked paper-lab build
uv run --locked python tests/review_103.py --preflight --site site --out /tmp/featurearc-preflight
```

`run.py`は実際の関数の戻り値を固定した期待値と比較し、10条件×3段階と最終検査、分子・分母を生成する。`render.py`は初期状態をHTMLに残し、`interactive.js`は同じJSONの記録を閲覧する。JSで別の性能モデルを計算しない。run.pyからの生成はresults.jsonとexperiment.mdの2ファイル。各条件の記録は書き換えず、前へボタンは閲覧位置だけを戻す。

入力範囲は固定fixtureの有限整数列・非負の上限に限定。ネットワーク、LLM、著者コードを呼ばない。PythonとJSの検証は生成記録と表示の一致であり、実モデルの再現ではない。

## 確認の範囲

- CONFIRMED：実行関数と独立の期待値による境界・空入力・合計、状態継承、回復、集計分母、生成の決定性をローカルテストで確認する。
- PARTIAL：論文の受入検査の区別を小さな例で表す。実repositoryの編集・会話保持・テスト抽出は再現しない。
- NOT OBSERVED：著者の公式code/data配布先は確認できていない。存在しないとの断定ではない。
- NOT TESTED：実LLMの性能、反復seedの信頼性、規模拡大、実務効果、修正方策の因果効果。画面の確認結果は対象commitの保護付きCIと独立レビューで判断し、単体テストと混同しない。

## 出典・権利

Wangほか、FeatureArc、arXiv:2610.37434v1、2026-10-27。https://arxiv.org/html/2610.37434v1

本文・図・コードはこのLab独自の説明と教材。著者の図・全表を転載せず、少数の集計値を出典付きで紹介する。arXiv perpetual non-exclusive licenseの原論文をCC-BYとは表示しない。FeatureLoop（2610.35488）は別論文で、この実験のデータではない。
