# 論文の仕組みと根拠を読む Lab（Interactive Research Library）

このリポジトリでは、個別の論文を読み解く121件のLabと、3件のテーマガイドを管理します。Labでは一次資料をもとに、モデルが何を受け取り、どう処理するかを数式や図で説明します。各Labには確認できた範囲を記し、条件による違いを理解するのに役立つ場合は、人工データを使った小実験を添えます。テーマガイドでは業務上の問いに沿って複数の研究を比べます。

公開先：https://mixidota2.github.io/paper-lab/

## 論文一覧とテーマガイド

個別の論文を探すときは[Labの一覧](https://mixidota2.github.io/paper-lab/)を、業務上のテーマから探すときは[テーマガイドの一覧](https://mixidota2.github.io/paper-lab/guides/)を開きます。生成したサイトではガイドを121件のLabと別に数え、ガイドの追加日と論文の発表・公開時期も区別して表示します。

| テーマ | ガイドで読めること | 生成に必要な原稿とLab |
| --- | --- | --- |
| 棚割り | カテゴリへの棚幅配分、置く商品、棚内と店内での置き方を分けて考えます。 | 原稿 `guides/shelf-decisions.md` と、棚幅配分・品揃えと棚在庫・棚内配置の3件のLab |
| 需要予測と補充 | 企業での事例、理論上保証されること、小さく試すための提案を分けて比べます。 | 棚割りガイドの生成条件に加え、共通閾値・ORPR・予測精度と在庫指標のLab、原稿と事例カードが必要です。 |
| 棚本数を固定した店舗レイアウト | カテゴリーごとの棚本数を固定した上で、棚をどの位置に置くか、同じカテゴリーの棚を連続して置くか、配置の組み合わせによって何が変わるかを比べます。棚を5・4・3本に分けた図は模式図です。別の合成例では12か所への配置27,720通りを調べ、同じカテゴリの棚がすべてつながり、通路をまたがない配置が16通りあることを確かめました。 | 原稿 `guides/store-layout-fixed-counts.md`、棚割りガイドの生成条件、Whole FoodsのLab |

全件をビルドすると、Labとガイドを生成します。一部のLabだけをビルドする場合、ガイドが参照するLabがそろわなければ、そのガイドは生成しません。一部だけをビルドするときは、本番サイトとは別の場所に出力してください。

## 手元でのサイト生成

手元でビルドするにはPython 3.10以上とuvが必要です。下の手順では検証にPython 3.12を使います。論文の解説や図を変更するには、`papers/<id>/lab.yaml` と、そのファイルが参照する資料を編集します。実験の計算結果は `results.json` に保存します。`site/` はビルドの出力先なので直接編集しません。

```bash
uv sync --locked --extra dev --python 3.12
uv run --locked pytest -q -ra --fail-on-skip
uv run paper-lab build
uv run python -m http.server --directory site 8000
```

サーバーが起動したら http://localhost:8000 を開きます。生成したHTMLを直接開いた場合も図を操作できます。図、フォント、スクリプトは外部の配信サービスやAPIを使いません。ただし、リンク先の原論文を開くにはネット接続が必要です。

## 検査の対象と限界

### 自動検査と公開

自動テストでは全121件のLabの読み込みに加え、同じ入力から同じファイルができること、配布ファイルが原本と一致すること、内部リンクが開くことを確かめます。SIM2REALのテストでは、在庫の収支が合うことと、未来の情報を参照しないことを確かめます。APのテストの確認対象は、有限個の候補をすべて列挙した結果です。検証用のNumPyはバージョンを固定しており、APの検査でSciPyの学習処理は実行しません。必要な依存が欠けたり、テストがスキップされたりすると、必須のpytestは不合格になります。

プルリクエストでは、GitHub Actionsがpytestに加えて全サイトのビルドと静的preflightを実行します。preflightはブラウザーを起動せずに行う事前検査です。生成したHTMLの操作も検査し、店舗レイアウトの表示と操作は保護を有効にしたmacOS Chromeでも確かめます。メインブランチを更新すると、GitHub Actionsがサイトを作り直してGitHub Pagesに公開します。その後、検査した生成物と公開ファイルが一致するかを別の手順で確かめます。公開後の手順には補充ガイドを保護付きChromeで検査する工程もあります。

全Labの `run.py` の実行と、著者のモデルの再学習は、必須の検査に含めません。追加で実験を試す場合は、必要な依存と計算量を確かめた上で、実行するものを選びます。

### 手元での画面確認

PlaywrightとChromeが使える環境なら、次のコマンドで生成したサイトを実ブラウザーでも確認できます。公開サイト自体にはPlaywrightを同梱しません。

```bash
uv run --with playwright tests/browser.py
# 必要に応じて CHROME_PATH にChrome実行ファイルを指定します。
```

このテストは画面幅360・768・1440pxで、Labの図、スライダーのキー操作と表示値、検索と絞り込みを確認し、ページが横にはみ出していないかを検査します。一部のLabではJavaScriptを無効にしたときの表示も確認します。

ブラウザーを起動せずに準備を確認するコマンドは `uv run --locked --extra dev pytest -q tests/test_review_103_preparation.py` です。このテストでは、忘却教材で小数を3桁表示する処理を実際のJavaScriptと照合し、ガイドから共通のLabに進めることを確かめます。一方、保護付きmacOSブラウザーで使う `tests/review_103.py` は、画面幅360pxと1440pxでガイドの一覧、本文、3件のLabの間を移動し、原寸の画像を保存します。

準備検査や自動テストに合格しても、実際の画面を開いたり操作したりしたことにはなりません。手元で保護を有効にしたChromeを起動できない場合は、画面・操作・読み上げを「未検証（NOT TESTED）」と記録します。手元での実ブラウザー確認は任意です。Chromeを起動できない場合でも、保護設定を変更して回避しません。

### 論文と小実験の区別

各Labで実験を始めるときに使うのは `run.py` です。`papers/_toy_common.py` にある11件の独立した小実験は、勝敗を固定した表を示すのではなく、人工データ、仮定した費用、単純化したルールから結果を計算します。原論文のモデルは学習せず、本番性能も再現しません。仕組みは一部を検証（Mechanism: PARTIAL）しています。性能、規模を広げた場合の挙動、本番適用性は未検証（Performance / Scaling / Production applicability: NOT TESTED）です。「確認済み（CONFIRMED）」と記すのは、実際に計算して確かめた限られた命題だけです。

2026-09-07の改修では、Amazon Scienceが公開するWhole Foods論文を全4ページ確認しました。論文には因果効果を検証した詳しい結果がなく、図でも売上の実額を公開せず、正規化した値を示しています。そのため、結果を独立に再現できたとは言えず、実店舗の売上が増えたかも確認できていません。

## Labの解説・図・実験の編集

### 著者の主張とLabの解釈

`lab.yaml` の `question` に日本語で問いを書き、`source_review` に確認日、一次資料のURL、確認した範囲を記録します。`core_idea.author_claim` には著者の主張、`core_idea.research_bot_interpretation` にはLabでの解釈を書きます。「モデル / 手法」の節に本文を表示するには、`sections.method` で各Labの `method.md` を指定します。

### 図の種類と設定

図の種類と内容は `teaching_figures` に記入します。どの図にも共通する項目は、識別子 `id`、種類 `kind`、題名 `title`、説明 `caption`、出典 `source`、出典の節・式・表を示す `locator`、図を選んだ理由 `rationale`、図を入れる節 `after` です。

| `kind` | 図が示すこと | 記入する項目 |
| --- | --- | --- |
| `architecture` | モデルが処理を分ける箇所と、同じ処理を使う箇所 | `rows` の `label`、`nodes` の `title` と `text` |
| `equations` | 一つの式を項に分けたときの、各項の役割 | `steps` の `name`、`formula`、`explanation` |
| `matrix` | 注意機構が参照できる範囲（attention mask）、実験の設計、表での比較 | `columns`、`rows` の `label` と `cells` |
| `logic` | 主張の内容、情報を参照できる範囲、選べる方式 | `rows` の `label`、`nodes` の `title` と `text` |
| `timeline` | 時間帯ごとに行う処理 | `rows` の `label`、`nodes` の `title` と `text` |
| `chart` | 一次資料が示す数値 | `unit`、`maximum`、`bars` の `label` と `value` |

ビルド時に図と式をHTMLに書き出すため、JavaScriptなしでも図と式を読めます。数式はUnicodeの添字や演算子に文章を組み合わせ、狭い画面では折り返します。棚割りの3件の数式図ではブラウザー標準のMathML（`formula_mathml`）を使い、添字、指数、分数を組版します。読み上げ用の文字式 `formula` も残します。長い数式や行列は、必要に応じて図の中だけを横にスクロールできます。グラフには0から始まる目盛りを使い、比較する値を同じ尺度にそろえた上で、正確な値を添えます。

各Labの `figures/` にSVGなどを置く場合は、`figures` の `path`、`title`、`caption` で図を指定します。任意の項目 `after` を `after: method` にすると、サイトは図を手法の節のすぐ後ろに表示します。挿入先を指定しなければ、ページの末尾に参考図としてまとめます。SVGに説明文と `viewBox` を付けると、拡大リンクも表示されます。文字の多い図に `layout: scroll` を指定すると、図の最低限の幅を保ち、スマートフォンでも図の中だけを横にスクロールできます。

### 条件を変えて比べる図

`interactives` の設定は任意です。処理の流れを示す `flow` と、条件別の結果を比べる `explorer` を、必要な数だけ読ませたい順に指定します。`explorer` を使うのは、条件を見比べて初めて分かることがある場合だけです。図には `title` と `caption` を付け、`results.json` にある計算済みの全条件を表示します。JavaScriptは棒・系列・注記の表示を切り替えるだけで、計算式を別に実装しません。図はキーボードで操作でき、JavaScriptを無効にしても初期条件の値は読めます。

### 日本語の点検

Labの日本語を書くときも、編集するときも、内容を説明するときも、毎回yomiyasuを使います。Explain Before Shortenに従い、誰が何をするか、何を比べるか、その結果がどの条件で成り立ち、どこまで確かめたかを先に説明します。短くするときも、数値・式・出典・比較対象・未検証の範囲は省きません。

本文、図の説明、実験の注記を抜き出して点検します。注記の違いが数値だけなら、同じ文型として1回点検します。下のコマンドは補助の表記チェックです。yomiyasuによる確認の代わりにはなりません。

```bash
uv run skills/natural-japanese/scripts/lint.py --genre tech --json /tmp/lab-prose.md
```

## 2026年9月の追加記録

ここでは各日に追加したLabと、その時点で確認できた範囲を記録しています。現在の全件を確認するときは、公開サイトの一覧を開いてください。

### 2026-09-08〜09

- 2026-09-08: `glide-spotify-sid`、`understanding-sids-isd`、`execution-state-unlearning` を追加しました。3件は候補を取得する経路ごとの比率と増分、意味ID（SID）の枝刈りと順位の統合、実行状態を再構成する方法をそれぞれ扱います。各 `run.py` は単体で実行でき、同じフォルダーに `results.json` を書き出します。
- 2026-09-09: 6件を追加しました。OTTOで損失に付ける重み、Multi-Harness RLの比較群、AutoLRがKEEPと判定する条件、SID-OPEが推定を分ける単位、Walmartでの需要転移、Harness-R1が実行中に処理を差し込む箇所を扱います。それぞれの `run.py` は単体で実行できます。確認した一次PDFの版とSHA-256は各 `lab.yaml` に記録しました。非公開の本番性能は再現したと扱いません。

### 2026-09-15〜16

- 2026-09-15: OxygenREC-v2 / IDGR、RecEvolve、QuaSIDの3件を追加しました。3件は順に、行動の指示と蒸留の損失、スコアを固定したときに候補集合を監査する方法、CVPMと幾何学的なマージンを扱います。各 `papers/<slug>/` にREADME、`lab.yaml`、`method.md`、`mapping.md`、`run.py`、`results.json` を置き、図も同じLabのディレクトリで管理します。産業用モデルの学習とオンライン性能は未検証です。
- 2026-09-16: UniVA / CQ-SID、EG-GRPO、Intervention Paradoxの3件を追加しました。各Labの操作図では、商用のSIDとGARが選ぶ枝、クラスタの展開と専門処理（expert）の追加、介入で利益が出る境目を確認できます。3件の一次PDFを通読し、UniVAのv1とv2ではトラフィック比率が異なること、チャネルの構成比はA/Bテストの改善幅と別の指標であること、介入の論文では数値に不整合があることを記録しました。各 `run.py` は独立して実行できます。

### 2026-09-17

GenPage、UniRec、AgentX、STATIC、FlashTrie、GateSID、CORALの7件を追加しました。この日に追加したLabでは、候補集合がどこまで及ぶか、表示面ごとにどれだけ改善したか、観察データから生産性をどう捉えたか、制約処理のどの部分を計測したか、順位付けにSIDをどう使ったか、費用削減額の分母は何かを区別して説明します。各 `mapping.md` には一次PDFの版とSHA-256、原典の節・表との対応を記録しました。各 `run.py` は標準ライブラリだけで実行できます。

UniRecではベイズ式や、容量制約を満たせず実行できない場合の反例も残しました。FlashTrieでサービスレベル目標（SLO）を変える図は、原論文の表1・6に載る実測点を使います。Labでレイテンシーを新たに計測したわけではありません。仕組みの一部は確認しましたが、本番性能、規模を広げた場合の挙動、本番適用性は未検証です。

### 2026-09-18

OGR、DREAM、PILOTの3件を追加しました。各 `mapping.md` に一次PDFの版、SHA-256、原典の節との対応を記録しています。各 `run.py` は標準ライブラリだけで独立して実行できます。

- OGR: SIDを統合する方法、処理どうしの依存関係、報酬の調整を扱います。理論上の依存の深さと、実測の処理量は区別します。
- DREAM: 既存の多段処理を制御して一部の判断を上書きする方法を扱い、改善が積み重なったときの効果を区別します。
- PILOT: 実験を始めてから終えるまでの流れと、別の課題で過去の結果を使う仕組みを扱います。比較は無作為に割り付けていない前後比較で、二つの要因を組み合わせた2×2の実験は行っていません。

この3件も仕組みの一部だけを確認しました。本番での性能、規模を広げた場合の挙動、本番適用性は未検証です。

### 2026-09-21：生成型推薦が置き換える処理

生成型推薦に置き換える範囲を比べるLabを6件追加しました。各Labには一次論文の版とハッシュ、実行コード、実行結果、原典との対応表があります。

- 優先（Must）：[LIGE-GR](papers/lige-gr-meta-listwise/README.md)。既存の順位付けモデルに、候補の並び全体の情報、価値、探索を加えます。
- 優先（Must）：[Sona](papers/sona-yandex-music/README.md)。8,000件の履歴と知識蒸留を使って多段処理を置き換えます。
- 読む価値あり（Worth）：[Wolt UVR](papers/uvr-wolt-trial-reorder/README.md)。Transformerが確率に変換する前の値（logit）とCatBoostで、初回注文と再注文を調整します。
- 注目（Radar）：[PushDualGen](papers/pushdualgen-kuaishou/README.md)。先にSIDを生成し、通知文が必要なときは後から生成します。
- 注目（Radar）：[SnapLGR](papers/snaplgr-snapchat/README.md)。Qwen3-0.6Bを使って複数のリクエストをまとめて処理します。
- 注目（Radar）：[SIDScope](papers/sidscope-diagnostics/README.md)。SIDの対応表と生成経路の記録を診断します。Labでは公式のクイックスタートも実行しました。

この6件を追加で検査するには、`uv run pytest tests/test_september21_labs.py` と `uv run --with playwright tests/browser_september21.py` を実行します。ブラウザー検査は `/opt/google/chrome/chrome` を使います。本番での性能と規模を広げた場合の挙動は未検証です。

### 2026-09-22：検索の価値、注文の完納、修正前の診断

[VARG](https://mixidota2.github.io/paper-lab/papers/varg-tmall-value-generative-retrieval.html) では、初回に商品IDを作るとき、先頭2つの符号が同じ商品どうしを、購入につながる見込みの推定値で並べ、その順位を3つ目の符号に使います。全商品を一列に並べた順位ではありません。生成モデルが選んだ候補は、専用の枠を使って粗い順位付けを省き、既存の最終順位付けへ進みます。[Accuracy Is Not Service](https://mixidota2.github.io/paper-lab/papers/accuracy-not-service-intermittent-demand.html) は予測精度による順位と、注文をすべてそろえて出せた割合による順位を扱います。[AURA](https://mixidota2.github.io/paper-lab/papers/aura-disney-agentic-rec-diagnosis.html) は原因を診断し、修正を保留する判断を扱います。各 `mapping.md` にPDFの版とハッシュ、Labで実行した範囲を記録しています。

注目枠の図では、[GRACE](https://mixidota2.github.io/paper-lab/papers/grace-meta-ads-gtm-serving.html) のマスクがリクエストごとに候補をどう制限するか、[ICEGR](https://mixidota2.github.io/paper-lab/papers/icegr-baidu-intent-generative-retrieval.html) が使うマージンの係数、[EvoPilot](https://mixidota2.github.io/paper-lab/papers/evopilot-verify-dont-trust-autoresearch.html) で評価器の不具合がどう推移したか、[SIDInspector](https://mixidota2.github.io/paper-lab/papers/sidinspector-mapping-diagnostics.html) がIDの対応表をどう診断するかを確認できます。画面幅を変えてこの日の7件の表示を確認するには、`uv run --with playwright tests/browser_september22.py` を実行します。

### 2026-09-23：測定・統合・配信

この日は優先の3件を先に公開し、注目の4件を追加しました。参照した一次資料と検証記録は [BATCH-2026-09-23.md](BATCH-2026-09-23.md) にまとめています。

- [Netflix：反実仮想の測定](https://mixidota2.github.io/paper-lab/papers/netflix-counterfactual-observability.html)
- [UNIQUE：候補検索の処理内で表現を共有](https://mixidota2.github.io/paper-lab/papers/unique-baidu-unified-retrieval-ranking.html)
- [FlashVector：システム全体の性能から採用を判断](https://mixidota2.github.io/paper-lab/papers/flashvector-unity-serving-stack-agent.html)
- [YouTube Music](https://mixidota2.github.io/paper-lab/papers/youtube-music-llm-rationales-discovery.html)
- [MuSeR](https://mixidota2.github.io/paper-lab/papers/muser-baidu-long-sequence-multi-interest.html)
- [HGenPush](https://mixidota2.github.io/paper-lab/papers/hgenpush-kuaishou-heterogeneous-push-gr.html)
- [t0：外部の説明変数を使う時系列基盤モデル](https://mixidota2.github.io/paper-lab/papers/t0-tsfm-forecasting-with-context.html)
