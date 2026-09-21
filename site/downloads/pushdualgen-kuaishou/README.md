# PushDualGen: Enabling LLMs to Generate Semantic IDs with Interpretable Copy for Industrial Push Recommendation

Qwen3-0.6BがSID→任意copyを生成し、Top-20 SIDsの表現を既存user特徴へ融合する。pushの14日A/BでEPR +8.50%、Dislike Rate −37.70%。

優先度: Watch。確認日: 2026-09-21。

## 実行

```sh
uv run papers/pushdualgen-kuaishou/run.py
uv run paper-lab build
```

## Overview

PushDualGenはKuaishouのpush通知向け推薦で、先にSID、その後に任意のcopyを生成する。14日間、platform trafficの計15%を均等に割り当てたA/Bで、Effective Play Rateは+8.50%、Dislike Rateは−37.70%。feed全体を生成器へ置き換えた実験ではない。

## Problem

クリックの先で、期待に応えられるかが問題になる。長い履歴を文字で入力し、候補を決める前に説明文まで生成すると、通知の内容を選ぶための計算と待ち時間が増えてしまう。クリック履歴だけでは全嗜好を表せないため、生成したSIDを既存のオンライン特徴へ融合する。

## Core Idea

parallel SIDで履歴を圧縮し、SID-firstの二段生成でcopyをskip可能にする。生成信号と既存user特徴を融合してANN検索へ渡す。

解釈: 追加の生成経路を既存推薦へ接続する点で[LIGE-GR](lige-gr-meta-listwise.html)と比較できる。ただし変更場所はpushの候補表現であり、列内の順序最適化ではない。

## モデル / 手法

[method.md](method.md) の図と数式を読む。

## Why It Might Work

SIDを先に生成すれば、説明を見たい場面だけcopyを続けられる。推論で省略できても、学習時のcopy損失はSIDを意味に結び付ける補助信号になりうる。ただし、後から出た文章はモデルがその動画を選んだ因果的理由の証明ではない。既存user表現と融合するので、push clickだけにない行動信号も残せる。

## Evidence

一次資料の著者報告。

[原典 §4・Tables 1–2](https://arxiv.org/html/2608.07989v1)。計15%のtrafficを等分し、約150M usersを含む14日間の比較。CUPEDを使い、主要4指標はp<0.05と報告される。

| 指標 | control → treatment | 相対差 |
| --- | --- | ---: |
| Click PV | 82.04M → 82.39M | +0.43% |
| DAU | 414.89M → 415.08M | +0.05% |
| Effective Play Rate | 64.46% → 69.94% | +8.50% |
| Dislike Rate | 0.053% → 0.033% | −37.70% |

EPRの絶対差は+5.48 percentage points。−37.70%は小さなdislike率の相対変化で、不満の全種類が37.70%減ったという測定ではない。DAUの集計値と約150Mの割当usersについて、本文だけでは集計母数の関係を十分に特定できないため、人数へ換算しない。

SID Pass@20はfull 0.422、SID adaptationなし0.366、parallel SIDなし0.401。これはオフラインSID予測で、copy省略だけのオンライン因果効果は報告されていない。

## Executable Understanding

有限の履歴→SID→copy頻度モデルで、同じ履歴からcopy on/offを実行する。SID不変と出力単位削減を確認し、別の3動画の内積検索でuser-onlyとuser+SIDを比較する。Qwen学習や通知文の品質を擬似的な精度値で代用しない。

## Results

以下はこのLabの実行結果。上のEvidenceに載せた著者報告のA/Bとは、データも評価対象も異なる。

## What We Verified

Mechanism PARTIAL。2つの履歴条件でcopyを省略しても先行SIDが変わらない。固定ベクトルの融合で候補順が変わることを確認した。文字単位のstep数は説明用で、壁時計の高速化率ではない。

## What We Did NOT Verify

Performance / Scaling / Production applicabilityはNOT TESTED。Omniの圧縮学習、parallel K-means、Qwen3のadaptationとSFT、ANN recall、copyの忠実性、通知の頻度制御、A/Bは未再現。原典§6にcopy then SIDという記述があるが、§3.2の式と結論はSID then copyで一致するため、ここでは後者を採用した。

## Implementation

`decode()`は経験頻度でSIDを選んだ後にcopyを選ぶ。`rank(beta)`はEq. 7の融合を内積全探索で例示する。ANN indexは省略。

Python標準ライブラリだけで実行する。乱数を使う実験はseedを固定し、結果をコードと同じ場所に保存する。

## Original Paper / Official Code Mapping

[mapping.md](mapping.md)
