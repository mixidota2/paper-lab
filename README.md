# Personal Research Library

arXiv の原論文を起点にした、個人用の静的研究ライブラリです。公開ページは日本語で表示し、論文に書かれたことと読書メモを明確に分けます。

対象は三本だけです。

`papers/<id>/lab.yaml` が唯一のコンテンツソースです。`site/` は毎回作り直す生成物なので、直接編集しません。

## ビルドと確認

Python 3.10 以上と [uv](https://docs.astral.sh/uv/) を使います。

```bash
uv sync --extra dev
uv run pytest
uv run paper-lab build
uv run python -m http.server --directory site 8000
```

## 各 Lab の小実験

三つの実験は CPU と標準ライブラリだけを使い、各 paper directory の `results.json` を更新します。論文の再現ではなく、仕組みと比較軸を動かして確かめるための実装です。

```bash
uv run papers/scaffold-effects-gaia/run.py
uv run papers/case-against-generation-retrieval/run.py
uv run papers/unipinrec/run.py
```

最後のコマンドのあと、<http://localhost:8000> を開きます。ビルドは決定的で、古い生成ファイルを残しません。

## 論文を追加・更新する

1. `papers/<url-safe-id>/lab.yaml` を作る。
2. arXiv の abs ページと本文から、題名、全著者、ID、投稿日、本文の要約を確認する。
3. `arxiv_id` と `urls.arxiv` を同じ ID にする。生成前の検証でも不一致を拒否する。
4. 読書メモは `core_idea.research_bot_interpretation` と「なぜ効きそうか」にだけ書き、著者の主張と混ぜない。
5. 実行していない実験の数値や結果は載せない。検証欄は正直に `NOT TESTED` とする。
6. `uv run pytest` と `uv run paper-lab build` を実行する。

## デプロイ

GitHub Pages は `site/` を配信します。ローカルでも同じ `uv run paper-lab build` が通常の生成手順です。
