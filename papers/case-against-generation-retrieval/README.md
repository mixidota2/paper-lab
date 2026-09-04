# Case Against Generation for Retrieval — 小実験

`uv run papers/case-against-generation-retrieval/run.py` は合成 catalog で逐次 ID decode と因子化検索を比べ、`results.json` を更新する。Meta の LLM、ANN、NE を再現しない。

原論文 §4 の teacher/student、§5 の serving、§6.2.3 の CE2TT ablation を説明するための最小実装である。
