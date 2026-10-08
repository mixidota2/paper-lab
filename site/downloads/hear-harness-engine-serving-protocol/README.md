# Can Agent Harnesses and Inference Engines Hear Each Other? The HEAR Protocol for Agentic LLM Serving

## Overview — 概要

**Radar：harnessが知る再利用予定と、engineが知る現在のKV状態を接続する。** HEARは両者の交換内容と、その言葉の効力を定めるプロトコルである。SCBenchでは待機保護付きの方策がbatch処理を1.61倍速め、最初のtokenまでの時間（TTFT）の中央値を2.23倍、P95を1.45倍改善した。

効率の結果であり、エージェントの正しさを端から端まで保証するものではない。2つの調査タスク群で品質低下を観測しなかったことも、一般的な同等性証明とは分ける。

## Problem — 問題設定

harnessは次に必要な文脈と依存関係を知るが、GPUにそのKVが残っているかは知らない。engineはキャッシュやqueueを知るが、tool待ち中のagentがすぐ戻るかは知らない。この分断は、再利用直前の追い出しや、温かい要求を待たせて冷たい要求を先に処理する原因になる。

「後で使う」という予測を「必ず保持せよ」と解釈すると、今度は混雑時に資源を塞ぐ。情報の種類だけでなく、要求なのか希望なのかを区別する必要がある。

## Core Idea — 著者の主張とLabの解釈

著者の主張：HEARは要求・文脈version・serving instanceへ紐づく双方向の意味規約を用意し、最適化方策から切り離す。cache-aware調整と役割別の実行構成選択で、同じ規約を使った効率改善を示した（§3–4）。

本Labの解釈：Parrot、KVFlow、PBKV、Pythiaなどにも跨層の情報利用はある。HEARの焦点は、特定のschedulerを標準にすることより、意図・状態・制御・実行結果を同じ意味で接続することにある。[本日のharness費用Lab](harness-buys-tokens-not-pass-rate.html)と合わせると、harnessは毎stepの入力を増やす側にも、再計算を減らす情報を渡す側にもなりうる。

## モデルと式

### 4種類のメッセージ

Harness→EngineのExecution Description and Intentは、役割、準備完了、依存関係、文脈の寿命、明示的に予測とした再利用予定を伝える。Execution Requirements and Controlは、待機制約、保持・準備・解放、実行構成を要求する。

Engine→HarnessのState and Capabilitiesは、KVの所在、queue、資源圧力、対応操作を返す。Execution Outcomesは、accepted、completed、rejected、unsupported、failedと実際の構成・再利用・費用を返す（Table 1）。

Table 2のmessage forceは4対ある。説明は命令ではない。希望はbest effort、要件は実行の制約。状態観測は予約保証ではない。受理は完了ではない。満たせない要件は拒否するか、明示的に許された代替を使う。

### 方策は2つの時間粒度で動く

Eq.1の`dᵢ=π(hᵢ,sⱼ)`は、harness情報hと最新の関連engine状態sから実行を決める。jとiは同時刻とは限らない。cache-aware方策では連続する再利用可能prefixが50%以上ならhotとし、再利用block数の多い要求を優先する。Guard-WはW秒待った要求を保護し、後続hot要求の追い越しを止める。完了時刻をW以内に収める保証ではない。

MooncakeのSession-Awareは別の保持方策で、完了済み会話から推定した継続確率pとidle時間を用いて`r=p exp(−idle/400)`で保持優先度を決める。意図を保持命令とは扱わない。

役割別選択は`{vLLM, OmniKV} × {vLLM, H2O, SnapKV}`の6構成を開発時に測る。品質・安定性の条件を通した後、makespanが小さい組を凍結する。BrowseComp-Plusは(vLLM,H2O)、DeepResearchBenchは(OmniKV,H2O)。正式評価の結果から後付けで選ばない。

## Why It Might Work — 解釈

解釈：既にあるKVを使えばprefillを減らせるが、hot要求だけを先にするとcold要求が待ち続ける。engine状態は再利用機会を教え、harnessの待機要件はその利用に制限を付ける。この両方を表現できる点が効率と応答性の調整に役立つ。

役割別には、長い出力ほど実行モード固有の準備費用を回収しやすい。GLM-4.7-FlashのMain出力はBrowseComp-Plusで約0.4K、DeepResearchBenchで約4.4K token。すべての役割へ同じKV圧縮構成を当てる理由はない。

## Evidence — 著者報告

