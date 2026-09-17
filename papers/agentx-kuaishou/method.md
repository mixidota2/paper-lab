### 四段階に異なる証拠を要求する

Brainstorm（§4）は過去実験、architecture、データ分析、外部研究から仮説を作り、変更可能性と重複を検査する。Developing（§5）はrepositoryの実装規約と依存関係に沿ってpatchを作り、コンパイル、動作、dry-run、実験投入契約を確認する。Evaluation（§6）は段階的に配信し、観測窓を満たしたA/Bを評価する。

KEEPには最小効果量、有意性、許容できるguardrailのすべてが必要。判定recordは `verdict, primary_effect, guardrail_status, statistical_method, observation_window, caveats` を持つ。重大な悪化はblock、中程度は人の例外審査、観察用指標はmonitoringとする。単一指標が少し悪化したら必ずDISCARDする設計ではない。複数の事業指標を合わせた経済価値の交換指標も使う（§6.3）。

失敗recordには原因、pipeline段、目的、segment、変更leverを付け、次のBrainstormから検索可能にする。EXTENDは観測不足・不確実性を保持するために必要であり、KEEPの弱い言い換えではない。

### SGPOは数値勾配でモデルを訓練する手法ではない

§7.1、式7–9。評価agentがtraceとrubricから自然言語の診断gを作り、refinement agentが対象subagentのharness hをh′へ局所更新する。

`(loss_text, g) = Evaluator(h, traces, rubrics)`

`h′ = Refiner(h, g)`

`admit(h′) ⇔ mean[J(h′, task)−J(h, task)] > ε AND Safe(h′−h)`

新旧harnessを同じreplay tasksで評価する点が重要だ。SGPO-Iはsession trace、SGPO-IIは過去MRをrequirement-only taskに変えたcoding replayを使う。後者は答えのpatchを実行agentから隠す。schema、tool境界、人のreview条件を壊す更新は採用しない。学習済みLLMの重み更新や、オンラインA/Bの代替ではない。

### funnelの分母を固定する

表5・式10は `374 → 106 → 100 → 10`。案→review通過、通過→code/launch、launch→LRという条件付き比率である。表の丸め値9.9%を、整数10/100の10%と完全一致させるために改変しない。10/374は約2.67%で、別のAutoML poolのfunnel（§8後半）とは混ぜない。

出典：[2606.26859v2](https://arxiv.org/pdf/2606.26859v2)。上記で「Lab」とした式・条件は説明用の補助である。


<figure class="teaching batch17"><h3>同じ主効果でも、採用判定は変わる</h3><div class="matrix-scroll" tabindex="0" role="region" aria-label="比較表"><table><thead><tr><th>条件</th><th>判定の方向</th><th>残す情報</th></tr></thead><tbody><tr><td>主効果・有意性・guardrail通過</td><td>KEEP</td><td>効果、窓、統計手法</td></tr><tr><td>観測不足・不確実</td><td>EXTEND</td><td>延長理由と残る不確実性</td></tr><tr><td>重大な副作用</td><td>DISCARD / hard block</td><td>影響segmentと失敗原因</td></tr><tr><td>中程度のguardrail警告</td><td>人の例外審査</td><td>交換条件と承認の根拠</td></tr></tbody></table></div><figcaption>§6.3–6.4。中程度の警告を自動DISCARDにしない。下の実験では審査待ちをEXTENDで表す。</figcaption></figure>
