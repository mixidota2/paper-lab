### 38手法の比較とChronos-2補正は別の実験

横断benchmarkにはWMA、Croston/SBA/TSB、LightGBM/XGBoost、DeepAR、TimesFM、Moirai、Chronos-Bolt tiny/smallなどを含む。正規化を修正したChronos-2は適応実験で扱うモデルであり、Boltと同一のcheckpointではない。

### 誤差の定義を先に揃える

Eq. 1はlead time Hの需要合計Yと予測H r̂を比較する。Eq. 2のMASEは、各品目の絶対誤差eを直近3観測平均によるlead-time誤差dで割り、d=0なら未scaleのeを使う独自定義。一般的なin-sample差分scaleとは異なり、1未満なら必ずbaselineよりよいとは言えない。Table Vの適応比較はΣe/Σdのpooled ratioである。

補充はS=max(0, μ̂(L+R)+z σ̂√(L+R))。z=Φ⁻¹(τ)、L=6月、R=1月を基本とし、初期在庫S・空の補充pipelineで開始する。受入を需要より先に処理し、注文を固定順序で評価。全明細を満たせない注文は在庫を消費せず、backorderにもせず棄却する。品目proxyは部分消費を許す別のreplayなのでCOFRに読み替えない。

### BDDは誤差を符号付きで読む手順

Bias-Direction Diagnosticは新しいforecasting modelではない。まず精度とservice順位の符号を確認し、signed lead-time bias、zero-periodの誤差寄与、在庫量を併記する。MAEのゼロ期間項はΣ[y=0]|ŷ|/N。Croston/SBAでは誤差の53〜54%がここにあり、正の余分な予測がspikeの不足を相殺しうる。過剰在庫を無料の改善として数えない。

### 非ゼロ平均へ移すと、入力と逆変換の両方が変わる

Chronos-2の(x−mean)/stdを、正需要だけのmean/stdへ置き換える。未来の正需要を使わず、各originの学習contextだけから統計を求める。全ゼロなら中心0、scaleが0ならmodelのε。arcsinhが有効なら逆arcsinhの後で保存した中心とscaleへ戻す。

下の例は8割ゼロ、正値2と6。平均0.8に対し正値平均4.0となる。正規化出力が0の定数代理を逆変換すれば0.8/4.0に分かれるが、これはChronosの予測値ではない。実モデルは変換後の全系列を処理するため、平均を置き換えただけで同じ改善が出る保証はない。
