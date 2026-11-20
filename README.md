# 論文の仕組みと根拠を読む Lab（Interactive Research Library）

個別の論文を読み解く114件のLabと、3件のテーマガイドがあります。ガイドでは、業務上の問いから複数の研究を比べます。Labでは、一次資料をもとに、モデルが何を入力し、どう処理するかを数式や図で説明します。どこまで確かめたかも記し、条件を変えたときの違いが理解に役立つ場合は、人工データを使った小実験を添えます。

公開先：https://mixidota2.github.io/paper-lab/

## 読みたい内容から探す

最新の研究とLabの一覧は公開サイトの `index.html`、テーマから探す場合は `guides/index.html` を開きます。ガイドは114件のLabとは別に数えています。ガイドを追加した日と、論文が発表・公開された時期も分けて表示します。

| テーマ | 読めること | 生成に必要なもの |
| --- | --- | --- |
| 棚割り | 棚の本数や配分、置き方を考えるための3件のLabへ進めます。 | 原稿 `guides/shelf-decisions.md` と参照先の3件のLab |
| 需要予測と補充 | 企業の事例、理論上保証されること、小規模な検証の提案を分けて比較します。 | 棚割りガイドの生成条件に加え、共通閾値・ORPR・予測精度と在庫指標のLab、原稿と事例カードが必要です。 |
| 棚本数を固定した店舗レイアウト | カテゴリーごとの本数を固定し、棚をどの位置に割り当てるか、同じカテゴリーを続けて置くか、配置の組み合わせで何が変わるかを比べます。5・4・3本の図は模式図で、人工データを使った最適化実験は行っていません。 | 原稿 `guides/store-layout-fixed-counts.md`、棚割りガイドの生成条件、Whole FoodsのLab |

全件をビルドするとガイドも生成します。一部のLabだけをビルドし、参照先が足りない場合は、対応するガイドを生成しません。限定ビルドの出力先は本番サイトと分けてください。

## 手元でサイトを作る

Python 3.10以上とuvが必要です。下の手順は検証用にPython 3.12を使います。論文の解説や図を直す場合は、`papers/<id>/lab.yaml` とそこから参照する資料を編集します。実験の計算結果は `results.json` に保存します。`site/` は出力先なので直接編集しません。

```bash
uv sync --locked --extra dev --python 3.12
uv run --locked pytest -q -ra --fail-on-skip
uv run paper-lab build
uv run python -m http.server --directory site 8000
```

サーバーの起動後は http://localhost:8000 を開きます。生成したHTMLを直接開いても、操作できる図が動きます。図、フォント、スクリプトは外部の配信サービスやAPIに依存しません。原論文へのリンクを開くにはネット接続が必要です。

## 何を検査し、どこまで確かめたと言えるか

### 自動検査と公開

全114件のLabの読み込み、同じ入力から同じファイルができること、配布ファイルが原本と一致すること、内部リンクが開けることを検査します。SIM2REALでは在庫の収支が合うことと未来の情報を参照しないこと、APでは有限個の候補をすべて列挙した結果を確認します。検証用のNumPyはバージョンを固定しており、APの検査でSciPyの学習処理は実行しません。依存が欠けたりテストをスキップしたりすると、必須のpytestは不合格になります。

プルリクエストの公式検査では、pytestに加えて全サイトのビルドと静的preflight（ブラウザーを起動しない事前検査）を行います。生成したHTMLの操作と、保護を有効にしたmacOS Chromeでの店舗レイアウトの表示・操作も検査します。メインブランチの更新後は、GitHub Actionsがサイトを再生成してGitHub Pagesへ公開し、検証した生成物と公開ファイルが一致するかを別の手順で確かめます。公開後には、補充ガイドを保護付きChromeで検査する手順もあります。

全Labの `run.py` の実行や著者モデルの再学習は、必須の検査に含めません。追加で試す場合は、必要な依存と計算量を確認し、試したい実験を選びます。

### 手元で画面を確認する

生成したサイトを実ブラウザーで追加確認する場合は、PlaywrightとChromeが使える環境で次を実行します。Playwrightを公開サイトに同梱するわけではありません。

```bash
uv run --with playwright tests/browser.py
# 必要に応じて CHROME_PATH にChrome実行ファイルを指定します。
```

