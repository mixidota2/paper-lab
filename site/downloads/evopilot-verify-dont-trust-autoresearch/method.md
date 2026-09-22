### 実験対象はtwo-towerとinteraction head

Video Deep Diveはseed動画の後に関連動画を探す面。model-based retrieval（MBR）はrequest towerとcandidate towerからANN affinityを作り、上位P件へcandidate-conditioned interaction headを適用し、最終K件を残す。Pはheadへ入る候補数、Kはretrieval出力数である。

two-towerとheadは共同学習した同じcheckpointに含まれる。headを推論時に切る比較は学習からheadを削除する比較とは違う。indexとcandidate embeddingは時間単位で更新するが、neural weightsを毎時再学習するという意味ではない。

### 実行手順と証拠の受理を分離する

versioned domain skillはconfig探索、small preflight、train→publish-for-evaluation→evaluateのDAGと再開手順を定義する。typed adapterが承認variantを具体的操作へ結ぶ。workerは隔離環境で実行し、verifierがartifactを読み、analystが仮説treeを更新、plannerが次round案を作る。人間が毎round承認する。

計画・変更・結果統合・修復はClaude Opus 4.7/4.8、限定されたread-only監視はClaude Haiku。これらは本文に記載されたagent modelであり、推薦modelのbackbone名ではない。各役割はpromptまたはhash、model alias、session、status等を記録する。

### 許された差分だけが実現したか調べる

round protocol Rはcommon base、data pin、evaluator、metric、必須terminal artifact、許可差分、停止条件を指定する。両runが成功し、artifactの実現値が仕様と一致し、非treatment部分が同等であることを確認。どれかが欠ければreject。人間のmetric意味確認を掛け合わせて初めてadmitする。

memoryにはevent ledger、過去結果、incident catalog、実験記述が残る。ただしmemoryのlessonは助言であり、検査として実装されるまでgateを代替しない。初期incidentを自動guardが検知したという読みは避ける。
