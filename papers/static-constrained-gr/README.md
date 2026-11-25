# STATIC：業務制約のtrieを、アクセラレータで読める配列へ変える

著者は、生成推薦が決められた候補集合の外を選ばないようにして、その確認をTPU上で素早く行う方法を提案しました。STATICは、作品識別子（SID）を先頭の記号で分けた木を、まとめて参照できる配列に変えます。モデルが次の記号を出すたび、その先に許可された作品がある記号だけを残します。たとえば直近7日以内の動画に限る、といった条件を強制できます。

30億パラメータのモデルをTPU v6eで測ると、候補を制限する処理には1ステップあたり0.033ミリ秒かかりました。推論時間全体の約0.25%に当たります。別のYouTubeホーム画面のA/Bテストでは、公開から7日以内の動画の視聴が5.1%増えました。7日は対象動画の条件で、実験期間ではありません。0.033ミリ秒は候補制限だけの時間で、画面を届けるまでの時間ではありません。

一次資料：[2602.22647v2.pdf](https://arxiv.org/pdf/2602.22647v2)。SHA-256と節・表の対応は[mapping.md](mapping.md)。詳しい方法は[method.md](method.md)、サイト本文の原本は[lab.yaml](lab.yaml)。

## 実行

```bash
uv run papers/static-constrained-gr/run.py
```

5個の有効SIDのうち2個だけをfreshとする。2値・3段の全prefixを列挙してCSRと集合定義を照合する。同じ固定scoreでtop-1後filterとfresh集合内top-1を比べ、前者が空になる例を確かめる。

## 検証範囲

Mechanism PARTIAL。個別のCONFIRMED / NOT OBSERVEDは[results.json](results.json)のchecksに記録。Performance / Scaling / Production applicability NOT TESTED。

TPU/GPU kernel、dense前段、VNTK固定長slice、8-token・20M集合のメモリ、本番freshness更新、遅延、CTRはNOT TESTED。CPUの小さなCSR参照実装から948倍を再現したとは言わない。

## 実装の位置付け

公式実装を取得し、READMEとindex/decodingの対応を確認した。commit `ac18fa1870ac45e0a3559090a0ea9ec005226cf5`。JAX/PyTorch実装自体の実行はNOT TESTED。