360・768・1440pxで、Labの図、スライダーのキー操作と表示値、検索・絞り込み、ページに横はみ出しがないことを確認します。一部のLabはJavaScriptを無効にした状態でも表示を検査します。

ブラウザー起動前に行う `uv run --locked --extra dev pytest -q tests/test_review_103_preparation.py` では、忘却教材で小数を3桁表示する処理を実際のJavaScriptと照合し、ガイドから共通のLabへ進めることを検査します。一方、保護付きmacOSブラウザーで使う `tests/review_103.py` は、360pxと1440pxでガイドの一覧・本文・3件のLabを行き来し、原寸の画像を保存します。

準備検査や自動テストの合格は、実際の画面を開いたり、操作したりしたことを意味しません。手元で保護を有効にしたChromeを起動できない場合は、画面・操作・読み上げを「未検証（NOT TESTED）」と記録します。手元での実ブラウザー確認は任意です。起動できなくても、保護設定を変更して回避しません。

### 論文と小実験の区別

各Labの `run.py` が実験の入口です。`papers/_toy_common.py` には独立した小実験が11件あり、勝敗を固定した表ではなく、人工データ、仮定した費用、単純化したルールから結果を計算します。原論文のモデルを訓練したり、本番の性能を再現したりするものではありません。仕組みは一部を検証（Mechanism: PARTIAL）、性能・規模を拡大したときの挙動・本番適用性は未検証（Performance / Scaling / Production applicability: NOT TESTED）です。「確認済み（CONFIRMED）」は実際に計算で確かめた限定的な命題にだけ使います。

例として、2026-09-07の改修では、Amazon Scienceが公開するWhole Foods論文の全4ページを確認しました。本文には因果効果を検証した詳しい結果がなく、図の売上値も実額を公開せず正規化してあります。このため、結果の独立再現や実店舗の増収は確認できていません。

## Labの解説・図・実験を直す

### 原典とこちらの説明を分けて書く

`lab.yaml` の `question` に日本語の問いを書き、`source_review` に確認日、一次資料URL、どこまで確認したかを記録します。著者が述べたことは `core_idea.author_claim` に、このLabでの解釈は `core_idea.research_bot_interpretation` に分けて書きます。「モデル / 手法」の本文は、`sections.method` が各Labの `method.md` を読み込みます。

### 説明したいことに合った図を選ぶ

`teaching_figures` には図の種類と中身を書きます。共通の項目は、識別子 `id`、種類 `kind`、題名 `title`、説明 `caption`、出典 `source`、出典内の節・式・表 `locator`、この図を選んだ理由 `rationale`、挿入先の節 `after` です。

| `kind` | 何を示すか | 指定するデータ |
| --- | --- | --- |
| `architecture` | モデルのどこで処理が分かれ、どこで同じ処理を使うか | `rows` の `label`、`nodes` の `title` と `text` |
| `equations` | 一つの式をいくつかの項に分け、それぞれの役割を示す | `steps` の `name`、`formula`、`explanation` |
| `matrix` | 注意機構で参照できる範囲（attention mask）、実験設計、比較表 | `columns`、`rows` の `label` と `cells` |
| `logic` | 主張、どこまで情報を参照できるか、方式の選択肢 | `rows` の `label`、`nodes` の `title` と `text` |
| `timeline` | 時間帯ごとの処理 | `rows` の `label`、`nodes` の `title` と `text` |
| `chart` | 一次資料に載っている数値 | `unit`、`maximum`、`bars` の `label` と `value` |

図と式はHTMLに出力するため、JavaScriptなしでも読めます。数式はUnicodeの添字・演算子と文章を組み合わせ、狭い画面では折り返します。棚割りの3件の数式図はブラウザー標準のMathML（`formula_mathml`）で、添字・指数・分数を組版します。読み上げ用の文字式 `formula` を残し、長い数式や行列は必要に応じて図の内部だけを横にスクロールできるようにします。グラフは目盛りを0から始め、比較する値は同じ尺度で示し、正確な数値を添えます。

各Labの `figures/` にSVGなどを置く場合は、`figures` の `path`、`title`、`caption` で指定します。任意の `after` が `after: method` なら手法の節の直後に表示し、挿入先がなければ末尾に参考図としてまとめます。SVGに説明文と `viewBox` を付けると、拡大リンクも表示します。文字が多い図は `layout: scroll` で最低限の幅を保ち、スマートフォンでは図の中だけを横に動かせるようにします。

