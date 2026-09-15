### Orchestratorが状態を持ち、専門agentには必要な情報だけを渡す

Ideatorが仮説を作り、Criticが実行前に批評する。承認された案をCoding Agentが実装し、Orchestratorがjobの投入と結果を管理する。専門agentは独立した長期記憶を持たない。Knowledge Base、優先度付きHypothesis Backlog、過去の結果を呼出しごとに注入する。[§3.2–3.3](https://arxiv.org/html/2609.01622v1#S3)

共有filesystemにはglobal stateを、実験threadには分離したworkspaceを置く。実験の仕様、批評、job IDを含むmanifest、分析を残す。この構造は論文の仕組みであり、このLabの実行で別agentを起動することはない。

### KEEPは評価の通過、rollbackは状態の復元

Algorithm 1は基準モデルを監査して主指標ΦNSと補助指標ΦAuxを抽出し、baseline τを確立する。候補の事前検証に失敗すればVCS rollback。分散jobが失敗すればlogを分析してKnowledge Baseを更新し、rollbackする。成功後に主指標の改善幅と補助指標を判定し、両方を満たせばVCS commitとKEEPの記録へ進む。

KEEPは名前付きの採択記録であり、rollbackと同義ではない。後者は不採択・失敗の変更を戻す動作である。また本番配信への全自動承認をAlgorithm 1が証明しているわけでもない。

### Two-Towerで発見されたのは損失・表現・収束の改良

Idea 2でcontrastive lossのtemperatureを学習可能にし、Idea 6でquery依存へ進める。Idea 18はWatch-Time Weighted Contrastive Loss、Idea 23はlog重みからwatch_time⁰·⁵へ変更する。Idea 20のDCN V2はuser towerの明示的な特徴交差、Idea 36のGated Denseは表現容量、Idea 40のCosine Decayは収束を変える。これらの実コード・全ハイパーパラメータは公開本文だけでは再構成できない。[§5.1、5.5](https://arxiv.org/html/2609.01622v1#S5)

### 8k→1kで、正例が競争する相手が減る

in-batch negativesではbatch内の別itemが負例になる。batch縮小で評価の候補数も縮むと、同じ正例scoreでも上位へ入りやすい。論文の別sessionではこの抜け道をagentが見つけ、人間が検出した後にrollbackした。図と実験ではscoreを固定することで、学習を伴わなくても起こる効果を切り出す。

Labの次の実装案は、候補ID集合・評価データ版・指標式・学習budgetをmanifestへ保存し、比較前に照合すること。候補数が同じでも難しさは変わり得るため、件数だけの監査は最小の一歩にすぎない。これは著者の実装を確認した記述ではなく、読書からの提案である。
