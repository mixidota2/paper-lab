"""Deterministic, executable teaching models, never paper performance reproductions.

Every displayed quantity is computed below. Explorer frames are emitted to results.json
so the browser and the CLI share one numerical source of truth. No model APIs required.
"""
from __future__ import annotations
import json
import math
from pathlib import Path
from statistics import mean

IDS = ('scaffold-effects-gaia', 'case-against-generation-retrieval', 'unipinrec', 'tgr',
       'harness-bench', 'rest-sequence-ranking', 'apollopfn', 'vn2-stockout-catboost',
       'contextual-deconvolution', 'whole-foods-shelf', 'forecast-critic')


def bar(label, value):
    return {'label': label, 'value': round(value, 4)}


def line(label, values):
    return {'label': label, 'values': [round(v, 4) for v in values]}


def frame(value, bars, note, lines=None):
    return {'value': value, 'bars': bars, 'note': note, 'lines': lines or []}


def mae(actual, prediction):
    return mean(abs(a-b) for a, b in zip(actual, prediction))


def scaffold(retries):
    # A scripted tool fails on the first i % 4 calls, then returns a correct value.
    # Both controllers see the same tasks, failures and validation rule.
    def evaluate(budget):
        solved = calls = 0
        for task in range(60):
            for attempt in range(budget + 1):
                calls += 1
                if attempt >= task % 4:
                    solved += 1
                    break
        return solved, calls
    base, improved = evaluate(0), evaluate(retries)
    return frame(retries, [bar('再試行なし：完了タスク', base[0]), bar('再試行あり：完了タスク', improved[0])],
                 f'60タスクでツール呼出しは {base[1]} → {improved[1]} 回。回復には追加予算が必要。失敗回数は人工的に設定しており、LLMの能力差は含まない。')


def retrieval(width):
    # Identical leaf scores. A narrow greedy prefix may discard the best leaf.
    scores = [[.6, .6, .6, .6], [.99, .05, .05, .05], [.5, .4, .3, .2], [.4, .3, .2, .1]]
    prefixes = sorted(range(4), key=lambda i: mean(scores[i]), reverse=True)[:width]
    selected = [(scores[i][j], i, j) for i in prefixes for j in range(4)]
    best = max(selected)
    return frame(width, [bar('全候補から選択：関連度', max(max(s) for s in scores)), bar('枝を絞って選択：関連度', best[0])],
                 f'第1段で残す枝 {width}/4。調べる末端は {width*4}/16 件。平均点で枝を選ぶ例では、最良候補を含む枝を先に捨てる場合がある。無効IDは生成していない。',
                 [line('各枝の平均点', [mean(s) for s in scores]), line('各枝の最高点', [max(s) for s in scores])])


def cache(length):
    users, candidates = 80, 10
    separate = users*(2*length+candidates)
    shared = users*(length+candidates)
    return frame(length, [bar('段ごとに履歴を処理', separate), bar('履歴を共有', shared)],
                 f'80リクエスト、候補10件。履歴1要素と候補1件を各1単位と仮定。削減率 {(1-shared/separate)*100:.1f}%。転送・保存・失効の費用は含まない。')


def sid(depth):
    p = .9
    probability = p**depth
    return frame(depth, [bar('各段の正しい枝の選択率 (%)', p*100), bar('全段で正しい枝を選ぶ率 (%)', probability*100)],
                 '各段が独立に90%で正しい枝を選ぶ仮定。途中で枝を誤ると後段だけでは目標へ戻れない。BARGEの実測精度や改善幅を表す式ではない。',
                 [line('深さごとの到達率 (%)', [100*p**d for d in range(1, depth+1)])])


