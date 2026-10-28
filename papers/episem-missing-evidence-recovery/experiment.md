### 同じ依頼を二つの世界で進める

これは実LLMではなく、5種類の**自作の決定論的方策**を動かす教材です。支払い・データ提供という名前も架空で、実送信や外部API呼出しはありません。両側の依頼とツールの形は同じです。禁止側だけ、許可条件の一つが偽になります。

<div id="episem-toy" class="ep-toy">
<style>
.ep-toy{padding:clamp(12px,3vw,24px);border:1px solid #91aaa7;border-radius:16px;background:#f4faf8;color:#173b38}.ep-controls{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,220px),1fr));gap:12px}.ep-toy label{display:block;font-weight:650}.ep-toy select{display:block;width:100%;max-width:100%;font:inherit;padding:8px;background:white;color:#173b38}.ep-toy button{font:inherit;min-height:44px;margin:6px 4px 6px 0;padding:8px 12px}.ep-twins{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.ep-world{padding:12px;background:white;border:1px solid #91aaa7;border-radius:8px;min-width:0}.ep-world li{overflow-wrap:anywhere}.ep-flow{border-left:4px solid #47817a;padding-left:12px}.ep-scroll{overflow:auto;max-width:100%}.ep-scroll table{min-width:630px}.ep-pill{display:inline-block;padding:3px 8px;background:#dcece8;border-radius:6px}.ep-toy code{overflow-wrap:anywhere}.ep-toy :focus-visible{outline:3px solid #a04712;outline-offset:3px}@media(max-width:600px){.ep-twins{grid-template-columns:1fr}}
</style>
<div class="ep-controls">
<label>自作task<select id="ep-task"><option value="0">支払い：critical 2個</option><option value="1">データ提供：critical 3個</option></select></label>
<label>隠すcriticalの組合せ<select id="ep-mask"><option value="1">金額が上限内だけを隠す</option></select></label>
<label>無関係な表示ラベル<select id="ep-irrelevant"><option value="0">残す</option><option value="1">隠す</option></select></label>
<label>環境<select id="ep-setting"><option value="SE">SE：通常readのみ</option><option value="RE" selected>RE：独立auditあり</option></select></label>
<label>自作方策<select id="ep-policy"><option value="visible">見えた禁止理由がなければ実行</option><option value="refuse">常に拒否</option><option value="execute">無条件で実行</option><option value="recover">回収してから判断</option><option value="single_audit">欠落criticalが1個のときだけ回収</option></select></label>
<label>回収型方策の順序<select id="ep-timing"><option value="before">判断前にaudit</option><option value="after">先に判断、後でauditを予定</option></select></label>
</div>
<p>「後でaudit」は失敗を調べるための順序変更です。先に見えている情報で判断し、commitまたは停止で終端に達すると、予定したauditは実行できません。SEにはauditがありません。</p>
<div><button type="button" id="ep-next">1ステップ進める</button><button type="button" id="ep-end">最後まで進める</button><button type="button" id="ep-reset">初期状態へ戻す</button></div>
<output id="ep-output" aria-live="polite"><p>初期例：金額が上限内かを隠すと、両世界の通常readは同じになります。見えた禁止理由だけで実行する方策は、禁止側でもcommitします。下のJavaScript版で経過を追えます。</p></output>
<noscript>操作にはJavaScriptが必要です。Pythonのrun.pyとresults.jsonには全480条件と集計を保存しています。常に拒否する方策はUCR 0・SBM 100%でも、SWSとPURは0です。</noscript>
</div>
<script src="../downloads/episem-missing-evidence-recovery/model.js"></script>
<script src="../downloads/episem-missing-evidence-recovery/interactive.js"></script>
