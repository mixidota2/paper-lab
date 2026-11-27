"""商品を探す関数は固定し、失敗の型に応じて前後の処理を選びます。
モデルの学習、ネット接続、自由に生成したコードの実行は行いません。
"""
import json
from pathlib import Path

HOOKS = ("episode_init", "pre_decision", "pre_action", "post_feedback")


def target(context):
    # 欲しい結果がまだなければ検索する。修正役はこの関数を変えない。
    if context.get("result") == context["wanted"]:
        return {"tool": "finish"}
    return {"tool": "lookup", "key": context["key"]}


def run_task(task, patch):
    ctx = {"wanted": task["value"], "key": task["key"]}
    trace = []
    if "episode_init" in patch:
        ctx["session"] = "ready"
    for step in range(3):
        if "pre_decision" in patch and task["fault"] == "alias":
            ctx["key"] = task["canonical"]
        action = target(ctx)
        if "pre_action" in patch and action["tool"] == "lookup":
            action = {**action, "key": action["key"].lower()}
        if action["tool"] == "finish":
            return 1, trace
        if task["fault"] == "session" and ctx.get("session") != "ready":
            response = {"error": "session_missing"}
        elif action["key"] != task["canonical"]:
            response = {"error": "alias_unknown" if task["fault"] == "alias" else "case_mismatch"}
        elif task["fault"] == "wrapped":
            response = {"data": {"value": task["value"]}}
        else:
            response = {"value": task["value"]}
        if "post_feedback" in patch and "data" in response:
            response = response["data"]
        ctx["result"] = response.get("value")
        trace.append({"step": step, "action": action, "response": response})
    return 0, trace


def engineer(failures):
    patch = set()
    for _, trace in failures:
        for row in trace:
            response = row["response"]
            patch.update({"session_missing": {"episode_init"}, "alias_unknown": {"pre_decision"}, "case_mismatch": {"pre_action"}}.get(response.get("error"), set()))
            if "data" in response:
                patch.add("post_feedback")
    return patch


def tasks(offset):
    data = []
    for i in range(20):
        fault = ["none", "session", "alias", "case", "wrapped"][i % 5]
        canonical = f"item{offset+i}"
        key = canonical.upper() if fault == "case" else "alias" if fault == "alias" else canonical
        data.append({"fault": fault, "key": key, "canonical": canonical, "value": offset+i})
    return data


def evaluate(data, patch):
    return sum(run_task(t, patch)[0] for t in data)/len(data)


def experiment():
    evidence, held_out = tasks(0), tasks(100)
    failures = [(t, run_task(t, set())[1]) for t in evidence if not run_task(t, set())[0]]
    patch = engineer(failures)
    metrics = {"base": evaluate(held_out, set()), "full": evaluate(held_out, patch)}
    metrics.update({f"without_{hook}": evaluate(held_out, patch-{hook}) for hook in HOOKS})
    return {"note": "課題を解く関数は固定し、失敗に合わせて用意した処理を選びます。別の商品IDでも失敗の種類は同じです。学習したモデルや未知の失敗は扱いません。", "patch_hooks": sorted(patch), "experiments": [{"name": "商品IDを変え、処理を一つずつ外して比べる", "n": {"evidence": 20, "held_out": 20}, "metrics": metrics}], "failure_example": failures[0][1], "full_batch_before": evaluate(evidence, set()), "full_batch_after": evaluate(evidence, patch)}


def compute():
    result = experiment()
    result["verification"] = {
        "mechanism": "PARTIAL", "performance": "NOT TESTED",
        "scaling": "NOT TESTED", "production_applicability": "NOT TESTED",
    }
    return result


if __name__ == "__main__":
    Path(__file__).with_name("results.json").write_text(json.dumps(compute(), ensure_ascii=False, indent=2)+"\n")
