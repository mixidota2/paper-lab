# What Does a Harness Buy? Tokens, Mostly.

## Overview — 概要

**Worth Reading：harnessの差を、同じ構成の再実行の差と並べる。** SWE-bench Verifiedのhard45では、成否が入れ替わる課題の割合は再実行もharness交換も中央値13%。モデル交換は約22%だった。pool447の2つのQwenモデルでは、Claude Codeとmini-SWE-agentの差は±5ポイント内で等価と判定された。

これは「どんなharnessでも同じ」という結果ではない。有意な差はOpenCodeの不利として現れ、費用は同一モデルでも最大約3倍違う。小さな成功率差を主張する前に、再実行と十分な課題数を確保したい。

## Problem — 問題設定

モデルを固定しても、system prompt、tool schema、履歴圧縮、打ち切り時の回復はharnessごとに違う。一度の得点差だけでは、この構成差と実行ごとの揺れを分けられない。

著者はClaude Code 2.1、mini-SWE-agent 2.4.6、OpenCode 1.18を固定し、Harbor 0.22.0で1試行1コンテナー、300 step上限とした。ネットワークを切った492課題のうち45件がhard45、残りがpool447。初期のネット接続試行ではDeepSeek/Qwenの71%が上流の修正を取得したため、その試行群は捨てている。

## Core Idea — 著者の主張とLabの解釈

著者の主張：このSWE-bench設定ではharnessを交換して得られる成功率の上積みを再実行の揺れから区別できず、明確な差はOpenCodeの損失として現れる。一方、毎stepの入力とstep数は費用を大きく変える（§4）。

本Labの解釈：[Scaffold Effects on GAIA](scaffold-effects-gaia.html)の最大28ポイントや[Harness-Bench](harness-bench.html)の23.8ポイント幅と緊張関係にある。課題領域、ベンチマークとの接続、回復不能な失敗、指標や再実行の設計が違えば両立しうる。ただしGAIAにも反復試行の計画があり、「先行研究はすべて再実行なし」と片付けない。この論文だけでは両立の理由を識別できない。

## モデルと式

モデルは固定する。比較モデルはQwen3.6-35B-A3B、Qwen3.8-27B、DeepSeek-V4-Flash、GLM-5.3-Flash、HY4-Preview。Claude Opus 5はClaude Code内だけの参照で、pool447の比較は2つのQwenに限られる。

同じ課題でAだけ成功した件数をb、Bだけをcとすると、`Δ=(b−c)/n`、不一致率は`q=(b+c)/n`。得点差と、課題の成否が入れ替わる割合は別の量である。McNemarの両側正確検定を使い、対応差の95% Newcombe区間を示す。等価性はTOST、許容幅±5ポイント、90%区間で判定する。

検出力は`M∼Binomial(n,q)`、`B|M∼Binomial(M,(1+Δ/q)/2)`を積分する。不一致件数Mを丸めて固定しない。帰無仮説ではB|Mの成功確率は1/2で、両側p≤0.05となる確率が検出力である。

費用は別に測る。token費用の理解には`Iₖ ≈ P + U + gk`、`ΣIₖ = N(P+U)+gN(N−1)/2`を使う。Pはharnessの定型入力、Uは課題文、gは履歴の増加、Nはstep数。請求はcache hit、miss、出力の単価を分けて足す。下の計算機は入力のみの近似であり、圧縮時点を動かす操作も説明用である。

## Why It Might Work — 解釈

解釈：再実行を対照にすると、何も変えなくても起きる成否の交代が見える。45件では不一致が6件未満なら、すべて同じ側が勝っても5%両側検定で棄却できない。この離散性が小規模評価の限界を作る。

費用では、同じ定型文を毎回送るため小さな初期差が累積する。ただし軽いharnessでもstepが増えれば逆転する。DeepSeekではminiが141 step、Claude Codeが104 stepであり、定型入力の長さだけで安さは決まらない。

## Evidence — 著者報告

