| 論点 | 一次資料 | Labの対応 | 省略 |
| --- | --- | --- | --- |
| 反実仮想の状態 | [Definition 1・式(1)](https://arxiv.org/html/2609.04875) | advance・audit・数式図 | 実LLM・確率的生成 |
| cropと後半の再実行 | [Algorithm 1](https://arxiv.org/html/2609.04875) | replay・splice.svg | KVは記号辞書。provenanceは既知 |
| 複数probeと行動 | [表2–3](https://arxiv.org/html/2609.04875) | probes・audit・audit.svg | probeは手書き。実攻撃の再現ではない |
| 最小費用 | [Corollary 1](https://arxiv.org/html/2609.04875) | experiment・cost_sweep | token数・遅延は測定しない |

2026-09-07 UTCにarXiv v1のabs・HTMLを確認。公開公式コードの実体と行単位の照合は未確認。著者のoracleによる独立性ラベルが実運用でどの費用・精度で得られるかは検証できない。図はresearch_botによる教育用の再構成。

関連：[Harness-Bench](harness-bench.html)と[GAIAのscaffold効果](scaffold-effects-gaia.html)が測る実行基盤の違いに、状態の取り消しという新しい評価軸を足す。
