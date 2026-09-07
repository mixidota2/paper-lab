比較対象は **ReAct、Planner-Actor-Rater（PAR）、Planner-then-Executor** の3構成。同じモデルで役割を分け、Inspect AI上でGAIA validationのLevel 1・2を解く。PARは計画・実行・評価を反復し、Planner-then-Executorはツールを使わない計画を作ってから、新しいプロンプトで実行へ渡す。

モデルはClaude Opus 4.7、Sonnet 4.6、Haiku 4.5、Gemini 3.1 Pro Preview、GPT-5.5。論文ではreasoning設定を有効にしていない。各問題を3回試行し、公式scorerで採点する。これは新しいNNの提案ではなく、モデルと実行構成を掛け合わせる比較実験だ。

注意したいのは統制の範囲。ReActは既定のweb_browserを使うが、PARとPlanner-then-Executorはweb_searchを使う。観測差にはツール面の違いも含まれる。エラーを含めるprimary、特定のSDK不具合を除くrobust、共通問題に絞るintersectionも区別して読む。

[一次資料：方法と実験条件](https://arxiv.org/html/2606.08529)
