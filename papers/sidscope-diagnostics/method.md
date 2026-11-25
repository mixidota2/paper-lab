### 出典と一緒に、商品とSIDの対応表を受け取る

入力の中心は、商品集合、商品とSIDの対応表、データの出典である。必要な診断に応じて、商品情報、利用履歴、更新前後の表、生成ログも受け取る。C0で出典、C1で形式、C2で商品の対応関係、C3で診断の実行、C4でハッシュと再実行、C5で比較における役割を確認する。資料が欠けていれば、確かめられる診断の範囲を狭める。

### 診断ごとに何を数えるか

| 診断 | 調べる対象 |
| --- | --- |
| D1・D5 | 使われた符号や先頭の符号列の数、割り当ての偏り、索引の分岐数など。D5の重複SID率は、異なるSIDが商品数に対していくつ足りないかを見る指標の一つ |
| D2 | 同じ完全SIDや、同じ先頭の符号列を持つほかの商品がある商品の割合 |
| D3 | 利用履歴で一緒に現れた商品対のうち、最初から指定の段まで符号が一致する対の割合 |
| D4 | 人気が高い、中間、低い商品の各群の商品数に対し、異なる完全SIDが何種類あるか |
| D6 | 更新前後に共通するitemのうちコードが変わった割合。「item」はここでは商品を指す |
| D7 | 生成した符号列が有効か、そこから商品を一つに特定できるか、古い符号や重複があるか |

<figure class="teaching batch21" data-b21="diagnostics"><h3>同じSIDの共有と、最初の符号のまとまりを別に調べる</h3><label>条件を選ぶ <select><option value="0">同じSIDを共有する表</option><option value="1">商品bだけに別のSIDを割り当てる</option></select></label><div data-output aria-live="polite"><div class="b21-cards "><div><strong>商品数</strong><p>6</p></div><div><strong>異なる完全SIDの数</strong><p>5</p></div><div><strong>D2 SIDを共有する商品の割合</strong><p>33.3%</p></div><div><strong>D5 重複SID率</strong><p>16.7%</p></div></div><div class="matrix-scroll" tabindex="0"><table><thead><tr><th>先頭からの段数</th><th>先頭の符号列の数</th><th>情報量（ビット）</th><th>D3</th></tr></thead><tbody><tr><th>1</th><td>3</td><td>1.459148</td><td>0.833</td></tr><tr><th>2</th><td>5</td><td>2.251629</td><td>0.0</td></tr></tbody></table></div><p>モデルを引き続き使えるかは未検証（NOT TESTED）。SIDを直しても、旧モデルが正しい商品を取得するとは限らない。</p></div><script type="application/json" data-frames>["<div class=\"b21-cards \"><div><strong>商品数<\/strong><p>6<\/p><\/div><div><strong>異なる完全SIDの数<\/strong><p>5<\/p><\/div><div><strong>D2 SIDを共有する商品の割合<\/strong><p>33.3%<\/p><\/div><div><strong>D5 重複SID率<\/strong><p>16.7%<\/p><\/div><\/div><div class=\"matrix-scroll\" tabindex=\"0\"><table><thead><tr><th>先頭からの段数<\/th><th>先頭の符号列の数<\/th><th>情報量（ビット）<\/th><th>D3<\/th><\/tr><\/thead><tbody><tr><th>1<\/th><td>3<\/td><td>1.459148<\/td><td>0.833<\/td><\/tr><tr><th>2<\/th><td>5<\/td><td>2.251629<\/td><td>0.0<\/td><\/tr><\/tbody><\/table><\/div><p>モデルを引き続き使えるかは未検証（NOT TESTED）。SIDを直しても、旧モデルが正しい商品を取得するとは限らない。<\/p>", "<div class=\"b21-cards \"><div><strong>商品数<\/strong><p>6<\/p><\/div><div><strong>異なる完全SIDの数<\/strong><p>6<\/p><\/div><div><strong>D2 SIDを共有する商品の割合<\/strong><p>0.0%<\/p><\/div><div><strong>D5 重複SID率<\/strong><p>0.0%<\/p><\/div><\/div><div class=\"matrix-scroll\" tabindex=\"0\"><table><thead><tr><th>先頭からの段数<\/th><th>先頭の符号列の数<\/th><th>情報量（ビット）<\/th><th>D3<\/th><\/tr><\/thead><tbody><tr><th>1<\/th><td>3<\/td><td>1.459148<\/td><td>0.833<\/td><\/tr><tr><th>2<\/th><td>6<\/td><td>2.584963<\/td><td>0.0<\/td><\/tr><\/tbody><\/table><\/div><p>モデルを引き続き使えるかは未検証（NOT TESTED）。SIDを直しても、旧モデルが正しい商品を取得するとは限らない。<\/p>"]</script><figcaption>run.pyが使う架空の6商品の例。D2は同じSIDを共有する商品をすべて数え、D5はitem数から一意のleaf数を引いた差を、それぞれ全item数で割る。ここでのitemは商品、leafはSIDの符号列全体を指す。論文の評価データではない。</figcaption></figure>

### D3を別の表と比べる前に、商品対の選び方をそろえる

D3(k)=Σᵢⱼ wᵢⱼ 1[prefixₖ(cᵢ)=prefixₖ(cⱼ)] / Σᵢⱼ wᵢⱼ。先頭からk段まで符号が一致した商品対の重みを足し、全商品対の重みで割る。比べる表どうしで、利用履歴から商品対を選ぶ条件と、先頭から何段まで見るかをそろえる。

[論文初版](https://arxiv.org/html/2608.18779v1)の公開CLIの既定値は、商品ごとの近傍数m=20、1人あたりの最大商品数U=200、商品対の上限B=2,000,000。表4はm=5、U=50、B=10,000で計算した。条件が違うため、どちらの数値か分けて読む。

### 生成ログでは、残った符号と取得できた商品を別に数える

D7では、生成した符号が索引にない場合、古い符号の場合、同じ商品や符号が重複した場合、複数の商品に対応する場合を分ける。正解の符号が候補に残ったことと、その符号から正解の商品だけを取れたことも区別する。論文の表6では、これら二つの率はどちらも正解を指定した探索記録で割る。一方、曖昧な符号の割合は候補の行数で割る。
