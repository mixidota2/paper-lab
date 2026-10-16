# WRAPPED：店全体の販売と家庭の購入確率を分けて読む

2026年3月31日公開の既刊論文（DOI 10.1371/journal.pmed.1004575）を対象とする日本語Interactive Lab。36店舗のマッチド自然実験であり、ランダム化試験ではない。入口側への移動と品揃え拡大を同時に行っている。

主要な家庭指標の6か月差は+3.3ポイント、95% CI [−2.5, 9.2]。副次的な店舗の青果販売個数は直後+0.32 SD [0.11, 0.53]。両者を同じ成果として扱わない。公表された効果量・CIの切替図と、対照店のトレンド、一時的改装ショック、介入店だけの変化を操作する合成実験を収録する。

## 再実行

リポジトリ直下で実行する。依存定義は既存のpyproject.tomlとuv.lockを使用する。run.py自体はPython標準ライブラリのみで、単体でも実行できる。

```bash
uv sync --extra dev --frozen
uv run papers/wrapped-produce-placement-controlled-trial/run.py --test
uv run papers/wrapped-produce-placement-controlled-trial/run.py
uv run pytest
# 出力先は毎回新しい専用ディレクトリを選ぶ（既存出力は削除される）
uv run python -m paper_lab.build --root . --out /tmp/paper-lab-wrapped-review
uv run python -m http.server --directory /tmp/paper-lab-wrapped-review 8000
```

ホームのキャッシュが書込不可なら `UV_CACHE_DIR=/tmp/uv-cache` を指定する。ビルドは全papers/を入力する。限定した数件の出力で本番サイトを上書きしない。

ブラウザーで `/papers/wrapped-produce-placement-controlled-trial.html` を開く。指標2種類×時点3種類、合成条件3×3×3、初期化ボタンを確認する。360・390・768・1440pxの幅でページ全体の横はみ出し、図、キーボード操作、リンクとJavaScriptエラーを検査する。因果図だけは狭い画面で内部スクロールできる。JavaScript無効でも初期値と数値表は残る。

## 原本と生成物

- `lab.yaml`、`method.md`：自作の日本語説明と概念図。
- `run.py`：公開報告値の転記と決定的な合成実験、検証テスト。
- `results.json`：`reported` と `synthetic` を分離した結果。
- `evidence.md`、`experiment.md`：run.pyから再生成する操作図。手で変更しない。
- `mapping.md`：節・表との対応、省略、確認の範囲。

## 検証の境界

CONFIRMEDは、共通トレンドを除去する等の人工データ上の計算に限る。原論文の方法理解はPARTIAL。実店舗の効果の独立再現、健康改善、配置単独の効果、スケーリングはNOT TESTED。家庭の持続的な増加の断定はNOT OBSERVEDであり、効果ゼロを証明した意味ではない。

S2 Box本文の取得と式の照合が未完のため、この候補はdraftで公開保留。販売・購買の個票は原典のData Availabilityにより非公開。NIHR本文も今回取得できておらず、読んだとは扱わない。

## 出典と権利

Vogel C, Crozier S, Dhuria P, et al. (2026). *Impact of supermarket fruit and vegetable placement on store sales, customer purchasing, diet and household waste: A prospective matched-controlled cluster trial*. PLOS Medicine 23(3): e1004575. [本文](https://doi.org/10.1371/journal.pmed.1004575)、[S2 Box](https://doi.org/10.1371/journal.pmed.1004575.s006)。原論文と補足はCC BY（補足のFigshare記載はCC BY 4.0）。数値を出典付きで再描画し、文章・図・実験はLab用に制作した。原論文の図版や個票を転載していない。

Baird et al. (2024), [WRAPPEDプロセス評価](https://doi.org/10.1186/s12966-024-01679-3)。[NIHRレポート](https://www.ncbi.nlm.nih.gov/books/NBK623045/) は参照先のみで、今回の確認根拠には使わない。