[一次資料：原論文 Table 3–6 / Appendix A–B](https://arxiv.org/pdf/2610.06597v1)の著者報告。SCBench/MooncakeはQwen3-8B、調査タスク群はLangGraphとGLM-4.7-Flashを使う。記録した同じ要求軌跡を再生し、生成内容の変化をscheduler差へ混ぜない。

| SCBench | TTFT中央値 / P95 / 最大 秒 | batch 秒 | KV再利用 % |
| --- | --- | --- | --- |
| FCFS | 63.1 / 74.2 / 79.0 | 481 | 19.2 |
| Cache-Aware | 4.6 / 75.8 / 93.9 | 224 | 87.6 |
| + Guard-40 | 28.3 / 51.1 / 65.0 | 299 | 66.1 |
| + Guard-60 | 4.5 / 64.0 / 80.4 | 230 | 84.7 |

**出典訂正：87.6%、63.1→4.6秒、481→224秒はSCBenchのTable 3であり、Mooncakeではない。** guardなしでは中央値とbatchが良くなる一方、最大TTFTは悪化する。

Mooncakeの50%負荷ではSession-Awareが再利用を19.5→31.9%へ改善。75%では組合せが有利だが、100%負荷でSession+Cache+Guardのthroughputは108.9 turns/minとなりFCFSの122.7を下回る。Cache-Aware単独は128.3、中央値TTFTは163.9→86.8秒。混雑下で同じ組合せが常に勝つわけではない。

BrowseComp-Plus（208問）は5.69→4.62時間、1.23倍、Judge正答率46.15→46.63%。DeepResearchBench（100件）は5.93→2.42時間、2.45倍、RACE 40.6→41.1。開発時の構成探索費用は正式E2E時間に含まれない。

## Executable Understanding — 実行可能な理解

時刻0にcold要求B/C、2人工秒ごとにwarm文脈Aの要求が来る。1スロットのengineで、KVは1文脈だけ保持する。hitのprefillは1、missは6、decodeは1人工秒。FCFS、cache優先、cache優先+8秒guardを同じ到着列で比べる。

時間軸の各要求を選ぶと、実行前のKV、追い出し、最初のtoken、待機保護が見える。上の通信図では、受理と完了を別の段階として進める。通信図は意味の説明、時間軸はPythonの実行結果である。

## Results — 最小実験の結果

toyではFCFSの平均/最大TTFTは18.83/20、cache優先は5.50/45、guard付きは15.50/21人工秒だった。guardはcold要求の長い待機を抑えたが、全体をFCFSより速くする保証ではない。batchは51/46/51で、待機保護と再利用の交換条件が見える。

## What We Verified — 確認できた範囲

CONFIRMED：同じ到着列の全要求を一度ずつ処理し、到着前には実行しない。cache優先で平均が下がり最大が増える例、guardで古いcold要求の待機を抑える例を確認した。

PARTIAL：待機と再利用の仕組みだけを実行した。HEAR全体、prefix block、複数GPU、非同期状態更新、Session-Aware保持方策を実装したものではない。

## What We Did NOT Verify — 未検証

NOT TESTED：実LLM、GPU、KV圧縮、実際のprotocol adapter、4ベンチマークの再現、本番運用、古い状態通知や故障時の正しさ。論文の品質指標は限られたタスク群で低下を観測しなかったという結果であり、E2Eの正しさや同等性の保証ではない。公式リンクは匿名公開先で、今回の取得では内容を確認できなかった。固定版コードの実行はしていない。

## Implementation — 実行方法

リポジトリ直下で実行する。Python標準ライブラリだけを使い、APIへは接続しない。

```bash
uv run --no-project papers/hear-harness-engine-serving-protocol/run.py
uv run paper-lab build
```

lab.yamlとREADME.mdが説明、run.pyとresults.jsonが実験、mapping.mdが原典との対応を保持する。HTMLはビルドで生成し、直接編集しない。

## Original Paper / Official Code Mapping


一次資料：[arXiv 2610.06597v1](https://arxiv.org/pdf/2610.06597v1)。2026-10-08照合。PDF SHA-256: `ecdc8cdbeb1f3e93579141278a920ac9009f737785373af5a6694d2c122d3d0c`。

| 原典 | Lab | 境界 |
| --- | --- | --- |
| Table 1–2 / Fig.2 | 通信図 | 4方向の意味と受理/完了の違いを段階表示。wire formatの実装ではない。 |
| §4.2 / Appendix A.2 | schedule() | hot優先と待機保護を単一スロットで縮約。全prefix一致のtoy。 |
| Table 3–6 | lab.yaml / results.jsonのpaper | SCBenchとMooncakeを別の系列で保存。独立再現ではない。 |
| Eq.4–5 / Appendix A.1 | method節 | 6構成の役割別選択を説明。GPU/KVモードの実装は省略。 |

公式コード：[著者がPDFで案内した公開先](https://anonymous.4open.science/r/hear-3D1E/)。本Labはこのコードを実行・監査していない。

匿名公開先は今回の取得で内容を確認できなかった。コード内の関数や固定revisionとの対応はNOT TESTEDとする。
