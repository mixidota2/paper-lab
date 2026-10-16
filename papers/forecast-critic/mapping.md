# 原典と教材の対応

固定版：[arXiv:2512.12059v1](https://arxiv.org/html/2512.12059v1)。Dataset construction、M5 Dataset construction / Empirical results、Appendix Aを公開HTMLで照合した。原典バイト列のハッシュは未取得。

- 合成：各摂動334候補からSMAPE悪化上位75%の250件＋未変更250件。自然発生する失敗の無作為標本ではない。
- Appendix A：weighted F1はクラス別F1の件数加重平均。陽性単独F1ではない。
- M5：1000系列、履歴120日・予測28日、Chronosの中央値・10/90分位画像。共変量なし。過剰警告を受けpromptを調整（Appendix Eも参照）。群間sCRPS差は介入後の改善ではない。
- toy：固定10件、手製陽性ラベル6/10。ページの表は閾値5の保存結果。閾値UIはない。コードは0〜10を計算するが、警告0件のprecisionは未定義（null）。著者のF1や画像理解の再現ではない。

再実行はリポジトリルートで `uv run papers/forecast-critic/run.py`。標準ライブラリと共有 `papers/_toy_common.py` を使用し、結果JSONを更新する。
