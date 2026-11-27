求めるのは毎回3日目の在庫です。最初の在庫は2個で、変えるのはいつまでに届いた報告を使うかだけです。下の表には、到着後に内容が訂正された報告も含めました。

| 出来事ID | 版番号 | 商品が動いた日 | 報告が届いた日 | 報告の内容 |
| --- | ---: | ---: | ---: | --- |
| A | 1 | 1日目 | 1日目 | 需要5個 |
| C | 1 | 3日目 | 3日目 | 需要1個 |
| B | 1 | 2日目 | 4日目 | 入荷4個 |
| A | 2 | 1日目 | 5日目 | 需要を1個に訂正 |
| C | 2 | 5日目 | 6日目 | 発生日を5日目に訂正 |

将来の予定はどの条件でも同じです。4日目に需要3個、5日目に入荷2個、6日目に需要1個とします。Cの訂正版で発生日が5日目になっても、それを将来予定へ追加しません。過去の報告と、この先に起きると仮定した予定は別の入力です。

<div class="teaching" aria-label="いつまでの報告を使ったかで在庫を比較">
<details name="bitemporal-cutoff" open data-cutoff="2"><summary>受領の締切を2日目にする</summary><p>使えるのはAの初版だけです。3日目のCと、2日目の入荷を知らせるBはまだ届いていません。</p><p>採用した報告：Aの第1版</p><dl><dt>3日目の在庫</dt><dd>0個</dd><dt>3日目までの売り逃し</dt><dd>3個</dd><dt>6日目の最終在庫</dt><dd>1個</dd><dt>将来の売り逃し</dt><dd>3個</dd><dt>4日目以降で最初に売り逃しが出る日</dt><dd>4日目</dd></dl><table><caption>同じ予定を適用した後の各日の在庫と売り逃し</caption><thead><tr><th scope="col">日</th><th scope="col">予定</th><th scope="col">処理後の在庫</th><th scope="col">その日の売り逃し</th></tr></thead><tbody><tr><th scope="row">4日目</th><td>需要 3個</td><td>0個</td><td>3個</td></tr><tr><th scope="row">5日目</th><td>入荷 2個</td><td>2個</td><td>0個</td></tr><tr><th scope="row">6日目</th><td>需要 1個</td><td>1個</td><td>0個</td></tr></tbody></table></details>
<details name="bitemporal-cutoff" data-cutoff="4"><summary>受領の締切を4日目にする</summary><p>LabはA、B、Cの初版を発生順に並べます。2日目に入った4個から、3日目の需要1個を引きます。</p><p>採用した報告：Aの第1版、Bの第1版、Cの第1版</p><dl><dt>3日目の在庫</dt><dd>3個</dd><dt>3日目までの売り逃し</dt><dd>3個</dd><dt>6日目の最終在庫</dt><dd>1個</dd><dt>将来の売り逃し</dt><dd>0個</dd><dt>4日目以降で最初に売り逃しが出る日</dt><dd>なし</dd></dl><table><caption>同じ予定を適用した後の各日の在庫と売り逃し</caption><thead><tr><th scope="col">日</th><th scope="col">予定</th><th scope="col">処理後の在庫</th><th scope="col">その日の売り逃し</th></tr></thead><tbody><tr><th scope="row">4日目</th><td>需要 3個</td><td>0個</td><td>0個</td></tr><tr><th scope="row">5日目</th><td>入荷 2個</td><td>2個</td><td>0個</td></tr><tr><th scope="row">6日目</th><td>需要 1個</td><td>1個</td><td>0個</td></tr></tbody></table></details>
<details name="bitemporal-cutoff" data-cutoff="6"><summary>受領の締切を6日目にする</summary><p>Aは訂正版で需要が1個になり、Bの入荷を足します。Cは訂正版の発生日が5日目なので、3日目の計算から外します。古い版のCも使いません。</p><p>採用した報告：Aの第2版、Bの第1版</p><dl><dt>3日目の在庫</dt><dd>5個</dd><dt>3日目までの売り逃し</dt><dd>0個</dd><dt>6日目の最終在庫</dt><dd>3個</dd><dt>将来の売り逃し</dt><dd>0個</dd><dt>4日目以降で最初に売り逃しが出る日</dt><dd>なし</dd></dl><table><caption>同じ予定を適用した後の各日の在庫と売り逃し</caption><thead><tr><th scope="col">日</th><th scope="col">予定</th><th scope="col">処理後の在庫</th><th scope="col">その日の売り逃し</th></tr></thead><tbody><tr><th scope="row">4日目</th><td>需要 3個</td><td>2個</td><td>0個</td></tr><tr><th scope="row">5日目</th><td>入荷 2個</td><td>4個</td><td>0個</td></tr><tr><th scope="row">6日目</th><td>需要 1個</td><td>3個</td><td>0個</td></tr></tbody></table></details>
</div>

Labはこの例の報告と予定を作り、三つの締切に同じ計算を適用しました。モデルや予測は使っていません。配布した `run.py` を実行しても同じ結果が得られます。
