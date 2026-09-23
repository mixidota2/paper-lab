# Explainable Recommendations at Scale: LLM Rationales for YouTube Music Artist Discovery

YouTube MusicのYDD棚で、LLMの候補推薦と理由文をoffline生成。2週間A/Bで棚engagement +22.43%［95% CI 16.93–27.93%］。理由文を外すholdbackが主因を示すが、発見には候補追加も寄与する。

## 問い

未知のartistを増やす効果と、理由を添える効果を分けられるか

## 再実行

```bash
uv run papers/youtube-music-llm-rationales-discovery/run.py
```

Python標準ライブラリだけを使う。単体で取得した場合は `uv run run.py`。結果はスクリプトと同じ場所の `results.json` に保存する。

## 読む順序

`lab.yaml` の問題設定・根拠、`method.md` の仕組みと図、`run.py` と `results.json`、`mapping.md` の省略点。HTMLは `uv run paper-lab build` で生成する。

Mechanism PARTIAL。Performance / Scaling / Production applicability NOT TESTED。小実験で確認した局所条件のみCONFIRMEDとし、論文の本番数値を再現したとは扱わない。
