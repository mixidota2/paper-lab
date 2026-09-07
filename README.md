# Interactive Research Library

一次資料を読み、仕組み・根拠・限界を日本語で説明する11件のLabです。モデル・数式と論文に合った図を中心に、必要な箇所には条件を動かす合成実験を添えます。

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

`sections.method` は「モデル / 手法」の本文で、各Labの `method.md` を読み込みます。`teaching_figures` は図の計画とデータです。共通項目は `id`、`kind`、`title`、`caption`、`source`、`locator`（節・式・表）、`rationale`（その図を選ぶ理由）、`after`（挿入先の節）。以下から必要な種類を選びます。

| kind | 用途 | データ |
| --- | --- | --- |
| architecture | モデルの分岐と共有部分 | rows → label, nodes → title, text |
| equations | 数式を項別に説明 | steps → name, formula, explanation |
| matrix | attention mask・実験設計・比較表 | columns, rows → label, cells |
| logic | 主張・情報境界・方式の選択肢 | rows → label, nodes → title, text |
| timeline | 時間帯を分けた処理 | rows → label, nodes → title, text |
| chart | 一次資料の報告値 | unit, maximum, bars → label, value |

図と数式はHTMLで生成し、JSや数式CDNがなくても読めます。数式はUnicodeの添字・演算子と説明を使い、狭い画面では折り返します。行列だけは必要に応じて図の内部を横スクロールします。チャートは0起点の共通尺度と正確な数値を併記します。

`interactives` は任意の配列です。既存の `flow` と `explorer` を必要な個数・順序で選べます。今回の11件では処理図の一律使用をやめ、4件だけに `explorer` を残しています。`explorer` は `title` と `caption` を持ち、`results.json` の計算済み全条件を表示します。JavaScriptは計算式を再実装せず、棒・系列・注記を更新します。キーボードで操作でき、JavaScript無効時にも初期値が残ります。

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
