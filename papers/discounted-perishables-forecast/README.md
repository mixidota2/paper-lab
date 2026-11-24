# 値引き品の販売を、そのまま通常需要に戻してよいか

この教材は値引き品の販売と通常需要を分けて考えるための人工例です。回帰の傾きが1でも、値引きで増えた個数が0になる例を試せます。

三例の結果を見るコマンドは、リポジトリのルートから実行する `uv run --locked python papers/discounted-perishables-forecast/run.py` です。末尾に `--write` を付けると、同じディレクトリの `results.json` を作り直します。計算には、Python標準ライブラリの有理数を使います。画面は `interactive.html`、`model.js`、`interactive.js` を使い、外部への通信はしません。

[原論文](https://arxiv.org/html/2602.04464v1)は食品小売の販売記録を分析しています。この教材は二段階の回帰と反例を確認するもので、原論文の数値や値引きの因果効果は再現していません。
