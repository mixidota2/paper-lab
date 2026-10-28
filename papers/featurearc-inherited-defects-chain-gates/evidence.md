## 著者報告：最後の局所合格を全体合格に置き換えない

一次資料の[arXiv登録情報](https://arxiv.org/abs/2610.37434)と本文を参照した。対象は73 tasks・263 stages・53 repositories、10種類のmodelとharnessの構成。Table IIIの初段62.7%に対し、最終chainは28.5%。最後のstageを通った273実行でも69実行はchainを落とす。`69 / 273 × 100 = 25.2747…%`、小数1桁で25.3%となる。[§III-F、IV-A、V-A・Table III](https://arxiv.org/html/2610.37434v1#S5.SS1)

Table IVの72.9%は**失敗した後続段階の中で**以前の欠陥を継承した割合。「Prior awareness」94.9%は、直前の失敗に気づかなかった割合で、低い方がよい。全taskに対する割合でも、認識できた割合でもない。[§IV-B、V-B、V-C・Table IV](https://arxiv.org/html/2610.37434v1#S5.SS3)

著者の課題選定と実行軌跡は本Labでは再実行していない。以下の手作り例や仮想修正による変化を、この著者報告に足し合わせない。
