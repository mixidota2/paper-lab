# Trial by Trace：二層採点の自作教材
原典 arXiv:2610.32285v1。作者実装の再現ではありません。

`uv run --locked python papers/trial-by-trace-evidence-boundaries/run.py` で64条件を再生成。配布ディレクトリでは `uv run --no-project python run.py`。Node.jsが必要です。依存やブラウザを自動インストールしません。

成果2状態×基盤4状態×3チェック欄の2状態=64条件。モデル呼出し・乱数なし。各層第2項目を合格で固定し、第1項目だけ操作します。一般の複数候補関係APIではありません。

CONFIRMED：この限定例の計算と操作イベント。PARTIAL：原典規則との対応。NOT TESTED：原著実験再現、実ブラウザ、読み上げ、因果伝播。測定チェック欄は仮定です。
