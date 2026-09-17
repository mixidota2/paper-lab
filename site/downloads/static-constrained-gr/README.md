# STATIC：業務制約のtrieを、アクセラレータで読める配列へ変える

STATICは許可されたSID集合のtrieをdense tableとCSRへ変換する。YouTubeのTPU v6e実験で制約処理0.033ms/step、3Bモデル推論の約0.25%。有効SIDを出すだけでなく「直近7日」の集合へ生成を限定できる点が主題だ。

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
