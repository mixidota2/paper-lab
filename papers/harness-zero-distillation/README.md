# Harness-Zero: Harness Distillation via Agent-as-Harness

Harness-Zeroは実行前の応答を別エージェントが点検し、採用された履歴でQwen3.5-9Bを学習する。最小harness下の平均成功率は23.3%から44.3%へ上がるが、すべての領域で外付けharnessを超えるわけではない。

## Core Idea — 主張と解釈

著者の主張：進化させたharnessの振る舞いを学習用履歴へ変換し、重みに蒸留する。推論時にはh★、私的な参照harness K、点検役を外し、最小のhだけで動かす。

Labの解釈：SWE-Serveが扱う実行条件の感度やFlashVectorの配信最適化、AURAの診断とは変更する対象が異なる。ここでの対象はモデルの重みと推論時に必要な支援の範囲である。本番配信のA/Bや運用費用削減の実証とは分けたい。

## Overview — 概要

Harness-Zeroは実行前の応答を別エージェントが点検し、採用された履歴でQwen3.5-9Bを学習する。最小harness下の平均成功率は23.3%から44.3%へ上がるが、すべての領域で外付けharnessを超えるわけではない。

## Problem — 問題設定

外付けharnessの道具・技能・記憶・実行制御が成功を支えていても、そのままの実行環境を常に配備できるとは限らない。点検役にしか使えない道具の呼出しを学生へ模倣させると、最小環境で実行できない。

## Why It Might Work — 解釈

解釈：点検後の応答を学生が使えるBash操作へ変換すれば、訓練と推論の行動空間を合わせやすい。手順の確認や結果の再読込は履歴から学べても、反応化学の知識や専用バリデータの機能までは同じ量のデータで移せるとは限らない。

## Evidence — 著者報告

一次資料[Tables 2・4](https://arxiv.org/pdf/2609.24974) の著者報告。値は成功率またはAppWorldの目標達成率（%）。

| 設定 | SpreadsheetBench | AppWorld | USPTO | マクロ平均 |
| --- | --- | --- | --- | --- |
| 基準モデル + h | 31.0 | 26.8 | 12.0 | 23.3 |
| 基準モデル + h★ | 39.0 | 48.2 | 38.0 | 41.7 |
| 蒸留モデル + h | 44.0 | 58.9 | 30.0 | 44.3 |

平均は21.0 pp改善し、h★付きも2.6 pp上回る。ただしUSPTOでは38.0%から30.0%へ下がる。harnessに固有な28行動パターンの平均回収率は82.3%で、28件中の整数の成功件数ではない。

## モデル / 手法

## PASSかREPLACEかを、実行前に決める

Figure 1の第1段階でKimi K3を使い、h★を進化させる。h★を私的な参照Kへ変換し、GPT-5.6 Solの点検役が参照する。学生はQwen3.5-9Bで、固定プロンプトとBash一つのmini-SWE-agent型hを使う。

式(3)では学生の提案yₜを実行前に点検する。PASSならỹₜ = yₜ、REPLACEならỹₜ = zₜとし、採用したỹₜだけをhで実行する。次の学生文脈へ入れるのは採用応答と実行結果で、棄却提案や私的な点検履歴は入れない。

式(4)の学習損失はL = −Σ log πθʰ(ỹₜ|cₜ)。点検役の視点で書かれた推論が置換応答に混じる場合、その部分は損失からmaskする。採用応答をすべて無条件に教師にする実装ではない。

論文では成功して終了した履歴をフィルタし、487 / 282 / 500本を各領域で使う。Qwen3.5-9Bへ2 epochのLoRA SFTを行い、推論時には学生とhだけを残す。下の実験は応答の採用と除外の契約を確認し、学習そのものは行わない。


## Executable Understanding — 最小実験

`uv run papers/harness-zero-distillation/run.py`。標準ライブラリだけで実行でき、同じフォルダーのresults.jsonを更新する。

collect()でPASSとREPLACEを切り替え、実行対象・学生に見える履歴・教師対象を表示する。入力はBash相当の操作名を示す文字列であり、実際のファイルを変更しない。nll()は採用応答の確率を0.2から0.8へ変えたときの損失だけを計算する。

## Results — 人工例の結果

REPLACE例では棄却したoverwrite workbookが教師対象から消え、backup workbook then edit cell A1だけが残る。負の対数尤度は約1.609から0.223へ下がるが、これは仮定した確率の算術であり、モデル学習による能力獲得ではない。

## What We Verified — 確認範囲

CONFIRMED：採用応答だけを実行・学生履歴・教師対象へ渡し、棄却提案を除く契約。MechanismはPARTIAL。

## What We Did NOT Verify — 未検証

Performance / Scaling / Production applicabilityはNOT TESTED。harness進化、LLMによる点検、推論文のmask、LoRA SFT、28行動の検出、本番配信は実行していない。点検役を外した後の能力保持も人工例では確かめていない。

## Implementation — 実装

collect() → 式(3)のPASS/REPLACEと学生可視履歴。nll() → 式(4)の1応答分の算術。重み更新と私的推論maskは省略。

## Original Paper / Official Code Mapping

[対応表](mapping.md)
