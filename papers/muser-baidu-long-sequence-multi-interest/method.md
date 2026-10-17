### 古い履歴をpoolし、6 queryで異なる関心を読む

図2の10,000件の履歴では、古い8,000件を64件ずつ、中期の1,200件を16件ずつまとめて圧縮する。直近の800件は、一件ごとの情報を残す。本文の添字順と図の古い→新しい順は違うため、実装では順序を明記する。

encoderは6層、hidden 512、8 head、dropout 0.1。6つのlearnable queryでinterestを抽出し、candidateとのcosine類似度を温度0.07のsoftmaxへ通して混合する。Fig. 2にはargmaxの表現もあるが、本文Eq. 10はsoftな加重和なので、ここでは式の意味を採る。next-Kのcontrastive lossと、係数λ=0.01の直交正則化を合わせる。

### 意味付けと更新はrequestの外にも置く

ERNIE-4.0-Turboの要約生成をERNIE-Speedへ蒸留し、BGE-base-enの768次元表現をIDと融合する。必要に応じVisualized-BGE/VISTAも使う。long-term interestはcacheし、short-termをonline更新。Eq. 14のβ(t)は負荷・同時実行数に応じる融合係数で、固定の万能値ではない。

MGSはHNSWに基づくNANN型retrieval。indexのEuclidean距離と多目的DNN scoreのずれを、階層beam searchで再scoreしながら緩和する。新しい意味encoderだけでindex側のずれが消えるという主張ではない。
