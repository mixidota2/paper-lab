# WRAPPED：入口に青果を移した店で、何が変わったか

著者はイングランドのスーパー36店舗で、青果を入口近くに移し、品ぞろえを広げたときに何が変わるかを調べました。改装する18店に条件の似た18店を対応させています。店舗を無作為に割り付けた試験ではなく、青果の位置だけを変えた試験でもありません。

導入直後、店舗の青果販売数量は「導入しなかった場合」の予測を0.32標準偏差上回りました（95%信頼区間：0.11〜0.53）。6か月時点では、家庭が青果を買う確率は介入店側で3.3ポイント高い推定でしたが、95%信頼区間は−2.5〜9.2ポイントでした。店全体で青果が多く売れても、青果を買う家庭が継続して増えたとは言えません。

Labの図では、著者の推定値を指標と時点で切り替えられます。別の小実験では、対照店と共通の変化、改装直後の一時的な上振れ、改装した店だけの変化を動かし、推定値がどう変わるかを確かめられます。

## 小実験を再実行する

リポジトリの最上位で次のコマンドを実行してください。小実験の `run.py` はPython標準ライブラリだけで動きます。サイトを生成するときは、既存の `pyproject.toml` と `uv.lock` の依存関係を使います。

```bash
uv sync --extra dev --frozen
uv run papers/wrapped-produce-placement-controlled-trial/run.py --test
uv run papers/wrapped-produce-placement-controlled-trial/run.py
uv run pytest
# 出力先は毎回新しい専用ディレクトリを選ぶ（既存出力は削除される）
uv run python -m paper_lab.build --root . --out /tmp/paper-lab-wrapped-review
uv run python -m http.server --directory /tmp/paper-lab-wrapped-review 8000
```

ホームのキャッシュに書き込めない場合は `UV_CACHE_DIR=/tmp/uv-cache` を指定してください。ビルドには `papers/` 全体を使います。一部の記事だけを生成して本番サイトを上書きしないでください。

ブラウザーで `/papers/wrapped-produce-placement-controlled-trial.html` を開くと、2種類の指標と3種類の時点を切り替えられます。小実験には3×3×3通りの条件があり、ボタンで初期値に戻せます。幅360・390・768・1440pxで、図、リンク、キーボード操作、JavaScriptエラーと、ページ全体の横はみ出しを確認します。狭い画面では因果図だけを横にスクロールできます。JavaScriptが動かなくても初期値と数値表は読めます。

## どのファイルに何があるか

- `lab.yaml` と `method.md` に、日本語の本文と図があります。
- `run.py` は、論文の報告値を表示する図と、人工データの小実験を作ります。`results.json` では報告値を `reported`、小実験を `synthetic` に分けて保存します。
- `evidence.md` と `experiment.md` は `run.py` から再生成します。図の説明も `run.py` 側で直してください。
- `mapping.md` には、論文の節・表との対応とLabで再現していない処理があります。

## Labで確認できた範囲

人工データでは、両店に共通する変化だけなら、対照店を使うことで設定した効果を求められます。一方、実施店だけの変化や改装直後の一時的な上振れは、対照店を使っても除けません。店舗販売や家庭の購買を独立に再推定したわけではなく、配置単独の効果、健康への影響、規模を広げた場合の結果は検証していません。家庭が継続して多く買うとは確認できませんでしたが、効果がなかったと証明したわけでもありません。

S2 Boxの全1ページには、店舗の時系列モデルと家庭購買のロジスティック回帰の構成が書かれています。残差の相関、推定時の設定、購入確率差への変換手順は記載されていません。したがって、回帰係数と報告された+3.3ポイントは同じ値として扱えません。販売・購買の個票は公開されておらず、Labは著者の推定を再実行していません。NIHR本文も未取得です。

## 出典と権利

Vogel C, Crozier S, Dhuria P, et al. (2026). *Impact of supermarket fruit and vegetable placement on store sales, customer purchasing, diet and household waste: A prospective matched-controlled cluster trial*. PLOS Medicine 23(3): e1004575. [本文](https://doi.org/10.1371/journal.pmed.1004575)、[S2 Box](https://doi.org/10.1371/journal.pmed.1004575.s006)。論文と補足はCC BY（補足のFigshare表記はCC BY 4.0）。数値を出典付きで描き直し、原論文の図版と個票は転載していません。

Baird et al. (2024), [WRAPPEDプロセス評価](https://doi.org/10.1186/s12966-024-01679-3)。[NIHRレポート](https://www.ncbi.nlm.nih.gov/books/NBK623045/) は参照先のみで、Labの確認根拠には使っていません。
