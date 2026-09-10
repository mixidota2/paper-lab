### 変更したパスと、実際に読んだパスを照合する
workflow を DAG G=(V,E) とし、artifact ごとに版番号を持つ。読み取り selector (a,p,c) は artifact、内部のパス、data/control の区別を記録する。revision e=(a,v,v+1,op,Δ) は変更されたパス集合 Δ を運ぶ。古い版への revision は受け入れない。

構造化された状態を read-only proxy で包み、フィールド参照では leaf path、列挙では集合の `#members` を記録する。親子のパスは重なりとして扱い、要素の追加・削除はその集合の membership 読み取りと照合する。直接の読者から現在有効な子孫へ影響を伝播する。

```text
Direct = {n : Δ intersects (Rdata(n) ∪ Rcontrol(n))}
Affected = Direct ∪ active descendants(Direct)
reuse(x) ⇒ valid(x) ∧ effectSafe(x)            原典 Eq. (1)
```

最初の2式は Lab の整理である。原典 §3.2 の記述を集合で表した。依存が不明な読者は保守的な集合に入れ、再計算範囲を広げる。

### 完了・実行中・未着手では、取り消す操作が違う
無効な実行中の呼び出しは cancel、未着手なら avoid、必要な処理を新しい版で recompute する。有効性を示せる実行中の枝は continue、完了済みは reuse。許可は暫定である。

### 公開する直前に、最終的な読み取り履歴を検査する
変更が来た時点ではまだ読んでいなかった値を、後から読む場合がある。revision 時点だけの判定ではこの late read を見落とす。実行は immutable snapshot を使い、次の証明書を蓄積する。

```text
Cx = (id, vstart, Rdata, Rcontrol, P, mode)      原典 Eq. (2)
```

P は親 attempt の識別子、mode は complete/coarse/unknown。commit では開始後の全変更と最終的な read set を照合し、親が現在の committed attempt か確かめる。revision と commit は同じ lock で直列化する。外部への作用は検査が通るまで staged のまま保持する。不可逆な作用や証拠の欠落は明示的な処理または停止を必要とする。[一次資料：§3](https://arxiv.org/html/2609.00643)。
