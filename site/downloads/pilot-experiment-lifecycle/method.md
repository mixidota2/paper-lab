### 3つの役割と、変更できない境界

Experiment Managerはtaskの受付、観察、異常対応、終了後の振り返りを進める。Search PlannerはManagerに呼ばれたときだけ候補を提案し、Memory Curatorは終了したtaskから経験を抽出する。Curatorは非同期で失敗を隔離するため、記憶の保存が失敗しても当該実験の統計的結論は変わらない。採用LLMの具体的なcheckpointやparameter数は確認範囲で明記されておらず、DREAMのQwen3をPILOTへ当てはめない。

task仕様Tは目的、指標、予算、観察期間、登録済みfeatureとstrategy、権限を含む。incomplete → awaiting → ready → frozenと固め、runtimeのplaybookも固定する。安全・統計policy > task仕様 > playbook > approvedな方法論 > 暫定hint > agentの推論という優先順を守る。学習した記憶が上位規則を書き換えることはない（§3.1）。

実行可能なcommandを列挙するManager Guard、状態を唯一書き込むState Committer、変更不能なcertificateを出すStatistics Engineが、LLMの選択を囲む。Contract Builderは観測前に判断基準を固定し、Action EnumeratorとCandidate Validatorは探索可能なactionと提案の適合性を管理する（表2）。判断と強制を同じLLMへ任せないのが設計の中心である。

### 観察期間を、都合のよいliftで切らない

Managerは固定した観察計画に沿ってmetricsを収集し、freshness、成熟度、sample size、割付の異常を調べる。closeするかの判断時点ではliftの向きを隠し、「もう少しで有意だから待つ」「良い日だけ切り出す」を許さない。noiseらしい異常はdiagnostic-onlyにして窓を延長、反復やhard bound違反はpauseして人へ戻す（§3.2）。

roundはcontinue、reject、promoteで処理する。rejectならChampionは変わらず、promoteなら勝ったChallengerを次の基準にする。目標達成後も段階的なscale-upと独立Dconfirmでの確認があり、search期間のデータだけではproduction deliveryを確定しない。deploy、traffic拡大、仕様変更などには人の承認が必要と本文に明記される。「実験cycle中の人の介入なし」というabstractの結果記述を、無制限の権限と読まない。

### PolicyTree：同じ8次元の設定を、誰に適用するかも探す

各leafにstrategy bundleを持つ決定木で、登録済みの処置前featureだけを使ってユーザーを分岐する。全ユーザーは必ず1つのleafへ着地し、missing値の扱いも事前に定義する。木の深さ、leaf数、最小母集団比率、利用feature数、round数とtraffic予算には上限がある（§4.1）。

固定baseline T₀は実験を通して動かさない。Champion T*は現在の確認済み基準、Challengerはそこへatomic actionを1つだけ加えた木。actionはsplit、prune、hashExpand、collapse、updateStrategyの5種類。Plannerは許可集合A(T*)の外の操作を作れない。Δtotalは固定baselineとの差、Δstepは現在のChampionとの差なので、基準の混同を避ける。

ROAMもLLM agentであり、非agent baselineではない。ROAMはpage0 / pagingそれぞれのCTR・IPV・CVR・GMVの4次元、計8次元の値を全体へ一律適用する。PILOTは同じ基本parameter空間をsegment別に適用するPolicyTree、checkpoint、最低調整quota、事前登録した仮説と判断基準を加える。制御方法と探索空間の両方が変わっている。

### Memory Curator：1回の有意な結果を、再利用可能な知識に飛躍させない

Strategy Evidenceはfrom/to bundleとpopulation scope、Methodology Experienceはoperationとscenario条件をkeyとして記録する。taskごとのbranchへ書き、終了後にmain memoryへ照合してmergeする（§5）。task内で強いcertificateが得られても、新しい記憶はdraftから始まる。

同じscopeで独立taskによる一致が1つ増えるとsupportedへ、規定のcross-task閾値を満たし重大な未解決反証がなければapprovedへ進む。supportedはhintとして使え、approvedはstrategy recallや候補優先度などの助言に自律利用できる。同じtaskの複製は独立証拠にならない。反証は保存し、必要なら元のclaimをsupersededと記録する。新しい反対claimもdraftから始める。inconclusiveは否定的な証拠とは別の結果である。
<figure class="teaching batch18"><h3>実験の状態機械：失敗と保留の経路も残す</h3><ol class="b18-lifecycle"><li><strong>仕様・playbookをfreeze</strong><p>予算、feature、判断基準、権限を固定</p></li><li><strong>候補の検査 → 承認 → observe</strong><p>Champion + 1 action。データの健全性を先に確認</p></li><li><strong>continue / reject / promote</strong><p>異常ならpause。rejectならChampionを維持</p></li><li><strong>目標到達 → 段階拡大 → 独立確認 → delivery</strong><p>searchの勝ちだけでは配信を確定しない</p></li></ol><figcaption>図2・3、§3.1–3.4を要約した状態図。すべてのwire commandを列挙した実装図ではない。</figcaption></figure><figure class="teaching batch18"><h3>PolicyTree：固定baselineと探索基準を分ける</h3><div class="b18-cards"><div><strong>固定baseline T₀</strong><p>全roundのtotal効果の原点。動かさない。</p></div><div><strong>Champion T*</strong><p>epoch中は固定。新しい提案のstep効果を測る。</p></div><div><strong>Challenger T*ₐ</strong><p>登録済みsegmentでsplit、または1つのleafのbundleを変更。</p></div></div><div class="b18-tree"><strong>処置前のsegmentはfocusedか？</strong><div class="b18-cards"><div>yes → intent_bundle</div><div>no / missing → default_bundle</div></div></div><figcaption>上段は§4.1・図3–4。下段はrun.pyの10人の人工木。3人と7人に分岐し、元は全員default。</figcaption></figure><figure class="teaching batch18"><h3>記憶の昇格には、別taskの証拠が要る</h3><div class="b18-cards"><div><strong>draft</strong><p>1つのtask。大標本・有意差でもここから開始。</p></div><div><strong>supported</strong><p>同じscopeの独立taskで一致を確認。hintに使える。</p></div><div><strong>approved</strong><p>規定の確認閾値を満たし、重大な反証が未解決でない。</p></div></div><p>同じtaskを10回保存 → 証拠は1件。inconclusive → 反証とは分けて保存。対立 → 昇格を止め、理由を記録。</p><figcaption>§5.2。approvedでも安全policyやtask仕様の上位権限にはならない。</figcaption></figure>
