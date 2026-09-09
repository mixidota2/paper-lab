### Councilは案を出し、controllerが状態を確定する
専門家は同じ凍結briefingを読み、互いの初稿を見ずに提案する。役割は構造、特徴相互作用、系列、多タスク、損失、業務知識、実装可能性など。roundtableで案を整理し、adversarial reviewで前提や実装リスクを反証し、Coordinatorが仮説・変更可能なfile:symbol・検証方法・保護指標を持つ候補へまとめる（§3.2）。

controllerは適格候補から多様性を保った有限windowを作り、その中をCouncilに順位付けさせる。window外の候補は選べない。過去の成功、期待改善、新規性、実現可能性、安定性、確信度、リスクを使うmemory gateを訓練前に通す。成功率の特徴量は `p̂ = (n_success+1)/(n_attempt+2)`。Beta(1,1)の疑似件数を使うが、posteriorからサンプルするThompson samplingではない（§3.3）。

知識は外部研究、稼働中システムの事実、DASHENの業務知識に分ける。試行後の設定・patch・ログ・失敗・指標は実験memoryへ蓄積する。役割ごとに必要な情報を取り出し、全記録を毎回文脈へ詰め込まない。

### KEEPだけが次の実験のtrunkを変える
現在のコードをT、候補patchをπとすると、`T_next = T ⊕ π` になるのはKEEP時だけ。PACKは候補と系譜を保持し、DISCARDは棄却する。保護指標を通り、オフライン差分Δsが閾値τ_keep以上ならKEEP_E1となる。E1は1回の測定で閾値を越えた意味で、確認済み効果ではない（式6–7）。

任意の分散調整は `τ_impl = max(τ_keep, λσ̂)` だが、監査対象ではノイズ校正が無効で、互換のある反復評価profileも保持されていなかった。profile不足で昇格を止めるCALIBRATION_REQUIREDは著者が提案する将来の防止策で、稼働していた状態ではない（式8、§6.1）。

[一次資料：arXiv v1 本文](https://arxiv.org/pdf/2609.04871v1)