[一次資料：原論文 Table 1 / Fig.2 / Appendix F–G](https://arxiv.org/pdf/2610.04433v1)の著者報告。pool447は集合名で、有効ペア数は444〜445件である。

| モデル・差の向き | n | b / c | 差 pp [95% CI] | 判定 |
| --- | --- | --- | --- | --- |
| Qwen3.6 CC−mini | 445 | 26 / 34 | −1.8 [−5.2,1.6] | TOST等価 |
| Qwen3.6 CC−OC | 445 | 43 / 30 | 2.9 [−0.9,6.7] | 未確定 |
| Qwen3.6 mini−OC | 445 | 45 / 24 | 4.7 [1.1,8.4] | p=.02 |
| Qwen3.8 CC−mini | 444 | 17 / 23 | −1.4 [−4.2,1.5] | TOST等価 |
| Qwen3.8 CC−OC | 444 | 52 / 17 | 7.9 [4.3,11.5] | p<.001 |
| Qwen3.8 mini−OC | 445 | 57 / 16 | 9.2 [5.5,12.9] | p<.001 |

CC−miniの90%区間は[−4.7,1.1] / [−3.7,1.0]で±5内に収まる。図の95%区間が±5を越えても、このTOST判定とは矛盾しない。6比較のHolm補正後に残るのはQwen3.8の2差である。OpenCodeの出力上限で打ち切られた課題を除くと一部の差は約半分になるが、除外比較だけで原因の全てを確定できない。

定型入力はCC 16,581、OC 7,025、mini 829 token。GLMの履歴増加は937/681/648 token/step、step数は88.1/55.1/80.2、費用は1.81/0.56/0.97 CNY。cache hit率は96〜99%。hit/miss価格比0.287と0.033による再課金でも、論文で測ったtokenの費用順は変わらなかった。

### §4.5で探したが見つからなかった効果

DeepSeek純正dshは21/45でCCと同数、miniは22。CCのファイル編集toolまたはshellを除いた条件、1年前の1.0.100も対照から1課題以内だった。旧版費用は0.44倍だが、extended thinkingの既定値も異なる。

例外はthinkingとの相互作用。Qwen3.6でthinkingを切るとminiは11ポイント低下（p=.04）、CC/OCでは同程度の低下は出ない。HY4のCCでは11ポイント低下する。harnessのあらゆる部品が無意味だとは結論できない。

## Executable Understanding — 実行可能な理解

不一致率と課題数を選び、50% / 80%の検出力で見える最小差を調べる。Pythonでは厳密な二項分布の総和と12,000回の乱数試行を突き合わせる。図の値はこの計算結果を読む。

定型入力・履歴増加・step数にはAppendix Gの値を使う。cache単価を替えると入力費用の尺度が変わる。圧縮を仮定すると段差が現れるが、これは原論文のログを再生したものではない。実測のCNY請求額は出力tokenを含むため、計算機の値とは比較しない。

## Results — 最小実験の結果

公開コードの入力値まで照合し、本文の丸めを解いた。hard45の不一致率は0.1400894188、pool447は0.1439280360。Labの独立計算で、45件の50%境界は約12.90ポイント、検出力上限は61.69%、447件の80%境界は約5.159ポイントとなった。論文の12.9 / 約62% / 約5.2と整合する。

参考にqを0.14ちょうどへ丸めると447件の境界は5.088ポイントとなる。対話図では両方を選べる。丸めによる差を手法の不一致と扱わない。

## What We Verified — 確認できた範囲

CONFIRMED：著者コードで用いた不一致率を使うと、45件の12.9ポイント、上限約62%、447件の約5.2ポイントが独立計算で整合する。12,000回の乱数試行と厳密計算の差は2ポイント未満。GLMの代表値による入力token近似ではCC > mini > OCの順になった。

PARTIAL：token式は入力だけの近似であり、実測CNY請求額や圧縮ログを再現していない。

## What We Did NOT Verify — 未検証

NOT TESTED：実LLMやSWE-benchの再実行、TOSTの元の課題別データからの再現、完全な出力・cache課金、現行版harnessの比較。本論文は主に1ベンチマーク、300 step上限であり、閉鎖型の最上位モデルを3つのharnessすべてで比べていない。ローカルQwen群の時間上限差、課題の学習混入も残る。

## Implementation — 実行方法

リポジトリ直下で実行する。Python標準ライブラリだけを使い、APIへは接続しない。

```bash
uv run --no-project papers/harness-buys-tokens-not-pass-rate/run.py
uv run paper-lab build
```

lab.yamlとREADME.mdが説明、run.pyとresults.jsonが実験、mapping.mdが原典との対応を保持する。HTMLはビルドで生成し、直接編集しない。

## Original Paper / Official Code Mapping


一次資料：[arXiv 2610.04433v1](https://arxiv.org/pdf/2610.04433v1)。2026-10-08照合。PDF SHA-256: `c0c4899a732bb57aab9bac01fb64c83bc343c2a53e65554024ae292113726a32`。

| 原典 | Lab | 境界 |
| --- | --- | --- |
| Appendix F / Fig.A2 | binom(), rejection(), power(), mde(), simulation() | 二項分布を積分し、45/447件を乱数試行と照合。 |
| Appendix G / Table A4 | token_bill() | 定型入力と履歴増加を用いる。出力費用・実圧縮ログは省略。 |
| Table 1 / §4.5 | lab.yaml / results.jsonのpaper | 対応差と探索した効果の著者報告。元試行表の再解析ではない。 |

公式コード：[著者がPDFで案内した公開先](https://github.com/YangzeLiu/what-does-a-harness-buy)。公開commit `3f0c13208c8b71eefcf7b764e2372ac7200c3117` の `analysis/paper_numbers.py`（exact_power / mde_pp_exact）と `reference_outputs/numbers.json` を読み、入力不一致率を照合した。公式スクリプト全体は実行していない。

公式の `data/trials.csv` は元試行表、`analysis/main_table.py` は有効試行の選択、`analysis/tab_a4_budget.py` はtoken分解に対応する。これらの課題別再集計は未実施。
