# Case Against Generation for Retrieval — Interactive Lab

Zhe Xu et al. (Meta), arXiv:2607.25346（2026）。LLM を two-tower の意味バックボーンとして
使う枠組みのラボ。

## 「意味は LLM、配信は ANN」が工業的に効く理由

- 生成 SID デコードがレイテンシと grounding で不利になり得る形（玩具）
- 古典 two-tower を LLM 表現で立て直す設計の骨格

## やっていないこと

Amazon 学習、CE 蒸留、本番 NE は再現しない。

```bash
uv run python papers/case-against-generation-retrieval/run.py
```
