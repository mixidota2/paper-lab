# SGC：今の状態に沿って助言する

SGCは意図・所持条件・対話履歴から生成前の制御を作る。200セッションでSGA 83.5%、最初のtokenまで1.5秒。製品A/Bの改善量は未開示。

## Overview
SGCは、利用者の今の状態に応じて、何を調べ、どの制約を説明し、いつ提案するかを生成前に決める設計である。Tencentのゲームコーチを対象に、200セッション・約1,000回答の人手評価を報告する。Full SGCのTGAは96.7%、SGAは83.5%。製品の利用継続率や勝率を改善したA/Bの数値は開示されていない。

## Problem
図鑑では正しい技でも、その利用者が未解放なら戦術として使えない。回答が質問に沿って完結していても、現在の所持品や直前の助言に反する方向へ進む失敗を、著者はdirection driftと呼ぶ。静的な事実の誤り、未所持品の誤認、反復による疲労は重なる場合もある。分類の名称より、判断時点の状態を評価の参照先に含める点が実装上の焦点になる。

## Core Idea
著者の主張：Perception / Grounding / Interactionのwrapperへ状態に応じた制御を移す。LLMはその制御変数に従って文章を生成する。3つを順に加えた比較で、速度とgroundingの改善を報告する。

解釈：[IGPO](igpo-huawei-inventory-grounded-search.html)が候補の存在を検索して誤った不在判断を減らすのに対し、SGCは利用可能な候補をどう説明し、いつ再提案するかまで扱う。これはLabの比較であり、両方式を組み合わせた実験はない。著者の「promptはlive stateに対応できない」という強い表現も一般的な不可能性としては読まない。比較対象の設計と調整条件を確認する必要がある。

## Why It Might Work
解釈：制約の判定を明示すれば、自然な文章が書けたかと、助言の前提が満たされるかを別々に調べられる。履歴を入力とする規則は、同じseedで選択を再生できる。ただし、誤ったslot抽出や古いsnapshotを与えれば、決定的な規則も誤った結論を安定して返す。生成文の意味まで保証する方法ではない。

## Evidence
[一次資料 §7 / Table 3–4 / Appendix G](https://arxiv.org/pdf/2609.27606v1) の著者報告。約4週間の本番ログから200セッションを抽出し、同じLLM・tool schema・参照証拠で比較する。2名の独立評定と第3者の裁定を用い、テスト集計にはLLM judgeを使わない。

| 構成 | 最初のtokenまで・秒 ↓ | TGA % ↑ | SGA % ↑ | TGQ / DGP / CCC |
| --- | --- | --- | --- | --- |
| Prompting | 2.3 | 61.1 | 20.0 | 6.2 / 4.7 / 8.3 |
| PE-Agent | 6.1 | 69.8 | 26.5 | 6.5 / 5.5 / 8.1 |
| W1 | 1.5 | 89.1 | 46.5 | 8.4 / 7.7 / 9.0 |
| W1 + W2 | 1.5 | 89.9 | 56.5 | 8.4 / 7.7 / 8.9 |
| W1 + W2 + W3 | 1.5 | 96.7 | 83.5 | 8.6 / 8.5 / 9.2 |

TGAは各セッション内の正解率を平均する。SGAは全回答が正しいセッションの割合である。TGQは助言の質、DGPは対話を通じた進展、CCCはターン間の一貫性を1–10で評価する。SGAの失敗率は73.5%から16.5%へ下がり、相対減少は約78%。これは製品障害の発生率ではない。

PE-AgentにはSGCと同じ量の製品固有prompt調整が行われておらず、差には設計と調整の両方が含まれる。累積追加の比較からwrapper単独の効果や追加順序への不変性は分からない。LLMの具体的なmodel ID、全評定者の一致度や一部の統計表は公開版では未開示。

## Executable Understanding
`uv run papers/sgc-state-grounded-conditioning/run.py`。人工的な所持品A/B/Cを固定し、Aに必要なskill-Xだけを未解放にする。固定優先順、所持条件の照合、照合と履歴制御を同じ12ターンで比べる。LLMを呼ばず、W1の分岐、W2のhard conflict、W3の抽選と履歴更新を小さく切り出す。



## Results
固定優先順では12回とも使えないAを提案する。所持条件の照合を加えると無効提案は0回になるが、Bの連続反復が11回残る。履歴制御を加えると無効提案と連続反復はともに0回、見送りは2回となる。これらは人工設定の結果であり、論文のTGAやSGAの再現値ではない。

## What We Verified
Mechanism PARTIAL。hard conflict時の候補除外、同一seedでの再生、直前候補の除外、候補が空のときの見送りを確認した。これらの局所規則はCONFIRMED。W1ではsnapshotがない場合と未登録intentの場合にfallbackへ進むことを確認した。

## What We Did NOT Verify
Performance / Scaling / Production applicability NOT TESTED。自然言語のintent・slot抽出、streaming parser、実toolの並列実行、生成文の整合性、200セッションの人手評価、1.5秒の速度、本番A/Bは再検証していない。本文の製品A/B改善量は未開示。IGPOとの統合、ECの在庫推薦やコード補完への転用も未検証である。

## Implementation
標準ライブラリだけで動く。freeze_tools()は状態付きlookup、ground()は必要slotと所持slotの差分、schedule()はhard filter→Bernoulli抽選→重み付き選択を担う。replay()が選択を履歴へ書き戻す。待機期間は1ターンに固定し、soft/hint、複数段落の完全なmutex表、自然言語生成を省いた。

## Original Paper / Official Code Mapping
[対応表](mapping.md)と[手法](method.md)を参照。HTMLはlab.yaml、Markdown、run.py、results.jsonから生成する。
