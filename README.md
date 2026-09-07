# Interactive Research Library

一次資料を読み、仕組み・根拠・限界を日本語で説明する11件のLabです。各Labには、処理を追う比較図と、条件を動かす合成実験があります。

公開先：https://mixidota2.github.io/paper-lab/

## 生成と検証

Python 3.10以上とuvを使います。コンテンツは `papers/<id>/lab.yaml`、実験値は `results.json` が原本です。`site/` は生成物なので直接編集しません。

```bash
uv sync --extra dev
for lab_run in papers/*/run.py; do uv run "$lab_run"; done
uv run pytest
uv run paper-lab build
uv run python -m http.server --directory site 8000
```

サーバー起動後に http://localhost:8000 を開きます。生成済みHTMLを直接開いても図は動きます。図・フォント・スクリプトに外部CDNやAPIは使っていません。原論文へのリンクを開く際はネットワーク接続が必要です。

## 図の定義

`lab.yaml` の `question` は日本語の研究上の問い、`source_review` は確認日・一次資料URL・確認範囲です。著者の主張は `core_idea.author_claim`、解釈は `core_idea.research_bot_interpretation` に分けます。

`interactives` には次の2種類を順に定義します。

- `flow`：`title`、`caption`、`source`、`stages` を持ちます。各段は `title`、`baseline`、`proposed`、`detail` で定義します。比較切替・段選択・前後移動で処理を追えます。
- `explorer`：`title` と `caption` を持ち、数値は `results.json` の `explorer` から読みます。スライダー、1段ずつの移動、初期条件への復帰、棒の尺度切替、数値表を備えます。

全条件をPythonで計算し、JSONをページ内へ埋め込みます。JavaScriptは数値を再実装せず、選んだ条件の棒・系列・注記を更新します。数値の表と本文はキーボードでも読め、JavaScript無効時には処理の説明と初期値が残ります。静止図は補助資料です。

`run.py` は各Labの入口、`papers/_toy_common.py` は11個の独立した小実験です。固定の勝敗表は使いません。ただし人工データ・仮定した費用・簡略な規則による説明であり、原論文のモデルを訓練したり性能を再現したりする実験ではありません。検証範囲は全LabでMechanism PARTIAL、Performance / Scaling / Production applicability NOT TESTEDです。

## ブラウザーと日本語の確認

PlaywrightとChromeがある環境では、生成後に実ブラウザーの確認を実行できます。Playwrightは配信するサイトには含めません。

```bash
node tests/browser.cjs
# 環境に応じて PLAYWRIGHT_MODULE と CHROME_PATH を指定できます。
```

360・768・1440pxで全Labの図、スライダーのキー操作、表示値、検索・絞込み、ページ幅を確認し、JavaScript無効の表示も検査します。

日本語は指定スキルで推敲します。本文、図の説明、実験注記をテキストへ抽出し、数値だけが違う注記は同じ文型として1回ずつ検査します。

```bash
uv run skills/natural-japanese/scripts/lint.py --genre tech --json /tmp/lab-prose.md
```

## 公開と資料の限界

`origin/main` へのpushでGitHub Actionsが再生成し、GitHub Pagesへ公開します。2026-09-07の改修では、Amazon Scienceが公開するWhole Foods論文の全4ページPDFを確認できました。因果効果の詳細な実証結果は本文で省略され、図の売上値も非公開・正規化されているため、独立再現や実店舗での増収確認はできていません。
