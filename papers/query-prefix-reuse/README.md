# ReuseGR：検索語の計算をどこまで共有するか

検索・推薦の仕組みを読む人向けの理解実験です。prefix（コードの先頭部分）の共有範囲と、現在の履歴で変える範囲を分けます。最初にmethod.mdの機構と自作規則を読み、生成Labの合成木、Table 5の投影、Table 1の指標を操作してください。原モデルの学習・推論を再現する教材ではありません。

一次資料は[ReuseGR v1](https://arxiv.org/html/2611.04259v1)。HTMLの§3〜5、Eq.3、Tables1/5、Appendix Aの履歴条件とC/Dを読解しました。PDF全画素・公式実装・生ログは未監査です。

## 再実行

このディレクトリで `uv run run.py` を実行するとresults.jsonを再生成します。外部データや第三者コードを実行しません。リポジトリでは `uv run pytest -q -ra --fail-on-skip tests/test_reusegr.py` で専用検査を行います。全サイトのビルドと静的preflightはルートREADMEの現行手順に従い、未使用の出力先を指定してください。

## 計算APIの契約

Pythonの`toy(prepared=True, depth=1, query='wide', history='left', budget=4)`とJavaScriptの`ReuseGR.toy(...)`は同じスカラー入力を受け付けます。preparedは真偽値のみ、depthは0〜3の整数、budgetは0〜8の整数。queryはwide/narrow、historyはleft/rightです。整数位置へのbool、文字列、配列、null、NaN/Infinity、範囲外は拒否します。`projection(p)`は有限数0〜1のみ。Python/JSの同等性はこの共通領域で検査します。任意配列を渡すAPIはありません。

内部の候補集合は固定の非空16葉から作り、平均で割る可変分母はありません。budget=0の空ランキングは有効です。不正入力は例外にし、NaNをJSONのnullへ変えて保存しません。出力はJSONで再計算できます。prepared d=0とcoldは、数値が一致する場合も経路識別を保ちます。

## 根拠と限界

CONFIRMEDは自作の入力境界・経路・到達可能性・採点と採用の順序、および公表値の算術検算です。MechanismはPARTIAL。学習済みモデルと商用ログはNOT OBSERVED、原実験の再現・性能・スケーリング・実務適用はNOT TESTEDです。Nodeの代用DOMは実ブラウザーではありません。実画面幅、実ブラウザー保存、日本語lintは未実施として記録します。

prepared経路は7Bのtop1 coarse codeで履歴を絞り、baseline/coldはlogged query-match maskを使います。他のcomponentも同時に変わるため、全差をprefix共有だけの効果にしません。商用ログは非公開で、現代LLMの二塔対照もありません。query付き検索広告の結果を無queryのfeedへ一般化できません。

疑問が残る場合はmapping.mdで一次節と自作コードの対応を確認してください。用語：Qは準備済みquery数の割合、Pは準備済みlogged rowsの割合、HRは1件以上の正解を得たqueryの割合、Recallはqueryごとの全正解の回収割合です。
