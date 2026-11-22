# Explainable Recommendations at Scale: LLM Rationales for YouTube Music Artist Discovery

YouTube Musicのホームには、新しいアーティストを見つけるための推薦欄（YDD）がある。論文の方式は、候補となるアーティストと「なぜすすめるのか」を伝える理由文を、画面の応答とは別に大規模言語モデル（LLM）で生成する。

2週間のA/Bテストでは、この推薦欄のエンゲージメントが22.43%増えた（95%信頼区間：16.93–27.93%）。理由文を外した比較では、候補を追加する機能よりも、理由を表示する機能のほうがエンゲージメントへの寄与は大きかった。アーティストの発見を測る指標では、候補の追加も寄与した。

## このLabの問い

まだ聴いていないアーティストを候補に加える効果と、候補に理由を添える効果は、どの比較で見分けられるか。

## 人工例を再実行する

```bash
uv run papers/youtube-music-llm-rationales-discovery/run.py
```

Pythonの標準ライブラリだけで動く。スクリプトだけ取得した場合は `uv run run.py` で実行する。結果はスクリプトと同じ場所の `results.json` に保存される。

## 原本と検証範囲

問いと報告値は `lab.yaml`、処理の流れは `method.md`、人工例の実行と結果は `run.py` と `results.json` にある。どの処理を簡略化したかは `mapping.md` を参照。HTMLは `uv run paper-lab build` で生成する。

仕組みは一部確認済み（Mechanism PARTIAL）。人工例で動作した条件のみ確認済み（CONFIRMED）とする。性能、規模を拡大した場合の動作、本番への適用は未検証（NOT TESTED）。論文の本番結果は再現していない。
