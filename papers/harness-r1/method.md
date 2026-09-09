### engineerは解答を出さず、4つの介入箇所を編集する
targetは主実験でQwen3.5-9B。別の9B engineer（修正担当）が、失敗だけを圧縮した記録packetを読み、実行コードへの変更patchを一度だけ生成する。engineerは解答役ではない。修正を渡した後は、targetだけが環境で課題を解く。overlayはepisode初期化、判断前、行動直前、feedback後の4箇所へ入る（図2、§3.1、付録C）。

初期化はcontextや状態を準備し、判断前は検索した手順や制約を渡す。行動直前は提案されたtool callを正規化・書換え・拒否し、feedback後は観測を解析して停滞から回復させる。文脈だけを編集する方式より広い実行権限を持つので、patchの検証と許可された返り値が重要になる。

### 成功していた課題も含めて再実行する
batch Bの元のrewardをR⁰、patch後をRᴾとすると、`Δ_B(P)=(1/|B|)Σᵢ(Rᵢᴾ−Rᵢ⁰)`。有効かつ完全に評価できたpatchにはこの差を、invalid/no-op/未完了にはゼロを与える。たとえば失敗4件を成功へ直しても、元の成功5件を壊せば全体では悪化する。この回帰を見逃さないよう、再実行は全batchを対象にする（式1）。

初期の教師あり学習（SFT）には、GPT-5.5 teacherが提案し、実行検証を通った約1,000編集例を使う。RLは別課題splitの約1,500failure packetで学習する。1packetにつきK=8のpatchをsampleし、`A_k=(r_k−mean(r))/std(r)` と群内で標準化する。このadvantageをengineerのtoken確率比に掛けるclipped GRPOを使う。targetの重みへは逆伝播しない（式2–4、Algorithm 1）。

WebShopの学習rewardはshaped score、ALFWorldとDBBenchは二値成功であり、全てを二値rewardだと理解してはいけない。主結果では3環境の成功率を等重みで平均する。

### 同じbatchでの改善と、未見課題への移植を分ける
主目的は失敗を見たbatchの同じ課題を再実行するtransductiveな改善。別課題・別targetへの適用は追加実験で扱う。未見targetへの転移では、そのtarget自身の失敗から新しいpatchを作るため、一つのpatchの万能性とは違う。

[一次資料：arXiv v1 本文](https://arxiv.org/pdf/2608.02276v1)
