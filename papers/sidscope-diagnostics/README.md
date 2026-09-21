# SIDScope: A Diagnostic Resource for Semantic-ID Interfaces in Generative Recommendation

SIDScopeは利用率・衝突・prefix整合・更新・生成traceを診断する資源。trie内の有効pathと一意item取得を区別し、mapping修復後のcheckpoint再利用を別途検証する。

優先度: Watch。確認日: 2026-09-21。

## 実行

```sh
uv run papers/sidscope-diagnostics/run.py
uv run paper-lab build
```

## Overview

SIDScopeは、item→SID対応表を受け取ったときに使う診断資源である。利用率、衝突、prefixの行動整合、人気別の解像度、trie構造、更新差、生成traceを分ける。オンラインA/Bはない。公式v1.0.1にはadapter、固定結果、CPU verifierがある。

## Problem

trieで有効なSIDを生成しても、そのSIDが複数itemを指していれば正解itemを一意に取れない。逆に衝突ゼロでも、prefixに行動上の近さがなければ探索の手掛かりになりにくい。対応表を更新して欠損を埋めても、旧checkpointが新しいコードの意味を知るとは限らない。

## Core Idea

source-traced mappingを共通contractへ正規化し、D1–D7でaddressability、prefix exposure、refresh、traceを診断する。D3の予測力はprefixを使う機構に条件付けられる。

解釈: [QuaSID](quasid-collision-qualified-sid.html)と合わせ、衝突を減らす設計と、衝突や更新の影響を受け入れ時に点検する手順を分けて蓄積したい。[SnapLGR](snaplgr-snapchat.html)のSID→動画展開にも直結する。

## モデル / 手法

[method.md](method.md) の図と数式を読む。

## Why It Might Work

[QuaSID](quasid-collision-qualified-sid.html)の衝突を条件付きで評価する発想を、tokenizerを受け入れ、更新し、generatorへ渡す作業へ広げられる。D3がよい理由を「prefixを実際に候補探索に使うから」と限定すれば、診断から次の実験を選びやすい。全generatorのNDCGを予測する万能scoreにすると、原典が示す適用範囲を超える。

## Evidence

一次資料の著者報告。

[原典 Tables 4–7・§8](https://arxiv.org/html/2608.18779v1)。8つの実行可能なrouteと追加のauditable snapshotを区別する。異なるcatalog・depthの行をtokenizer順位表として扱わない。

D3とprefix candidate recallの相関は8 exportsでρ=0.976。ただしcatalog単位の5群で集計するとρ=0.900、exact p=0.083。学習済みSID generatorのNDCGとの相関は−0.564〜0.205で安定せず、prefix診断から本番品質への一般化は確認されていない。

constrained beamではGRID/P5のpath survival 6.4%に対してunique-item hitは3.4%（差3.0pp）。別foldは5.0%対3.0%、DIGERは6.6%対5.4%。1.2–3.0は相対%ではなくpercentage pointsである。

DACT 0.6→0.7では275 itemのSID欠損を埋めたが、共通9,610 itemの23.6%のコードが変わった。旧modelのnew-item Recall@20は0のまま。適応学習3 seedは宣言したhandoff gateを通った。旧itemのmapping-only差の区間は0をまたぐため、「mapping更新が品質を悪化させることを証明」とはしない。

## Executable Understanding

`run.py`はJSONの実対応表を読み、prefix使用数・entropy・衝突item率・重複SID率・任意の重み付きpair整合・旧mappingとのchurnを計算する。既定は説明用6 itemで、公式benchmarkとは別。CLIでは任意の実mapをそのまま診断できる。

```sh
uv run papers/sidscope-diagnostics/run.py --mapping map.json --previous old.json --pairs pairs.json --out /tmp/my-diagnostics.json
```

mapは `{"item-a":[0,1],"item-b":[0,2]}`、pairsは `[["item-a","item-b",3]]`。D3の近傍抽出は外で済ませる。popularityがないのでD4はNOT TESTED、traceがなければgenerator品質も出さない。

既定実行は公式MIT公開の12 item mapにも独立診断を適用する。公式quickstartは別途実行済みで、確認値とhashを`official-check.json`、利用条件を`NOTICE.txt`に保存した。

## Results

以下はこのLabの実行結果。上のEvidenceに載せた著者報告のA/Bとは、データも評価対象も異なる。

## What We Verified

Mechanism PARTIAL。6 item中2 itemが同じleafに入るとD2=2/6、D5=1/6になること、pathが有効でも曖昧な場合はunique-item hitにならないことを確認した。固定depthと非負整数codeを検査し、input hashを保存する。公式v1.0.1のreviewer quickstartを実行し、preflight passedとD1–D5出力を確認。公開12 item入力のleaf数11、D2=2/12、D5=1/12、prefix数3/6/11は独立実装と一致した。これは本番mappingではない。

## What We Did NOT Verify

Performance / Scaling / Production applicabilityはNOT TESTED。公式の全route、125,000 trace、4,999 bootstrap、学習済みgeneratorのhandoff、online A/Bは再現しない。独立実装の範囲は一部の診断に限る。D4や公式の近傍抽出・provenance admissionは省略する。

## Implementation

`validate()`はmapの形式、`diagnose()`はprefix/leafの集計、`trace()`はSID→itemの曖昧性を扱う。公式packageのimport名は互換性のため`sidinspector`のまま。公式の関数対応とrelease hashはmapping.mdに記録する。

Python標準ライブラリだけで実行する。乱数を使う実験はseedを固定し、結果をコードと同じ場所に保存する。

## Original Paper / Official Code Mapping

[mapping.md](mapping.md)