def harness(mode):
    # Each of 60 artifacts has one observable defect. Validators execute rules.
    artifacts = [{'format': i % 5 != 0, 'evidence': i % 5 != 1, 'saved': i % 5 != 2} for i in range(60)]
    def valid(a): return all(a.values())
    before = sum(map(valid, artifacts))
    for a in artifacts:
        if mode >= 1: a['format'] = True
        if mode >= 2: a['saved'] = True
        # Grounding cannot be repaired merely by declaring it valid.
    after = sum(map(valid, artifacts))
    return frame(mode, [bar('修復前：合格成果物', before), bar('修復後：合格成果物', after)],
                 ['修復なし。形式・根拠・保存の全条件を満たした成果物だけを数える。',
                  '形式を修復。内容の根拠不足や未保存は残る。',
                  '形式と保存を修復。根拠不足の12件は不合格のまま。検査を通す操作と、正しい仕事をすることは別。'][mode])


def rest(weight):
    # Squared-loss gradient for a sequence branch in a shortcut-dominated toy.
    # y=1, non-seq=0.9, seq=0.2, fusion=non-seq+0.1*seq.
    y, nonseq, seq, gate = 1., .9, .2, .1
    main_grad = 2*(nonseq + gate*seq-y)*gate
    aux_grad = 2*weight*(seq-y)
    return frame(weight, [bar('主損失から系列枝への勾配絶対値', abs(main_grad)), bar('補助損失を足した勾配絶対値', abs(main_grad+aux_grad))],
                 f'主予測は {nonseq+gate*seq:.2f}、系列枝単独は {seq:.2f}、正解は1。L=(主予測−1)² + λ(系列予測−1)²。大きい勾配だけでは汎化改善を保証しない。')


def apollo(shift):
    actual = [10+2*math.sin(t*math.pi/4)+ (12 if 8 <= t <= 10 else 0) for t in range(16)]
    history = [10+2*math.sin(t*math.pi/4) for t in range(16)]
    known = [v+(12 if 8+shift <= t <= 10+shift else 0) for t,v in enumerate(history)]
    return frame(shift, [bar('季節性だけ：MAE', mae(actual,history)), bar('販促予定を使う：MAE', mae(actual,known))],
                 f'真の販促は9〜11期。予定を {shift} 期ずらす。効果量12は既知と仮定し、推定していない。予定が誤れば情報追加が悪化要因にもなる。',
                 [line('合成需要',actual),line('季節性だけ',history),line('販促予定あり',known)])


def stockout(cap):
    latent = [18,20,22,19,21,20,18,22]
    sales = [min(x,cap) for x in latent]
    available = [s for s in sales if s < cap]
    masked = mean(available) if available else 0
    return frame(cap, [bar('合成の潜在需要：平均',mean(latent)),bar('観測販売：平均',mean(sales)),bar('非欠品日のみ：平均',masked)],
                 '観測販売=min(需要,在庫)。在庫上限と同値の期間を除外する簡略例。'+('非欠品期間がないため推定不能（棒は0で表示）。' if not available else '非欠品日の平均も選択バイアスを含む。欠品日の真の需要を復元した値ではない。'),
                 [line('合成の潜在需要',latent),line('観測販売',sales)])


def cost(ratio):
    demand = [10,10,30,10,10,30,10,10]
    responsive = [18,18,28,18,18,28,18,18]
    smooth = [12]*8
    def parts(stock):
        holding = sum(max(s-d,0) for s,d in zip(stock,demand))
        shortage = sum(max(d-s,0) for s,d in zip(stock,demand))
        return holding,shortage
    a,b=parts(responsive),parts(smooth)
    return frame(ratio,[bar('変動を追う在庫：総費用',ratio*a[0]+a[1]),bar('平滑な在庫：総費用',ratio*b[0]+b[1])],
                 f'費用=h×余剰+p×不足、p=1。余剰/不足は追従 {a[0]}/{a[1]}、平滑 {b[0]}/{b[1]}。各期独立で持越しなし。この反転点は論文の約0.20とは別。',
                 [line('需要',demand),line('変動を追う在庫',responsive),line('平滑な在庫',smooth)])


