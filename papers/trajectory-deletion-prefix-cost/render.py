from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import run
import yaml
p=Path(__file__).resolve().parent
intro='''合成実験：まず初期状態で、延べ入力が減っても費用が増えることを確認する。次に割引を0%へ変え、順位がどう変わるかを見る。削除位置を後ろへ動かすと、再利用できる先頭部分が長くなる。再取得を足すと、読取り結果だけでなく追加呼出しの出力も課金される。これらは仮定した記号列の計算であり、モデルの成功率を予測しない。

'''
choices=[('discount','再利用入力の割引率',[(0,'0%（通常入力と同額）'),(.5,'50%'),(.9,'90%（論文の単価比）'),(1,'100%（再利用は無料）')],.9),('position','削除するターン',[(0,'T1（先頭寄り）'),(1,'T2'),(2,'T3（後ろ寄り）'),(3,'削除なし')],1),('timing','削除する通常呼出し',[(2,'2回目（対象が存在する最初まで待つ）'),(4,'4回目'),(6,'6回目')],4),('retrieval','削除直後の追加読取り（仮定）',[(0,'追加しない'),(2,'2トークン取得＋1出力'),(4,'4トークン取得＋1出力')],0)]
widget='''<style>
#deletion-toy{background:#f5faf8;padding:18px;border:1px solid #8b9e99;border-radius:12px;max-width:100%;color:#162d29}#deletion-toy label{display:block;margin:12px 0}#deletion-toy select{display:block;width:100%;font:inherit;padding:8px;white-space:normal}#deletion-output{display:block}.deletion-ledger{overflow-x:auto;max-width:100%}.deletion-ledger table{min-width:640px;table-layout:auto}.tokens{display:flex;flex-wrap:wrap;gap:3px;min-width:200px}.token{padding:2px 4px;border:1px solid #62776e;font-size:12px}.cached{background:#c4e9d5}.rebilled{background:#ffd4a0}.new{background:#e7e9ed}
</style><div id="deletion-toy"><h3>自作のトークン台帳</h3>'''
for id,label,options,default in choices:
 widget+=f'<label>{label}<select id="deletion-{id}">'+''.join(f'<option value="{v}"'+(' selected' if v==default else '')+f'>{s}</option>' for v,s in options)+'</select></label>'
