"""記号列で計算した結果と、対応する Lab のページを生成する。"""
from pathlib import Path
import json
import sys
import yaml

p = Path(__file__).resolve().parent
sys.path.insert(0, str(p))
import run
intro = ('初期設定の表では、2記号を消すと延べ入力が72から66に減る。ただし、再利用入力の割引が90%のときは、合計費用が87.00から87.30へ増える。割引を0%に変えると、削除した方が安くなる。次に削除位置と、追加の読み取りを変えて確かめられる。この作例は、固定した記号列を数えるだけで、モデルの成功率を予測しない。\n'
 '\n')

choices = [('discount',
  '再利用する入力の割引率',
  [(0, '0%（通常と同じ料金）'), (0.5, '50%'), (0.9, '90%（著者の推計で使った割引）'), (1, '100%（再利用は無料）')],
  0.9),
 ('position', 'どのターンから2記号を消すか', [(0, 'T1（前の方）'), (1, 'T2'), (2, 'T3（後ろの方）'), (3, '消さない')], 1),
 ('timing', '何回目の呼び出しで消すか', [(2, '2回目（まだ対象がなければ待つ）'), (4, '4回目'), (6, '6回目')], 4),
 ('retrieval',
  '消した直後に、追加で読む記号の数',
  [(0, '追加しない'), (2, '2記号を入力に足し、1記号を出力'), (4, '4記号を入力に足し、1記号を出力')],
  0)]

widget = ('<style>\n'
 '#deletion-toy{background:#f5faf8;padding:18px;border:1px solid '
 '#8b9e99;border-radius:12px;max-width:100%;color:#162d29}#deletion-toy '
 'label{display:block;margin:12px 0}#deletion-toy '
 'select{display:block;width:100%;font:inherit;padding:8px;white-space:normal}#deletion-output{display:block}.deletion-ledger{overflow-x:auto;max-width:100%}.deletion-ledger '
 'table{min-width:800px;table-layout:auto}.deletion-ledger th,.deletion-ledger '
 'td{width:96px}.deletion-ledger th:first-child{width:64px}.deletion-ledger '
 'th:nth-child(2),.deletion-ledger td:nth-child(2){width:320px;min-width:240px}.deletion-ledger '
 'thead th,.deletion-ledger tbody th,.deletion-ledger '
 'td:not(:nth-child(2)){white-space:nowrap;overflow-wrap:normal;word-break:normal}.tokens{display:flex;flex-wrap:wrap;gap:3px;min-width:200px}.token{padding:2px '
 '4px;border:1px solid '
 '#62776e;font-size:12px}.cached{background:#c4e9d5}.rebilled{background:#ffd4a0}.new{background:#e7e9ed}\n'
 '</style><div id="deletion-toy"><h3>Lab の作例：履歴を消す位置で費用はどう変わるか</h3>')

end = ('\n'
 '\n'
 '### 作例では何を固定したか\n'
 '\n'
 '元の入力は、先頭に S1 と S2 があり、呼び出しが進むたびに4記号を後ろへ足す。削除する条件では、T1〜T3 '
 'のどれか一つから中央の2記号を一度だけ取り除く。通常の呼び出しは各条件で6回、1回の出力は2記号。指定した時点に削除対象がまだなければ、その対象が入力に含まれるまで待つ。著者の実験はすべてのターンを順に判定するため、この作例とは処理が異なる。\n'
 '\n'
 '追加の読み取りを選ぶと、削除の直後に1回だけ呼び出しを増やす。その呼び出しは R で始まる記号を入力に足し、出力を1記号増やす。後の呼び出しでも追加した記号を送る。Lab '
 'は、エージェントが実際にどのくらいの頻度で情報を読み直すかを推定していない。要約を生成する費用や、削除したことを示す注記は含めない。\n'
 '\n'
 '表の n はその行の入力記号数、c '
 'は前回と先頭から一致した記号数。作例の入力には同じ記号が重複しない。橙色の「残ったが通常単価」の個数は、前回にもあった同じ記号を数えたものだ。実際のトークンの値が何度も出る場合の対応づけを表さない。先頭から一致した数は、どちらの場合も順序どおりに比べる。\n')

