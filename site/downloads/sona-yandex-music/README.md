# Sona Technical Report

Sonaは8,192件の履歴を共有し、深い処理を直近2,048件へ集中する。My Vibeの各群15%・7日A/BでAU +4.53%。全流量展開とcatalog coverageは未解決。

優先度: Must Read。確認日: 2026-09-21。

## 実行

```sh
uv run papers/sona-yandex-music/run.py
uv run paper-lab build
```

## Overview

Sonaは候補生成・prerank・最終rankを、共有履歴encoder、SID decoder、Ranking Moduleを持つ一つの配信モデルへまとめる。My Vibeのスマートスピーカー面で、各群15%・7日間の最終A/BはActive Users +4.53%、Total Listening Time +6.30%。論文時点で全流量には展開しておらず、catalog coverage低下を課題としている。

## Problem

音楽では同じ曲を繰り返し聴くこと自体に価値があり、動画feedと同じ重複抑制は当てはまらない。次の曲を当てる生成尤度だけでは、likeや聴き続ける価値に沿う順序を作れない。一方、重いteacherを各requestに出すと配信コストが高い。長い履歴を保持しつつ、teacherの採点を軽いRanking Moduleへ移す必要がある。

## Core Idea

生成と順位を共有encoderで共同学習し、重いteacherの採点をRanking Moduleへ蒸留する。最終実験では推薦cascade全体を置換した。

解釈: [Gryphon-v2](gryphon-v2-cascade.html)で追った生成・順位の統合を、tokenizer、長期履歴、teacherの事前学習、オンライン更新の詳細まで示す報告。構成要素ごとのA/B寄与は限定して読む。

## モデル / 手法

[method.md](method.md) の図と数式を読む。

## Why It Might Work

古い履歴もmemoryに残せば、直近だけでは分からない嗜好を生成と順位の双方で使える。計算をrecentへ集中するのは、その情報を全層で混ぜ直す費用を避けるためだ。蒸留の候補をrolloutと実表示の両方にすれば、生成分布への追従とログに残る行動の両方を扱える。ただし、教師と一致することは利用者の満足度と一致することを意味しない。

## Evidence

一次資料の著者報告。

[原典 §7・Tables 7.6–7.12](https://arxiv.org/html/2608.11015v2) の著者報告。最終A/Bの相対差はAU +4.53%、聴取時間+6.30%、Likes +11.42%、Repeat commands +17.99%、Deeply Engaged Users +7.37%。最終表はすべてp<0.01。Repeatは発話等のコマンド指標で、一般的な曲の重複率ではない。

<figure class="teaching batch21"><h3>5つのA/Bは、段階を外せるかを別々に確かめる</h3><div class="matrix-scroll" tabindex="0"><table><thead><tr><th>実験</th><th>配信側の変更</th><th>各群の比率</th><th>読むべき差</th></tr></thead><tbody><tr><th>1</th><td>enc–dec + teacher、Likes重みを変更</td><td>5%</td><td>重みαのAU +1.83%</td></tr><tr><th>2</th><td>teacherへSID特徴を追加</td><td>4%</td><td>SIDありAU +2.23%</td></tr><tr><th>3</th><td>teacherでrankのみ / 生成も置換</td><td>3%</td><td>AU +1.22% / +2.72%</td></tr><tr><th>4</th><td>蒸留RM / さらにteacherでrerank</td><td>8%</td><td>AU +1.41% / +2.81%</td></tr><tr><th>5</th><td>8k + History Compression + RM</td><td>15%</td><td>AU +4.53%、7日</td></tr></tbody></table></div><figcaption>原典 Tables 7.8–7.12。すべて各実験のproduction control比。実験間の差を介入の因果効果とみなさない。</figcaption></figure>

[Gryphon-v2](gryphon-v2-cascade.html)のAU +1.41%は、この報告の実験4に対応する値で、最終Sonaとの直接対決ではない。実験4と5の差から「履歴だけで+3.12ポイント」とは結論できない。Argusに対する2.35倍も、過去のAU改善+1.93%との改善幅の比で、利用者数やモデル精度が2.35倍になったわけではない。

オフラインではimpressions onlyのTeacher Recall@10は0.2983、rollouts + impressionsは0.5654。2k・RMなしの0.0381から、4層RMでは0.6005へ上がる。8k full attentionは0.6586、History Compressionは0.6474で、完全に同じ精度ではない。WPAは圧縮版0.6033、full版0.6029。指標間で優劣が違う。

## Executable Understanding

解析的teacherを同じ線形studentへ蒸留し、impressions only、rollouts only、両source平均の和を比較する。学習で使わないrollout候補120件でMAEとpair accuracyを測る。別に履歴attentionの項数を計算するが、これは計算構造の比較で、論文の「約半分の推論費用」を再測定した値ではない。

## Results

合成条件では両sourceのpair accuracyは1.0、impressions onlyは約0.791。両sourceのMAEはrollouts onlyより大きく、全指標で勝ったとは言えない。impression側で一つの特徴が常に0という設計なので、その特徴の係数を学べない状況を意図的に作っている。

## What We Verified

Mechanism PARTIAL。候補分布を変えると、同じteacher・studentでも未使用候補との一致が変わることを確認した。2つのsourceで個別に平均を取り、Eq. §4.2どおり加算した。seedと訓練回数を固定した。

## What We Did NOT Verify

Transformer、Qwen tokenizer、残差量子化、NTPとの共有勾配、実catalog collision、45分の更新loopは未検証。Performance / Scaling / Production applicabilityはNOT TESTED。数カ月の長期効果、他の推薦面、catalog coverage回復も原典の未解決事項である。

## Implementation

`train()`は線形studentのMAE subgradient、`teacher()`は固定の解析式、`compute()`は未使用候補での比較。teacherが一年のログを学習する部分と、本番の二つのheadは省略した。

Python標準ライブラリだけで実行する。乱数を使う実験はseedを固定し、結果をコードと同じ場所に保存する。

## Original Paper / Official Code Mapping

[mapping.md](mapping.md)
