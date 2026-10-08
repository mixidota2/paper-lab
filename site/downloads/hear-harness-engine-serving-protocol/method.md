### 4種類のメッセージ

Harness→EngineのExecution Description and Intentは、役割、準備完了、依存関係、文脈の寿命、明示的に予測とした再利用予定を伝える。Execution Requirements and Controlは、待機制約、保持・準備・解放、実行構成を要求する。

Engine→HarnessのState and Capabilitiesは、KVの所在、queue、資源圧力、対応操作を返す。Execution Outcomesは、accepted、completed、rejected、unsupported、failedと実際の構成・再利用・費用を返す（Table 1）。

Table 2のmessage forceは4対ある。説明は命令ではない。希望はbest effort、要件は実行の制約。状態観測は予約保証ではない。受理は完了ではない。満たせない要件は拒否するか、明示的に許された代替を使う。

### 方策は2つの時間粒度で動く

Eq.1の`dᵢ=π(hᵢ,sⱼ)`は、harness情報hと最新の関連engine状態sから実行を決める。jとiは同時刻とは限らない。cache-aware方策では連続する再利用可能prefixが50%以上ならhotとし、再利用block数の多い要求を優先する。Guard-WはW秒待った要求を保護し、後続hot要求の追い越しを止める。完了時刻をW以内に収める保証ではない。

MooncakeのSession-Awareは別の保持方策で、完了済み会話から推定した継続確率pとidle時間を用いて`r=p exp(−idle/400)`で保持優先度を決める。意図を保持命令とは扱わない。

役割別選択は`{vLLM, OmniKV} × {vLLM, H2O, SnapKV}`の6構成を開発時に測る。品質・安定性の条件を通した後、makespanが小さい組を凍結する。BrowseComp-Plusは(vLLM,H2O)、DeepResearchBenchは(OmniKV,H2O)。正式評価の結果から後付けで選ばない。
