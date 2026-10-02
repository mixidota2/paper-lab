§3.1–3.3、図1、Algorithm 1–2、表1・3–6を確認した。

|一次資料|Labの対応|省略・境界|
|---|---|---|
|§3.3、式(1)–(3)、Algorithm 2|run.py: replay、100候補の全探索、在庫日数の図|2カテゴリ、固定レビュー・リードタイム。代替需要と実データを省略|
|図1、§3.1、表5|method.mdと学習段階の図|0.93M Transformer＋VAEは未学習|
|§3.2、Algorithm 1|run.py: rloo、式の説明|報酬4個の基準値だけ。方策勾配・KL・ハイブリッド報酬の実装なし|
|表1|results.json: paper_evidence.offline_total_cost|著者報告の転記。非公開JDデータは未取得|
|表3・4、図7|現場指標を切り替える図|PSM・DiDの再推定なし。単位と比較基準を分離|

原論文：[2512.19001v2](https://arxiv.org/abs/2512.19001v2)。提供PDFで公式コードのURLを確認できず、公式実装は未実行。図は原論文の構造・数値から独自に作成した。

比較地図はLabの解釈。[DeepStock](deepstock-policy-regularized-inventory-drl.html)、[SabreAgent](sabreagent-design-time-inventory.html)、[InvEvolve](invevolve-whitebox-inventory-evolution.html)は既存Labの一次資料対応を参照する。手法間の直接実験はない。