lab = {'id': 'trajectory-deletion-prefix-cost',
 'title': 'The Hidden Costs of Forgetting: A Study of Trajectory Deletion in Software '
          'Engineering Agents',
 'authors': ['Fernando Vallecillos-Ruiz', 'Islem Bouzenia', 'Michael Pradel', 'Leon Moonen'],
 'year': 2026,
 'arxiv_id': '2610.35496',
 'submitted': '2026-10-26',
 'topics': ['ai-agents', 'ml-systems'],
 'urls': {'paper': 'https://arxiv.org/html/2610.35496v1',
          'arxiv': 'https://arxiv.org/abs/2610.35496',
          'pdf': 'https://arxiv.org/pdf/2610.35496v1'},
 'verdict': 'Worth Reading',
 'status': 'draft',
 'question': '履歴を短くすると、モデルに払う費用も減るのか',
 'summary': '著者は、古い推論やツールの出力を消して、必要な情報を読み直す回数と費用を調べた。直近2ターンを残した42評価で、再利用の割引を含めると費用が下がった評価はなかった。',
 'verification': {'mechanism': 'PARTIAL',
                  'performance': 'NOT TESTED',
                  'scaling': 'NOT TESTED',
                  'production_applicability': 'NOT TESTED'},
 'source_review': {'checked': '2026-10-27',
                   'url': 'https://arxiv.org/html/2610.35496v1',
                   'scope': '公開された本文と表I〜IIIを確認した。著者の実行ログと分析コードは未確認。'},
 'core_idea': {'author_claim': '著者は、コーディングエージェントの履歴を削るとき、解決数だけではなく、同じ情報を取り直す手間と、前回の入力を安く再利用できなくなる費用も測る必要があると指摘した。',
               'research_bot_interpretation': 'Lab '
                                              'では、短くなった入力の量と、割引を失って通常単価になる入力の量を分けて数える。著者の実行とは別に、固定の記号列で計算を追う。'},
 'sections': {'overview': '著者は、コーディングエージェントが過去の推論やツールの出力を消すと、解決する課題の数と費用がどう変わるかを調べた。SWE-bench '
                          'Verified '
                          'の100課題で、同じモデルを使う2種類のエージェントを比較した。削除する範囲・単位・量・タイミングを変えた42条件と削除なしの基準を合わせて、9,400回の実行を調べた。\n'
                          '\n'
                          '直近2ターンを残した42評価では、削除なしより解決した課題数が有意に減ったのは5評価だった。すぐに削ると、19評価に増えた。また、著者は、残した出力よりも消した出力の方が、後から読み直されやすいことを確認した。\n'
                          '\n'
                          '直近2ターンを残した42評価では、すべての入力を同じ単価で数えると、26評価で費用の推計値が下がった。一方、前回と同じ入力の先頭を安く再利用できる料金を使うと、費用が下がった評価はなかった。途中の履歴を書き換えると、最初に変わった位置より後ろを通常単価で数え直すためだ。',
              'problem': '長い作業では、エージェントはモデルを呼ぶたびに、それまでの推論とツールの結果を送る。古い情報を消せば次の入力は短くなる。ただし、入力の途中を変えると、それより後ろに残した情報まで安い単価で再利用できなくなる。消した情報が次の操作に必要なら、モデルは同じファイルをもう一度読むこともある。その分の呼び出しと出力まで含めなければ、費用が減ったか判断できない。',
              'method': 'method.md',
              'why_it_might_work': 'モデルへの費用を、通常の入力、安く再利用した入力、出力に分けると、履歴を変えた結果を説明できる。以前と同じ入力が後ろに残っていても、途中が変わればその部分は通常単価になる。次の呼び出しで変更後の履歴をそのまま使えば、その変更済みの部分はまた再利用の対象になる。',
              'evidence': 'evidence.md',
              'executable_understanding': 'experiment.md',
              'results': 'Lab '
                         'の作例の初期設定では、過去の2記号を消すと、延べ入力は72から66に減った。再利用料金を90%割り引くと、合計費用は87.00から87.30へ増えた。割引をなくすと、132.00から126.00へ減った。これは作例の料金単位での比較で、著者の推計額や実際の請求額ではない。\n'
                         '\n'
                         '配布ファイルの `results.json` は、著者の主な集計を `reported` に、Lab が計算した144条件の結果を '
                         '`synthetic` に収める。',
              'what_we_verified': 'Lab '
                                  'は、前回と先頭から一致する記号を数え、再利用する入力と通常の入力を分ける計算を確かめた。作例では、同じ履歴を消しても、再利用の割引を使うかどうかで、削除前後の費用の大小が入れ替わる。追加の読み取りで呼び出しと出力が増える条件も確認した。',
              'what_we_did_not_verify': 'Lab '
                                        'は著者の9,400回を実行していない。モデルの性能や待ち時間、キャッシュの最小長、失効や追い出し、書き込み料金、本番運用の費用は未検証だ。著者が配布した実行ログと分析コードも確認していない。別の料金や要約方法でも結果が同じになるとは言えない。',
              'implementation': '`README.md` のコマンドをリポジトリの直下で実行する。Python '
                                'が144条件の費用を計算する。ブラウザーは選んだ条件の結果を JavaScript で表示し、外部サービスへは接続しない。'},
 'figures': [],
 'interactives': [],
 'teaching_figures': [{'id': 'prefix',
                       'kind': 'timeline',
                       'title': '履歴の途中を変えると、その先は通常単価になる',
                       'after': 'method',
                       'source': 'https://arxiv.org/html/2610.35496v1',
                       'locator': '§II-C・Fig. 1',
                       'rationale': '前回と今回の入力の順序を比べて、どこまで再利用できるかを示す。',
                       'caption': 'これは仕組みを説明する図。次の呼び出しで変更後の履歴をそのまま使うと、その変更を含む先頭部分をまた再利用できる。',
                       'rows': [{'label': '前回の呼び出し',
                                 'nodes': [{'title': 'S → T1 → T2 → T3', 'text': 'モデルに渡した入力全体'}]},
                                {'label': '途中を変更した呼び出し',
                                 'nodes': [{'title': 'S → T1', 'text': '前回と同じ順序なので、安く再利用する。'},
                                           {'title': 'T2′ → T3 → T4',
                                            'text': 'T2 から順序が変わったので、残っている T3 も通常単価。'}]},
                                {'label': '次の呼び出し',
                                 'nodes': [{'title': 'S → T1 → T2′ → T3 → T4',
                                            'text': '前回の変更後の履歴と一致し、安く再利用できる。'},
                                           {'title': 'T5', 'text': 'ここだけ今回追加した入力。'}]}]},
                      {'id': 'cost',
                       'kind': 'equations',
                       'title': '1回ごとに入力と出力を数え、作業全体を合計する',
                       'after': 'method',
                       'source': 'https://arxiv.org/html/2610.35496v1',
                       'locator': '§III-C・VI-B',
                       'rationale': '読み直しで増えた入力や出力も、作業全体の費用に含める。',
                       'caption': '著者の料金の数え方を式にした。ここでの単位は相対費用で、通貨ではない。',
                       'steps': [{'name': '1回の費用',
                                  'formula': 'C_t = (n_t − c_t) + q c_t + 5 o_t',
                                  'explanation': 'n は入力、c は前回と先頭から一致した入力、o は出力。q '
                                                 'は再利用入力の単価で、90%の割引なら0.1。'},
                                 {'name': '作業全体の費用',
                                  'formula': 'C = Σ_t C_t',
                                  'explanation': '読み直しのために追加した呼び出しも含め、すべての費用を足す。'}]}]}

