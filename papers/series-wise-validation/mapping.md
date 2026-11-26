# 一次資料とLabの対応

| 一次資料 | Labで説明または確認したこと | 確認していないこと |
| --- | --- | --- |
| [原論文v1](https://arxiv.org/html/2611.08252v1)の本文、付録A、表1〜11、図1〜5のキャプション | §3.3・§4.1の情報の分け方を、`run.py` の `origins()`、`fit()`、`select()`、`evaluate()` で説明します。 | PDFの全画素、全CV方式やニューラルモデルは確認・再現していません。 |
| §5、表3 | 丸め済みの掲載値を `table3.json` に保存し、表示行の平均、勝数、Weatherの寄与を計算します。掲載平均は別に残します。 | 著者の未丸めの値や実行ログは使っていません。 |
| [著者のリポジトリ](https://github.com/vcerqueira/experiments-tscv)の `src/config.py` | 読み取り時のツリーは `3ba404c160ff9e59bd554fc7bd0352f7497434eb` です。SEEDは456、N_FOLDSは5、N_SAMPLESは20、OUT_SET_MULTIPLIERは2、STEP_SIZEは1、HOLDOUT_FOR_OUTSETは0でした。既定値のままでは主実験の約30%除外になりません。 | 論文に対応するコミットや、公式実装全体とQ=0の処理は確認せず、コードも実行していません。 |

`model.js` は合成例を計算し、`interactive.js` は分割図、条件変更、初期化、JSON保存を担当します。LabはPython版と照合し、最終評価の値を変えても選んだモデルが変わらないことを確認しました。原論文のPDF、第三者コード、管理記録は配布していません。
