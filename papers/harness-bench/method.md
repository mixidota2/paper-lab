Harness-Benchは **106タスク × 6ハーネス × 8モデル** の比較設計。OpenClaw、NanoBot、Hermes、ZeroClaw、NullClaw、Moltisを、同じ初期ファイル・予算・時間制限・評価器で動かす。モデル群はClaude Opus 4.6、Sonnet 4.6、Gemini 3.1 Pro Preview、Qwen3.6 Plus、GLM-5.1、Kimi K2.5、GPT-5.4、DeepSeek V4 Flash（付録B）。各ハーネス固有のプロンプトや復旧方法は保持するため、個々の機能の因果効果を測る設計ではない。

成果物はタスク固有の検査器またはrubricで採点し、実行履歴の評価には固定の **claude-sonnet-4.6** を使う。完了度、許可違反の有無、実行過程の品質を掛け合わせるのが特徴だ。Codex（本文ではGPT-5.4）は106件を別枠で評価し、8モデル平均のハーネスと混ぜない。

最終点だけでは、未完了だったのか過程の評価が低かったのか分からない。下の式を分解してから報告値を見る。

[一次資料：方法と実験条件](https://arxiv.org/html/2605.27922)