def shelf(exponent):
    # Two departments, fixed total 100, each at least 10.
    def value(a): return 20*a**exponent+18*(100-a)**.5
    choices = list(range(10,91))
    optimum=max(choices,key=value)
    return frame(exponent,[bar('等分：目的値',value(50)),bar('制約内の最適配分：目的値',value(optimum))],
                 f'A部門 {optimum}、B部門 {100-optimum}、合計100。各部門10以上。目的値=20×A^β + 18×B^0.5。係数は教材用。因果効果・部門間効果・長期価値は推定していない。',
                 [line('A面積10〜90に対する目的値',[value(a) for a in choices])])


def critic(threshold):
    # Forecast plausibility classification from level discrepancy; future unseen.
    residuals = [0,1,2,3,4,5,6,7,8,9]
    bad = [False,False,False,True,False,True,True,True,True,True]
    flags=[x>=threshold for x in residuals]
    tp=sum(f and b for f,b in zip(flags,bad));fp=sum(f and not b for f,b in zip(flags,bad));fn=sum(not f and b for f,b in zip(flags,bad))
    precision=tp/(tp+fp) if tp+fp else 0
    recall=tp/(tp+fn)
    return frame(threshold,[bar('適合率 (%)',100*precision),bar('再現率 (%)',100*recall)],
                 f'合成10件：正しく警告 {tp}、誤警告 {fp}、見逃し {fn}。適合率は警告の正しさ、再現率は問題を拾う割合。正解ラベルは教材用に人為設定。LLMや論文F1の再現ではない。',
                 [line('不自然さの規則スコア',residuals),line('警告の閾値',[threshold]*10)])


SPECS = {
    IDS[0]: (scaffold, list(range(5)), 1, '失敗後の再試行上限', '回', '完了タスク数'),
    IDS[1]: (retrieval, list(range(1,5)), 0, '残す候補の枝', '本', '関連度（合成スコア）'),
    IDS[2]: (cache, list(range(0,129,8)), 2, '履歴の長さ', '要素', '仮定した計算単位'),
    IDS[3]: (sid, list(range(1,9)), 2, '商品IDの階層の深さ', '段', '確率 (%)'),
    IDS[4]: (harness, [0,1,2], 0, '修復範囲：0なし／1形式／2形式と保存', '', '合格成果物数'),
    IDS[5]: (rest, [i/20 for i in range(21)], 4, '系列枝への補助損失の重み λ', '', '勾配の絶対値'),
    IDS[6]: (apollo, list(range(-4,5)), 4, '販促予定のずれ', '期', '平均絶対誤差（小さいほどよい）'),
    IDS[7]: (stockout, list(range(12,26)), 8, '各期の在庫上限', '個', '平均数量'),
    IDS[8]: (cost, [i/20 for i in range(41)], 4, '保管費用 / 欠品費用 h/p', '', '合成費用'),
    IDS[9]: (shelf, [i/20 for i in range(21)], 10, 'A部門の面積弾力性 β', '', '合成の目的値'),
    IDS[10]: (critic, list(range(11)), 5, '警告する不自然さの閾値', '', '割合 (%)'),
}


def compute(lab_id):
    fn, values, default, label, unit, metric = SPECS[lab_id]
    frames=[fn(v) for v in values]
    return {'note':'教材用の合成実験。論文モデルの再現・性能比較ではありません。',
            'verification':{'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'},
            'experiments':[{'name':'条件を変える最小実験','dataset':'deterministic synthetic','metrics':{b['label']:b['value'] for b in frames[default]['bars']}}],
            'explorer':{'label':label,'unit':unit,'metric':metric,'default':default,'frames':frames}}


def run_lab(lab_id):
    result=compute(lab_id)
    (Path(__file__).parent/lab_id/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(lab_id+': '+str(len(result['explorer']['frames']))+' computed frames')
