"""人工データで二つの経路の動画候補をまとめ、前のコードを変えて次のコードの確率を比べる。"""
import json,math
from pathlib import Path
def retrieve(video_code,mixed_code,video_index,author_index):
    video=video_index.get(video_code,[]);author=author_index.get(mixed_code,[])
    return dict(video=video,author=author,merged=sorted(set(video+author)))
def token_probs(anchor,previous):
    z=[x+sum(e[j] for e in previous) for j,x in enumerate(anchor)]
    w=[math.exp(v-max(z)) for v in z];return [v/sum(w) for v in w]
def main():
    paths=retrieve((1,2,3),(7,8,1),{(1,2,3):['v1']},{(7,8,1):['v1','v2'],(7,8,2):['v3']})
    rank_scores={'v1':.4,'v2':.7,'v3':.9}
    r=dict(note='人工データを使い、動画と投稿者の二つの経路で候補を探す処理と、前のコードを使う確率計算を確かめました。推薦の精度、処理件数、本番のDAUは測っていません。',verification=dict(mechanism='PARTIAL',performance='NOT TESTED',scaling='NOT TESTED',production_applicability='NOT TESTED'),paths=paths,ranked=sorted(paths['merged'],key=lambda v:-rank_scores[v]),conditional=dict(prefix_a=token_probs([.2,.3],[[1,0]]),prefix_b=token_probs([.2,.3],[[0,1]])))
    Path(__file__).with_name('results.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
