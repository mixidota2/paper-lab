# UNIQUE: A Unified Retrieval and Ranking System for Large-Scale Feed Recommendation

UNIQUEは、推薦候補を集めるモデルと、その候補を詳しく採点するモデルに、同じ利用者情報と学習結果を使わせます。Baiduと北京航空航天大学の著者は、Mobile Baiduで1週間のA/Bテストを行い、旧方式に比べ、視聴時間が0.96%、配信量が1.08%増えたと報告しました。99パーセンタイルの89 msは、所定の条件で測った候補取得サービスの応答時間です。推薦画面全体の応答時間ではありません。

## 候補を集める段階と、採点する段階で何を共有するか

最初に商品を、内容や利用者の反応が似たものをまとめるコードに割り当てます。推薦時は、利用者の履歴に合うコードを選び、そこに属する商品を候補にします。候補を内積で絞ってから、商品ごとに履歴の参照先を変えて詳しく採点します。学習する表現は共有しますが、商品を絞る手順も、その後の推薦処理も残ります。

## 読む順番と再実行

`lab.yaml` で問題と著者報告を確認し、`method.md` でコードの割り当てから配信までを追います。`run.py` と `results.json` は人工例の計算と結果です。どの式を確かめ、何を省いたかは `mapping.md` に記しました。

```bash
uv run papers/unique-baidu-unified-retrieval-ranking/run.py
```

Python標準ライブラリだけを使います。単体で取得した場合は `uv run run.py`。結果はスクリプトと同じ場所の `results.json` に保存します。HTMLは `uv run paper-lab build` で生成します。

仕組み全体の検証はPARTIALです。人工例で確かめた条件だけをCONFIRMEDとします。実運用での性能、件数を増やしたときの性能、導入の可否は未検証（NOT TESTED）です。