### 条件を動かす図は、必要なときだけ添える

`interactives` は任意です。処理を示す `flow` と条件を変えて結果を比べる `explorer` を、必要な数だけ、読ませたい順に指定します。条件を見比べて初めて分かることがある場合に `explorer` を使います。`title` と `caption` を付け、`results.json` から計算済みの全条件を表示します。JavaScriptは棒、系列、注記を切り替えるだけで、計算式を別に実装しません。キーボードで操作でき、JavaScriptを無効にしても初期条件の値は読めます。

### 日本語を確認する

Explain Before Shortenに従い、前提、何を比べているか、その結果が成り立つ条件を先に説明します。短くするときも、数値・式・出典・比較対象・未検証の範囲は省きません。本文、図の説明、実験の注記を抜き出して点検し、数値だけが違う注記は同じ文型として1回点検します。

```bash
uv run skills/natural-japanese/scripts/lint.py --genre tech --json /tmp/lab-prose.md
```

## 2026年9月の追加記録

以下は各日に追加した内容と、当時確認できた範囲です。現在の全件一覧は公開サイトを参照してください。

### 2026-09-08〜09

- **2026-09-08:** `glide-spotify-sid`、`understanding-sids-isd`、`execution-state-unlearning` を追加。候補を取得する経路の比率と増分、意味ID（SID）の枝刈りと順位の統合、実行状態の再構成を扱います。それぞれの `run.py` は単体で動き、同じフォルダーに `results.json` を書き出します。
- **2026-09-09:** 6件を追加。OTTOの損失の重み、Multi-Harness RLの比較群、AutoLRのKEEP判定、SID-OPEで推定を分ける粒度、Walmartでの需要転移、Harness-R1が実行中に処理を差し込む箇所を扱います。それぞれの `run.py` は単体で動きます。一次PDFの版とSHA-256は各 `lab.yaml` に記録し、非公開の本番性能は再現したと扱いません。

### 2026-09-15〜16

- **2026-09-15:** OxygenREC-v2 / IDGR、RecEvolve、QuaSIDの3件を追加。行動の指示と蒸留の損失、スコアを固定したときの候補集合の監査、CVPMと幾何学的なマージンをそれぞれ扱います。各 `papers/<slug>/` にREADME、`lab.yaml`、`method.md`、`mapping.md`、`run.py`、`results.json` を置き、図も同じLabのディレクトリで管理します。産業用モデルの学習とオンライン性能は未検証です。
- **2026-09-16:** UniVA / CQ-SID、EG-GRPO、Intervention Paradoxの3件を追加。商用のSIDとGARが選ぶ枝、クラスタの展開と専門処理（expert）の追加、介入で利益が出る境目を、各Labの操作図で確認できます。3件の一次PDFを通読しました。UniVAのv1とv2でトラフィック比率が異なること、チャネルの構成比とA/Bテストの改善幅は別であること、介入の論文では数値に不整合があることを記録しました。各 `run.py` は独立して実行できます。

### 2026-09-17

GenPage、UniRec、AgentX、STATIC、FlashTrie、GateSID、CORALの7件を追加しました。候補集合の境界、表示面ごとの改善率、観察データで見た生産性、制約処理の計測範囲、順位付けでのSID利用、費用削減額の分母を区別して説明します。一次PDFの版とSHA-256、節・表との対応は各 `mapping.md` に記録し、`run.py` は標準ライブラリだけで動きます。

UniRecでは、ベイズ式や容量制約を満たせず実行できない場合の反例も残しました。FlashTrieのサービスレベル目標（SLO）を変える図は原論文の表1・6に載る実測点を使い、レイテンシーを新しく計測したわけではありません。仕組みは一部を確認し、本番での性能、規模を拡大したときの挙動、本番適用性は未検証です。

### 2026-09-18

OGR、DREAM、PILOTの3件を追加しました。一次PDFの版、SHA-256、節との対応は `mapping.md` に記録し、各 `run.py` は標準ライブラリだけで独立して動きます。

- **OGR:** SIDの統合、処理間の依存関係、報酬の調整。理論上の依存の深さと、実測の処理量を分けています。
- **DREAM:** 既存の多段処理を制御し、一部の判断を上書きする方法。改善が積み重なったときの効果を区別します。
- **PILOT:** 実験の開始から終了までの流れと、別の課題で過去の結果を使う仕組み。無作為に割り付けていない前後比較であり、二つの要因を組み合わせた2×2の実験は未実施です。

