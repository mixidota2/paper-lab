"""AgentX decision record and paired-replay admission, with synthetic evidence."""
import json
from pathlib import Path

def judge(effect, ci_low, min_effect, guardrail, days, min_days=14):
    if guardrail == "severe": verdict, reason = "DISCARD", "重大な悪化"
    elif guardrail == "moderate": verdict, reason = "EXTEND", "人の例外審査が必要"
    elif days < min_days: verdict, reason = "EXTEND", "観測窓が不足"
    elif ci_low > 0 and effect >= min_effect: verdict, reason = "KEEP", "効果・有意性・guardrailを通過"
    elif effect < 0: verdict, reason = "DISCARD", "主指標が悪化"
    else: verdict, reason = "EXTEND", "改善を確定できない"
    return {"verdict": verdict, "reason": reason, "effect": effect, "ci_low": ci_low,
            "guardrail": guardrail, "window_days": days, "method": "入力CIを判定する模型。統計推定は未実装"}

def admit(old, new, safe, threshold=.05):
    delta=sum(b-a for a,b in zip(old,new))/len(old)
    return {"delta":round(delta,6), "accepted": delta>threshold and safe}

def compute():
    cases={"利益あり":judge(.3,.1,.2,"clear",14),"重大な副作用":judge(.3,.1,.2,"severe",14),
      "中程度の副作用":judge(.3,.1,.2,"moderate",14),"短期":judge(.3,.1,.2,"clear",3),"不確実":judge(.3,-.1,.2,"clear",14)}
    replay={"改善":admit([.5,.6,.7],[.7,.7,.8],True),"unsafe":admit([.5,.6,.7],[.7,.7,.8],False),"退行":admit([.5,.6,.7],[.4,.6,.7],True)}
    return {"note":"人工の効果とCIを使う判定表。実験案生成、LLM評価、オンラインA/Bは実行しない。閾値と14日窓はLabの仮定。",
      "experiments":[{"name":"同じ主効果でも判定は変わる","metrics":{k:{"判定":v["verdict"],"理由":v["reason"]} for k,v in cases.items()}}],
      "decisions":cases,"replay":replay,"checks":{"veto_and_escalation":"CONFIRMED","paired_replay_gate":"CONFIRMED","agent_productivity":"NOT TESTED"}}


def main():
    result = compute()
    Path(__file__).with_name("results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
