### 同じ依頼を、許可される側と禁止される側で試す

まず、仮想の支払いかデータ提供を選び、判断に使う事実のうち何を隠すか決めてください。左右に出す依頼と使える道具は同じです。ただし禁止側だけは実際には許可条件を一つ満たしていません。この教材は決められた5種類の判断規則を比べます。実際の言語モデル、データ送信、外部APIは使いません。

<div id="episem-toy" class="ep-toy">
<style>
.ep-toy{padding:clamp(12px,3vw,24px);border:1px solid #91aaa7;border-radius:16px;background:#f4faf8;color:#173b38}.ep-controls{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,220px),1fr));gap:12px}.ep-toy label{display:block;font-weight:650}.ep-toy select{display:block;width:100%;max-width:100%;font:inherit;padding:8px;background:white;color:#173b38}.ep-toy button{font:inherit;min-height:44px;margin:6px 4px 6px 0;padding:8px 12px}.ep-twins{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.ep-world{padding:12px;background:white;border:1px solid #91aaa7;border-radius:8px;min-width:0}.ep-world li{overflow-wrap:anywhere}.ep-flow{border-left:4px solid #47817a;padding-left:12px}.ep-scroll{overflow:auto;max-width:100%}.ep-scroll table{min-width:630px}.ep-pill{display:inline-block;padding:3px 8px;background:#dcece8;border-radius:6px}.ep-toy code{overflow-wrap:anywhere}.ep-toy :focus-visible{outline:3px solid #a04712;outline-offset:3px}@media(max-width:600px){.ep-twins{grid-template-columns:1fr}}
</style>
<div class="ep-controls">
<label>どの依頼を試すか<select id="ep-task"><option value="0">支払い：許可判断に関わる事実が2個</option><option value="1">データ提供：許可判断に関わる事実が3個</option></select></label>
<label>可否を決める事実のうち、どれを隠すか<select id="ep-mask"><option value="1">「金額が上限内か」を隠す</option></select></label>
<label>可否に影響しない表示ラベル<select id="ep-irrelevant"><option value="0">残す</option><option value="1">隠す</option></select></label>
<label>どの方法で確かめられるか<select id="ep-setting"><option value="SE">SE：通常の読み取りだけ</option><option value="RE" selected>RE：別の方法でも確かめられる</option></select></label>
<label>どの規則で判断するか<select id="ep-policy"><option value="visible">見えている情報に禁止理由がなければ実行</option><option value="refuse">常に拒否</option><option value="execute">無条件で実行</option><option value="recover">隠れた事実を確かめてから判断</option><option value="single_audit">重要な事実が1個だけ欠けたら照会</option></select></label>
<label>照会と判断の順番<select id="ep-timing"><option value="before">照会してから判断</option><option value="after">先に判断し、あとで照会する予定</option></select></label>
</div>
<p>先に判断する設定では、規則が実行を確定するか、実行せずに止まることを選ぶと、その時点で処理が終わります。あとで照会する予定でも実際には照会しません。REで照会と判断の順番を切り替えると、結果がどう変わるか比べられます。SEではどちらの順番を選んでも照会は使えません。</p>
<div><button type="button" id="ep-next">1ステップ進める</button><button type="button" id="ep-end">最後まで進める</button><button type="button" id="ep-reset">初期設定に戻す</button></div>
<output id="ep-output" aria-live="polite"><p>初期設定では「金額が上限内か」を隠しています。通常の読み取りだけでは、左右のどちらで支払ってよいかわかりません。それでも、見える情報に禁止理由がなければ進む規則を選ぶと、禁止側でも支払いを確定します。途中の動きを画面で追うにはJavaScriptが必要です。</p></output>
<noscript>操作にはJavaScriptが必要です。操作できない場合は、全480条件の集計を results.json で読むか、run.py で計算し直してください。常に拒否する規則は、禁止された操作をしませんが、許可側でも依頼を終えません。事実を回収してからの成功もありません（UCR 0・SBM 100%・SWS 0・PUR 0）。</noscript>
</div>
<script src="../downloads/episem-missing-evidence-recovery/model.js"></script>
<script src="../downloads/episem-missing-evidence-recovery/interactive.js"></script>
