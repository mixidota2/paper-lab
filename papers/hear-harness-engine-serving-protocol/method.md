### 4種類のメッセージ

Harness→EngineのExecution Description and Intentは、役割、準備完了、依存関係、文脈の寿命、明示的に予測とした再利用予定を伝える。Execution Requirements and Controlは、待機制約、保持・準備・解放、実行構成を要求する。

Engine→HarnessのState and Capabilitiesは、KVの所在、待ち行列、資源の混雑状況、対応操作を返す。Execution Outcomesは、受理（accepted）、完了（completed）、拒否（rejected）、未対応（unsupported）、失敗（failed）と実際の構成・再利用・費用を返す（Table 1）。

Table 2は、メッセージが相手に何を求め、何を保証するか（message force）を4対で整理する。状態の説明を送っても、操作を命じたことにはならない。希望は可能な範囲で応じるbest effortだが、要件は実行時に守る制約となる。また、状態の観測結果は資源の予約を保証せず、要求の受理も処理の完了を意味しない。満たせない要件は拒否するか、明示的に許された代替を使う。

### 方策は2つの時間粒度で動く

Eq.1の`dᵢ=π(hᵢ,sⱼ)`は、harness情報hと最新の関連engine状態sから実行を決める。jとiは同時刻とは限らない。cache-aware方策では先頭から連続する再利用可能な部分（prefix）が50%以上ならhotとし、再利用できる保存単位（block）の多い要求を優先する。Guard-WはW秒待った要求を保護し、後続hot要求の追い越しを止める。完了時刻をW以内に収める保証ではない。

MooncakeのSession-Awareは別の保持方策で、完了済み会話から推定した継続確率pと処理していない時間（idle）を用いて`r=p exp(−idle/400)`で保持優先度を決める。意図を保持命令とは扱わない。

役割別選択は`{vLLM, OmniKV} × {vLLM, H2O, SnapKV}`の6構成を開発時に測る。品質・安定性の条件を通した後、全体が完了するまでの時間（makespan）が小さい組を凍結する。BrowseComp-Plusは(vLLM,H2O)、DeepResearchBenchは(OmniKV,H2O)。正式評価の結果から後付けで選ばない。
