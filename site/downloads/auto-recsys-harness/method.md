### 待ち時間をまたぐ単位は会話ではなく実験の状態
実験は `ideating → implementing → validating → training → analyzing` を進む。training失敗からdebuggingへ分岐し、結果から次のideatingへ戻る。案ごとにstate fileを持たせる。別案は別々に進める。serverも段階も揃えなくてよい。共通baselineとtraining date rangeを揃えて比較する（§3、§5.2）。

中央memoryにはglobal registry、案別state、baseline履歴、append-onlyのexperiment history、案のbacklog、model別playbook、knowledge base、session trajectoryを置く。job IDやcommit hashも保存する。会話だけには残さない。案別の分離で影響範囲は狭まる。ただしglobal registryの競合は残る。

### skillは次の判断を教え、scriptは正確な状態を確定する
自然言語skillは各段階の目的、判断基準、escalation条件を説明する。LLMが次の操作を選ぶ。決定的scriptが入力と遷移前提を検査し、API操作やatomicな状態更新を行う。scriptの戻り値から次の判断へ進む。この分離がcognitive-procedural separationである（§2.2）。

知識には三つの寿命がある。model共通のorchestrator skillは研究の進め方を定義する。model固有のplaybookは主要file、configuration規則、validation command、submission recipe、dead ends、proven strategiesを持つ。案別stateにはその実験だけのcommit、job、validation結果、verdictを残す。手順と今回の値を分ける。

### 二つのループは異なる失敗を覚える
Execution Evolution Loopは「なぜjobが通らなかったか」を学ぶ。trajectoryから失敗の原因と修正、成功したtoolの順序、hardwareやpackageの条件をplaybookへ追記する。単にerror文字列を貯めるより、次の試行で何を避けるべきかを説明できる。

Idea Evolution Loopは「なぜ仮説が効かなかったか」を学ぶ。baselineとの差をpositive/neutral/negativeに分類し、構造化した教訓とともにhistoryへ追加する。次の提案はmodelのarchitecture・task heads・featuresと過去の結果を参照し、重複や既知の失敗を避ける。新モデルへ移すのは型だ。hardware条件などの内容は人と確認して埋め直す（§4.4–5）。

この論文の手法の中心は新しいNNや損失関数ではない。LLM名や対象モデルの具体的な設定は確認できず、式で能力を推定することもできない。図では状態の遷移と知識の更新先を明確にする。

### sessionが落ちても成果物を探して続ける
新sessionはregistryとactive ideaのstateを読み、前sessionのtrajectoryから経緯を復元する。training中ならremote jobをpollし、次の処理へ進む（§6.2）。§7.3の事例では別serverのcheckoutに元commitがなくても、stateに保存されたdraft diffを共有review systemから取得して続行した。ログに何をしたか書くだけでなく、コード成果物へ到達できることが復旧の条件になる。

research_botの批評として、atomic writeは単一更新の途中破損を防いでも、複数writerのlost updateを自動的に防がない。所有権移譲、冪等なjob投入、baselineの版を含む比較条件を別途確認したい。

### human bandwidthとwall-clockを分けて測る
人の作業時間Hは、review・復旧などに注意を使った時間の和である。経過時間Wはqueueやtrainingの待ちを含む。以下は本Labの測定定義であり、原論文の数式ではない。

`H = Σ_j (review_minutes_j + recovery_attention_j)`

`W = max_j finish_time_j − min_j start_time_j`

非同期化はWや単位期間の完了件数へ、playbook成熟は主にHへ効く。ただし並列化が同じ未知の失敗を重複させる場合もある。toyではその費用を隠さない。

[AutoLR](autolr-dashen.html)のKEEPは採用した差分だけを次のtrunkへ反映する仕組みである。Auto-RecSysのpositive verdictを同じ採用保証と扱わない。次に試すなら、運用のzero-fix率と研究案の再測定成功率を別々に記録し、失敗の少ない実行が有益な探索につながったかを調べたい。

[一次資料：arXiv v1](https://arxiv.org/pdf/2609.10922v1)
