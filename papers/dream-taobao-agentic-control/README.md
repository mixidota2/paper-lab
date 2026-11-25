# DREAM Technical Report

TaobaoのDREAMは、利用者がいま何を探しているかを推定し、既存の推薦システムの設定に反映します。長く続く好み、その時に探している商品、価格やブランドなどの細かな条件を分けて扱う設計です。その情報を、推薦の各段階で使える設定に変えます。一部の設定を変える方式なので、従来の設定に戻せます。

著者がTaobaoのホーム画面で行ったA/Bテストでは、最終段階の並べ替えだけを調整した構成で、商品詳細ページへの訪問数が従来方式より2.06%増えました。その手前の詳しい順位付けも調整した構成では、同じ従来方式より2.71%増えています。二つの数値は足し合わせられません。また、人とエージェントに同じ条件で改善案を探させた比較ではありません。

## 読み方

DREAM：今のintentに合わせて、既存推薦器の設定を動かす。まず問題設定と手法を読み、図で操作の単位を追う。Evidenceでは比較の分母と観察範囲を確認し、小実験と原論文の性能を分けて評価する。

著者は、知覚・strategyの編成・監査を可能にするpolicy層を既存cascadeへ重ね、モデルの置換なしにユーザー価値とbusiness指標を改善できると主張する。

【Labの解釈】学ぶべき境界は、LLMが意図と意味的なactionを提案し、決定的なTool Processが実行可能な設定へ変換する点にある。モデルを変えずに制御可能性を増やせるが、変更可能なmenuが狭ければ効果もその範囲に限られる。

## 再実行

```bash
uv run papers/dream-taobao-agentic-control/run.py
uv run paper-lab build
```

lab.yaml、method.md、mapping.md、run.py、results.jsonが原本。site/は生成物であり直接編集しない。実験は標準ライブラリのみ。

## 検証範囲

**Mechanism: PARTIAL**。人工条件の計算と境界条件を確認した。results.jsonのCONFIRMEDは小さな計算命題にだけ適用する。原論文の学習済みモデルや産業環境を再現した意味ではない。

GRU・Intent Agent・Qwen3の学習、LLMのstrategy品質、TTL最適化、memory更新、実service replay、端末費用、online liftは検証していない。toyで失敗時にdefaultへ戻す処理はschemaの小部分だけを対象としており、本番の安全性を保証しない。

Performance / Scaling / Production applicability: NOT TESTED。モデル学習とオンラインA/Bは実行していない。

[一次PDF](https://arxiv.org/pdf/2608.09408v3)。版・ハッシュ・節とコードの対応はmapping.md。公式コードは確認範囲で案内を見つけられず、実行していない。
