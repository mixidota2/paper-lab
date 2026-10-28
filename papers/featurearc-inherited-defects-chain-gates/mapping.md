# 原典と自作実装の対応

原典：https://arxiv.org/html/2610.37434v1 。v1 submitted 2026-10-27 15:45:50 UTC。2026-10-28にHTMLの§I–VIII、Tables I–IVと図キャプションを確認。PDFのページ画像や著者実行artifactは未確認。

| 対象 | 原典 | このLabの対応・境界 |
| --- | --- | --- |
| 同じ状態を引き継ぐ | §II-B | `edit`は同一dictを更新。gateは入力に渡さずrollbackしない |
| F2P/P2Pの区別 | §III-D | `F2P`, `P2P`, `CHAIN`, `BASE`の固定期待値を`execute`で検査。正解referenceの前後状態でも検証 |
| 段階と最終のAND | §II-B・IV-D | `simulate`のstage/chain gate。chainは最終状態への別suite |
| 分母 | §IV-D・V-A | `metrics`, `ratio`。継続・回復・最終段階合格後の全体失敗を区別 |
| 主要集計 | §III-F・Table III・V-A | reported欄。69/273を再計算。原実行の追試ではない |
| 継承・見逃し | Table IV・§IV-B・V-B/C | 72.9%と94.9%の分母を本文で明示 |
| 合格した自己テストの期待値が誤る | §V-C | `WRONG_SELF`の固定誤期待値と`F2P`を別定義 |
| 教材独自の修正 | 原典の介入実験ではない | 第3段階でinclusive/signedを直す固定編集。著者の修復策や因果推定にしない |

stage P2Pは既存動作の有限な標本で、以前の全suiteの和集合ではない。chain F2Pは以前の追加要求も調べ、chain P2Pは最初からある合計の負値を調べる。この検査範囲の差を明示した自作設計であり、著者の個別taskを写したものではない。
