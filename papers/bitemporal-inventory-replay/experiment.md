同じ3日目の在庫を求めます。最初の在庫は2個です。受領の締切を変えて、どの報告が過去の計算に使われるか、将来の結果がどう変わるかを見比べてください。

| 報告 | 版 | 発生日 | 受領日 | 内容 |
| --- | ---: | ---: | ---: | --- |
| A | 1 | 1日目 | 1日目 | 需要5個 |
| C | 1 | 3日目 | 3日目 | 需要1個 |
| B | 1 | 2日目 | 4日目 | 入荷4個 |
| A | 2 | 1日目 | 5日目 | 需要を1個に訂正 |
| C | 2 | 5日目 | 6日目 | 発生日を5日目に訂正 |

将来は4日目に需要3個、5日目に入荷2個、6日目に需要1個があると仮定します。Cの発生日を5日目に訂正しても、この将来予定にCを追加しません。過去の報告と将来予定は別の入力です。

<div class="teaching" aria-label="受領締切を変えて在庫を比べる">
<details name="bitemporal-cutoff" open data-cutoff="2"><summary>2日目までに届いた報告を使う</summary><p>報告Aの初版だけを使います。BとCは締切までに届いていません。</p><p>採用した報告：Aの第1版</p><dl><dt>3日目の在庫</dt><dd>0個</dd><dt>過去の売り逃し</dt><dd>3個</dd><dt>6日目の最終在庫</dt><dd>1個</dd><dt>将来の売り逃し</dt><dd>3個</dd><dt>最初に将来の売り逃しが出る日</dt><dd>4日目</dd></dl><table><caption>固定した将来予定を適用した結果</caption><thead><tr><th scope="col">日</th><th scope="col">予定</th><th scope="col">処理後の在庫</th><th scope="col">その日の売り逃し</th></tr></thead><tbody><tr><th scope="row">4日目</th><td>需要 3個</td><td>0個</td><td>3個</td></tr><tr><th scope="row">5日目</th><td>入荷 2個</td><td>2個</td><td>0個</td></tr><tr><th scope="row">6日目</th><td>需要 1個</td><td>1個</td><td>0個</td></tr></tbody></table></details>
<details name="bitemporal-cutoff" data-cutoff="4"><summary>4日目までに届いた報告を使う</summary><p>A、B、Cの初版を発生順に適用します。2日目に入荷し、3日目に1個を販売します。</p><p>採用した報告：Aの第1版、Bの第1版、Cの第1版</p><dl><dt>3日目の在庫</dt><dd>3個</dd><dt>過去の売り逃し</dt><dd>3個</dd><dt>6日目の最終在庫</dt><dd>1個</dd><dt>将来の売り逃し</dt><dd>0個</dd><dt>最初に将来の売り逃しが出る日</dt><dd>なし</dd></dl><table><caption>固定した将来予定を適用した結果</caption><thead><tr><th scope="col">日</th><th scope="col">予定</th><th scope="col">処理後の在庫</th><th scope="col">その日の売り逃し</th></tr></thead><tbody><tr><th scope="row">4日目</th><td>需要 3個</td><td>0個</td><td>0個</td></tr><tr><th scope="row">5日目</th><td>入荷 2個</td><td>2個</td><td>0個</td></tr><tr><th scope="row">6日目</th><td>需要 1個</td><td>1個</td><td>0個</td></tr></tbody></table></details>
<details name="bitemporal-cutoff" data-cutoff="6"><summary>6日目までに届いた報告を使う</summary><p>Aの訂正版とBを使います。Cは訂正後の発生日が5日目なので、3日目までの計算から外します。</p><p>採用した報告：Aの第2版、Bの第1版</p><dl><dt>3日目の在庫</dt><dd>5個</dd><dt>過去の売り逃し</dt><dd>0個</dd><dt>6日目の最終在庫</dt><dd>3個</dd><dt>将来の売り逃し</dt><dd>0個</dd><dt>最初に将来の売り逃しが出る日</dt><dd>なし</dd></dl><table><caption>固定した将来予定を適用した結果</caption><thead><tr><th scope="col">日</th><th scope="col">予定</th><th scope="col">処理後の在庫</th><th scope="col">その日の売り逃し</th></tr></thead><tbody><tr><th scope="row">4日目</th><td>需要 3個</td><td>2個</td><td>0個</td></tr><tr><th scope="row">5日目</th><td>入荷 2個</td><td>4個</td><td>0個</td></tr><tr><th scope="row">6日目</th><td>需要 1個</td><td>3個</td><td>0個</td></tr></tbody></table></details>
</div>

この例の報告と予定はLabが作りました。モデルや予測は使わず、同じルールで3ケースを計算しています。配布した `run.py` でも結果を確認できます。
