TGRは1つのNN名ではなく、Tencentの推薦を改める3方向の枠組み。**CCFormer**は既存の順位付けを置き換え、feature-field別cross attention、長い系列のsubspace token mixing、階層圧縮を使う。出力は商品別の複数タスクのスコアだ。

候補生成には2つの方式がある。**BARGE**は階層的semantic IDの次トークン生成を改良し、商品境界を意識したattentionと経路の再順位付けを使う。**HiGR**はPCRQ-VAEで構造化したIDを用い、Hierarchical Slate Decoderで一覧全体の粗い計画から個別商品へ進む。ORPOによるlistwise alignmentで一覧の品質を調整する。

**TGR-Reason / LatentRec**は別の時間帯で動く。Thinkモデルが作ったreason tokenを保存し、オンラインのGenモデルに渡す。ユーザーのリクエストごとに長い思考文を生成する構成とは区別する。導入面・比較条件が異なるため、各モジュールの改善率を足し合わせない。

[一次資料：方法と実験条件](https://arxiv.org/html/2609.00986)
