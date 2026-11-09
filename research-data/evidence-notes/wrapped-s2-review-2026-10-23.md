# Dated research notes: wrapped-s2-review-2026-10-23

These are historical authored summaries and source-reading limitations. Publication and retrieval dates are those recorded at the time. No new primary verification or experimental reproduction is claimed.

## 一次資料と確認範囲

Vogel et al. (2026), DOI 10.1371/journal.pmed.1004575 の S2 Box。
正規DOI: https://doi.org/10.1371/journal.pmed.1004575.s006
公式取得URL: https://journals.plos.org/plosmedicine/article/file?id=10.1371%2Fjournal.pmed.1004575.s006&type=supplementary
2026-10-22T23:58:02ZにHTTP200、53,090 bytesで取得。PLOS corpus版1、Last-Modified 2026-03-31T17:23:55Z、generation 1774977835705145。
SHA256: 6362fec57b34ea85153a7a6bd2382a01abd4c176440a33e2d34df27894395451

DOCXを全1ページとしてレンダーし、本文抽出と目視で全ページを確認。「Interrupted Time Series analysis – store sales data」と「Difference in difference analysis – household purchasing data」の2節を読了。数式・追加結果表はない。以下は自作要約であり、原文全文は保存しない。

## 著者が記載したモデル

店舗販売は各店舗ペア別のITS。ベースラインからの週の線形項、介入群、介入後を示すlevel、介入後の週を表すtrend、および介入群と週・level・trendの交互作用を含む。モデル適合のために、クリスマス週、2020年6月のロックダウン終了週、介入前週の追加項を入れる。介入群×levelが即時の変化を検定し、3・6か月の効果の信頼区間はデルタ法で算出する。

家庭購買はロジスティック回帰。介入群、0–3か月と3–6か月を表す2個の期間ダミー、群×期間の交互作用を固定効果とする。女性のランダム効果を入れ、女性内に週が入る階層構造を扱う。

## 解釈と残る限界

ロジット尺度の交互作用係数を、そのまま本文の+3.3パーセントポイントと読んではならない。S2には確率差への変換・周辺化手順、係数・共分散、ITSの残差相関構造、推定オプション、実行コード、個票はない。trendの正確な符号化式も表示されていないため、中心化したpost-time等を著者の式として創作しない。

今回は新しい実験結果や独立再現を得たのではない。NIHR本文は引き続き未読。本文の主要/副次指標、非無作為割付、位置と品揃えの同時変更、非公開データの限界を変えない。
