# 論文初版とLabの対応

[論文初版（arXiv v1）](https://arxiv.org/pdf/2606.10375v1)の確認記録は2026-09-22。保存したPDFのSHA-256は `4fc33c243ac3dae6dcd04666b3ab85a677fcdc089531c5e8edd77aff78300cb5` です。

| 論文・公式コードの箇所 | Labで確かめたこと | Labで扱わなかったこと |
| --- | --- | --- |
| §2 / `sidinspector.preflight` | `validate()` が人工の入力を点検 | 公式の項目やデータ来歴をすべて検査する処理 |
| §3 / `sidinspector.metrics` | `probe()` が固定した商品対でD1〜D5を計算 | 学習用の利用履歴から、商品ごとに上位k件の近傍を作る処理 |
| 表2 | ある条件で書き出した対応表の測定値を掲載 | 各方式で対応表を作り直すこと |
| §5 / `examples/minimal_adapter.py` | 実行の手順はREADMEに案内 | 公式パッケージの全検査 |
| `tools/verify_package.py` | 公式の検証入口として参照 | 新規に取得した環境での独立追試 |

論文初版の公開タグは `sidinspector-cikm2026-resource-v0.6` です。2026-09-22に確認した[公式リポジトリ](https://github.com/jdding/sidinspector)のmainにあるREADMEはv1.0を案内していました。確認したREADMEのSHA-256は `ab9e9927ddf8d74725746714634c727f5255ec4b5f897272f2ad8a88a7f5fed0` です。論文の報告値をv1.0で再計算したわけではありません。