for key, label, options, default in choices:
    widget += '<label>' + label + '<select id="deletion-' + key + '">'
    for value, text in options:
        selected = ' selected' if value == default else ''
        widget += f'<option value="{value}"{selected}>{text}</option>'
    widget += '</select></label>'

s = run.scenario()
widget += f"""<button type="button" id="deletion-reset">初期設定に戻す</button><output id="deletion-output" aria-live="polite"><p>消さない場合：{s['baseline']['total']:.2f}。消す場合：{s['changed']['total']:.2f}。いずれも作例の費用単位。</p></output><noscript>条件を変えるには JavaScript が必要です。初期設定では、割引率を90%にし、4回目に T2 を消し、追加の読み取りはしません。その場合の費用は上に載せています。全条件の結果は results.json で読めます。</noscript>"""
data = json.dumps(run.results(), ensure_ascii=False, separators=(',', ':'))
widget += '<script type="application/json" id="deletion-data">' + data + '</script><script>'
widget += (p / 'interactive.js').read_text() + '\n</script></div>'
(p / 'experiment.md').write_text(intro + widget + end)

class BlockDumper(yaml.SafeDumper):
    pass

def represent_str(dumper, value):
    return dumper.represent_scalar('tag:yaml.org,2002:str', value, style='|' if '\n' in value else None)

BlockDumper.add_representer(str, represent_str)
(p / 'lab.yaml').write_text(yaml.dump(lab, Dumper=BlockDumper, allow_unicode=True, sort_keys=False, width=120))