ここでも仕組みの確認は一部に限り、本番性能、規模拡大、本番適用性は未検証です。

### 2026-09-21：生成型推薦に置き換える範囲を比べる

6件を追加しました。各Labに一次論文の版とハッシュ、実行コード、結果、原典対応表があります。

- 優先（Must）：[LIGE-GR](papers/lige-gr-meta-listwise/README.md)。既存の順位付けモデルに、候補の並び全体の情報、価値、探索を加えます。
- 優先（Must）：[Sona](papers/sona-yandex-music/README.md)。8,000件の履歴と知識蒸留を使い、多段処理を置き換えます。
- 読む価値あり（Worth）：[Wolt UVR](papers/uvr-wolt-trial-reorder/README.md)。Transformerが確率に変換する前の値（logit）とCatBoostを使い、初回注文と再注文を調整します。
- 注目（Radar）：[PushDualGen](papers/pushdualgen-kuaishou/README.md)。先にSIDを生成し、必要なら後から通知文を生成します。
- 注目（Radar）：[SnapLGR](papers/snaplgr-snapchat/README.md)。Qwen3-0.6Bを使い、複数のリクエストをまとめて処理します。
- 注目（Radar）：[SIDScope](papers/sidscope-diagnostics/README.md)。SIDの対応表と生成経路の記録を診断します。公式のクイックスタートも実行しました。

追加検査は `uv run pytest tests/test_september21_labs.py` と `uv run --with playwright tests/browser_september21.py` です。後者は `/opt/google/chrome/chrome` を使います。本番性能と規模拡大は未検証です。

### 2026-09-22：検索の価値、注文の完納、修正前の診断

[VARG](https://mixidota2.github.io/paper-lab/papers/varg-tmall-value-generative-retrieval.html) は検索に使うID（住所）の安定性、[Accuracy Is Not Service](https://mixidota2.github.io/paper-lab/papers/accuracy-not-service-intermittent-demand.html) は予測精度と注文をすべてそろえて出せた割合の順位、[AURA](https://mixidota2.github.io/paper-lab/papers/aura-disney-agentic-rec-diagnosis.html) は原因を診断して修正を保留する判断を扱います。各PDFの版とハッシュ、実行した範囲は `mapping.md` にあります。

注目枠では、[GRACE](https://mixidota2.github.io/paper-lab/papers/grace-meta-ads-gtm-serving.html) でリクエストごとに候補を制限するマスク、[ICEGR](https://mixidota2.github.io/paper-lab/papers/icegr-baidu-intent-generative-retrieval.html) でマージンの係数、[EvoPilot](https://mixidota2.github.io/paper-lab/papers/evopilot-verify-dont-trust-autoresearch.html) で評価器の不具合の時系列、[SIDInspector](https://mixidota2.github.io/paper-lab/papers/sidinspector-mapping-diagnostics.html) でIDの対応表の診断を図で追えます。7件の画面幅ごとの表示を確認するコマンドは `uv run --with playwright tests/browser_september22.py` です。

### 2026-09-23：何を測るか、どこを統合するか、何を配信するか

優先3件を先に公開し、注目4件を追加しました。一次資料と検証記録は [BATCH-2026-09-23.md](BATCH-2026-09-23.md) にまとめています。

- [Netflix：反実仮想の測定](https://mixidota2.github.io/paper-lab/papers/netflix-counterfactual-observability.html)
- [UNIQUE：候補検索の処理内で表現を共有](https://mixidota2.github.io/paper-lab/papers/unique-baidu-unified-retrieval-ranking.html)
- [FlashVector：システム全体の性能から採用を判断](https://mixidota2.github.io/paper-lab/papers/flashvector-unity-serving-stack-agent.html)
- [YouTube Music](https://mixidota2.github.io/paper-lab/papers/youtube-music-llm-rationales-discovery.html)
- [MuSeR](https://mixidota2.github.io/paper-lab/papers/muser-baidu-long-sequence-multi-interest.html)
- [HGenPush](https://mixidota2.github.io/paper-lab/papers/hgenpush-kuaishou-heterogeneous-push-gr.html)
- [t0：外部の説明変数を使う時系列基盤モデル](https://mixidota2.github.io/paper-lab/papers/t0-tsfm-forecasting-with-context.html)
