### parallel SIDの作り方と、出力の順序を分ける
Qwen2.5-Omni-3Bに8個のlearnable compression tokenを置き、動画を8つの埋め込みslotへ圧縮する。各slotを独立に512 centroidのK-meansで量子化し、8 tokenのSIDにする。残差を次の段へ渡すRQとは異なる。parallelなのは表現slotの構成であり、SIDとcopyが同時に出るという意味ではない。

生成backboneはQwen3-0.6B。Text2SIDとSID2TextでSIDと文章を対応付け、元の語彙embeddingを凍結してSID token embeddingを学習する。次にuser profile、recency、履歴からSIDを予測し、区切りtokenの後ろにcopyを続ける。損失は Lgen = LSID + λcopy Lcopy。高頻度の2–4 gramなどをまとめるMulti-token Bindingでは、元token embeddingの平均で新tokenを初期化する。

<figure class="teaching batch21" data-b21="dual"><h3>SIDが先なら、copy生成を省いても候補を変えない</h3><label>条件を選ぶ <select><option value="0">copyを生成</option><option value="1">copyをskip</option></select></label><div data-output aria-live="polite"><div class="b21-tokens"><span>履歴 music</span><b>→</b><span>SID s0</span><b>→</b><span class="">歌の続きを聴く</span></div><p>合成の逐次出力単位 8。先に決まるSIDは同じ。文字数を使った操作数で、GPU時間ではない。</p></div><script type="application/json" data-frames>["<div class=\"b21-tokens\"><span>履歴 music<\/span><b>→<\/b><span>SID s0<\/span><b>→<\/b><span class=\"\">歌の続きを聴く<\/span><\/div><p>合成の逐次出力単位 8。先に決まるSIDは同じ。文字数を使った操作数で、GPU時間ではない。<\/p>", "<div class=\"b21-tokens\"><span>履歴 music<\/span><b>→<\/b><span>SID s0<\/span><b>→<\/b><span class=\"muted\">copyを省略<\/span><\/div><p>合成の逐次出力単位 1。先に決まるSIDは同じ。文字数を使った操作数で、GPU時間ではない。<\/p>"]</script><figcaption>原典 §3.2の条件付き分解を有限頻度モデルで例示。下流ANNの入力はSID由来の表現。</figcaption></figure>

### 本番ではSIDをuser表現へ足し、ANNで検索する
生成Top-20 SIDsをencoderでeₛへ変換し、既存user特徴eᵤと e′ᵤ=αeᵤ+βeₛ で融合する。実利用ではα=β=1。候補動画のeᵥを持つcollectionへANN検索する。したがって、「生成SIDを一意の動画IDへ戻せば完了」という配信構成ではない。
