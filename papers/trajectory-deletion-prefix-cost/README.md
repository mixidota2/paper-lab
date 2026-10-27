# 履歴を短くしても、安くなるとは限らない

arXiv 2610.35496v1を理解する日本語Lab。自作の記号トークン列で、削除位置から後ろの再課金と、追加読取り・出力の費用を追う。著者の9,400実行を再現するものではない。

```bash
uv run --locked python papers/trajectory-deletion-prefix-cost/run.py
uv run --locked pytest -q tests/test_deletion_cost.py
uv run --locked pytest -q -ra --fail-on-skip
uv run --locked paper-lab build
```

計算部分は標準ライブラリだけを使う。run.pyはcompact results.jsonと操作画面を再生成し、render.pyは既存依存のPyYAMLを使う。ブラウザーは計算済み144条件を表示する。実モデル・外部API・認証・送信は使わない。

Mechanism PARTIAL、Performance / Scaling / Production applicability NOT TESTED。公式データはNOT OBSERVED。原典と実装の対応はmapping.md、仮定はexperiment.mdを参照。実ブラウザー・目視の確認は数値テストと別に必要。
