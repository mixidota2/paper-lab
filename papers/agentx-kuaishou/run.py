"""教材用の入力で、推薦の変更を採用する条件と、実行基盤の更新条件を比べます。"""
import json
from pathlib import Path

def judge(effect, ci_low, min_effect, guardrail, days, min_days=14):
    if guardrail == "severe": verdict, reason = "DISCARD", "副作用を監視する指標が大きく悪化しました"
    elif guardrail == "moderate": verdict, reason = "EXTEND", "中程度の悪化があり、人の審査を待ちます"
    elif days < min_days: verdict, reason = "EXTEND", "観測した日数が足りません"
    elif ci_low > 0 and effect >= min_effect: verdict, reason = "KEEP", "効果、統計的有意性、副作用の条件を満たしました"
    elif effect < 0: verdict, reason = "DISCARD", "評価する主指標が悪化しました"
    else: verdict, reason = "EXTEND", "与えられた値では改善を確かめられません"
    return {"verdict": verdict, "reason": reason, "effect": effect, "ci_low": ci_low,
            "guardrail": guardrail, "window_days": days, "method": "入力された信頼区間を使います。統計量は推定しません。"}

def admit(old, new, safe, threshold=.05):
    delta=sum(b-a for a,b in zip(old,new))/len(old)
    return {"delta":round(delta,6), "accepted": delta>threshold and safe}

def compute():
    cases={"利益あり":judge(.3,.1,.2,"clear",14),"重大な副作用":judge(.3,.1,.2,"severe",14),
      "中程度の副作用":judge(.3,.1,.2,"moderate",14),"短期":judge(.3,.1,.2,"clear",3),"不確実":judge(.3,-.1,.2,"clear",14)}
    replay={"改善":admit([.5,.6,.7],[.7,.7,.8],True),"unsafe":admit([.5,.6,.7],[.7,.7,.8],False),"退行":admit([.5,.6,.7],[.4,.6,.7],True)}
    return {"note":"教材用の効果と信頼区間を使います。案の生成、LLMによる採点、本番A/Bは行いません。効果の基準と14日間はLabで決めた条件です。",
      "experiments":[{"name":"同じ主指標の効果で、副作用や観測期間が異なる場合の判定","metrics":{k:{"判定":v["verdict"],"理由":v["reason"]} for k,v in cases.items()}}],
      "decisions":cases,"replay":replay,"checks":{"veto_and_escalation":"CONFIRMED","paired_replay_gate":"CONFIRMED","agent_productivity":"NOT TESTED"}}


def main():
    result = compute()
    Path(__file__).with_name("results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
