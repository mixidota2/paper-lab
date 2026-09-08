"""Deterministic runtime replay with explicit derived state; no LLM calls.

The symbolic kv field is NOT an attention cache. Probe behavior is scripted,
so this illustrates audit blind spots rather than measuring model leakage.
"""
from copy import deepcopy
import json
from pathlib import Path

SECRET = "CANARY-731"


def initial():
    return {"transcript": [], "memory": {}, "summary": [], "kv": [],
            "avoid_a": False, "safe_total": 0, "silent": False}


def advance(state, observation):
    state = deepcopy(state)
    # Non-target observations are kept and recomputed in both worlds.
    state["safe_total"] += observation["safe_value"]
    state["transcript"].append(dict(observation))
    if "secret" in observation:
        state["memory"]["secret"] = observation["secret"]
        state["avoid_a"] = True
    known = state["memory"].get("secret", "")
    state["summary"].append({"known": known, "plan": "B" if state["avoid_a"] else "A"})
    state["kv"].append({"derived_secret": known, "avoid_a": state["avoid_a"], "total": state["safe_total"]})
    return state


def replay(state, observations):
    count = 0
    for obs in observations:
        state = advance(state, obs)
        count += 1
    return state, count


def observations(total, tau):
    if not 1 <= tau <= total:
        raise ValueError("tau must be inside session")
    obs = [{"safe_value": n} for n in range(1, total + 1)]
    obs[tau - 1]["secret"] = SECRET
    return obs


def sanitize(obs):
    return [{k: v for k, v in o.items() if k != "secret"} for o in obs]


def probes(state):
    # Scripted task probe respects silence; introspection reads derived state.
    known = next((v["derived_secret"] for v in reversed(state["kv"]) if v["derived_secret"]), "")
    return {"task": "unknown" if state["silent"] else known,
            "introspection": known, "summary": next((s["known"] for s in reversed(state["summary"]) if s["known"]), "")}


def audit(state, reference, count):
    answers = probes(state)
    action = "B" if state["avoid_a"] else "A"
    ref_action = "B" if reference["avoid_a"] else "A"
    return {"task_string_leak": int(SECRET in answers["task"]),
            "leak_at_probes": int(any(SECRET in a for a in answers.values())),
            "behavioral_choice": action, "behavioral_mismatch": int(action != ref_action),
            "behavioral_answer_string_leak": int(SECRET in action),
            "safe_total": state["safe_total"], "same_runtime_as_reference": state == reference,
            "recomputed_steps": count}


def experiment(total=12, tau=8, checkpoint=None):
    obs = observations(total, tau)
    clean = sanitize(obs)
    states = [initial()]
    for o in obs:
        states.append(advance(states[-1], o))
    contaminated = states[-1]
    reference, full_count = replay(initial(), clean)
    delete = deepcopy(contaminated)
    delete["memory"].pop("secret", None)
    instruction = deepcopy(contaminated)
    instruction["silent"] = True
    redact = deepcopy(contaminated)
    redact["memory"].pop("secret", None)
    redact["transcript"] = sanitize(redact["transcript"])
    # Stronger string scrub also misses a derived choice that has no canary.
    scrub = deepcopy(redact)
    for s in scrub["summary"]:
        s["known"] = ""
    for k in scrub["kv"]:
        k["derived_secret"] = ""
    boundary = tau - 1 if checkpoint is None else checkpoint
    if not 0 <= boundary < tau:
        raise ValueError("checkpoint must be clean")
    selective, selective_count = replay(states[boundary], clean[boundary:])
    methods = {"削除なし": (contaminated, 0), "記録削除": (delete, 0),
               "忘却指示": (instruction, 0), "元入力の除去": (redact, 0),
               "全文字列の除去": (scrub, 0), "全再実行": (reference, full_count),
               "選択的再実行": (selective, selective_count)}
    return {"name": f"T={total}, τ={tau}, checkpoint={boundary}", "dataset": "決定的な状態機械",
            "metrics": {name: audit(s, reference, n) for name, (s, n) in methods.items()}}


def compute():
    return {"note": "合成状態機械。KVは辞書の履歴でありTransformerではない。再計算は状態遷移回数だけを数え、token数・時間を測らない。",
            "verification": {"mechanism": "PARTIAL", "performance": "NOT TESTED", "scaling": "NOT TESTED", "production_applicability": "NOT TESTED"},
            "experiments": [experiment(), experiment(tau=1), experiment(tau=12), experiment(checkpoint=4)],
            "cost_sweep": [{"tau": t, "full": 12, "selective": experiment(tau=t)["metrics"]["選択的再実行"]["recomputed_steps"]} for t in range(1, 13)],
            "probe_contract": "task obeys silent; introspection reads symbolic kv; summary reads derived notes; choice reads avoid_a",
            "omissions": ["real LLM", "stochastic decoding", "provenance discovery", "external side effects", "token-level attribution"]}


if __name__ == "__main__":
    result = compute()
    Path(__file__).with_name("results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result["experiments"][0], ensure_ascii=False, indent=2))
