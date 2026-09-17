# Interactive Research Library

一次資料を読み、仕組み・根拠・限界を日本語で説明する42件のLabです。モデル・数式と論文に合った図を中心に、必要な箇所には条件を動かす合成実験を添えます。

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

`figures` には各Labの `figures/` に置いたSVGなどを指定できます。`path`、`title`、`caption` と任意の `after` を持ち、`after: method` なら手法の節の直後に図を表示します。挿入位置を指定しない参考図は末尾にまとめます。SVGには説明文とviewBoxを付け、拡大リンクも表示します。

`interactives` は任意の配列です。既存の `flow` と `explorer` を必要な個数・順序で選べます。処理図を一律には使わず、条件の比較が理解を助けるLabにだけ `explorer` を置きます。`explorer` は `title` と `caption` を持ち、`results.json` の計算済み全条件を表示します。JavaScriptは計算式を再実装せず、棒・系列・注記を更新します。キーボードで操作でき、JavaScript無効時にも初期値が残ります。

`run.py` は各Labの入口、`papers/_toy_common.py` は11個の独立した小実験です。固定の勝敗表は使いません。ただし人工データ・仮定した費用・簡略な規則による説明であり、原論文のモデルを訓練したり性能を再現したりする実験ではありません。検証範囲は全LabでMechanism PARTIAL、Performance / Scaling / Production applicability NOT TESTEDです。

2026-09-08追加分の `glide-spotify-sid`、`understanding-sids-isd`、`execution-state-unlearning` は、それぞれの `run.py` 単体で動きます。候補経路の比率と増分、SIDの枝刈りと順位融合、実行状態の再構成を扱います。結果はコードと同じフォルダーの `results.json` へ書き出します。

2026-09-09追加分の6本も `run.py` 単体で動きます。OTTOの損失重み、Multi-Harness RLの比較群、AutoLRのKEEP、SID-OPEの粒度、Walmartの需要転移、Harness-R1の実行hookを扱います。一次PDFの版とSHA-256を各 `lab.yaml` に記録し、非公開の本番性能は再現したと扱いません。

## ブラウザーと日本語の確認

PlaywrightとChromeがある環境では、生成後に実ブラウザーの確認を実行できます。Playwrightは配信するサイトには含めません。

```bash
uv run --with playwright tests/browser.py
# 必要に応じて CHROME_PATH にChrome実行ファイルを指定します。
```

360・768・1440pxで全Labの図、スライダーのキー操作、表示値、検索・絞込み、ページ幅を確認し、JavaScript無効の表示も検査します。

日本語は指定スキルで推敲します。本文、図の説明、実験注記をテキストへ抽出し、数値だけが違う注記は同じ文型として1回ずつ検査します。

```bash
uv run skills/natural-japanese/scripts/lint.py --genre tech --json /tmp/lab-prose.md
```

## 公開と資料の限界

`origin/main` へのpushでGitHub Actionsが再生成し、GitHub Pagesへ公開します。2026-09-07の改修では、Amazon Scienceが公開するWhole Foods論文の全4ページPDFを確認できました。因果効果の詳細な実証結果は本文で省略され、図の売上値も非公開・正規化されているため、独立再現や実店舗での増収確認はできていません。

## 2026-09-15追加分

OxygenREC-v2 / IDGR、RecEvolve、QuaSIDの3件を追加。各 `papers/<slug>/` にREADME・lab.yaml・method.md・mapping.md・run.py・results.jsonを置き、図も同じディレクトリで管理する。行動指示と蒸留損失、固定scoreの候補集合監査、CVPMと幾何マージンをそれぞれ検証する。産業モデルの学習とオンライン性能はNOT TESTED。


2026-09-16：UniVA / CQ-SID・EG-GRPO / Intervention Paradoxを追加。商用SIDとGARの枝選び、クラスタ展開とexpert注入、介入の損益分岐点を、それぞれ異なる操作図で確認する。3本とも一次PDFを通読し、UniVAのv1/v2トラフィック比率の違い、チャネル構成比とA/B liftの区別、介入論文内の数値不整合を明記した。各run.pyは独立実行できる。


## 2026-09-17追加分

GenPage、UniRec、AgentX、STATIC、FlashTrie、GateSID、CORALの7本を追加。一次PDFの版・SHA-256・節と表の対応を各mapping.mdへ記録した。候補集合の境界、面別の改善率、観察的な生産性比較、制約処理の計測範囲、rankingでのSID利用、費用削減額の分母を分けて説明する。

各run.pyは標準ライブラリだけで動く。人工実験のCONFIRMEDは限定した計算命題に適用し、MechanismはPARTIAL、本番性能・スケーリング・本番適用性はNOT TESTED。UniRecのBayes式と実行不能なcapacity条件には反例も残した。FlashTrieのSLO操作は表1・6の実測点を使い、新しい遅延測定とは扱わない。
