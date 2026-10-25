# TRACE：点数の変化を、行動と採点器に分ける

Radhika Gaonkar, *TRACE: Diagnosing Verifier Brittleness in Agentic Evaluation*, [arXiv 2610.11678v1](https://arxiv.org/html/2610.11678v1)（2026-10-08公開）を対象とした自作Lab。

在庫8を5へ直す小さな決定的スクリプトを使う。正しい操作を別名で呼ぶと、意図的に名前へ依存する採点器だけが減点する。同じ記録を正規化して再採点すると回復する。本当に書込みを省いた行動失敗は、再採点しても失敗のまま残る。いつも失敗するスクリプトも用意し、差の小ささと高い成功率を区別する。

## 再実行

```bash
uv sync --extra dev --frozen
uv run papers/trace-verifier-brittleness/run.py --test
uv run papers/trace-verifier-brittleness/run.py
# 既存出力が削除されるため、毎回新しい専用の出力先にする
uv run python -m paper_lab.build --root . --out /tmp/paper-lab-trace-review
uv run python -m http.server --directory /tmp/paper-lab-trace-review 8000
```

`/papers/trace-verifier-brittleness.html` を開く。3スクリプト×名前2条件×採点2条件の12通り、初期化、キーボード操作、hashの詳細表示を確認する。360・390・768・1440pxの幅とJavaScript無効時も確認する。全papers/を入力し、限定したビルドで既存サイトを上書きしない。

run.pyは標準ライブラリのみで単体実行可能。results.jsonとexperiment.mdを再生成する。公開報告値はreported、人工軌跡はsyntheticに分離する。ブラウザーは計算済みの12条件を表示し、採点式を重複実装しない。著者のコード、未知のスクリプト、モデルAPIは実行しない。

## 確認範囲

- CONFIRMED：名前だけの変更なら正規の操作列と状態hashが同じ。再採点が記録を変えず、点数だけが戻る。本当の行動失敗は残る。
- PARTIAL：論文の診断手順の最小例を表現。採点式と仕事は自作であり、原実験の再現ではない。
- NOT OBSERVED：公開コードでStudy 2/3対応のアーカイブを確認できなかった。
- NOT TESTED：論文のモデル性能、LLMの再実行ノイズ、実運用への一般化、判定の正確性。

## 出典とライセンス

論文は **CC BY-NC-SA 4.0**。出典：[Radhika Gaonkar, TRACE, v1](https://arxiv.org/abs/2610.11678v1)。原論文の図版や本文を大量に転載せず、このLabの文章・図は独自の在庫修正例と読解メモとして制作した。論文のライセンスをサイトの既定ライセンスへ変更するものではない。公式コードは読む対象として参照し、コピーしていない。論文のFig 1・2、Tables 6・8を読むための対応はmapping.mdに記載する。

## 通常テストと実ブラウザーでの検査

`tests/test_trace_lab.py` がrun.pyの4件の数値・不変性テストを通常のpytestから収集する。生成したresults.jsonとexperiment.mdが保存版に一致することも検査する。

```bash
uv sync --locked --extra dev --python 3.12
uv run --locked pytest -q -ra --fail-on-skip
uv run --locked paper-lab build --out /tmp/paper-lab-trace-105
uv run --locked python tests/review_103.py --preflight \
  --site /tmp/paper-lab-trace-105 --out /tmp/trace-preflight-new
```

最新mainの104件を保持し、TRACEを加えた105件をビルドする。出力先は毎回新しいパスにする。事前検査はブラウザーを起動しない。`tests/test_trace_integration.py` は実際のインラインJavaScriptをNodeで動かし、12条件と初期化を検査するが、DOMの代用品を使うため画面・キーボード操作の検証ではない。

実ブラウザー検査は既存のPR macOS Chrome reviewから実行する。`tests/review_103.py` が署名・loopback CDP・Seatbeltを確認したChromeで、`tests/trace_review.py` の検査を呼ぶ。360・390・768・1440pxの各幅で12条件の点数・操作列・hash・棒の幅、初期化、キー操作を検査し、JavaScript無効時の初期表示も確認する。全サイトの内部リンク検査と、TRACE専用の必須検査を独立レポート判定に含める。

旧 `tests/browser_trace.py` のLinux起動は使わない。以前のsandbox無効での48条件の結果は、今回の合格証拠にしない。保護確認に失敗した場合は停止し、設定・権限の変更や別の起動経路で回避しない。ローカルの数値・JavaScript・事前検査の成功と、macOS実ブラウザーの成功は別々に記録する。外部リンクの到達性、全文の目視、公開URLの版一致も別の確認事項である。
