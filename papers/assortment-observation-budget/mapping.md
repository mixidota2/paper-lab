# 原典と実装の対応

| 原典 | 自作コード | 範囲 |
| --- | --- | --- |
| §2 MNL・最終品揃え後悔 | probabilities / revenue / oracle | 非購入1、既知収益、独立観測。oracleは降順のprefix最大 |
| §3 Theorem 3.1 / Corollary 3.2 | component_a | 全cutと同値を返す。有限subsetテストはsupremumの証明ではない |
| §5 Theorem 5.1 式(2)(3) | b_choice / component_b | (3a,2a,a)の最小分割(k,l)=(1,2)。二項分布の厳密和 |
| §6 Theorem 6.1 式(5)–(7) | c_choice / component_c | d=2、4単点群、丸め不要。2群を同数観測。余りの判断不使用 |
| Lab独自比較 | integrated_case / generate | 4選好・96条件。有限グリッドは一般minimaxを求めない |
| 画面 | interactive.js / paper_lab.assortment_observation | 保存平均値の表示と例示経路の規則。選好を方策へ渡さない |

§2–3、§5–6のモデル・方策・定理を正規Webで読解。§4は比較の文脈のみ。原文ファイルの取得失敗は未解消で、別経路で転送していません。著者表の再制作や本文の配布は行いません。
