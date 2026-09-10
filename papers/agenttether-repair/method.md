### TUは一回の判断と、その結果を結ぶ
`TU_k = (o_k, b_k, a_k, f_k)`

oは観測、bはbeliefとしての推論、aはツール名と引数または応答、fは実行feedbackである。SDKへのbefore/after hookから取得したtraceを、この単位へまとめる。Critical Transition Graph（CTG）は実行順の辺と、共有artifactやerror signatureに基づく依存の辺を持つ。直前のTUだけが原因候補になる構造ではない（§III-B–C）。

### 学習済みの正常像と、実行内の外れ値を併用する
正常像を先に学ぶ。Heterogeneous Graph Transformer（HGT）は外部の成功軌跡21,143件から、TUとその周囲のspan、metric、log、verificationなどを型つきノードとして読み、telemetryの辺の復元と、隠されたtoolやstatusなどの属性予測を通じて正常な関係を学習する。推論時にはその二種類のsurpriseを平均し、scoreの最大の落差で異常候補を切る。τ-benchの履歴を学習する設定ではなく、外部の成功軌跡を用いる。

実行内の外れ値も探す。Isolation Forestには、TUの入出次数などの構造、実行状態とfeedbackの不整合、同じ部分目標やツール群を共有する連続区間のエラー比率など、一つの実行から抽出した25次元の特徴を渡す。二つの検出結果は別の証拠面として保持し、その和集合を局所的な証拠へ絞る。診断LLMは依存を逆にたどり、根本原因、回復可能な経路から外れた転換点、回復のヒントを返す。

実験設定はHGT hidden dimension 52、20 epochs、batch 128、Isolation Forest 100 trees、最大sample 256。補助の診断・検証・評価役はDeepSeek-V4-Proに固定し、修復されるエージェントと分ける。モデル名と設定は原典§IV-Aの記載であり、本LabはAPIを呼ばない。

### 診断を、その場で使える小さな修正へ変える
Repair Memoryはfixed/unresolvedを次の試行へ運ぶ。指示は失敗した操作の種類や制約を示すが、正解の引数をそのまま渡す設計ではない。初回は観察だけ。失敗してから修復へ入る。

| 段階 | 判断すること |
| --- | --- |
| Check | 同じ呼び出しの反復、意図からの逸脱、期待する修正の未実施、忘れた指示 |
| Decide | 証拠とactive guidanceがあるか、cooldownや回数上限に触れないか、最小の介入か |
| Inject | tool resultへ追記するか、text responseに対してsynthetic user messageを入れて再開するか |

意図逸脱はembeddingの非類似度で測り、破壊的操作は閾値0.35、通常0.50、情報取得0.55。高リスク候補はLLM verifierが確認する。tool-return側では5stepの指数移動平均（α=0.3）を使う。修正完了後は介入を止め、期待した状態変更の後はloop以外の介入を抑える。これらは誤検出の被害を抑える規則であり、成功の保証ではない（§III-D、§IV-A）。

### REVISEとは、回復のきっかけと根拠が違う
[REVISE Lab](revise-recovery.html)は実行途中の指示変更を受け、どの計算結果が最新版でも有効かを追う。AgentTetherは失敗した行動を診断し、次の試行での逸脱を抑える。前者の再利用に必要な妥当性証拠と、後者のLLMを含む診断の確からしさは同じ保証ではない。この対比はresearch_botの整理で、両手法の直接比較実験はない。

[一次資料：§III–IV、Figure 4](https://arxiv.org/html/2607.06273)。
