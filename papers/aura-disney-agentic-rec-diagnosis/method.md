### まずsessionを選び、失敗の分類を作る

Session selectionはrandom・stratified・engineer SQL・agent提案を組み合わせる。複数提案をdedupし、多数決でcohortを選ぶ。platformを必須parameterとして全段階へ渡し、data source、schema、promptの差を設定へ分ける。LLMが自由に本番DBを書き換える構成ではない。

診断の実装は6段階。Classificationがsessionへ分類と短い説明を付け、Consolidationが似たcategoryを統合。Samplingで大きいcategory・十分な件数・一定割合を残し、safety-criticalは閾値を迂回する。Analysisがbounded sampleを読み、証拠とroot-cause hypothesisを作る。Verificationがsampleとの整合とseverityを見直し、Synthesisが横断的な優先順位をまとめる。

原典のseverityは出現頻度の段階であり、一件当たりの危害の大きさではない。この区別をしないと、まれな年齢不適合が軽い問題に見える。割合のみの≥5%規則ではBの5分類のうち2つしか残らなかった。

### 高価な推論は圧縮後へ回す

Gemini 3 Flashが大量分類・統合、Gemini 3.1 Proが分析・検証・要約、Claude Opus 4.6がcode提案を担う（Table 5）。決定的なorchestratorがroutingする。rubricを採点するmodelと実際の作業modelを区別する。

Hypothesis stageはranker code、feature、label、training、schemaを参照し、変更箇所へ仮説を結び付ける。これは形式的な因果推論ではない。Code stageは生成→別model評価→修正を回し、最後にpath/importの実在をprogrammaticに検査する。session IDも入力に存在するか調べ、parse失敗をdata-quality flagとして残す。

### 現行の到達点と将来の自動化を分ける

現行はreviewed PRまで。mergeからtrainingを開始する部分と、offline評価からA/B-ready artifactを作る部分は拡張中。論文のgenre修正はoffline screeningの実例であり、全loopが無人運転している証拠ではない。engineerは最終段階だけでなく各段階で証拠を読み、仮説を却下できる。