s=run.scenario()
widget+=f'''<button type="button" id="deletion-reset">初期条件へ戻す</button><output id="deletion-output" aria-live="polite"><p>削除なし {s['baseline']['total']:.2f} ／ 削除あり {s['changed']['total']:.2f} 費用単位</p></output><noscript>条件変更にはJavaScriptが必要です。初期条件は割引90%、T2を4回目に削除、追加読取りなし。初期費用は上に表示しています。全条件の台帳はresults.jsonで確認できます。</noscript></div>'''
widget+='<script type="application/json" id="deletion-data">'+json.dumps(run.results(),ensure_ascii=False,separators=(',',':'))+'</script><script>'+ (p/'interactive.js').read_text()+'</script>'
end='''

### この実験だけの仮定

先頭のS1・S2と、各ターン4個の記号が入力になる。T1〜T3のうち一つから中央2記号を1回だけ削る。削除前後の通常呼出しは各6回、出力は各2記号。選んだターンがまだ存在しなければ削除を待つ。T1を4回目に削除する例ではT2とT3を保持し、論文の2ターン保持を説明できる。ただしtoyは全ターンへ順次適用する著者の介入ではない。

追加読取りは、削除直後にR記号を取得する呼出しを1回挿入する仮定。出力1記号と取得した入力、その後の再送を加算する。再取得の量や生起確率を論文から推定していない。削除注記や要約生成の費用も省いている。1記号＝1人工トークンであり、文章の文字数やモデル固有tokenizerとは対応しない。 各入力内の人工IDはすべて異なる。橙色と再課金数は、この一意なIDが前回の後続部分に含まれるかで判定する。繰り返し現れる実tokenizerの値への一般的な対応付けではない。一方、接頭辞の長さは集合ではなく、先頭から順序どおりに値を比較して求める。
'''
(p/'experiment.md').write_text(intro+widget+end)
lab=dict(id='trajectory-deletion-prefix-cost',title='The Hidden Costs of Forgetting: A Study of Trajectory Deletion in Software Engineering Agents',authors=['Fernando Vallecillos-Ruiz','Islem Bouzenia','Michael Pradel','Leon Moonen'],year=2026,arxiv_id='2610.35496',submitted='2026-10-26',topics=['ai-agents','ml-systems'],urls={'paper':'https://arxiv.org/html/2610.35496v1','arxiv':'https://arxiv.org/abs/2610.35496','pdf':'https://arxiv.org/pdf/2610.35496v1'},verdict='Worth Reading',status='draft',question='履歴を短くしたのに、なぜ入力の費用が増えるのか',summary='削除したトークン数だけでは費用を判断できない。先頭から一致する部分の再利用、最初の変更以降の再課金、情報を探し直す呼出しを分け、合成のトークン台帳で差額を追う。',verification=dict(mechanism='PARTIAL',performance='NOT TESTED',scaling='NOT TESTED',production_applicability='NOT TESTED'),source_review={'checked':'2026-10-27','url':'https://arxiv.org/html/2610.35496v1','scope':'HTML §I–IX・Tables I–III。Figshareの軌跡と分析コードはNOT OBSERVED。'},core_idea={'author_claim':'履歴削除の評価には、解決課題数だけでなく再取得・実行長・接頭辞キャッシュを含めた費用が必要。','research_bot_interpretation':'Worth Reading：保持トークン削減と再課金、情報回収の負担を切り分ける実験設計が役立つ。キャッシュ無効化の初発見という評価ではない。'},sections={'overview':'2026年10月26日公開のv1を扱う。著者の測定と、自作の決定論的な記号列の計算を分けて読む。','problem':'長い作業履歴から古い出力を消せば、次の入力は短くなる。しかし元の履歴をそのまま送れば安い単価で再利用できた部分まで、書き換えによって通常単価になる場合がある。','method':'method.md','why_it_might_work':'推論：費用を新規入力・再利用入力・出力に分解すれば、どこを削るかと、何を取り直すかを別々に比較できる。成功率が同じかどうかは、この会計実験だけでは分からない。','evidence':'evidence.md','executable_understanding':'experiment.md','results':'reportedは原典の主要集計、syntheticは144条件の自作台帳。入力削減と費用削減を別々に読む。','what_we_verified':'計算命題の確認範囲はREADMEとテストを参照。MechanismはPARTIAL：完全一致の接頭辞と費用の関係だけを扱い、実際のKVキャッシュを動かさない。','what_we_did_not_verify':'Performance / Scaling / Production applicabilityはNOT TESTED。実レイテンシ、キャッシュの失効・追い出し、最小prefix長、書込み割増、成功率、実請求は未検証。公式軌跡はNOT OBSERVED。あらゆる圧縮方式・プロバイダーで損になるとは言えない。','implementation':'READMEのuvコマンドで144条件を再生成する。自作Pythonが計算し、JavaScriptは条件選択と表示を担当する。外部通信や実モデルの実行はない。'},figures=[],interactives=[])
lab['teaching_figures']=[dict(id='prefix',kind='timeline',title='同じ文字列が残っていても、先頭の変更で再課金される',after='method',source=lab['urls']['paper'],locator='§II-C・Fig. 1',rationale='一致はトークンの集合ではなく順序付きの先頭部分で決まる。',caption='自作の模式図。最初の相違より後ろは再利用できず、変更後の履歴を次回そのまま伸ばすと再利用が戻る。',rows=[{'label':'変更前','nodes':[{'title':'S → T1 → T2 → T3','text':'前回の入力'}]},{'label':'変更時','nodes':[{'title':'S → T1','text':'先頭から一致：再利用単価'},{'title':'T2′ → T3 → T4','text':'最初の相違以降：通常単価'}]},{'label':'次の呼出し','nodes':[{'title':'S → T1 → T2′ → T3 → T4','text':'変更後の列が一致すれば再利用'},{'title':'T5','text':'新規入力'}]}]),dict(id='cost',kind='equations',title='削減した入力と、再利用を失った入力を分ける',after='method',source=lab['urls']['paper'],locator='§III-C・VI-B',rationale='出力を落とさず全費用を数える。',caption='論文の課金規則をこのLabで数式化。単位は相対費用であり通貨ではない。',steps=[{'name':'各呼出し','formula':'C_t = (n_t − c_t) + q c_t + 5 o_t','explanation':'qは再利用入力の価格比。割引90%ならq=0.1。'},{'name':'全実行','formula':'C = Σ_t C_t','explanation':'再取得が増やした呼出しと出力も合計する。'}])]
(p/'lab.yaml').write_text(yaml.safe_dump(lab,allow_unicode=True,sort_keys=False))
